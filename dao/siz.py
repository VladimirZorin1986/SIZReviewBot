from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from dao.base import BaseDAO
from database.models import SIZType, SIZModel, SIZModelReview


class SIZTypeDAO(BaseDAO):
    model = SIZType

    @classmethod
    async def get_filled_types(cls, session: AsyncSession):
        subq = select(SIZModel.__table__.c.type_id).where(SIZModel.__table__.c.is_active).distinct().subquery()
        query = select(cls.model).join(subq, cls.model.id == subq.c.type_id).where(cls.model.is_active)
        result = await session.execute(query)
        return result.scalars().all()


class SIZModelDAO(BaseDAO):
    model = SIZModel


class SIZReviewDAO(BaseDAO):
    model = SIZModelReview
