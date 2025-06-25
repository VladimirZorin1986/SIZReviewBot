import pytest
from datetime import datetime
from sqlalchemy import insert
from contextlib import asynccontextmanager
from services.faq import FAQService
from services.models import SQuestion, SAnswer
from database.models import SIZFAQ, QuestionPriority
from exceptions.questions import QuestionNotFound, NoQuestionsExist

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
    "index,expected",
    [
        (0, SQuestion(id=5,text="high?")),
        (1, SQuestion(id=4,text="Medium question?")),
        (2, SQuestion(id=6,text="low?"))
    ]
)
@pytest.mark.asyncio
async def test_get_questions(db_session_filled, index, expected) -> None:
    async with db_session_filled as session:
        res = await FAQService.get_questions(session)
        assert res[index] == expected

@pytest.mark.asyncio
async def test_get_questions_no_questions(db_session) -> None:
    async with db_session as session:
        with pytest.raises(NoQuestionsExist):
            await FAQService.get_questions(session)

@pytest.mark.parametrize(
    "id,expected",
    [
        (4, SAnswer(question_text="Medium question?", answer_text="medium answer")),
        (5, SAnswer(question_text="high?", answer_text="high!")),
        (6, SAnswer(question_text="low?", answer_text="low..."))
    ]
)
@pytest.mark.asyncio
async def test_get_answer(db_session_filled, id, expected) -> None:
    async with db_session_filled as session:
        res = await FAQService.get_answer(session, id)
        assert res == expected

@pytest.mark.asyncio
async def test_get_answer_question_not_found(db_session_filled) -> None:
    async with db_session_filled as session:
        with pytest.raises(QuestionNotFound):
            await FAQService.get_answer(session, 999)
