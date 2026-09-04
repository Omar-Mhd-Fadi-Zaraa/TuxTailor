import asyncio
import sqlite3

import pytest
from pwdlib.exceptions import UnknownHashError

from controllers import database_controller
from middlewares.auth import verify_password
from models.messages import (
    AssistantBehaviorMessage,
    AssistantMessage,
    ToolResponseMessage,
    UserMessage,
)
from models.schemas import ChatAddRequest, UserAddRequest


@pytest.mark.insert
def test_AddUserMessage(mock_db, make_chat_request):
    mock_db.AddMessage.return_value = None
    msg = make_chat_request()
    input = UserMessage(request=msg, content="Hi")

    try:
        asyncio.run(
            database_controller.AddUserMessage(userMessage=input, database=mock_db)
        )
    except TypeError:
        pytest.fail("AddUserMessage failed with TypeError")
    except RuntimeError:
        pytest.fail("AddUserMessage failed with RuntimeError")

    input.lcmsg.content = []
    with pytest.raises(TypeError) as err_info:
        asyncio.run(
            database_controller.AddUserMessage(userMessage=input, database=mock_db)
        )

    assert str(err_info.value) == "Message content must be a string"

    input.lcmsg.content = "A"
    mock_db.AddMessage.side_effect = sqlite3.OperationalError()
    with pytest.raises(RuntimeError) as err_info:
        asyncio.run(
            database_controller.AddUserMessage(userMessage=input, database=mock_db)
        )

    assert str(err_info.value) == "Couldn't add user message: "
    mock_db.AddMessage.assert_called_with(
        input.chat_id, input.user_id, input.lcmsg.content, input.role, input.date_sent
    )
    mock_db.AddMessage.reset_mock(side_effect=True, return_value=True)


@pytest.mark.insert
def test_AddAiMessage(mock_db, make_chat_request):
    mock_db.AddMessage.return_value = None
    msg = make_chat_request()
    input = AssistantMessage(reqeust=msg, content="Hi", tool_calls=[])

    try:
        asyncio.run(database_controller.AddAiMessage(aiMessage=input, database=mock_db))
    except TypeError:
        pytest.fail("AddAiMessage failed with TypeError")
    except RuntimeError:
        pytest.fail("AddAiMessage failed with RuntimeError")

    input.lcmsg.content = []
    with pytest.raises(TypeError) as err_info:
        asyncio.run(database_controller.AddAiMessage(aiMessage=input, database=mock_db))

    assert str(err_info.value) == "Message content must be a string"

    input.lcmsg.content = "A"
    mock_db.AddMessage.side_effect = sqlite3.OperationalError()
    with pytest.raises(RuntimeError) as err_info:
        asyncio.run(database_controller.AddAiMessage(aiMessage=input, database=mock_db))

    assert str(err_info.value) == "Couldn't add ai message: "
    mock_db.AddMessage.assert_called_with(
        input.chat_id,
        input.user_id,
        input.lcmsg.content,
        input.role,
        input.date_sent,
        toolCall=False,
        toolCalls=None,
    )
    mock_db.AddMessage.reset_mock(side_effect=True, return_value=True)


@pytest.mark.insert
def test_AddToolMessage(mock_db, make_chat_request):
    mock_db.AddMessage.return_value = None
    msg = make_chat_request()
    input = ToolResponseMessage(
        request=msg, content="Hi", tool_call_id=1, preceeding_message="Hi"
    )

    try:
        asyncio.run(
            database_controller.AddToolMessage(toolMessage=input, database=mock_db)
        )
    except TypeError:
        pytest.fail("AddToolMessage failed with TypeError")
    except RuntimeError:
        pytest.fail("AddToolMessage failed with RuntimeError")

    input.lcmsg.content = []
    with pytest.raises(TypeError) as err_info:
        asyncio.run(
            database_controller.AddToolMessage(toolMessage=input, database=mock_db)
        )

    assert str(err_info.value) == "Message content must be a string"

    input.lcmsg.content = "A"
    mock_db.AddMessage.side_effect = sqlite3.OperationalError()
    with pytest.raises(RuntimeError) as err_info:
        asyncio.run(
            database_controller.AddToolMessage(toolMessage=input, database=mock_db)
        )

    assert str(err_info.value) == "Couldn't add tool message: "
    mock_db.AddMessage.assert_called_with(
        input.chat_id,
        input.user_id,
        input.lcmsg.content,
        input.role,
        input.date_sent,
        toolCallStatus=input.lcmsg.status,
        preceedingMessage=input.preceeding_message,
    )
    mock_db.AddMessage.reset_mock(side_effect=True, return_value=True)


@pytest.mark.insert
def test_AddSystemMessage(mock_db, make_chat_request):
    mock_db.AddMessage.return_value = None
    msg = make_chat_request()
    input = AssistantBehaviorMessage(request=msg, content="Hi")

    try:
        asyncio.run(
            database_controller.AddSystemMessage(systemMessage=input, database=mock_db)
        )
    except TypeError:
        pytest.fail("AddSystemMessage failed with TypeError")
    except RuntimeError:
        pytest.fail("AddSystemMessage failed with RuntimeError")

    input.lcmsg.content = []
    with pytest.raises(TypeError) as err_info:
        asyncio.run(
            database_controller.AddSystemMessage(systemMessage=input, database=mock_db)
        )

    assert str(err_info.value) == "Message content must be a string"

    input.lcmsg.content = "A"
    mock_db.AddMessage.side_effect = sqlite3.OperationalError()
    with pytest.raises(RuntimeError) as err_info:
        asyncio.run(
            database_controller.AddSystemMessage(systemMessage=input, database=mock_db)
        )

    assert str(err_info.value) == "Couldn't add system message: "
    mock_db.AddMessage.assert_called_with(
        input.chat_id,
        input.user_id,
        input.lcmsg.content,
        input.role,
        input.date_sent,
    )
    mock_db.AddMessage.reset_mock(side_effect=True, return_value=True)


