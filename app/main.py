from fastapi import FastAPI
from sqlalchemy import text

from app import models  # noqa: F401
from app.core.config import settings
from app.db import engine
from app.routes.pipelines import router as pipelines_router
from app.routes.runs import router as runs_router

app = FastAPI(title=settings.app_name)

app.include_router(pipelines_router)
app.include_router(runs_router)


@app.get("/health")
async def get_health():
    return {
        "status": "ok",
        "app_name": settings.app_name,
    }


@app.get("/db-health")
def get_db_health():
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))
    return {"database": "ok"}
