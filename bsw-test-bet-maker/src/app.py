from fastapi import FastAPI, Depends
from .api.v1.bets.bets import router as bets_router
from src.storage.storage import BetStorage
from .api.v1.events.events import router as events_router
from src.api.v1.events.utils import get_http_client,get_events_cache
from src.config import settings
import redis.asyncio as redis


app = FastAPI()


async def get_redis_client():
    redis_client = redis.from_url(settings.redis_url)
    try:
        await redis_client.ping()
        return redis_client
    except Exception as e:
        await redis_client.close()
        raise RuntimeError(f"Redis connection error: {str(e)}")

async def get_storage() -> BetStorage:
    redis_client = await get_redis_client()
    return BetStorage(redis_client)

@app.on_event("startup")
async def startup():

    await get_redis_client()

app.include_router(bets_router, dependencies=[Depends(get_storage)])
app.include_router(
    events_router,
    dependencies=[Depends(get_http_client), Depends(get_events_cache)]
)