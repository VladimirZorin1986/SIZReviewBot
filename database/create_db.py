import asyncio
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession, create_async_engine
from database.models import Base
from config import load_config


async def insert_objects(async_session: async_sessionmaker[AsyncSession]) -> None:
    ...


async def async_main() -> None:
    config = load_config()

    engine = create_async_engine(
        config.db.url,
        echo=True,
    )

    # async_sessionmaker: a factory for new AsyncSession objects.
    # expire_on_commit - don't expire objects after transaction commit
    async_session = async_sessionmaker(engine, expire_on_commit=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    # await insert_objects(async_session)

    # for AsyncEngine created in function scope, close and
    # clean-up pooled connections
    await engine.dispose()


if __name__ == '__main__':
    asyncio.run(async_main())
