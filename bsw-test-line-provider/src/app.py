

from fastapi import FastAPI

from src.api.v1.events.events import router

app = FastAPI(
    title="Line Provider API",
    version="1.0.0",
    description="API для управления событиями ставок"
)
app.include_router(router)