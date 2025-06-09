import os
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager
from database.models import Base

# Фикстура для инициализации временной базы данных
@pytest.fixture(scope="session")
def engine():
    """Создаем движок SQLite"""
    return create_engine("sqlite:///:memory:", echo=True)

@pytest.fixture()
def tables(engine):
    """Создаем таблицы для каждой сессии тестов."""
    Base.metadata.create_all(engine)
    yield
    Base.metadata.drop_all(engine)

@pytest.fixture()
def db_session(engine, tables):
    """Инициализируем сессию для каждого отдельного теста."""
    Session = sessionmaker(bind=engine)
    with Session() as session:
        try:
            yield session
        finally:
            session.close()

@contextmanager
def transactional_session(db_session):
    """
    Обеспечивает автоматический откат изменений при возникновении исключений.
    """
    try:
        yield db_session
        db_session.commit()
    except Exception:
        db_session.rollback()
        raise