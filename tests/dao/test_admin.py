import pytest
from datetime import datetime
from dao.admin import AdminDAO
from database.models import AdminNotice
from sqlalchemy import insert
from contextlib import asynccontextmanager

admin_notice_rows = [
    (1, "Important notice", datetime(2025, 6, 9, 10, 0, 0), datetime(2025, 6, 9, 11, 0, 0), datetime(2025, 6, 10, 12, 0, 0)),
    (2, "Important notice", datetime(2025, 6, 6, 10, 0, 0), datetime(2025, 6, 12, 11, 0, 0), None),
    (3, "Important notice 3", datetime(2025, 6, 12, 10, 0, 0), datetime(2025, 6, 13, 11, 0, 0), datetime(2025, 6, 13, 12, 0, 0)),
    (4, "Important notice 4", datetime(2025, 6, 9, 10, 0, 0), datetime(2025, 6, 14, 11, 0, 0), datetime(2025, 6, 15, 12, 0, 0)),
]

@pytest.fixture()
@asynccontextmanager
async def db_session_filled(db_session):
    async with db_session as session:
        query = insert(AdminNotice).values([{'id': id, 'notice_text': notice_text, 'created_at': created_at, 'sent_from_eis': sent_from_eis, 'delivered_at': delivered_at} for id, notice_text, created_at, sent_from_eis, delivered_at in admin_notice_rows])
        await session.execute(query)
        yield session

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