from aiogram import Router, F
from aiogram.fsm.state import default_state
from aiogram.types import Message, CallbackQuery
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from services.notification import NotificationService
from presentation.keyboards.inline import show_yes_or_no
from presentation.keyboards.reply import initial_kb, authorization_kb, return_kb
from services.utils import terminate_state_branch
from states.auth import AuthState
from presentation.responses import message_response, callback_response
from services.user import UserService
from exceptions.user import UserNotExist
from states.notification import NotificationState
from handlers.base_functions import return_to_main_menu, response_back

router = Router()


@router.message(StateFilter(AuthState.get_contact), F.contact)
async def process_auth_with_contact(message: Message, state: FSMContext, session: AsyncSession):
    try:
        await UserService.authorize_user(session, message.from_user.id, message.contact.phone_number)
        text = 'Вы успешно авторизованы'
        reply_markup = initial_kb()
        await terminate_state_branch(message, state)
    except UserNotExist:
        text = 'Вас нет в списке пользователей'
        reply_markup = authorization_kb()
    await message_response(
        message=message,
        text=text,
        reply_markup=reply_markup
    )


@router.message(StateFilter(AuthState.get_contact), ~F.contact)
async def process_auth_no_contact(message: Message, state: FSMContext):
    await message_response(
        message=message,
        text='Необходимо дать доступ к контактным данным. '
             'Иначе авторизация невозможна.',
        state=state
    )


@router.message(StateFilter(default_state), F.text.endswith('Массовая рассылка'))
async def process_start_notification(message: Message, state: FSMContext):
    await response_back(
        message=message,
        state=state,
        msg_text='Введите текст уведомления:',
        delete_after=True,
        main_only=True
    )
    await state.set_state(NotificationState.set_text)


@router.message(StateFilter(NotificationState.set_text), F.text, ~F.text.endswith('Вернуться в главное меню'))
async def process_set_notification_text(message: Message, state: FSMContext):
    await state.update_data(notification_text=message.text.strip())
    await message_response(
        message=message,
        text='Отправить уведомление пользователям?',
        reply_markup=show_yes_or_no(),
        state=state
    )
    await state.set_state(NotificationState.get_confirm)


@router.callback_query(StateFilter(NotificationState.get_confirm), F.data == 'yes')
async def process_send_notification(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    data = await state.get_data()
    await NotificationService.send_mass_notification(
        bot=callback.bot,
        text=data['notification_text'],
        session=session
    )
    await callback_response(
        callback=callback,
        text='Сообщение отправлено',
        show_alert=True
    )
    await return_to_main_menu(callback.message, state, session, callback.from_user.id)


@router.callback_query(StateFilter(NotificationState.get_confirm), F.data == 'no')
@router.callback_query(StateFilter(NotificationState.get_confirm), F.data == 'cancel')
async def process_cancel_notification(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    await callback_response(
        callback=callback,
        text='Отправка отменена',
        show_alert=True
    )
    await return_to_main_menu(callback.message, state, session, callback.from_user.id)

