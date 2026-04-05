from fastapi import FastAPI

from app.db import Base, engine
from app import models #F401
from app.routes.pipelines import router as pipelines_router


Base.metadata.create_all(bind=engine)

app = FastAPI(title="Mini CI Runner")


@app.get("/health")
async def get_health():
	return {"status": "ok"}

app.include_router(pipelines_router) 
