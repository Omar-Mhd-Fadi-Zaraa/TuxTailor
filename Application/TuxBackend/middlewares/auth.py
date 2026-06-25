import httpx

from fastapi import HTTPException

async def validate_ollama_url(base_url: str, timeout: float = 5.0) -> RuntimeError | None:
    url = base_url.rstrip("/")
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            resp = await client.get(f"{url}/api/version")
            resp.raise_for_status()
    except httpx.RequestError as e:
        raise RuntimeError(f"Ollama unreachable at {url}: {e}") from e
    except httpx.HTTPStatusError as e:
        raise RuntimeError(f"Ollama returned {e.response.status_code} at {url}") from e


def verify_token(token: str | None):
    if token != "":
        raise HTTPException(status_code=402, detail="Unauthorized request")
