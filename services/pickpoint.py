from aiogram.fsm.context import FSMContext
from dao.pickpoint import PickPointDAO, PickPointRatingDAO
from sqlalchemy.ext.asyncio import AsyncSession
from services.base import BaseService
from exceptions.pickpoints import PickPointsNotFound, RatingRecordSaveError
from exceptions.cache import InvalidItems


class PickPointService(BaseService):

    @classmethod
    async def list_all_pickpoints(cls, session: AsyncSession) -> dict[int, str]:
        pickpoints = await PickPointDAO.find_all(session, is_active=True)
        if not pickpoints:
            raise PickPointsNotFound
        return {pickpoint.id: pickpoint.name for pickpoint in pickpoints}

    @classmethod
    async def save_rating(cls, state: FSMContext, session: AsyncSession) -> None:
        try:
            pickpoint_id, score, user_id, comment = await cls.get_variables_from_state(
                state, ['pickpoint_id', 'score', 'user_id', 'comment']
            )
            await PickPointRatingDAO.add_new_object(
                session,
                pickpoint_id=pickpoint_id,
                user_id=user_id,
                rating_score=score,
                score_comment=comment
            )
        except InvalidItems:
            raise RatingRecordSaveError
