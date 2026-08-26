import asyncio

from config import consts
from middlewares.auth import validate_ollama_url


def test_ollama_connection():
    assert consts.OLLAMA_BASE_URL != None
    assert asyncio.run(validate_ollama_url(consts.OLLAMA_BASE_URL)) == None
