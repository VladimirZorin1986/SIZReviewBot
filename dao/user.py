from dao.base import BaseDAO
from database.models import SIZUser
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select


class UserDAO(BaseDAO):
    model = SIZUser

    @classmethod
    async def get_all_bot_users(cls, session: AsyncSession):
        query = select(SIZUser).where(SIZUser.tg_id is not None).where(SIZUser.is_active)
        result = await session.execute(query)
        return result.scalars().all()
