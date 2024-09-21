from sqlalchemy import select, insert, delete, update
from sqlalchemy.ext.asyncio import AsyncSession


class BaseDAO:
    model = None

    @classmethod
    async def find_by_id(cls, model_id: int, async_session: AsyncSession):
        query = select(cls.model).filter_by(id=model_id)
        result = await async_session.execute(query)
        return result.scalar_one()

    @classmethod
    async def find_one_or_none(cls, async_session: AsyncSession, **filter_options):
        query = select(cls.model).filter_by(**filter_options)
        result = await async_session.execute(query)
        return result.scalar_one_or_none()

    @classmethod
    async def find_all(cls, async_session: AsyncSession, **filter_options):
        query = select(cls.model).filter_by(**filter_options)
        result = await async_session.execute(query)
        return result.scalars().all()

    @classmethod
    async def add_new_object(cls, async_session: AsyncSession, **data):
        query = insert(cls.model).values(**data)
        await async_session.execute(query)
        await async_session.commit()

    @classmethod
    async def update_object(cls, async_session: AsyncSession, model_id: int, **data):
        query = update(cls.model).filter_by(id=model_id).values(**data)
        await async_session.execute(query)
        await async_session.commit()

    @classmethod
    async def delete_object(cls, model_id: int, async_session: AsyncSession):
        query = delete(cls.model).filter_by(id=model_id)
        await async_session.execute(query)
        await async_session.commit()
