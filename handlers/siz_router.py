from aiogram import Router, F
from aiogram.fsm.state import default_state
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
import emoji
from sqlalchemy.ext.asyncio import AsyncSession
from presentation.keyboards.inline import show_siz_types, show_siz_models, show_yes_or_no
from presentation.keyboards.reply import return_kb
from states.siz import SIZInfoState, SIZReviewState
from presentation.responses import message_response, callback_response
from services.siz import SIZService
from services.models import SModel
from services.utils import add_message_to_track, erase_last_messages
from handlers.base_functions import return_to_main_menu, navigate_to_auth, response_back


router = Router()


@router.message(
    StateFilter(default_state), F.text.endswith('Информация по СИЗ') | F.text.endswith('Оставить отзыв на СИЗ'))
async def process_listing_types(message: Message, state: FSMContext, session: AsyncSession):
    if not await SIZService.is_authorized_user(session, message.from_user.id):
        await navigate_to_auth(message, state)
    else:
        siz_types = await SIZService.list_all_types(session)
        new_state = SIZInfoState.get_type if message.text.endswith('Информация по СИЗ') else SIZReviewState.get_type
        await message_response(
            message=message,
            text='Выберите интересующий тип СИЗ из списка:',
            reply_markup=show_siz_types(siz_types),
            state=state
        )
        await response_back(
            message=message,
            state=state,
            msg_text='Для возврата в главное меню нажмите на кнопку "Вернуться в главное меню"',
            delete_after=True,
            main_only=True
        )
        await SIZService.cache_user(session, state, message.from_user.id)
        await SIZService.remember_variables_in_state(state, types=siz_types)
        await state.set_state(new_state)


