import pytest
from datetime import datetime
from services.faq import FAQService
from services.models import SQuestion, SAnswer
from database.models import SIZFAQ, QuestionPriority
from exceptions.questions import QuestionNotFound, NoQuestionsExist

db_tables = {
    QuestionPriority: [
        {"id": 1, "name": "High",   "order_value": 1},
        {"id": 2, "name": "Medium", "order_value": 5},
        {"id": 3, "name": "Low",    "order_value": 10},
    ],
    SIZFAQ: [
        {"id": 4, "priority_id": 2, "question_text": "Medium question?", "answer_text": "medium answer", "is_active": True, "last_modified_at": datetime(2025, 6, 9, 10, 0, 0)},
        {"id": 5, "priority_id": 1, "question_text": "high?",            "answer_text": "high!",         "is_active": True, "last_modified_at": datetime(2025, 6, 6, 10, 0, 0)},
        {"id": 6, "priority_id": 3, "question_text": "low?",             "answer_text": "low...",        "is_active": True, "last_modified_at": datetime(2025, 6, 12, 10, 0, 0)},
    ]
}

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
