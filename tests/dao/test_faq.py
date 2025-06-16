import pytest
from datetime import datetime
from dao.faq import FaqDAO
from database.models import SIZFAQ, QuestionPriority
from sqlalchemy import insert
from contextlib import asynccontextmanager

question_priority_rows = [
    (1, "High", 1),
    (2, "Medium", 5),
    (3, "Low", 10),
]

faq_rows = [
    (4, 2, "Medium question?", "medium answer", True, datetime(2025, 6, 9, 10, 0, 0)),
    (5, 1, "high?", "high!", True, datetime(2025, 6, 6, 10, 0, 0)),
    (6, 3, "low?", "low...", True, datetime(2025, 6, 12, 10, 0, 0)),
]

@pytest.fixture()
@asynccontextmanager
async def db_session_filled(db_session):
    async with db_session as session:
        query = insert(QuestionPriority).values([{'id': id, 'name': name, 'order_value': order_value} for id, name, order_value in question_priority_rows])
        await session.execute(query)
        query = insert(SIZFAQ).values([{'id': id, 'priority_id': priority_id, 'question_text': question_text, 'answer_text': answer_text, 'is_active': is_active, 'last_modified_at': last_modified_at} for id, priority_id, question_text, answer_text, is_active, last_modified_at in faq_rows])
        await session.execute(query)
        yield session

@pytest.mark.parametrize(
    "index,id",
    [
        (0, 5),
        (1, 4),
        (2, 6)
    ]
)
@pytest.mark.asyncio
async def test_find_all_sort_by_priority(db_session_filled, index, id):
    async with db_session_filled as session:
        res = await FaqDAO.find_all_sort_by_priority(session)
        assert res[index].id == id