@router.callback_query(StateFilter(SIZInfoState.get_type), F.data.startswith('type'))
@router.callback_query(StateFilter(SIZReviewState.get_type), F.data.startswith('type'))
async def process_choice_type(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    type_id = int(callback.data.split(':')[-1])
    type_name = await SIZService.get_item_name(state, type_id, 'types')
    models = await SIZService.list_all_models_by_type(session, type_id)
    new_state = SIZReviewState.get_model if await state.get_state() == SIZReviewState.get_type else SIZInfoState.get_model
    await message_response(
        message=callback.message,
        text=f'Вы выбрали тип СИЗ:\n<strong>{type_name}</strong>\nВыберите интересующую модель СИЗ из списка:',
        reply_markup=show_siz_models(models),
        state=state,
        num_of_msgs_to_delete=1
    )
    await response_back(
        message=callback.message,
        state=state,
        msg_text='Для возврата к списку типов СИЗ нажмите на кнопку "Назад"',
        delete_after=True,
        main_only=False
    )
    await SIZService.remember_variables_in_state(state, type_id=type_id, models=models)
    await state.set_state(new_state)
    await callback.answer()


@router.message(StateFilter(SIZReviewState.get_model), F.text.endswith('Назад'))
@router.message(StateFilter(SIZInfoState.get_model), F.text.endswith('Назад'))
async def process_return_to_types_list(message: Message, state: FSMContext):
    siz_types = await SIZService.get_variable_from_state(state, 'types')
    new_state = SIZInfoState.get_type if await state.get_state() == SIZInfoState.get_model else SIZReviewState.get_type
    await message_response(
        message=message,
        text='Выберите интересующий тип СИЗ из списка:',
        reply_markup=show_siz_types(siz_types),
        state=state,
        num_of_msgs_to_delete=3
    )
    await response_back(
        message=message,
        state=state,
        msg_text='Для возврата в главное меню нажмите на кнопку "Вернуться в главное меню"',
        delete_after=True,
        main_only=True
    )
    await state.set_state(new_state)


@router.callback_query(StateFilter(SIZInfoState.get_model), F.data.startswith('model'))
async def process_choice_model(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    model = await SIZService.get_model_info(session, int(callback.data.split(':')[-1]))
    await post_model_photo(
        callback, state, session, model,
        caption=f'Вы выбрали модель СИЗ:\n<strong>{model.name}</strong>'
    )
    if model.protect_props:
        await message_response(
            message=callback.message,
            text=f'<strong>Защитные свойства:</strong>\n<code>{model.protect_props}</code>',
            state=state
        )
    if model.care_procedure:
        await message_response(
            message=callback.message,
            text=f'<strong>Порядок ухода:</strong>\n<code>{model.care_procedure}</code>',
            state=state
        )
    if model.writeoff_criteria:
        await message_response(
            message=callback.message,
            text=f'<strong>Критерии преждевременного списания:</strong>\n<code>{model.writeoff_criteria}</code>',
            state=state
        )
    if model.operating_rules:
        await message_response(
            message=callback.message,
            text=f'<strong>Правила эксплуатации:</strong>\n<code>{model.operating_rules}</code>',
            state=state
        )
    await response_back(
        message=callback.message,
        state=state,
        msg_text='Для возврата к списку моделей СИЗ нажмите на кнопку "Назад"',
        delete_after=True,
        main_only=False
    )
    await state.set_state(SIZInfoState.show_info)
    await callback.answer()


@router.callback_query(StateFilter(SIZReviewState.get_model), F.data.startswith('model'))
async def process_set_model(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    model = await SIZService.get_model_info(session, int(callback.data.split(':')[-1]))
    await post_model_photo(
        callback, state, session, model,
        caption=f'Вы выбрали модель СИЗ:\n<strong>{model.name}</strong>\n\nНапишите, пожалуйста, отзыв на выбранную модель.'
    )
    await response_back(
        message=callback.message,
        state=state,
        msg_text='Для возврата к списку моделей СИЗ нажмите на кнопку "Назад"',
        delete_after=True,
        main_only=False
    )
    await SIZService.remember_variables_in_state(state, model_id=model.id)
    await state.set_state(SIZReviewState.set_review)
    await callback.answer()


@router.message(StateFilter(SIZReviewState.set_review), F.text.endswith('Назад'))
@router.message(StateFilter(SIZInfoState.show_info), F.text.endswith('Назад'))
async def process_return_to_models_list(message: Message, state: FSMContext):
    models = await SIZService.get_variable_from_state(state, 'models')
    current_state = await state.get_state()
    new_state = SIZReviewState.get_model if current_state == SIZReviewState.set_review else SIZInfoState.get_model
    msgs_to_delete = 6 if current_state == SIZInfoState.show_info else 3
    await message_response(
        message=message,
        text=f'Выберите интересующую модель СИЗ из списка:',
        reply_markup=show_siz_models(models),
        state=state,
        num_of_msgs_to_delete=msgs_to_delete
    )
    await response_back(
        message=message,
        state=state,
        msg_text='Для возврата к списку типов СИЗ нажмите на кнопку "Назад"',
        delete_after=True,
        main_only=False
    )
    await state.set_state(new_state)


@router.message(StateFilter(SIZReviewState.set_review), F.text,
                ~F.text.endswith('Назад'), ~F.text.endswith('Вернуться в главное меню'))
async def process_set_review(message: Message, state: FSMContext):
    await message_response(
        message=message,
        text='Сохранить отзыв?',
        reply_markup=show_yes_or_no(),
        state=state,
        add_to_track=True
    )
    await SIZService.remember_variables_in_state(state, review=emoji.replace_emoji(message.text.strip(), replace=''))
    await state.set_state(SIZReviewState.confirm_review)


@router.callback_query(StateFilter(SIZReviewState.confirm_review), F.data.startswith('yes'))
async def process_save_review(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    await SIZService.save_review(session, state)
    await callback_response(
        callback=callback,
        text='Ваш отзыв успешно сохранен!',
        show_alert=True
    )
    await return_to_main_menu(callback.message, state, session, callback.from_user.id)


@router.callback_query(StateFilter(SIZReviewState.confirm_review), F.data.startswith('no'))
async def process_return_to_set_review(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    model_id = await SIZService.get_variable_from_state(state, 'model_id')
    model = await SIZService.get_model_info(session, model_id)
    await post_model_photo(
        callback, state, session, model,
        caption=f'Вы выбрали модель СИЗ:\n<strong>{model.name}</strong>\n\nНапишите, пожалуйста, отзыв на выбранную модель.',
        num_of_msgs_to_delete=4
    )
    await response_back(
        message=callback.message,
        state=state,
        msg_text='Для возврата к списку моделей СИЗ нажмите на кнопку "Назад"',
        delete_after=False,
        main_only=False
    )
    await state.set_state(SIZReviewState.set_review)


@router.callback_query(StateFilter(SIZReviewState.confirm_review), F.data.endswith('cancel'))
async def process_return_to_main_menu(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    await return_to_main_menu(callback.message, state, session, callback.from_user.id)
    await callback.answer()


async def post_model_photo(
        callback: CallbackQuery,
        state: FSMContext,
        session: AsyncSession,
        model: SModel,
        caption: str,
        num_of_msgs_to_delete: int = 1
):
    photo = model.file_id or FSInputFile(f'static/images/model_{model.id}.png')
    msg = await callback.message.answer_photo(
        photo=photo,
        caption=caption,
        reply_markup=return_kb(main_only=False)
    )
    if not model.file_id:
        await SIZService.upload_model_file_id(session, model.id, msg.photo[0].file_id)
    await erase_last_messages(
        state, msg_cnt_to_delete=num_of_msgs_to_delete, bot=callback.bot, chat_id=callback.message.chat.id)
    await add_message_to_track(msg, state)
