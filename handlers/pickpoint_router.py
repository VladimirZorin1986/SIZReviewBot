from aiogram import Router, F
from aiogram.fsm.state import default_state
from aiogram.types import Message, CallbackQuery
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
import emoji
from presentation.keyboards.inline import show_pickpoints, show_potential_score, show_yes_or_no
from presentation.keyboards.reply import return_kb
from presentation.pickpoint_views import score_comment_view, set_score_view
from states.pickpoint import PickPointState
from presentation.responses import message_response, callback_response
from services.pickpoint import PickPointService
from handlers.base_functions import return_to_main_menu, navigate_to_auth, response_back, handle_exception
from exceptions.cache import CacheError
from exceptions.pickpoints import RatingRecordSaveError, PickPointsNotFound
from exceptions.user import UserNotExist

router = Router()


@router.message(StateFilter(default_state), F.text.endswith('Оценить работу пункта выдачи'))
async def process_show_pickpoints(message: Message, state: FSMContext, session: AsyncSession):
    if not await PickPointService.is_authorized_user(session, message.from_user.id):
        await navigate_to_auth(message, state)
    else:
        try:
            pickpoints = await PickPointService.list_all_pickpoints(session)
            await PickPointService.cache_user(session, state, message.from_user.id)
            await message_response(
                message=message,
                text='Выберите пункт выдачи для оценки:',
                reply_markup=show_pickpoints(pickpoints),
                state=state
            )
            await response_back(
                message=message,
                state=state,
                msg_text='Для возврата в главное меню нажмите на кнопку <b>Вернуться в главное меню</b>',
                delete_after=True,
                main_only=True
            )
            await PickPointService.remember_variables_in_state(state, pickpoints=pickpoints)
            await state.set_state(PickPointState.get_pickpoint)
        except PickPointsNotFound:
            await message_response(
                message=message,
                text='Не найдены пункты выдачи доступные для оценки.',
                reply_markup=message.reply_markup,
                state=state,
                delete_after=True
            )
        except UserNotExist:
            await message_response(
                message=message,
                text='Произошла ошибка при идентификации пользователя. Выполните команду /start и попробуйте снова.',
                reply_markup=message.reply_markup,
                state=state,
                delete_after=True
            )


@router.callback_query(StateFilter(PickPointState.get_pickpoint), F.data.startswith('pickpoint'))
async def process_choice_pickpoint(callback: CallbackQuery, state: FSMContext):
    try:
        pp_id = int(callback.data.split(':')[-1])
        pp_name = await PickPointService.get_item_name(state, pp_id, 'pickpoints')
        await message_response(
            message=callback.message,
            text=set_score_view(pp_name),
            reply_markup=show_potential_score(),
            state=state,
            num_of_msgs_to_delete=1
        )
        await response_back(
            message=callback.message,
            state=state,
            msg_text='Для возврата к списку пунктов выдачи нажмите на кнопку <b>Назад</b>',
            delete_after=True,
            main_only=False
        )
        await PickPointService.remember_variables_in_state(state, pickpoint_id=pp_id)
        await state.set_state(PickPointState.set_score)
    except CacheError:
        await handle_exception(callback.message, state)
    finally:
        await callback.answer()


@router.message(StateFilter(PickPointState.set_score), F.text.endswith('Назад'))
async def process_return_to_pickpoints(message: Message, state: FSMContext):
    try:
        pickpoints = await PickPointService.get_variable_from_state(state, 'pickpoints')
        await message_response(
            message=message,
            text='Выберите пункт выдачи для оценки:',
            reply_markup=show_pickpoints(pickpoints),
            state=state,
            num_of_msgs_to_delete=3
        )
        await response_back(
            message=message,
            state=state,
            msg_text='Для возврата в главное меню нажмите на кнопку <b>Вернуться в главное меню</b>',
            delete_after=True,
            main_only=True
        )
        await state.set_state(PickPointState.get_pickpoint)
    except CacheError:
        await handle_exception(message, state)


@router.callback_query(StateFilter(PickPointState.set_score), F.data.in_({'1', '2', '3', '4', '5'}))
async def process_set_score(callback: CallbackQuery, state: FSMContext):
    score = int(callback.data)
    await message_response(
        message=callback.message,
        text=score_comment_view(score),
        reply_markup=return_kb(main_only=False),
        state=state,
        num_of_msgs_to_delete=1,
        delete_after=True
    )
    await PickPointService.remember_variables_in_state(state, score=score)
    await state.set_state(PickPointState.set_comment)
    await callback.answer()


@router.message(StateFilter(PickPointState.set_comment), F.text.endswith('Назад'))
async def process_return_to_set_score(message: Message, state: FSMContext):
    try:
        pp_id = await PickPointService.get_variable_from_state(state, 'pickpoint_id')
        pp_name = await PickPointService.get_item_name(state, pp_id, 'pickpoints')
        await message_response(
            message=message,
            text=set_score_view(pp_name),
            reply_markup=show_potential_score(),
            state=state,
            num_of_msgs_to_delete=4
        )
        await response_back(
            message=message,
            state=state,
            msg_text='Для возврата к выбору пункта выдачи нажмите на кнопку <b>Назад</b>',
            delete_after=True,
            main_only=False
        )
        await state.set_state(PickPointState.set_score)
    except CacheError:
        await handle_exception(message, state)


@router.message(StateFilter(PickPointState.set_comment), F.text,
                ~F.text.endswith('Назад'), ~F.text.endswith('Вернуться в главное меню'))
async def process_set_comment(message: Message, state: FSMContext):
    await message_response(
        message=message,
        text='Сохранить отзыв?',
        reply_markup=show_yes_or_no(),
        state=state,
        add_to_track=True
    )
    await PickPointService.remember_variables_in_state(
        state, comment=emoji.replace_emoji(message.text.strip(), replace='')
    )
    await state.set_state(PickPointState.get_confirm)


@router.callback_query(StateFilter(PickPointState.get_confirm), F.data == 'yes')
async def process_save_rating(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    try:
        await PickPointService.save_rating(state, session)
        await callback_response(
            callback=callback,
            text='Ваша оценка пункта выдачи сохранена!',
            show_alert=True
        )
        await return_to_main_menu(callback.message, state, session, callback.from_user.id)
    except RatingRecordSaveError:
        await handle_exception(callback.message, state)
        await callback.answer()


@router.callback_query(StateFilter(PickPointState.get_confirm), F.data == 'no')
async def process_return_to_set_comment(callback: CallbackQuery, state: FSMContext):
    try:
        score = await PickPointService.get_variable_from_state(state, 'score')
        await message_response(
            message=callback.message,
            text=score_comment_view(score),
            reply_markup=return_kb(main_only=False),
            state=state,
            num_of_msgs_to_delete=4
        )
        await state.set_state(PickPointState.set_comment)
    except CacheError:
        await handle_exception(callback.message, state)
    finally:
        await callback.answer()


@router.callback_query(StateFilter(PickPointState.get_confirm), F.data == 'cancel')
async def process_cancel_branch(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    await return_to_main_menu(callback.message, state, session, callback.from_user.id)
    await callback.answer()


@router.message(F.text.endswith('Вернуться в главное меню'))
async def process_return_to_main_menu(message: Message, state: FSMContext, session: AsyncSession):
    await return_to_main_menu(message, state, session, message.from_user.id)