@pytest.mark.insert
def test_AddChat(mock_db):
    mock_db.AddChat.return_value = 1
    input = ChatAddRequest(userId=1, title="X", dateCreated="2026-9-1")

    ret = asyncio.run(database_controller.AddChat(input, mock_db))

    assert ret == 1

    mock_db.AddChat.side_effect = sqlite3.OperationalError()
    with pytest.raises(RuntimeError) as err_info:
        asyncio.run(database_controller.AddChat(input, mock_db))

    assert str(err_info.value) == "Couldn't add chat: "
    mock_db.AddChat.assert_called_with(input.user_id, input.title, input.date_created)


@pytest.mark.insert
def test_AddUser(mock_db):
    mock_db.AddUser.return_value = 1
    input = UserAddRequest(
        userName="X",
        password="A",
        level="Z",
        dateCreated="2026-9-1",
        systemPrompt="D",
        distroOfChoice="H",
    )

    ret = asyncio.run(database_controller.AddUser(input, mock_db))

    assert ret == 1

    mock_db.AddUser.side_effect = sqlite3.OperationalError()
    with pytest.raises(RuntimeError) as err_info:
        asyncio.run(database_controller.AddUser(input, mock_db))

    assert str(err_info.value) == "Couldn't add user: "
    hash = mock_db.AddUser.call_args.args[1]
    assert verify_password(input.password, hash)


@pytest.mark.select
def test_Login(mock_db, mocker):
    mock_db.GetUser.return_value = (1, "X")

    with pytest.raises(UnknownHashError) as err_info:
        asyncio.run(database_controller.Login("A", "X", mock_db))

    assert (
        str(err_info.value)
        == "This hash can't be identified. Make sure it's valid and that its corresponding hasher is enabled."
    )

    mock_pass_ver = mocker.patch(
        "controllers.database_controller.verify_password", return_value=False
    )
    ret = asyncio.run(database_controller.Login("A", "X", mock_db))

    id, found = ret
    assert id == 1
    assert found == False

    mock_pass_ver.return_value = True
    ret = asyncio.run(database_controller.Login("A", "X", mock_db))

    id, found = ret
    assert id == 1
    assert found == True

    mock_db.GetUser.return_value = None
    ret = asyncio.run(database_controller.Login("A", "X", mock_db))

    id, found = ret
    assert id is None
    assert found == False

    mock_db.GetUser.side_effect = sqlite3.OperationalError()
    with pytest.raises(RuntimeError) as err_info:
        asyncio.run(database_controller.Login("A", "X", mock_db))

    assert str(err_info.value) == "Couldn't log in: "

    mock_db.GetUser.assert_called_with("A")
    mock_pass_ver.assert_called_with("X", "X")


@pytest.mark.select
def test_GetUserSysMessage(mock_db):
    mock_db.GetUserSysPrompt.return_value = ["Hi"]

    ret = asyncio.run(database_controller.GetUserSysMessage(1, mock_db))

    assert ret == "Hi"

    mock_db.GetUserSysPrompt.return_value = None

    ret = asyncio.run(database_controller.GetUserSysMessage(1, mock_db))

    assert ret is None

    mock_db.GetUserSysPrompt.side_effect = sqlite3.OperationalError()

    with pytest.raises(RuntimeError) as err_info:
        asyncio.run(database_controller.GetUserSysMessage(1, mock_db))

    assert str(err_info.value) == "Couldn't fetch user system prompt: "

    mock_db.GetUserSysPrompt.assert_called_with(1)


@pytest.mark.select
def test_GetUserChats(mock_db):
    mock_db.GetUserChats.return_value = [
        (1, 1, "Chat One", 3, "2026-01-01"),
        (2, 1, "Chat Two", 0, "2026-01-02"),
    ]

    ret = asyncio.run(database_controller.GetUserChats(1, mock_db))

    assert ret == [(1, "Chat One"), (2, "Chat Two")]

    mock_db.GetUserChats.return_value = []

    ret = asyncio.run(database_controller.GetUserChats(1, mock_db))

    assert ret == []

    mock_db.GetUserChats.side_effect = sqlite3.OperationalError()

    with pytest.raises(RuntimeError) as err_info:
        asyncio.run(database_controller.GetUserChats(1, mock_db))

    assert str(err_info.value) == "Could not get user chats for user 1: "

    mock_db.GetUserChats.assert_called_with(1)


@pytest.mark.select
def test_GetChatMessages(mock_db):
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

    ret = asyncio.run(database_controller.GetChatMessages(1, mock_db))

    assert ret == [
        (1, "Hi there", "user"),
        (2, "Hello! How can I help?", "assistant"),
        (3, "What's the weather?", "user"),
    ]

    mock_db.GetChatMessages.return_value = []

    ret = asyncio.run(database_controller.GetChatMessages(1, mock_db))

    assert ret == []

    mock_db.GetChatMessages.side_effect = sqlite3.OperationalError()

    with pytest.raises(RuntimeError) as err_info:
        asyncio.run(database_controller.GetChatMessages(1, mock_db))

    assert str(err_info.value) == "Could not get chat messages for chat 1: "

    mock_db.GetChatMessages.assert_called_with(1)
