import asyncio
import sqlite3

import pytest

from controllers import database_controller
from models.messages import (
    AssistantBehaviorMessage,
    AssistantMessage,
    ToolResponseMessage,
    UserMessage,
)


@pytest.mark.insert
def test_AddUserMessage(mock_db, make_chat_request, mocker):
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
def test_AddAiMessage(mock_db, make_chat_request, mocker):
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
def test_AddToolMessage(mock_db, make_chat_request, mocker):
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
def test_AddSystemMessage(mock_db, make_chat_request, mocker):
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
