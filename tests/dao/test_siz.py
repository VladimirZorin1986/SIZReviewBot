import pytest
from datetime import datetime
from dao.siz import SIZTypeDAO
from database.models import SIZType, SIZModel
from sqlalchemy import insert
from contextlib import asynccontextmanager

siz_type_rows = [
    (3, "Тип А", datetime(2025, 6, 6, 10, 0, 0)),
    (4, "Тип Б", datetime(2025, 6, 12, 10, 0, 0)),
    (5, "Тип В", datetime(2025, 6, 12, 10, 0, 0)),
]

siz_model_rows = [
    (1, 3, "SIZ A", datetime(2025, 6, 12, 10, 0, 0)),
    (2, 3, "СИЗ А", datetime(2025, 9, 12, 10, 0, 0)),
    (3, 4, "СИЗ Б", datetime(2025, 12, 12, 10, 0, 0)),
]

@pytest.fixture()
@asynccontextmanager
async def db_session_filled(db_session):
    async with db_session as session:
        query = insert(SIZType).values([{'id': id, 'name': name, 'is_active': True, 'last_modified_at': last_modified_at} for id, name, last_modified_at in siz_type_rows])
        await session.execute(query)
        query = insert(SIZModel).values([{"id": id, "type_id": type_id, "name": name, "last_modified_at": last_modified_at} for id, type_id, name, last_modified_at in siz_model_rows])
        await session.execute(query)
        yield session

@pytest.mark.parametrize(
    "index,id",
    [
        (0, 3),
        (1, 4),
    ]
)
@pytest.mark.asyncio
async def test_get_filled_types(db_session_filled, index, id):
    async with db_session_filled as session:
        res = await SIZTypeDAO.get_filled_types(session)
        assert res[index].id == id
