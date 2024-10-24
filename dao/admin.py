from dao.base import BaseDAO
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from database.models import AdminNotice


class AdminDAO(BaseDAO):
    model = AdminNotice

    @classmethod
    async def get_new_notifications(cls, session: AsyncSession):
        query = select(cls.model).where(cls.model.delivered_at == None)
        result = await session.execute(query)
        return result.scalars().all()

