import pytest
from datetime import datetime
from services.pickpoint import PickPointService
from database.models import PickPoint
from exceptions.pickpoints import PickPointsNotFound, RatingRecordSaveError
from dao.pickpoint import PickPointRatingDAO

db_tables = {
    PickPoint: [
        {"id": 1, "name": "Pickpoint A", "is_active": True,  "last_modified_at": datetime(2025, 1, 6, 10, 0, 0)},
        {"id": 2, "name": "Pickpoint B", "is_active": False, "last_modified_at": datetime(2025, 2, 6, 10, 0, 0)},
        {"id": 3, "name": "Pickpoint C", "is_active": True,  "last_modified_at": datetime(2025, 3, 6, 10, 0, 0)},
    ]
}

@pytest.mark.asyncio
async def test_list_all_pickpoints(db_session_filled) -> None:
    async with db_session_filled as session:
        res = await PickPointService.list_all_pickpoints(session)
        assert res == {1: "Pickpoint A", 3: "Pickpoint C"}

@pytest.mark.asyncio
async def test_test_list_all_pickpoints_no_pickpoints(db_session) -> None:
    async with db_session as session:
        with pytest.raises(PickPointsNotFound):
            await PickPointService.list_all_pickpoints(session)

@pytest.mark.parametrize(
    "dao_add_new_object_id,pickpoint_id,score,user_id,comment",
    [
        (1, 1, 5, 10, "Great Pickpoint!")
    ],
    indirect=["dao_add_new_object_id"]
)
@pytest.mark.asyncio
async def test_save_rating(db_session_filled, context, dao_add_new_object_id, pickpoint_id, score, user_id, comment) -> None:
    async with db_session_filled as session:
        await context.update_data(pickpoint_id=pickpoint_id, score=score, user_id=user_id, comment=comment)
        await PickPointService.save_rating(state=context, session=session)
        res = await PickPointRatingDAO.find_by_id(dao_add_new_object_id, session)
        assert res.pickpoint_id == pickpoint_id
        assert res.rating_score == score
        assert res.user_id == user_id
        assert res.score_comment == comment

@pytest.mark.asyncio
async def test_save_rating_record_save_error(db_session_filled, context) -> None:
    async with db_session_filled as session:
        with pytest.raises(RatingRecordSaveError):
            await PickPointService.save_rating(state=context, session=session)