from aiogram.fsm.context import FSMContext
from dao.siz import SIZTypeDAO, SIZModelDAO, SIZReviewDAO
from dao.user import UserDAO
from services.models import SModel, SType
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from services.utils import save_variable_in_state, get_variables_from_state
from services.base import BaseService


class SIZService(BaseService):

    @classmethod
    async def list_all_types(cls, session: AsyncSession) -> dict[int, str]:
        siz_types = await SIZTypeDAO.get_filled_types(session)
        return {siz_type.id: siz_type.name for siz_type in siz_types}

    @classmethod
    async def list_all_models_by_type(cls, session: AsyncSession, type_id: int) -> dict[int, str]:
        siz_models = await SIZModelDAO.find_all(session, type_id=type_id, is_active=True)
        return {siz_model.id: siz_model.name for siz_model in siz_models}

    @classmethod
    async def get_model_info(cls, session: AsyncSession, model_id: int) -> SModel:
        raw_model = await SIZModelDAO.find_by_id(model_id, session)
        return SModel(
            id=raw_model.id,
            name=raw_model.name,
            protect_props=raw_model.protect_props,
            care_procedure=raw_model.care_procedure,
            writeoff_criteria=raw_model.writeoff_criteria,
            operating_rules=raw_model.operating_rules,
            file_id=raw_model.file_id
        )

    @classmethod
    async def upload_model_file_id(cls, session: AsyncSession, model_id: int, file_id: str) -> None:
        await SIZModelDAO.update_object(session, model_id, file_id=file_id)

    @classmethod
    async def save_review(cls, session: AsyncSession, state: FSMContext) -> None:
        model_id, user_id, review_text = await cls.get_variables_from_state(
            state, ['model_id', 'user_id', 'review']
        )
        await SIZReviewDAO.add_new_object(
            session,
            model_id=model_id,
            user_id=user_id,
            review_text=review_text
        )

    @classmethod
    async def get_item_name(cls, state: FSMContext, item_id: int, items_name: str) -> str:
        items = await cls.get_variable_from_state(state, items_name)
        return items.get(item_id)


