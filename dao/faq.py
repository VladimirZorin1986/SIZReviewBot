from dao.base import BaseDAO
from database.models import SIZFAQ, QuestionPriority
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select


class FaqDAO(BaseDAO):
    model = SIZFAQ

    @classmethod
    async def find_all_sort_by_priority(cls, async_session: AsyncSession):
        query = (
            select(cls.model)
            .join(QuestionPriority, cls.model.priority_id == QuestionPriority.id)
            .where(cls.model.is_active)
            .order_by(QuestionPriority.order_value)
        )
        result = await async_session.execute(query)
        return result.scalars().all()
