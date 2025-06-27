import pytest
from datetime import datetime
from dao.user import UserDAO
from database.models import SIZUser
from services.user import UserService
from exceptions.user import UserNotExist

db_tables = {
    SIZUser: [
        {"id": 1,      "tg_id": 123,  "phone_number": "+78887776655", "is_active": True,  "last_modified_at": datetime(2025, 6, 6, 10, 0, 0)},
        {"id": 4,      "tg_id": None, "phone_number": "+74445556677", "is_active": True,  "last_modified_at": datetime(2025, 6, 12, 10, 0, 0)},
        {"id": 648987, "tg_id": 321,  "phone_number": "+79992323232", "is_active": False, "last_modified_at": datetime(2025, 6, 12, 10, 0, 0)},
    ]
}

@pytest.mark.parametrize(
    "phone_number,tg_id,last_modified_at",
    [
        ("+78887776655", 123, datetime(2025, 6, 6, 10, 0, 0)),
        ("74445556677", None, datetime(2025, 6, 12, 10, 0, 0))
    ]
)
@pytest.mark.asyncio
async def test_get_user_by_phone(db_session_filled, phone_number, tg_id, last_modified_at):
    async with db_session_filled as session:
        res = await UserService._get_user_by_phone(phone_number, session)
        assert res.tg_id == tg_id
        assert res.last_modified_at == last_modified_at

@pytest.mark.asyncio
async def test_get_user_by_phone_not_exist(db_session_filled):
    async with db_session_filled as session:
        with pytest.raises(UserNotExist):
            await UserService._get_user_by_phone("BAD", session)

@pytest.mark.parametrize(
    "phone_number,tg_id",
    [
        ("+78887776655", 128),
        ("+74445556677", 999)
    ]
)
@pytest.mark.asyncio
async def test_authorize_user(db_session_filled, phone_number, tg_id):
    async with db_session_filled as session:
        await UserService.authorize_user(session, tg_id, phone_number)
        res = await UserDAO.find_one_or_none(session, phone_number=phone_number)
        assert res.phone_number == phone_number
        assert res.tg_id == tg_id

@pytest.mark.asyncio
async def test_authorize_user_not_exist(db_session_filled):
    async with db_session_filled as session:
        with pytest.raises(UserNotExist):
            await UserService.authorize_user(session, 999, "BAD")

@pytest.mark.parametrize(
    "tg_id,expectation",
    [
        (123, True),
        (321, False),
        (999, False)
    ]
)
@pytest.mark.asyncio
async def test_is_admin_user(db_session_filled, tg_id, expectation):
    async with db_session_filled as session:
        res = await UserService.is_admin_user(session, tg_id)
        assert res == expectation
