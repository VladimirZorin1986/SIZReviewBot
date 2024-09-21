from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from presentation.keyboards.reply import initial_kb
from states.auth import AuthState
from presentation.responses import message_response
from services.user import UserService
from exceptions.user import UserNotExist


router = Router()


@router.message(StateFilter(AuthState.get_contact), F.contact)
async def process_auth_with_contact(message: Message, state: FSMContext, session: AsyncSession):
    try:
        await UserService.authorize_user(session, message.from_user.id, message.contact.phone_number)
        text = 'Вы успешно авторизованы'
        reply_markup = initial_kb()
    except UserNotExist:
        text = 'Вас нет в списке пользователей'
        reply_markup = ReplyKeyboardRemove()
    await message_response(
        message=message,
        text=text,
        reply_markup=reply_markup
    )
    await state.clear()


@router.message(StateFilter(AuthState.get_contact), ~F.contact)
async def process_auth_no_contact(message: Message):
    await message_response(
        message=message,
        text='Необходимо дать доступ к контактным данным. '
             'Иначе авторизация невозможна.'
    )
