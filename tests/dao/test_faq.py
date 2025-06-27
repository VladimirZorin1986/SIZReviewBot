import pytest
from datetime import datetime
from dao.faq import FaqDAO
from database.models import SIZFAQ, QuestionPriority

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
