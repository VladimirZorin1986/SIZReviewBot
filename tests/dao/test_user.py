import pytest
from datetime import datetime
from dao.user import UserDAO
from database.models import SIZUser

db_tables = {
    SIZUser: [
        {"id": 3, "tg_id": 123,  "phone_number": "+78887776655", "is_active": True,  "last_modified_at": datetime(2025, 6, 6, 10, 0, 0)},
        {"id": 4, "tg_id": None, "phone_number": "+74445556677", "is_active": True,  "last_modified_at": datetime(2025, 6, 12, 10, 0, 0)},
        {"id": 5, "tg_id": 123,  "phone_number": "+79992323232", "is_active": False, "last_modified_at": datetime(2025, 6, 12, 10, 0, 0)},
    ]
}

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
