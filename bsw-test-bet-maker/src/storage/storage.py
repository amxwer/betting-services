import redis.asyncio as redis
from uuid import uuid4
from fastapi import Depends
from src.config import settings
from src.api.v1.bets.schemas import BetResponse, BetState
from typing import List

class BetStorage:
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client

    async def create_bet(self, bet_data: dict) -> BetResponse:
        bet_id = str(uuid4())
        bet = BetResponse(
            bet_id=bet_id,
            **bet_data,
            state=BetState.PENDING
        )
        await self.redis.hset(f"bet:{bet_id}", mapping=bet.dict())
        return bet

    async def get_bets(self) -> List[BetResponse]:
        """Возвращает список всех ставок"""
        if not self.redis:
            raise RuntimeError("Redis connection not initialized")

        try:
            keys = await self.redis.keys("bet:*")
            if not keys:
                return []

            bets = []
            for key in keys:

                bet_data = await self.redis.hgetall(key)
                if bet_data:

                    decoded_data = {
                        k.decode('utf-8'): v.decode('utf-8')
                        for k, v in bet_data.items()
                    }
                    bets.append(BetResponse(**decoded_data))
            return bets
        except Exception as e:
            raise RuntimeError(f"Failed to get bets: {str(e)}")
    async def update_bet_state(self, bet_id: str, state: BetState):
        """Обновляет статус ставки"""
        if not self.redis:
            raise RuntimeError("Redis connection not initialized")

        try:
            exists = await self.redis.exists(f"bet:{bet_id}")
            if not exists:
                raise ValueError(f"Bet {bet_id} not found")

            await self.redis.hset(f"bet:{bet_id}", "state", state.value)
        except Exception as e:
            raise RuntimeError(f"Failed to update bet state: {str(e)}")



async def get_bet_storage() -> BetStorage:
    redis_client = redis.from_url(settings.redis_url)
    try:
        await redis_client.ping()
        return BetStorage(redis_client)
    except Exception as e:
        await redis_client.close()
        raise RuntimeError(f"Redis connection error: {str(e)}")