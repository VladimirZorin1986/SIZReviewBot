from datetime import datetime
from dao.user import UserDAO
from exceptions.user import UserNotExist
from sqlalchemy.ext.asyncio import AsyncSession
from services.base import BaseService


class UserService(BaseService):

    admins = {1, 648987}

    @classmethod
    async def _get_user_by_phone(cls, phone_number: str, async_session: AsyncSession):
        phone_number = phone_number if len(phone_number) == 12 else f'+{phone_number}'
        user = await UserDAO.find_one_or_none(async_session, phone_number=phone_number, is_active=True)
        if not user:
            raise UserNotExist
        return user

    @classmethod
    async def authorize_user(cls, async_session: AsyncSession, tg_id: int, phone_number: str) -> None:
        user = await cls._get_user_by_phone(phone_number, async_session)
        await UserDAO.update_object(
            async_session,
            user.id,
            tg_id=tg_id,
            last_modified_at=datetime.now(),
            registered_at=datetime.now()
        )

    @classmethod
    async def is_admin_user(cls, async_session: AsyncSession, tg_id: int) -> bool:
        user = await UserDAO.find_one_or_none(async_session, tg_id=tg_id, is_active=True)
        if user.id in cls.admins:
            return True
        return False


