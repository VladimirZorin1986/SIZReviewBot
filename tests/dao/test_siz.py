import pytest
from datetime import datetime
from dao.siz import SIZTypeDAO
from database.models import SIZType, SIZModel

db_tables = {
    SIZType: [
        {"id": 3, "name": "Тип А", "is_active": True, "last_modified_at": datetime(2025, 6, 6, 10, 0, 0)},
        {"id": 4, "name": "Тип Б", "is_active": True, "last_modified_at": datetime(2025, 6, 12, 10, 0, 0)},
        {"id": 5, "name": "Тип В", "is_active": True, "last_modified_at": datetime(2025, 6, 12, 10, 0, 0)},
    ],
    SIZModel: [
        {"id": 1, "type_id": 3, "name": "SIZ A", "last_modified_at": datetime(2025, 6, 12, 10, 0, 0)},
        {"id": 2, "type_id": 3, "name": "СИЗ А", "last_modified_at": datetime(2025, 9, 12, 10, 0, 0)},
        {"id": 3, "type_id": 4, "name": "СИЗ Б", "last_modified_at": datetime(2025, 12, 12, 10, 0, 0)},
    ]
}

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
