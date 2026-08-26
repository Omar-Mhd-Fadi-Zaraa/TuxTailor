from fastapi.testclient import TestClient
from app import main
from unittest.mock import AsyncMock, MagicMock, patch
import pytest


@pytest.fixture(scope="module")
def test_client():
    mock_response = MagicMock()
    mock_response.raise_for_status = lambda: None

    with patch("routes.routes.validate_ollama_url", return_value=None), patch(
        "httpx.AsyncClient.post", new_callable=AsyncMock, return_value=mock_response
    ), TestClient(main.app) as client:
        yield client
