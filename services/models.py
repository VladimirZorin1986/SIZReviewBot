from dataclasses import dataclass
from typing import Optional
from aiogram.types import Message
from pydantic import BaseModel


@dataclass
class TrackCallback:
    message: Message
    callback_data: str


class SUser(BaseModel):
    id: int
    tg_id: Optional[int]
    phone_number: str
