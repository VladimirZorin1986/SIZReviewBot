from typing import Any
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from dao.user import UserDAO


class BaseService:

    @classmethod
    async def remember_variables_in_state(cls, state: FSMContext, **kwargs) -> None:
        await state.update_data(**kwargs)

    @classmethod
    async def cache_user(cls, session: AsyncSession, state: FSMContext, tg_id: int) -> None:
        user = await UserDAO.find_one_or_none(session, tg_id=tg_id, is_active=True)
        await state.update_data(user_id=user.id)

    @classmethod
    async def get_variables_from_state(cls, state: FSMContext, var_names: list[str]) -> list[Any]:
        data = await state.get_data()
        return [data[var_name] for var_name in var_names]

    @classmethod
    async def get_variable_from_state(cls, state: FSMContext, var_name: str) -> Any:
        data = await state.get_data()
        return data[var_name]

    @classmethod
    async def is_authorized_user(cls, async_session: AsyncSession, tg_id: int) -> bool:
        if not await UserDAO.find_one_or_none(async_session, tg_id=tg_id, is_active=True):
            return False
        return True




