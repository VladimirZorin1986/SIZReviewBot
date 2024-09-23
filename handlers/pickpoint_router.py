from aiogram import Router, F
from aiogram.fsm.state import default_state
from aiogram.types import Message, CallbackQuery
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from presentation.keyboards.inline import show_pickpoints, show_potential_score, show_yes_or_no
from presentation.keyboards.reply import return_kb, initial_kb
from states.pickpoint import PickPointState
from presentation.responses import message_response, callback_response
from services.pickpoint import PickPointService
from services.utils import terminate_state_branch


router = Router()


@router.message(StateFilter(default_state), F.text.endswith('Оценить пункт выдачи'))
async def process_show_pickpoints(message: Message, state: FSMContext, session: AsyncSession):
    pickpoints = await PickPointService.list_all_pickpoints(session)
    await message_response(
        message=message,
        text='Выберите пункт выдачи для оценки:',
        reply_markup=show_pickpoints(pickpoints),
        state=state
    )
    await message_response(
        message=message,
        text='Для возврата в главное меню нажмите на кнопку "Вернуться в главное меню"',
        reply_markup=return_kb(main_only=True),
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
        text=f'Вы выбрали пункт выдачи: <b>{name}</b>\nПоставьте оценку от <b>1</b> до <b>5</b>:',
        reply_markup=show_potential_score(),
        state=state,
        num_of_msgs_to_delete=1
    )
    await message_response(
        message=callback.message,
        text='Для возврата к списку пунктов выдачи нажмите на кпопку "Назад"',
        reply_markup=return_kb(main_only=False),
        state=state,
        delete_after=True
    )
    await PickPointService.remember_pickpoint(state, int(pp_id))
    await state.set_state(PickPointState.set_score)
    await callback.answer()


@router.message(StateFilter(PickPointState.set_score), F.text.endswith('Назад'))
async def process_return_to_pickpoints(message: Message, state: FSMContext, session: AsyncSession):
    pickpoints = await PickPointService.list_all_pickpoints(session)
    await message_response(
        message=message,
        text='Выберите пункт выдачи для оценки:',
        reply_markup=show_pickpoints(pickpoints),
        state=state,
        num_of_msgs_to_delete=3
    )
    await message_response(
        message=message,
        text='Для возврата в главное меню нажмите на кнопку "Вернуться в главное меню"',
        reply_markup=return_kb(main_only=True),
        state=state,
        delete_after=True
    )
    await state.set_state(PickPointState.get_pickpoint)


@router.callback_query(StateFilter(PickPointState.set_score), F.data.in_({'1', '2', '3', '4', '5'}))
async def process_set_score(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    await message_response(
        message=callback.message,
        text=f'Вы поставили оценку <strong>{callback.data}</strong>.\n'
             f'Оставьте, пожалуйста комментарий к оценке.\n'
             f'Обратите внимание, что комментарий является <strong>обязательным</strong>.',
        reply_markup=return_kb(main_only=False),
        state=state,
        num_of_msgs_to_delete=1,
        delete_after=True
    )
    await PickPointService.remember_score(state, int(callback.data))
    await state.set_state(PickPointState.set_comment)
    await callback.answer()


@router.message(StateFilter(PickPointState.set_comment), F.text.endswith('Назад'))
async def process_return_to_set_score(message: Message, state: FSMContext, session: AsyncSession):
    data = await state.get_data()
    pickpoint_id = data.get('pickpoint')
    name = await PickPointService.get_pickpoint_name(session, pickpoint_id)
    await message_response(
        message=message,
        text=f'Вы выбрали пункт выдачи: <strong>{name}</strong>\nПоставьте оценку от <b>1</b> до <b>5</b>:',
        reply_markup=show_potential_score(),
        state=state,
        num_of_msgs_to_delete=4
    )
    await message_response(
        message=message,
        text='Для возврата к выставлению оценки нажмите на кпопку "Назад"',
        reply_markup=return_kb(main_only=False),
        state=state,
        delete_after=True
    )
    await state.set_state(PickPointState.set_score)


@router.message(StateFilter(PickPointState.set_comment), F.text)
async def process_set_comment(message: Message, state: FSMContext, session: AsyncSession):
    await message_response(
        message=message,
        text='Сохранить отзыв?',
        reply_markup=show_yes_or_no(),
        state=state,
        add_to_track=True
    )
    await PickPointService.remember_comment(state, message.text.strip())
    await state.set_state(PickPointState.get_confirm)


@router.callback_query(StateFilter(PickPointState.get_confirm), F.data == 'yes')
async def process_save_rating(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    await PickPointService.save_rating(state, session)
    await callback_response(
        callback=callback,
        text='Ваша оценка пункта выдачи сохранена!',
        show_alert=True
    )
    await terminate_state_branch(callback.message, state)
    await message_response(
        message=callback.message,
        text='Возврат в главное меню',
        reply_markup=initial_kb()
    )


@router.callback_query(StateFilter(PickPointState.get_confirm), F.data == 'no')
async def process_return_to_set_comment(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    data = await state.get_data()
    score = data.get('score')
    await message_response(
        message=callback.message,
        text=f'Вы поставили оценку <strong>{score}</strong>.\n'
             f'Оставьте, пожалуйста комментарий к оценке.\n'
             f'Обратите внимание, что комментарий является <strong>обязательным</strong>.',
        reply_markup=return_kb(main_only=False),
        state=state,
        num_of_msgs_to_delete=4
    )
    await state.set_state(PickPointState.set_comment)
    await callback.answer()


@router.callback_query(StateFilter(PickPointState.get_confirm), F.data == 'cancel')
async def process_cancel_branch(callback: CallbackQuery, state: FSMContext) -> None:
    await terminate_state_branch(callback.message, state)
    await message_response(
        message=callback.message,
        text='Возврат в главное меню',
        reply_markup=initial_kb()
    )
    await callback.answer()


@router.message(F.text.endswith('Вернуться в главное меню'))
async def process_return_to_main_menu(message: Message, state: FSMContext, session: AsyncSession):
    await message_response(
        message=message,
        text='Возврат в главное меню',
        reply_markup=initial_kb(),
        delete_after=True
    )
    await terminate_state_branch(message, state)

