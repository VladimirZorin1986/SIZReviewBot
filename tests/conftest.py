import pytest
from sqlalchemy import insert
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from dao.base import BaseDAO
from database.models import Base
from contextlib import asynccontextmanager
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.storage.base import StorageKey
from aiogram.fsm.context import FSMContext

class MockBot:
    faulty: bool
    deleted_messages: list[str]
    def __init__(cls, faulty: bool = False):
        cls.faulty = faulty
        cls.deleted_messages = []

    async def send_message(cls, **data):
        if cls.faulty:
            raise Exception
        return None

    async def delete_message(cls, message_id=None, **data):
        if cls.faulty:
            return False
        if message_id:
            cls.deleted_messages.append(message_id)
        return True

    async def delete_messages(cls, message_ids=None, **data):
        if cls.faulty:
            return False
        if message_ids:
            cls.deleted_messages=message_ids
        return True

class MockSessionMaker:
    session: AsyncSession
    def __init__(cls, session: AsyncSession):
        cls.session = session

    def __call__(cls) -> AsyncSession:
        return cls.session

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

@pytest.fixture()
def context():
    return FSMContext(storage=MemoryStorage(), key=StorageKey(1, 2, 8))

@pytest.fixture()
def dao_add_new_object_id(monkeypatch, request):
    @classmethod
    async def add_new_object(cls, async_session: AsyncSession, **data):
        query = insert(cls.model).values(**data, id=request.param)
        await async_session.execute(query)
        await async_session.commit()

    monkeypatch.setattr(BaseDAO, 'add_new_object', add_new_object)

    return request.param