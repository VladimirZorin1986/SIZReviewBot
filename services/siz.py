from aiogram.fsm.context import FSMContext
from dao.siz import SIZTypeDAO, SIZModelDAO, SIZReviewDAO
from services.models import SModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import NoResultFound
from services.base import BaseService
from exceptions.cache import InvalidVariable
from exceptions.siz import NoTypesFound, NoModelsFound, InvalidModelError, ReviewSaveError


class SIZService(BaseService):

    @classmethod
    async def list_all_types(cls, session: AsyncSession) -> dict[int, str]:
        siz_types = await SIZTypeDAO.get_filled_types(session)
        if not siz_types:
            raise NoTypesFound
        return {siz_type.id: siz_type.name for siz_type in siz_types}

    @classmethod
    async def list_all_models_by_type(cls, session: AsyncSession, type_id: int) -> dict[int, str]:
        siz_models = await SIZModelDAO.find_all(session, type_id=type_id, is_active=True)
        if not siz_models:
            raise NoModelsFound
        return {siz_model.id: siz_model.name for siz_model in siz_models}

    @classmethod
    async def get_model_info(cls, session: AsyncSession, model_id: int) -> SModel:
        try:
            raw_model = await SIZModelDAO.find_by_id(model_id, session)
            return SModel(
                id=raw_model.id,
                name=raw_model.name,
                protect_props=raw_model.protect_props,
                care_procedure=raw_model.care_procedure,
                writeoff_criteria=raw_model.writeoff_criteria,
                operating_rules=raw_model.operating_rules,
                file_id=raw_model.file_id,
                file_name=raw_model.file_name
            )
        except NoResultFound:
            raise InvalidModelError

    @classmethod
    async def upload_model_file_id(cls, session: AsyncSession, model_id: int, file_id: str) -> None:
        await SIZModelDAO.update_object(session, model_id, file_id=file_id)

    @classmethod
    async def save_review(cls, session: AsyncSession, state: FSMContext) -> None:
        try:
            model_id, user_id, review_text = await cls.get_variables_from_state(
                state, ['model_id', 'user_id', 'review']
            )
            await SIZReviewDAO.add_new_object(
                session,
                model_id=model_id,
                user_id=user_id,
                review_text=review_text
            )
        except InvalidVariable:
            raise ReviewSaveError
