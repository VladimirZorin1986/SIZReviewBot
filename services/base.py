from typing import Any
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from dao.user import UserDAO
from exceptions.cache import InvalidItems, InvalidVariable, ItemNotFound
from exceptions.user import UserNotExist


class BaseService:

    @classmethod
    async def remember_variables_in_state(cls, state: FSMContext, **kwargs) -> None:
        await state.update_data(**kwargs)

    @classmethod
    async def cache_user(cls, session: AsyncSession, state: FSMContext, tg_id: int) -> None:
        user = await UserDAO.find_one_or_none(session, tg_id=tg_id, is_active=True)
        if not user:
            raise UserNotExist
        await state.update_data(user_id=user.id)

    @classmethod
    async def get_variables_from_state(cls, state: FSMContext, var_names: list[str]) -> list[Any]:
        data = await state.get_data()
        try:
            return [data[var_name] for var_name in var_names]
        except KeyError:
            raise InvalidVariable

    @classmethod
    async def get_variable_from_state(cls, state: FSMContext, var_name: str) -> Any:
        data = await state.get_data()
        try:
            return data[var_name]
        except KeyError:
            raise InvalidVariable

    @classmethod
    async def is_authorized_user(cls, async_session: AsyncSession, tg_id: int) -> bool:
        if not await UserDAO.find_one_or_none(async_session, tg_id=tg_id, is_active=True):
            return False
        return True

    @classmethod
    async def get_item_name(cls, state: FSMContext, item_id: int, items_name: str) -> str:
        try:
            items = await cls.get_variable_from_state(state, items_name)
            item_name = items.get(str(item_id)) or items.get(item_id)
        except AttributeError:
            raise InvalidItems
        else:
            if not item_name:
                raise ItemNotFound
            return item_name




