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


class SQuestion(BaseModel):
    id: int
    text: str


class SAnswer(BaseModel):
    question_text: str
    answer_text: str


class SPickPoint(BaseModel):
    id: int
    name: str


class SModel(BaseModel):
    id: int
    name: str
    protect_props: Optional[str] = None
    care_procedure: Optional[str] = None
    writeoff_criteria: Optional[str] = None
    operating_rules: Optional[str] = None
    file_id: Optional[str] = None
    file_name: Optional[str] = None

