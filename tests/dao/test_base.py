import pytest
from datetime import datetime
from dao.admin import AdminDAO
from database.models import AdminNotice
from sqlalchemy import insert
from contextlib import asynccontextmanager
from sqlalchemy.exc import NoResultFound, MultipleResultsFound

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
    "id,expectation",
    [(id, {'notice_text': notice_text, 'created_at': created_at, 'sent_from_eis': sent_from_eis, 'delivered_at': delivered_at}) for id, notice_text, created_at, sent_from_eis, delivered_at in admin_notice_rows]
)
@pytest.mark.asyncio
async def test_find_by_id(db_session_filled, id, expectation):
    async with db_session_filled as session:
        res = await AdminDAO.find_by_id(id, session)
        assert res.notice_text == expectation['notice_text']
        assert res.created_at == expectation['created_at']
        assert res.sent_from_eis == expectation['sent_from_eis']
        assert res.delivered_at == expectation['delivered_at']

@pytest.mark.asyncio
async def test_find_by_id_no_result(db_session_filled):
    async with db_session_filled as session:
        with pytest.raises(NoResultFound):
            await AdminDAO.find_by_id(999, session)

@pytest.mark.parametrize(
    "test_values,id",
    [
        ({"notice_text": "Important notice", "created_at": datetime(2025, 6, 9, 10, 0, 0)}, 1),
        ({"delivered_at": None}, 2),
        ({"created_at": datetime(2025, 6, 12, 10, 0, 0)}, 3),
        ({"sent_from_eis": datetime(2025, 6, 14, 11, 0, 0)}, 4),
        ({"notice_text": "BAD"}, None),
    ],
)
@pytest.mark.asyncio
async def test_find_one_or_none(db_session_filled, test_values, id):
    async with db_session_filled as session:
        res = await AdminDAO.find_one_or_none(session, **test_values)
        if id:
            assert res.id == id
        else:
            assert res == None


@pytest.mark.parametrize(
    "test_values",
    [
        ({"notice_text": "Important notice"}),
        ({"created_at": datetime(2025, 6, 9, 10, 0, 0)}),
    ],
)
@pytest.mark.asyncio
async def test_find_one_or_none_multiple(db_session_filled, test_values):
    async with db_session_filled as session:
        with pytest.raises(MultipleResultsFound):
            await AdminDAO.find_one_or_none(session, **test_values)

@pytest.mark.parametrize(
    "test_values, ids",
    [
        ({"notice_text": "Important notice"}, [1, 2]),
        ({"created_at": datetime(2025, 6, 9, 10, 0, 0)}, [1, 4]),
        ({"created_at": datetime(2025, 6, 12, 10, 0, 0)}, [3]),
        ({"sent_from_eis": datetime(2025, 6, 14, 11, 0, 0)}, [4]),
        ({"notice_text": "BAD"}, []),
    ],
)
@pytest.mark.asyncio
async def test_find_all(db_session_filled, test_values, ids):
    async with db_session_filled as session:
        res = await AdminDAO.find_all(session, **test_values)
        assert [item.id for item in res] == ids

@pytest.mark.parametrize(
    "test_values",
    [
        ({"id": 10, "notice_text": "text", "created_at": datetime.now(), "sent_from_eis": datetime.now(), "delivered_at": datetime.now()}),
        ({"notice_text": "text", "created_at": datetime.now(), "sent_from_eis": datetime.now()}),
    ],
)
@pytest.mark.asyncio
async def test_add_new_object(db_session_filled, test_values):
    async with db_session_filled as session:
        await AdminDAO.add_new_object(session, **test_values)
        res = await AdminDAO.find_one_or_none(session, **test_values)
        assert res.notice_text == test_values['notice_text']
        assert res.created_at == test_values['created_at']
        assert res.sent_from_eis == test_values['sent_from_eis']

@pytest.mark.parametrize(
    "id,test_values,expectation",
    [
        (1, {"notice_text": "Important notice (NEW)"}, {"notice_text": "Important notice (NEW)", "created_at": datetime(2025, 6, 9, 10, 0, 0), "sent_from_eis": datetime(2025, 6, 9, 11, 0, 0), "delivered_at": datetime(2025, 6, 10, 12, 0, 0)}),
        (2, {"notice_text": "Notice", "created_at": datetime(2024, 6, 9, 10, 0, 0)}, {"notice_text": "Notice", "created_at": datetime(2024, 6, 9, 10, 0, 0), "sent_from_eis": datetime(2025, 6, 12, 11, 0, 0), "delivered_at": None}),
        (3, {"sent_from_eis": datetime(2022, 6, 13, 11, 0, 0), "delivered_at": datetime(2023, 6, 13, 12, 0, 0)}, {"notice_text": "Important notice 3", "created_at": datetime(2025, 6, 12, 10, 0, 0), "sent_from_eis": datetime(2022, 6, 13, 11, 0, 0), "delivered_at": datetime(2023, 6, 13, 12, 0, 0)}),
        (4, {"notice_text": "Important notice IV"}, {"notice_text": "Important notice IV", "created_at": datetime(2025, 6, 9, 10, 0, 0), "sent_from_eis": datetime(2025, 6, 14, 11, 0, 0), "delivered_at": datetime(2025, 6, 15, 12, 0, 0)}),
    ],
)
@pytest.mark.asyncio
async def test_update_object(db_session_filled, id, test_values, expectation):
    async with db_session_filled as session:
        await AdminDAO.update_object(session, id, **test_values)
        res = await AdminDAO.find_by_id(id, session)
        assert res.notice_text == expectation['notice_text']
        assert res.created_at == expectation['created_at']
        assert res.sent_from_eis == expectation['sent_from_eis']
        assert res.delivered_at == expectation['delivered_at']

@pytest.mark.parametrize(
    "id",
    [
        (1),
        (2),
        (3),
        (4),
        (999),
    ],
)
@pytest.mark.asyncio
async def test_delete_object(db_session_filled, id):
    async with db_session_filled as session:
        await AdminDAO.delete_object(id, session)
        with pytest.raises(NoResultFound):
            await AdminDAO.find_by_id(id, session)
