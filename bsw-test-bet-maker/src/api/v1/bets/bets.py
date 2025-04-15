import time

from fastapi import APIRouter, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from src.storage.storage import BetStorage,get_bet_storage
from starlette import status
import httpx
from src.api.v1.events.utils import get_http_client,get_events_cache
from .schemas import BetCreate, BetResponse, EventCallback, BetState
from src.config import settings
from src.api.v1.events.events import fetch_events_from_provider

router = APIRouter(prefix="/api/v1/bets", tags=["Bets"])


@router.post(
    "",
    response_model=BetResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        404: {"description": "Событие не найдено"},
        400: {"description": "Событие уже завершено или дедлайн прошел"},
        500: {"description": "Ошибка при создании ставки"}
    }
)
async def create_bet(
        bet: BetCreate,
        storage: BetStorage = Depends(get_bet_storage),
        client: httpx.AsyncClient = Depends(get_http_client),
        cache: dict = Depends(get_events_cache)
):
    try:
        current_time = time.time()
        cached_events = cache.get("data", [])
        event = next((e for e in cached_events if e.event_id == bet.event_id), None)


        if not event:
            print(f"Event {bet.event_id} not in cache, fetching from provider...")
            all_events = await fetch_events_from_provider(client, settings.line_provider_url)
            event = next((e for e in all_events if e.event_id == bet.event_id), None)

            if not event:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Событие не найдено"
                )


        if event.state != "NEW":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Нельзя сделать ставку на завершенное событие"
            )

        if event.deadline <= current_time:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Дедлайн для ставок на это событие уже прошел"
            )


        bet_data = jsonable_encoder(bet)
        return await storage.create_bet(bet_data)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при создании ставки: {str(e)}"
        )
@router.get("", response_model=list[BetResponse])
async def get_bets(storage: BetStorage =  Depends(get_bet_storage)):
    return await storage.get_bets()


@router.post("/callback")
async def handle_callback(
    data: EventCallback,
    storage: BetStorage =Depends(get_bet_storage)
):
    bets = await storage.get_bets()
    for bet in bets:
        if bet.event_id == data.event_id:
            new_state = BetState.WIN if data.new_status == "FINISHED_WIN" else BetState.LOSE
            await storage.update_bet_state(bet.bet_id, new_state)
    return {"status": "updated"}