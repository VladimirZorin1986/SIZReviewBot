import pytest
from sqlalchemy import insert
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, AsyncEngine, async_sessionmaker
from dao.base import BaseDAO
from database.models import Base
from contextlib import asynccontextmanager
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.storage.base import StorageKey
from aiogram.fsm.context import FSMContext

class MockBot:
    """
    Класс для мокирования Bot

    :param faulty: Если True, методы класса будут проваливаться
    :type faulty: bool
    :param deleted_messages: Список сообщений, которые были "удалены" при вызове delete_message(s)
    :type deleted_messages: list[int]
    """
    faulty: bool
    deleted_messages: list[int]
    def __init__(cls, faulty: bool = False):
        cls.faulty = faulty
        cls.deleted_messages = []

    async def send_message(cls, **data) -> None:
        """
        Метод который "отправляет" сообщение

        Фактически no-op
 
        :return: Возрашает None
        :raise Exception: Если faulty
        """
        if cls.faulty:
            raise Exception
        return None

    async def delete_message(cls, message_id: int | None = None, **data) -> bool:
        """
        Метод который "удаляет" сообщение

        Фактически добавляет message_id сообщения в deleted_messages для дальнейшего тестирования
 
        :param message_id: Id удаляемого сообщения
        :type message_id: int | None
        :return: Возращает True, либо же False если faulty
        """
        if cls.faulty:
            return False
        if message_id:
            cls.deleted_messages.append(message_id)
        return True

    async def delete_messages(cls, message_ids: list[int] | None=None, **data) -> bool:
        """
        Метод который "удаляет" сообщение

        Фактически записывает message_ids сообщения в deleted_messages для дальнейшего тестирования
 
        :param messages_id: Id удаляемых сообщений
        :type messages_id: list[int] | None
        :return: Возращает True, либо же False если faulty
        """
        if cls.faulty:
            return False
        if message_ids:
            cls.deleted_messages=message_ids
        return True

class MockSessionMaker:
    """
    Класс для мокирования async_sessionmaker

    :param session: Сессия которая будет возращаться при вызове объекта
    :type session: AsyncSession
    """
    session: AsyncSession
    def __init__(cls, session: AsyncSession):
        cls.session = session

    def __call__(cls) -> AsyncSession:
        """
        Метод вызова

        :return: Возращает session заданный при создании объекта
        """
        return cls.session

# Фикстура для инициализации временной базы данных
@pytest.fixture(scope="session")
def engine() -> AsyncEngine:
    """Создаем движок SQLite"""
    return create_async_engine("sqlite+aiosqlite:///:memory:", echo=True)

@pytest.fixture()
@asynccontextmanager
async def db_session(engine):
    """Инициализируем сессию для каждого отдельного теста."""
    connection = await engine.connect()

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
@asynccontextmanager
async def db_session_filled(request, db_session):
    """
    Инициализируем сессию заполненную таблицами

    :param db_tables: Словарь "таблица: строки", задаётся непосредственно в модуле, который использует данную фикстуру
    :type db_tables: Dict[database.models.Base, list[Dict[str, Any]]]
    """
    test_module = request.module

    if not hasattr(test_module, 'db_tables'):
        pytest.fail(f"В модуле {test_module.__name__} нет db_tables")

    db_tables = test_module.db_tables

    async with db_session as session:
        for table, rows in db_tables.items():
            query = insert(table).values(rows)
            await session.execute(query)
        yield session

@pytest.fixture()
def context() -> FSMContext:
    """Инициализируем FSM контекст для каждого отдельного теста."""
    return FSMContext(storage=MemoryStorage(), key=StorageKey(1, 2, 8))

@pytest.fixture()
def dao_add_new_object_id(monkeypatch, request) -> int:
    """
    Monkey patch для метода add_new_object_id BaseDAO
    
    К сожалению в SQLite автоинкремент работает только с `INTEGER PRIMARY KEY <https://www.sqlite.org/autoinc.html>`_
    что означает что запуск данной функции для таблиц у которых первичный ключ BigInteger выбрасывает sqlite3.IntegrityError,
    потому что id будет NULL

    Данная фикстура использует `косвенную параметризацию <https://docs.pytest.org/en/latest/example/parametrize.html#indirect-parametrization>`_
    для того чтобы вручную задать id

    :return: Возращает id заданное в @pytest.mark.parametrize
    """
    @classmethod
    async def add_new_object(cls, async_session: AsyncSession, **data):
        query = insert(cls.model).values(**data, id=request.param)
        await async_session.execute(query)
        await async_session.commit()

    monkeypatch.setattr(BaseDAO, 'add_new_object', add_new_object)

    return request.param