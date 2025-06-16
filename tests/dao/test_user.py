import pytest
from datetime import datetime
from dao.user import UserDAO
from database.models import SIZUser
from sqlalchemy import insert
from contextlib import asynccontextmanager

user_rows = [
    (3, 123, "+78887776655", True, datetime(2025, 6, 6, 10, 0, 0)),
    (4, None, "+74445556677", True, datetime(2025, 6, 12, 10, 0, 0)),
    (5, 123, "+79992323232", False, datetime(2025, 6, 12, 10, 0, 0)),
]

@pytest.fixture()
@asynccontextmanager
async def db_session_filled(db_session):
    async with db_session as session:
        query = insert(SIZUser).values([{'id': id, 'tg_id': tg_id, 'phone_number': phone_number, 'is_active': is_active, 'last_modified_at': last_modified_at} for id, tg_id, phone_number, is_active, last_modified_at in user_rows])
        await session.execute(query)
        yield session

@pytest.mark.parametrize(
    "index,id",
    [
        (0, 3)
    ]
)
@pytest.mark.asyncio
async def test_get_all_bot_users(db_session_filled, index, id):
    async with db_session_filled as session:
        res = await UserDAO.get_all_bot_users(session)
        assert res[index].id == id
