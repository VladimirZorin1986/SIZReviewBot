import pytest
from datetime import datetime
from dao.siz import SIZModelDAO, SIZReviewDAO
from database.models import SIZType, SIZModel
from sqlalchemy import insert
from contextlib import asynccontextmanager
from services.siz import SIZService
from exceptions.siz import NoTypesFound, NoModelsFound, InvalidModelError, ReviewSaveError
from services.models import SModel

siz_type_rows = [
    (3, "Тип А", True, datetime(2025, 6, 6, 10, 0, 0)),
    (4, "Тип Б", True, datetime(2025, 6, 12, 10, 0, 0)),
    (5, "Тип В", False, datetime(2025, 6, 12, 10, 0, 0)),
]

siz_model_rows = [
    (1, 3, "SIZ A", False, datetime(2025, 6, 12, 10, 0, 0)),
    (2, 3, "СИЗ А", True, datetime(2025, 9, 12, 10, 0, 0)),
    (3, 4, "СИЗ Б", True, datetime(2025, 12, 12, 10, 0, 0)),
]

@pytest.fixture()
@asynccontextmanager
async def db_session_filled(db_session):
    async with db_session as session:
        query = insert(SIZType).values([{'id': id, 'name': name, 'is_active': is_active, 'last_modified_at': last_modified_at} for id, name, is_active, last_modified_at in siz_type_rows])
        await session.execute(query)
        query = insert(SIZModel).values([{"id": id, "type_id": type_id, "name": name, 'is_active': is_active, "last_modified_at": last_modified_at} for id, type_id, name, is_active, last_modified_at in siz_model_rows])
        await session.execute(query)
        yield session

@pytest.mark.asyncio
async def test_list_all_types(db_session_filled) -> None:
    async with db_session_filled as session:
        res = await SIZService.list_all_types(session)
        assert res == {3: "Тип А", 4: "Тип Б"}

@pytest.mark.asyncio
async def test_list_all_types_none_found(db_session) -> None:
    async with db_session as session:
        with pytest.raises(NoTypesFound):
            await SIZService.list_all_types(session)

@pytest.mark.asyncio
async def test_all_models_by_type(db_session_filled) -> None:
    async with db_session_filled as session:
        res = await SIZService.list_all_models_by_type(session=session, type_id=3)
        res == {2: "СИЗ А"}

@pytest.mark.asyncio
async def test_all_models_by_type_none_found(db_session_filled) -> None:
    async with db_session_filled as session:
        with pytest.raises(NoModelsFound):
            await SIZService.list_all_models_by_type(session=session, type_id=5)

@pytest.mark.parametrize(
    "id,expected",
    [
        (1, SModel(id=1,name="SIZ A")),
        (2, SModel(id=2,name="СИЗ А")),
        (3, SModel(id=3,name="СИЗ Б"))
    ]
)
@pytest.mark.asyncio
async def test_get_model_info(db_session_filled, id, expected) -> None:
    async with db_session_filled as session:
        res = await SIZService.get_model_info(session, id)
        assert res == expected

@pytest.mark.asyncio
async def test_get_model_info_none_found(db_session_filled) -> None:
    async with db_session_filled as session:
        with pytest.raises(InvalidModelError):
            await SIZService.get_model_info(session, 999)

@pytest.mark.parametrize(
    "id,name,file_id",
    [
        (1, "SIZ A", "bWlrZWxqb2huc29u")
    ]
)
@pytest.mark.asyncio
async def test_upload_model_file_id(db_session_filled, id, name, file_id) -> None:
    async with db_session_filled as session:
        await SIZService.upload_model_file_id(session, id, file_id)
        res = await SIZModelDAO.find_by_id(id, session)
        assert res.name == name
        assert res.file_id == file_id


@pytest.mark.parametrize(
    "dao_add_new_object_id,model_id,user_id,review_text",
    [
        (1, 2, 8, "Great Model!")
    ],
    indirect=["dao_add_new_object_id"]
)
@pytest.mark.asyncio
async def test_save_review(db_session_filled, context, dao_add_new_object_id, model_id, user_id, review_text) -> None:
    async with db_session_filled as session:
        await context.update_data(model_id=model_id, user_id=user_id, review=review_text)
        await SIZService.save_review(state=context, session=session)
        res = await SIZReviewDAO.find_by_id(dao_add_new_object_id, session)
        assert res.model_id == model_id
        assert res.user_id == user_id
        assert res.review_text == review_text

@pytest.mark.asyncio
async def test_save_review_save_error(db_session_filled, context) -> None:
    async with db_session_filled as session:
        with pytest.raises(ReviewSaveError):
            await SIZService.save_review(state=context, session=session)
