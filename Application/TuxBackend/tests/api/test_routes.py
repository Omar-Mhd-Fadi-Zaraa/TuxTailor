import pytest


@pytest.mark.post
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
    fail_response_content = {"detail": "Could not get user chats: "}

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
