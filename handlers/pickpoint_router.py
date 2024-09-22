from aiogram import Router, F
from aiogram.fsm.state import default_state
from aiogram.types import Message, CallbackQuery
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from presentation.faq_views import answer_view
from presentation.keyboards.inline import show_pickpoints, show_potential_score, show_yes_or_no
from presentation.keyboards.reply import return_kb
from states.pickpoint import PickPointState
from presentation.responses import message_response, callback_response
from services.pickpoint import PickPointService


router = Router()


@router.message(StateFilter(default_state), F.text.endswith('Оценить пункт выдачи'))
async def process_show_pickpoints(message: Message, state: FSMContext, session: AsyncSession):
    pickpoints = await PickPointService.list_all_pickpoints(session)
    await message_response(
        message=message,
        text='Выберите пункт выдачи для оценки:',
        reply_markup=show_pickpoints(pickpoints),
        state=state,
        delete_after=True
    )
    await PickPointService.remember_user(session, state, message.from_user.id)
    await state.set_state(PickPointState.get_pickpoint)


@router.callback_query(StateFilter(PickPointState.get_pickpoint), F.data.startswith('pickpoint'))
async def process_choice_pickpoint(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    _, pp_id, name = callback.data.split(':')
    await message_response(
        message=callback.message,
        text=f'Вы выбрали пункт выдачи: {name}\nПоставьте оценку от 1 до 5:',
        reply_markup=show_potential_score(),
        state=state,
        delete_after=True
    )
    await PickPointService.remember_pickpoint(state, int(pp_id))
    await state.set_state(PickPointState.set_score)
    await callback.answer()


@router.callback_query(StateFilter(PickPointState.set_score), F.data.in_({'1', '2', '3', '4', '5'}))
async def process_set_score(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    await message_response(
        message=callback.message,
        text=f'Вы поставили оценку {callback.data}.\nНапишите отзыв. Обратите внимание, что отзыв является обязательным.',
        reply_markup=None,
        state=state
    )
    await PickPointService.remember_score(state, int(callback.data))
    await state.set_state(PickPointState.set_comment)
    await callback.answer()


@router.message(StateFilter(PickPointState.set_comment), F.text)
async def process_set_comment(message: Message, state: FSMContext, session: AsyncSession):
    await message_response(
        message=message,
        text='Сохранить отзыв?',
        reply_markup=show_yes_or_no(),
        state=state
    )
    await PickPointService.remember_comment(state, message.text.strip())
    await state.set_state(PickPointState.get_confirm)


@router.callback_query(StateFilter(PickPointState.get_confirm), F.data == 'yes')
async def process_save_rating(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    await PickPointService.save_rating(state, session)
    await callback_response(
        callback=callback,
        text='Ваша оценка пункта выдачи сохранена!',
        show_alert=True,
        delete_after=True
    )
