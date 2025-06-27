import pytest
from datetime import datetime
from services.notification import notification_job, NotificationService
from database.models import SIZUser, AdminNotice
from exceptions.admin import InvalidNotificationError
from dao.admin import AdminDAO
from tests.conftest import MockBot, MockSessionMaker

db_tables = {
    AdminNotice: [
        {"id": 1, "notice_text": "Important notice",   "created_at": datetime(2025, 6, 9, 10, 0, 0),    "sent_from_eis": datetime(2025, 6, 9, 11, 0, 0),    "delivered_at": datetime(2025, 6, 10, 12, 0, 0)},
        {"id": 2, "notice_text": "Important notice",   "created_at": datetime(2025, 6, 6, 10, 0, 0),    "sent_from_eis": datetime(2025, 6, 12, 11, 0, 0),   "delivered_at": None},
        {"id": 3, "notice_text": "Important notice 3", "created_at": datetime(2025, 6, 12, 10, 0, 0),   "sent_from_eis": datetime(2025, 6, 13, 11, 0, 0),   "delivered_at": datetime(2025, 6, 13, 12, 0, 0)},
        {"id": 4, "notice_text": "Important notice 4", "created_at": datetime(2025, 6, 9, 10, 0, 0),    "sent_from_eis": datetime(2025, 6, 14, 11, 0, 0),   "delivered_at": datetime(2025, 6, 15, 12, 0, 0)},
    ],
    SIZUser: [
        {"id": 3, "tg_id": 123,  "phone_number": "+78887776655", "is_active": True,  "last_modified_at": datetime(2025, 6, 6, 10, 0, 0)},
        {"id": 4, "tg_id": None, "phone_number": "+74445556677", "is_active": True,  "last_modified_at": datetime(2025, 6, 12, 10, 0, 0)},
        {"id": 5, "tg_id": 123,  "phone_number": "+79992323232", "is_active": False, "last_modified_at": datetime(2025, 6, 12, 10, 0, 0)},
    ]
}

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