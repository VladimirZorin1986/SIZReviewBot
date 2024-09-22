from aiogram.fsm.context import FSMContext
from dao.pickpoint import PickPointDAO, PickPointRatingDAO
from dao.user import UserDAO
from services.models import SPickPoint
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from services.utils import save_variable_in_state, get_variables_from_state


class PickPointService:

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
    async def get_pickpoint_name(cls, session: AsyncSession, pickpoint_id: int) -> str:
        pickpoint = await PickPointDAO.find_by_id(pickpoint_id, session)
        return pickpoint.name

    @classmethod
    async def remember_pickpoint(cls, state: FSMContext, pickpoint_id: int) -> None:
        await save_variable_in_state(state, pickpoint_id, 'pickpoint', convert_func=int)

    @classmethod
    async def remember_score(cls, state: FSMContext, score: int) -> None:
        await save_variable_in_state(state, score, 'score', convert_func=int)

    @classmethod
    async def remember_user(cls, session: AsyncSession, state: FSMContext, tg_id: int) -> None:
        user = await UserDAO.find_one_or_none(session, tg_id=tg_id)
        await save_variable_in_state(state, user.id, 'user', convert_func=int)

    @classmethod
    async def remember_comment(cls, state: FSMContext, comment: str) -> None:
        await save_variable_in_state(state, comment, 'comment', convert_func=str.strip)

    @classmethod
    async def save_rating(cls, state: FSMContext, session: AsyncSession) -> None:
        pickpoint_id, score, user_id, comment = await get_variables_from_state(
            state, ['pickpoint', 'score', 'user', 'comment']
        )
        await PickPointRatingDAO.add_new_object(
            session,
            pickpoint_id=pickpoint_id,
            user_id=user_id,
            rating_score=score,
            score_comment=comment
        )

