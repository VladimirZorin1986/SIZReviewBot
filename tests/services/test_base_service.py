import pytest
from datetime import datetime
from sqlalchemy import insert
from contextlib import asynccontextmanager
from services.base import BaseService
from database.models import SIZUser
from exceptions.user import UserNotExist
from exceptions.cache import InvalidItems, InvalidVariable, ItemNotFound

user_rows = [
    (3, 123, "+78887776655", True, datetime(2025, 6, 6, 10, 0, 0)),
    (4, None, "+74445556677", True, datetime(2025, 6, 12, 10, 0, 0)),
    (5, 128, "+79992323232", False, datetime(2025, 6, 12, 10, 0, 0)),
]

@pytest.fixture()
@asynccontextmanager
async def db_session_filled(db_session):
    async with db_session as session:
        query = insert(SIZUser).values([{'id': id, 'tg_id': tg_id, 'phone_number': phone_number, 'is_active': is_active, 'last_modified_at': last_modified_at} for id, tg_id, phone_number, is_active, last_modified_at in user_rows])
        await session.execute(query)
        yield session

@pytest.mark.asyncio
async def test_remember_variables_in_state(context) -> None:
    await BaseService.remember_variables_in_state(state=context, foo="bar")
    data = await context.get_data()
    assert data["foo"] == "bar"

@pytest.mark.asyncio
async def test_cache_user(db_session_filled, context) -> None:
    async with db_session_filled as session:
        await BaseService.cache_user(session=session, state=context, tg_id=123)
        data = await context.get_data()
        assert data["user_id"] == 3

@pytest.mark.asyncio
async def test_cache_user_not_exist(db_session_filled, context) -> None:
    async with db_session_filled as session:
        with pytest.raises(UserNotExist):
            await BaseService.cache_user(session=session, state=context, tg_id=999)

@pytest.mark.asyncio
async def test_get_variables_from_state(context) -> None:
    await context.update_data(foo="bar", hello="world", welcome="home")
    res = await BaseService.get_variables_from_state(context, ["foo", "hello", "welcome"])
    assert res == ["bar", "world", "home"]

@pytest.mark.asyncio
async def test_get_variables_from_state_invalid(context) -> None:
    await context.update_data(foo="bar", hello="world", welcome="home")
    with pytest.raises(InvalidVariable):
        await BaseService.get_variables_from_state(context, ["bar"])

@pytest.mark.asyncio
async def test_get_variable_from_state(context) -> None:
    await context.update_data(foo="bar")
    res = await BaseService.get_variable_from_state(context, "foo")
    assert res == "bar"

@pytest.mark.asyncio
async def test_get_variable_from_state_invalid(context) -> None:
    await context.update_data(foo="bar")
    with pytest.raises(InvalidVariable):
        await BaseService.get_variable_from_state(context, "bar")

@pytest.mark.parametrize(
    "tg_id,result",
    [
        (123, True),
        (128, False),
        (999, False)
    ]
)
@pytest.mark.asyncio
async def test_is_authorized_user(db_session_filled, tg_id, result) -> None:
    async with db_session_filled as session:
        res = await BaseService.is_authorized_user(async_session=session, tg_id=tg_id)
        assert res == result

@pytest.mark.asyncio
async def test_get_item_name(context) -> None:
    names = { 123: "hello", 234: "lovely", 345: "world" }
    await context.update_data(names=names)
    res = await BaseService.get_item_name(state=context, item_id=123, items_name="names")
    assert res == "hello"

@pytest.mark.asyncio
async def test_get_item_name_invalid_variable(context) -> None:
    with pytest.raises(InvalidVariable):
        await BaseService.get_item_name(state=context, item_id=123, items_name="BAD")

@pytest.mark.asyncio
async def test_get_item_name_items_not_found(context) -> None:
    names = { 123: "hello", 234: "lovely", 345: "world" }
    await context.update_data(names=names)
    with pytest.raises(ItemNotFound):
        await BaseService.get_item_name(state=context, item_id=999, items_name="names")

@pytest.mark.asyncio
async def test_get_item_name_invalid_items(context) -> None:
    await context.update_data(names="hello")
    with pytest.raises(InvalidItems):
        await BaseService.get_item_name(state=context, item_id=1, items_name="names")
