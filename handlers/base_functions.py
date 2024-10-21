from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from presentation.keyboards.reply import initial_kb, authorization_kb, return_kb
from services.utils import terminate_state_branch
from presentation.responses import message_response
from services.base import BaseService
from states.auth import AuthState


async def return_to_main_menu(message: Message, state: FSMContext, session: AsyncSession, user_id: int):
    await terminate_state_branch(message, state)
    if not await BaseService.is_authorized_user(session, user_id):
        await state.set_state(AuthState.get_contact)
        reply_markup = authorization_kb()
    else:
        reply_markup = initial_kb()
    await message_response(
        message=message,
        text='Возврат в главное меню',
        reply_markup=reply_markup,
        state=state
    )


async def navigate_to_auth(message: Message, state: FSMContext):
    await state.set_state(AuthState.get_contact)
    await message_response(
        message=message,
        text='Для работы Вам необходимо авторизоваться',
        reply_markup=authorization_kb(),
        state=state,
        delete_after=True
    )


async def response_back(
        message: Message, state: FSMContext, msg_text: str, delete_after: bool = False, main_only: bool = False):
    await message_response(
        message=message,
        text=msg_text,
        reply_markup=return_kb(main_only=main_only),
        state=state,
        delete_after=delete_after
    )
