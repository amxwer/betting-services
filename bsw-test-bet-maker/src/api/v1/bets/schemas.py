import time
from decimal import Decimal
from enum import Enum
from typing import List

from pydantic import BaseModel, condecimal

class BetState(str, Enum):
    PENDING = "PENDING"
    WIN = "WIN"
    LOSE = "LOSE"

class BetCreate(BaseModel):
    event_id: str
    amount: condecimal(gt=0, decimal_places=2)

class BetResponse(BetCreate):
    bet_id: str
    state: BetState
    amount: float

    class Config:
        json_encoders = {
            Decimal: lambda v: float(v)
        }


class EventCallback(BaseModel):
    event_id: str
    new_status: str


class EventState(str, Enum):
    NEW = "NEW"
    FINISHED_WIN = "FINISHED_WIN"
    FINISHED_LOSE = "FINISHED_LOSE"

class Event(BaseModel):
    event_id: str
    coefficient: condecimal(gt=0, decimal_places=2)
    deadline: int
    state: EventState


    @property
    def is_active(self) -> bool:

        return self.state == EventState.NEW and self.deadline > time.time()


class PageResponseFromProvider(BaseModel):
    items: List[Event]

    page_number: int
    page_size: int
    total_pages: int
    total_records: int