import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from database.models import Base
from contextlib import asynccontextmanager

# Фикстура для инициализации временной базы данных
@pytest.fixture(scope="session")
def engine():
    """Создаем движок SQLite"""
    return create_async_engine("sqlite+aiosqlite:///:memory:", echo=True)

@pytest.fixture()
@asynccontextmanager
async def db_session(engine):
    """Инициализируем сессию для каждого отдельного теста."""
    connection = await engine.connect()
    transaction = await connection.begin()

    SessionMaker = async_sessionmaker(
        bind=connection,
        class_=AsyncSession,
        expire_on_commit=False
    )
    session = SessionMaker()

    await connection.run_sync(Base.metadata.create_all)
    yield session

    await session.close()
    await connection.run_sync(Base.metadata.drop_all)
    await connection.close()
