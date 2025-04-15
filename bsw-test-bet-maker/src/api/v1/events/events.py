import time
import httpx
import asyncio
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from src.config import settings
from src.api.v1.bets.schemas import Event, EventState, PageResponseFromProvider
from src.api.v1.events.utils import get_http_client,get_events_cache


router = APIRouter(prefix="/api/v1/events", tags=["Events"])

cache_update_lock = asyncio.Lock()


async def fetch_events_from_provider(
        client: httpx.AsyncClient,
        provider_base_url: str
) -> List[Event]:
    """Запрашивает события у line-provider."""
    events_list_url = f"{provider_base_url}/api/v1/events/events-list"

    payload = {
        "page_number": 1,
        "page_size": 100
       
    }

    try:
        response = await client.post(events_list_url, json=payload, timeout=5.0)
        response.raise_for_status()
        return PageResponseFromProvider.parse_obj(response.json()).items

    except httpx.HTTPStatusError as exc:
        error_detail = f"Line-provider error: {exc.response.status_code} - {exc.response.text}"
        raise HTTPException(status_code=502, detail=error_detail)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("", response_model=List[Event])
async def get_active_events(
        client: httpx.AsyncClient = Depends(get_http_client),
        cache: dict = Depends(get_events_cache),
):
    """Возвращает активные события (NEW и дедлайн не наступил)"""
    current_time = time.time()

    def is_active_event(event: Event) -> bool:
        return event.state == "NEW" and event.deadline > current_time


    if cache["data"] is not None and cache["expiry"] > current_time:
        active_events = [event for event in cache["data"] if is_active_event(event)]
        return active_events


    async with cache_update_lock:

        if cache["data"] is not None and cache["expiry"] > current_time:
            active_events = [event for event in cache["data"] if is_active_event(event)]
            return active_events

        try:

            all_events = await fetch_events_from_provider(client, settings.line_provider_url)

            cache["data"] = all_events
            cache["expiry"] = current_time + settings.cache_duration_seconds


            active_events = [event for event in all_events if is_active_event(event)]
            return active_events

        except HTTPException as http_exc:

            if cache["data"] is not None:
                active_events = [event for event in cache["data"] if is_active_event(event)]
                return active_events
            raise http_exc
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error"
            )