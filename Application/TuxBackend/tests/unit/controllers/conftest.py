from unittest.mock import MagicMock

import pytest

from db.db import Database
from models.schemas import ChatAgentRequest


@pytest.fixture(scope="module")
def make_chat_request():
    def _make(
        chat_id: int = 1,
        user_id: int = 1,
        date_sent: str = "2026-09-04T12:00:00",
        **overrides,
    ):
        return ChatAgentRequest(
            token="X",
            userMessage="A",
            chatId=chat_id,
            userId=user_id,
            dateSent=date_sent,
        )

    return _make


@pytest.fixture(scope="module")
def mock_db():
    db = MagicMock(spec=Database)
    return db
