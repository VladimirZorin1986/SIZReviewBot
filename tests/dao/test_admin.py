import pytest
from datetime import datetime
from dao.admin import AdminDAO
from database.models import AdminNotice

db_tables = {
    AdminNotice: [
        {"id": 1, "notice_text": "Important notice",   "created_at": datetime(2025, 6, 9, 10, 0, 0),    "sent_from_eis": datetime(2025, 6, 9, 11, 0, 0),    "delivered_at": datetime(2025, 6, 10, 12, 0, 0)},
        {"id": 2, "notice_text": "Important notice",   "created_at": datetime(2025, 6, 6, 10, 0, 0),    "sent_from_eis": datetime(2025, 6, 12, 11, 0, 0),   "delivered_at": None},
        {"id": 3, "notice_text": "Important notice 3", "created_at": datetime(2025, 6, 12, 10, 0, 0),   "sent_from_eis": datetime(2025, 6, 13, 11, 0, 0),   "delivered_at": datetime(2025, 6, 13, 12, 0, 0)},
        {"id": 4, "notice_text": "Important notice 4", "created_at": datetime(2025, 6, 9, 10, 0, 0),    "sent_from_eis": datetime(2025, 6, 14, 11, 0, 0),   "delivered_at": datetime(2025, 6, 15, 12, 0, 0)},
    ]
}

@pytest.mark.parametrize(
    "index,expectation",
    [(0, {'notice_text': "Important notice", 'created_at': datetime(2025, 6, 6, 10, 0, 0), 'sent_from_eis': datetime(2025, 6, 12, 11, 0, 0), 'delivered_at': None})]
)
@pytest.mark.asyncio
async def test_get_new_notifications(db_session_filled, index, expectation):
    async with db_session_filled as session:
        res = await AdminDAO.get_new_notifications(session)
        assert res[index].notice_text == expectation['notice_text']
        assert res[index].created_at == expectation['created_at']
        assert res[index].sent_from_eis == expectation['sent_from_eis']
        assert res[index].delivered_at == expectation['delivered_at']