from fastapi import FastAPI

import app.core.config  # noqa: F401
from app.core.auth import router as auth_router
from app.api.router import api_router

app = FastAPI(title="Stipend API")

app.include_router(auth_router)
app.include_router(api_router)


@app.get("/")
def healthcheck():
    return {"status": "ok"}
