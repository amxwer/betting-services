import time
from asyncio import Lock
from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query
from starlette import status
from src.api.v1.events.schemas import Event, EventState, UpdateEvent, PageResponseBaseSchema, \
    FilterSortInputSchema, SortOrders
import httpx
from src.config.config import settings
from fastapi import BackgroundTasks



router = APIRouter(prefix="/api/v1/events", tags=["events"])

events: dict[str, Event] = {
    '1': Event(event_id='1', coefficient=1.2, deadline=int(time.time()) + 600, state=EventState.NEW),
    '2': Event(event_id='2', coefficient=1.15, deadline=int(time.time()) + 60, state=EventState.NEW),
    '3': Event(event_id='3', coefficient=1.67, deadline=int(time.time()) + 90, state=EventState.NEW)
}
events_lock = Lock()


async def send_callback(event_id: str, status: EventState):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{settings.BET_MAKER_URL}/api/v1/bets/callback",
                json={
                    "event_id": event_id,
                    "new_status": status.value
                },
                timeout=5.0
            )
            response.raise_for_status()
            return response.json()
    except Exception as e:

        raise


@router.put("/create",response_model=Event)
async def create(event: Event,):
    async with events_lock:
        events[event.event_id] = event
    return event


@router.patch("/{event_id}", response_model=Event)
async def update_event(
        event_id: str,
        update_data: UpdateEvent,
) -> Event:
    async with events_lock:
        if event_id not in events:
            raise HTTPException(status_code=404, detail="Event not found")


        current_event = events[event_id]


        update_dict = update_data.dict(exclude_unset=True)
        for field, value in update_dict.items():
            setattr(current_event, field, value)
        try:
            updated_event = Event(**current_event.dict())
            events[event_id] = updated_event
            return updated_event

        except ValueError as e:
            raise HTTPException(status_code=422, detail=str(e))

@router.post("/{event_id}/finish",    response_model=Event)
async def finish_event(
        event_id: str,
        result: EventState = EventState.FINISHED_WIN,
        background_tasks: BackgroundTasks = BackgroundTasks()

) -> Event:
    async with events_lock:
        if event_id not in events:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Event not found"
            )

        if events[event_id].state != EventState.NEW:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Event already finished"
            )

        events[event_id].state = result

        callback_status = (
            EventState.FINISHED_WIN if result == EventState.FINISHED_WIN
            else EventState.FINISHED_LOSE
        )
        background_tasks.add_task(send_callback, event_id, callback_status)

        return events[event_id]


@router.post("/events-list", response_model=PageResponseBaseSchema)
async def all_events(
        input_data: FilterSortInputSchema
) -> PageResponseBaseSchema:
    async with events_lock:

        filtered_events = list(events.values())

        if input_data.filters:
            for filter_item in input_data.filters:
                filtered_events = [
                    e for e in filtered_events
                    if str(getattr(e, filter_item.field.value)) == filter_item.value
                ]


        if input_data.sort:
            for sort_item in reversed(input_data.sort):
                filtered_events.sort(
                    key=lambda x: getattr(x, sort_item.field.value),
                    reverse=sort_item.order == SortOrders.DESC
                )


        total_records = len(filtered_events)
        total_pages = (total_records + input_data.page_size - 1) // input_data.page_size
        start_idx = (input_data.page_number - 1) * input_data.page_size
        paginated_items = filtered_events[start_idx:start_idx + input_data.page_size]

        return PageResponseBaseSchema(
            page_number=input_data.page_number,
            page_size=input_data.page_size,
            total_pages=total_pages,
            total_records=total_records,
            items=paginated_items
        )