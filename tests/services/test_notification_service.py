import pytest
from datetime import datetime
from sqlalchemy import insert
from contextlib import asynccontextmanager
from services.notification import notification_job, NotificationService
from database.models import SIZUser, AdminNotice
from exceptions.admin import InvalidNotificationError
from dao.admin import AdminDAO
from tests.conftest import MockBot, MockSessionMaker

admin_notice_rows = [
    (1, "Important notice", datetime(2025, 6, 9, 10, 0, 0), datetime(2025, 6, 9, 11, 0, 0), datetime(2025, 6, 10, 12, 0, 0)),
    (2, "Important notice", datetime(2025, 6, 6, 10, 0, 0), datetime(2025, 6, 12, 11, 0, 0), None),
    (3, "Important notice 3", datetime(2025, 6, 12, 10, 0, 0), datetime(2025, 6, 13, 11, 0, 0), datetime(2025, 6, 13, 12, 0, 0)),
    (4, "Important notice 4", datetime(2025, 6, 9, 10, 0, 0), datetime(2025, 6, 14, 11, 0, 0), datetime(2025, 6, 15, 12, 0, 0)),
]

user_rows = [
    (3, 123, "+78887776655", True, datetime(2025, 6, 6, 10, 0, 0)),
    (4, None, "+74445556677", True, datetime(2025, 6, 12, 10, 0, 0)),
    (5, 123, "+79992323232", False, datetime(2025, 6, 12, 10, 0, 0)),
]

@pytest.fixture()
@asynccontextmanager
async def db_session_filled(db_session):
    async with db_session as session:
        query = insert(AdminNotice).values([{'id': id, 'notice_text': notice_text, 'created_at': created_at, 'sent_from_eis': sent_from_eis, 'delivered_at': delivered_at} for id, notice_text, created_at, sent_from_eis, delivered_at in admin_notice_rows])
        await session.execute(query)
        query = insert(SIZUser).values([{'id': id, 'tg_id': tg_id, 'phone_number': phone_number, 'is_active': is_active, 'last_modified_at': last_modified_at} for id, tg_id, phone_number, is_active, last_modified_at in user_rows])
        await session.execute(query)
        yield session


@pytest.mark.asyncio
async def test_notification_job(db_session_filled) -> None:
    async with db_session_filled as session:
        await notification_job(MockBot(), MockSessionMaker(session))
        res = await AdminDAO.find_by_id(2, session)
        assert res.delivered_at != None

@pytest.mark.asyncio
async def test_notification_job_fail(db_session_filled) -> None:
    async with db_session_filled as session:
        await notification_job(MockBot(faulty=True), MockSessionMaker(session))
        res = await AdminDAO.find_by_id(2, session)
        assert res.delivered_at == None


@pytest.mark.asyncio
async def test_send_mass_notification(db_session_filled) -> None:
    async with db_session_filled as session:
        await NotificationService.send_mass_notification(MockBot(), "notification", session)

@pytest.mark.asyncio
async def test_send_mass_notification_fail(db_session_filled) -> None:
    async with db_session_filled as session:
        with pytest.raises(InvalidNotificationError):
            await NotificationService.send_mass_notification(MockBot(faulty=True), "notification", session)

@pytest.mark.asyncio
async def test_send_mass_admin_notification(db_session_filled) -> None:
    async with db_session_filled as session:
        await NotificationService.send_mass_admin_notification(MockBot(), session)
        res = await AdminDAO.find_by_id(2, session)
        assert res.delivered_at != None

@pytest.mark.asyncio
async def test_send_mass_admin_notification_fail(db_session_filled) -> None:
    async with db_session_filled as session:
        await NotificationService.send_mass_admin_notification(MockBot(faulty=True), session)
        res = await AdminDAO.find_by_id(2, session)
        assert res.delivered_at == None