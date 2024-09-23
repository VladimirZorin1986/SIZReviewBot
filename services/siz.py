from aiogram.fsm.context import FSMContext
from dao.siz import SIZTypeDAO, SIZModelDAO, SIZReviewDAO
from dao.user import UserDAO
from services.models import SModel, SType
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from services.utils import save_variable_in_state, get_variables_from_state


class SIZService:

    @classmethod
    async def list_all_types(cls, session: AsyncSession) -> List[SType]:
        siz_types = await SIZTypeDAO.find_all(session, is_active=True)
        return [SType(id=siz_type.id, name=siz_type.name) for siz_type in siz_types]

    @classmethod
    async def list_all_models_by_type(cls, session: AsyncSession, type_id: int) -> List[SModel]:
        siz_models = await SIZModelDAO.find_all(session, type_id=type_id, is_active=True)
        return [SModel(id=siz_model.id, name=siz_model.name) for siz_model in siz_models]

    @classmethod
    async def get_model_info(cls, session: AsyncSession, model_id: int) -> SModel:
        raw_model = await SIZModelDAO.find_by_id(model_id, session)
        return SModel(
            id=raw_model.id,
            name=raw_model.name,
            protect_props=raw_model.protect_props,
            care_procedure=raw_model.care_procedure,
            writeoff_criteria=raw_model.writeoff_criteria
        )

    @classmethod
    async def remember_type(cls, state: FSMContext, type_id: int) -> None:
        await save_variable_in_state(state, type_id, 'type', convert_func=int)

    @classmethod
    async def remember_model(cls, state: FSMContext, model_id: int) -> None:
        await save_variable_in_state(state, model_id, 'model', convert_func=int)

    @classmethod
    async def remember_user(cls, session: AsyncSession, state: FSMContext, tg_id: int) -> None:
        user = await UserDAO.find_one_or_none(session, tg_id=tg_id, is_active=True)
        await save_variable_in_state(state, user.id, 'user', convert_func=int)

    @classmethod
    async def remember_review(cls, state: FSMContext, review: str) -> None:
        await save_variable_in_state(state, review, 'review', convert_func=str.strip)

    @classmethod
    async def save_review(cls, session: AsyncSession, state: FSMContext) -> None:
        model_id, user_id, review_text = await get_variables_from_state(state, ['model', 'user', 'review'])
        await SIZReviewDAO.add_new_object(
            session,
            model_id=model_id,
            user_id=user_id,
            review_text=review_text
        )


