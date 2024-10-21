from aiogram.fsm.context import FSMContext
from dao.pickpoint import PickPointDAO, PickPointRatingDAO
from dao.user import UserDAO
from services.models import SPickPoint
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from services.utils import save_variable_in_state, get_variables_from_state
from services.base import BaseService


class PickPointService(BaseService):

    @classmethod
    async def list_all_pickpoints(cls, session: AsyncSession) -> List[SPickPoint]:
        pickpoints = await PickPointDAO.find_all(session, is_active=True)
        return [
            SPickPoint(
                id=pickpoint.id,
                name=pickpoint.name
            ) for pickpoint in pickpoints
        ]

    @classmethod
    async def save_rating(cls, state: FSMContext, session: AsyncSession) -> None:
        pickpoint_id, score, user_id, comment = await get_variables_from_state(
            state, ['pickpoint_id', 'score', 'user_id', 'comment']
        )
        await PickPointRatingDAO.add_new_object(
            session,
            pickpoint_id=pickpoint_id,
            user_id=user_id,
            rating_score=score,
            score_comment=comment
        )
