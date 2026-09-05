import asyncio
import json
from unittest.mock import AsyncMock, MagicMock

import httpx2
import pytest
from httpx2._types import AsyncByteStream

from app.main import app
from db.db import Database
from routes.routes import get_chat_agent, get_db


class StreamingASGITransport(httpx2.AsyncBaseTransport):
    """
    Like httpx2.ASGITransport, but returns as soon as response headers are
    sent and forwards each response.body chunk to the caller as it's
    produced, instead of collecting the whole response before returning.
    """

    def __init__(self, app, client: tuple = ("127.0.0.1", 123)):
        self.app = app
        self.client = client

    async def handle_async_request(self, request: httpx2.Request) -> httpx2.Response:
        scope = {
            "type": "http",
            "asgi": {"version": "3.0"},
            "http_version": "1.1",
            "method": request.method,
            "headers": [(k.lower(), v) for (k, v) in request.headers.raw],
            "scheme": request.url.scheme,
            "path": request.url.path,
            "raw_path": request.url.raw_path.split(b"?")[0],
            "query_string": request.url.query,
            "server": (request.url.host, request.url.port),
            "client": self.client,
            "root_path": "",
        }

        request_body_chunks = request.stream.__aiter__()
        request_complete = False
        response_started = asyncio.Event()
        response_complete = asyncio.Event()
        body_queue: asyncio.Queue = asyncio.Queue()

        status_code = None
        response_headers = None
        app_exception: BaseException | None = None

        async def receive():
            nonlocal request_complete
            if request_complete:
                await response_complete.wait()
                return {"type": "http.disconnect"}
            try:
                body = await request_body_chunks.__anext__()
            except StopAsyncIteration:
                request_complete = True
                return {"type": "http.request", "body": b"", "more_body": False}
            return {"type": "http.request", "body": body, "more_body": True}

        async def send(message):
            nonlocal status_code, response_headers
            if message["type"] == "http.response.start":
                status_code = message["status"]
                response_headers = message.get("headers", [])
                response_started.set()
            elif message["type"] == "http.response.body":
                body = message.get("body", b"")
                more_body = message.get("more_body", False)
                if body and request.method != "HEAD":
                    await body_queue.put(body)
                if not more_body:
                    response_complete.set()

        async def run_app():
            nonlocal app_exception
            try:
                await self.app(scope, receive, send)
            except BaseException as exc:
                app_exception = exc
            finally:
                response_started.set()
                response_complete.set()
                await body_queue.put(None)

        app_task = asyncio.create_task(run_app())

        await response_started.wait()

        """Uncomment this, and comment the 2 lines above to cause a deadlock"""
        # await self.app(scope, receive, send)

        if app_exception is not None:
            raise app_exception

        class _QueueStream(AsyncByteStream):
            def __init__(self):
                self._gen = self._iterate()

            async def _iterate(self):
                try:
                    while True:
                        chunk = await body_queue.get()
                        if chunk is None:
                            break
                        yield chunk
                finally:
                    if not app_task.done():
                        app_task.cancel()
                    await asyncio.gather(app_task, return_exceptions=True)

            async def __aiter__(self):
                async for chunk in self._gen:
                    yield chunk

            async def aclose(self) -> None:
                await self._gen.aclose()

        return httpx2.Response(
            status_code, headers=response_headers, stream=_QueueStream()
        )


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.fixture
def mock_db():
    db = MagicMock(spec=Database)
    return db


@pytest.mark.anyio
@pytest.mark.post
async def test_invoke_agent(mocker, mock_db):
    mocker.patch("routes.routes.validate_ollama_url", return_value=None)
    mock_db.GetChatMessages.return_value = [
        (1, 1, 1, "Hi there", "user", None, None, None, None, "2026-01-01T12:00:00"),
        (
            2,
            1,
            1,
            "Hello! How can I help?",
            "assistant",
            False,
            None,
            None,
            None,
            "2026-01-01T12:00:05",
        ),
        (
            3,
            1,
            1,
            "What's the weather?",
            "user",
            None,
            None,
            None,
            None,
            "2026-01-01T12:01:00",
        ),
    ]
    mocker.patch("routes.routes.AddUserMessage", new=AsyncMock())
    mocker.patch(
        "routes.routes.GetUserSysMessage",
        new=AsyncMock(return_value="You are a helpful assistant"),
    )

    release = asyncio.Event()

    async def controlled_stream(agent, messages, result):
        yield json.dumps({"type": "text", "content": "hello"}) + "\n"
        await release.wait()  # won't resolve until the test says so
        yield json.dumps({"type": "text", "content": "world"}) + "\n"
        result["messages"] = []

    mocker.patch("routes.routes.stream_filtered_response", new=controlled_stream)
    persist_mock = mocker.patch("routes.routes.persist_agent_messages", new=AsyncMock())

    app.dependency_overrides[get_chat_agent] = lambda: AsyncMock()
    app.dependency_overrides[get_db] = lambda: mock_db

    transport = StreamingASGITransport(app=app)
    async with asyncio.timeout(5), httpx2.AsyncClient(
        transport=transport, base_url="http://test"
    ) as client, client.stream(
        "POST",
        "/chat/invoke",
        json={
            "token": "x",
            "userId": 1,
            "chatId": 1,
            "userMessage": "hi",
            "dateSent": "2026-09-05T00:00:00",
        },
    ) as response:
        lines = response.aiter_lines()
        assert json.loads(await lines.__anext__()) == {
            "type": "text",
            "content": "hello",
        }

        persist_mock.assert_not_called()  # proves persistence waits for full drain
        release.set()

        assert json.loads(await lines.__anext__()) == {
            "type": "text",
            "content": "world",
        }

    persist_mock.assert_called_once()
    app.dependency_overrides.clear()


