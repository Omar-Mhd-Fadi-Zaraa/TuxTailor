from fastapi import FastAPI
from scalar_fastapi import get_scalar_api_reference

from routes.routes import base, agent, lifespan
from db.db import Database

db = Database()

app = FastAPI(lifespan=lifespan)
app.include_router(base)
app.include_router(agent)


@app.get("/scalar", include_in_schema=False)
async def scalar_html():
    return get_scalar_api_reference(
        openapi_url=app.openapi_url,
        title=app.title,
        dark_mode=True
    )
