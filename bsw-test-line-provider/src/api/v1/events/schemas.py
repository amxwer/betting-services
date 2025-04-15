import enum
from datetime import datetime
from enum import Enum
from typing import Optional, List

from pydantic import BaseModel, condecimal
from pydantic.v1 import validator
class SortField(str, Enum):
    EVENT_ID = "event_id"
    COEFFICIENT = "coefficient"
    DEADLINE = "deadline"

class SortOrders(str, Enum):
    ASC = "asc"
    DESC = "desc"

class SortFieldBaseSchema(BaseModel):
    field: SortField
    order: SortOrders

class FilterFieldBaseSchema(BaseModel):
    field: SortField
    value: str



class FilterSortInputSchema(BaseModel):
    page_number: int = 1
    page_size: int = 10
    sort: Optional[List[SortFieldBaseSchema]] = None
    filters: Optional[List[FilterFieldBaseSchema]] = None

    @validator('page_size')
    def validate_page_size(cls, v):
        if not 1 <= v <= 100:
            raise ValueError("Page size must be between 1 and 100")
        return v

class EventState(str, Enum):
    NEW = "NEW"
    FINISHED_WIN = "FINISHED_WIN"
    FINISHED_LOSE = "FINISHED_LOSE"

class Event(BaseModel):
    event_id: str
    coefficient: condecimal(gt=0, decimal_places=2)
    deadline: int
    state: EventState = EventState.NEW

class UpdateEvent(BaseModel):
    coefficient: condecimal(gt=0, decimal_places=2)
    deadline: int
    state: EventState = EventState.NEW

    @validator('deadline')
    def validate_deadline(cls, v):
        if v <= datetime.now().timestamp():
            raise ValueError('Deadline must be in the future')
        return v

class PageResponseBaseSchema(BaseModel):
    page_number: int
    page_size: int
    total_pages: int
    total_records: int
    items: List[Event]

class ErrorResponse(BaseModel):
    detail: str


class EventCallback(BaseModel):
    event_id: str
    new_status: EventState