def test_add_chat(
    test_client,
    mocker,
):
    success_fake_result = 1
    success_fake_arguments = {
        "userId": 1,
        "title": "Test Title",
        "dateCreated": "2026-7-8",
    }

    mocker.patch("routes.routes.AddChat", return_value=success_fake_result)

    response = test_client.post(
        "/chat",
        json=success_fake_arguments,
    )
    assert response.status_code == 200
    assert response.json() == {"chatId": 1}

    mocker.patch("routes.routes.AddChat", side_effect=RuntimeError())

    response = test_client.post("/chat", json=success_fake_arguments)

    assert response.status_code == 500
    assert response.json() == {"detail": "Couldn't add chat: "}


@pytest.mark.post
def test_add_user(test_client, mocker):
    AddUser_success_return_value = 1
    route_arguments = {
        "userName": "A",
        "password": "1233",
        "level": "X",
        "dateCreated": "4-9-2026",
        "systemPrompt": "F",
        "distroOfChoice": "P",
    }

    AddUser_fail_return_value = RuntimeError()

    mocker.patch("routes.routes.AddUser", return_value=AddUser_success_return_value)

    response = test_client.post("/user/signup", json=route_arguments)

    assert response.status_code == 200
    assert response.json() == {"userId": AddUser_success_return_value}

    mocker.patch("routes.routes.AddUser", side_effect=AddUser_fail_return_value)

    response = test_client.post("/user/signup", json=route_arguments)

    assert response.status_code == 500
    assert response.json() == {"detail": "Couldn't add user: "}


@pytest.mark.post
def test_log_in(test_client, mocker):
    Login_success_logged_return_value = (1, True)
    Login_success_not_logged_return_value = (1, False)
    route_arguments = {"userName": "A", "password": "B"}

    mocker.patch("routes.routes.Login", return_value=Login_success_logged_return_value)

    response = test_client.post("/user/login", json=route_arguments)

    assert response.status_code == 200
    assert response.json() == {"userId": 1, "message": "Logged in!"}

    mocker.patch(
        "routes.routes.Login", return_value=Login_success_not_logged_return_value
    )

    response = test_client.post("/user/login", json=route_arguments)

    assert response.status_code == 400
    assert response.json() == {
        "userId": None,
        "message": "Username or password is wrong",
    }


@pytest.mark.get
def test_get_user_chats(test_client, mocker):

    GetUserChats_success_return_value = [("1", "A"), ("2", "B"), ("3", "C")]
    GetChatMessages_success_return_value = [
        [1, "X", "A"],
        [2, "Y", "B"],
        [3, "Z", "C"],
    ]
    success_response_content = {}
    for id, title in GetUserChats_success_return_value:
        success_response_content[id] = {
            "title": title,
            "messages": GetChatMessages_success_return_value,
        }

    GetUserChats_fail_return_value = RuntimeError()
    GetChatMessages_fail_return_value = RuntimeError()
    fail_response_content = {
        "detail": {
            "message": "Error while getting chats",
            "errors": [{"type": "RuntimeError", "message": ""}],
        }
    }

    mocker.patch(
        "routes.routes.GetUserChats", return_value=GetUserChats_success_return_value
    )
    mocker.patch(
        "routes.routes.GetChatMessages",
        return_value=GetChatMessages_success_return_value,
    )

    response = test_client.get("user/chats/1")

    assert response.status_code == 200
    assert response.json() == success_response_content

    mocker.patch(
        "routes.routes.GetUserChats", side_effect=GetUserChats_fail_return_value
    )
    mocker.patch(
        "routes.routes.GetChatMessages", side_effect=GetChatMessages_fail_return_value
    )

    response = test_client.get("user/chats/1")

    assert response.status_code == 500
    assert response.json() == fail_response_content


@pytest.mark.patch
def test_update_chat_info(test_client, mocker):
    UpdateChatInfo_success_return_value = None
    UpdateChatInfo_fail_return_value = RuntimeError()
    route_arguments = {"title": "A", "systemPrompt": "X"}

    mocker.patch(
        "routes.routes.UpdateChatInfo", return_value=UpdateChatInfo_success_return_value
    )

    response = test_client.patch("/chat/1", json=route_arguments)

    assert response.status_code == 200
    assert response.json() == {"message": "chat 1 info updated"}

    mocker.patch(
        "routes.routes.UpdateChatInfo", side_effect=UpdateChatInfo_fail_return_value
    )

    response = test_client.patch("/chat/1", json=route_arguments)

    assert response.status_code == 500
    assert response.json() == {"detail": "Couldn't update chat info: "}


@pytest.mark.patch
def test_update_user_info(test_client, mocker):
    UpdateUser_success_return_value = None
    UpdateUser_fail_return_value = RuntimeError()
    route_arguments = {
        "level": "X",
        "systemPrompt": "Y",
        "distroOfChoice": "Z",
    }

    mocker.patch(
        "routes.routes.UpdateUser", return_value=UpdateUser_success_return_value
    )

    response = test_client.patch("/user/1", json=route_arguments)

    assert response.status_code == 200
    assert response.json() == {"message": "User updated"}

    mocker.patch("routes.routes.UpdateUser", side_effect=UpdateUser_fail_return_value)

    response = test_client.patch("/user/1", json=route_arguments)

    assert response.status_code == 500
    assert response.json() == {"detail": "Couldn't update user: "}
