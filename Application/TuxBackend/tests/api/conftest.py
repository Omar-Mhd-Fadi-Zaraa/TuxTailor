from fastapi.testclient import TestClient
from app import main
import pytest


@pytest.fixture(scope="module")
def test_client():
    with TestClient(main.app) as client:
        yield client
