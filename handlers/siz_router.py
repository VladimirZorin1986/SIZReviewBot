from aiogram import Router, F
from aiogram.fsm.state import default_state
from aiogram.types import Message, CallbackQuery
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from presentation.keyboards.inline import show_siz_types, show_siz_models, show_yes_or_no
from presentation.keyboards.reply import return_kb
from states.siz import SIZInfoState, SIZReviewState
from presentation.responses import message_response, callback_response
from services.siz import SIZService


router = Router()


@router.message(
    StateFilter(default_state), F.text.endswith('Информация по СИЗ') | F.text.endswith('Оставить отзыв на СИЗ'))
async def process_listing_types(message: Message, state: FSMContext, session: AsyncSession):
    siz_types = await SIZService.list_all_types(session)
    new_state = SIZInfoState.get_type if message.text.endswith('Информация по СИЗ') else SIZReviewState.get_type
    await message_response(
        message=message,
        text='Выберите интересующий тип СИЗ из списка:',
        reply_markup=show_siz_types(siz_types),
        delete_after=True
    )
    await SIZService.remember_user(session, state, message.from_user.id)
    await state.set_state(new_state)


@router.callback_query(StateFilter(SIZInfoState.get_type), F.data.startswith('type'))
@router.callback_query(StateFilter(SIZReviewState.get_type), F.data.startswith('type'))
async def process_choice_type(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    _, type_id, name = callback.data.split(':')
    models = await SIZService.list_all_models_by_type(session, int(type_id))
    new_state = SIZReviewState.get_model if await state.get_state() == SIZReviewState.get_type else SIZInfoState.get_model
    await message_response(
        message=callback.message,
        text=f'Вы выбрали тип СИЗ:\n<strong>{name}</strong>',
        reply_markup=show_siz_models(models),
        delete_after=True
    )
    await state.set_state(new_state)
    await callback.answer()


@router.callback_query(StateFilter(SIZInfoState.get_model), F.data.startswith('model'))
async def process_choice_model(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    _, model_id, name = callback.data.split(':')
    model = await SIZService.get_model_info(session, int(model_id))
    await message_response(
        message=callback.message,
        text=f'Вы выбрали модель СИЗ:\n<strong>{name}</strong>',
        reply_markup=return_kb(),
        state=state
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
            text=f'<strong>Условия использования:</strong>\n<code>{model.care_procedure}</code>',
            state=state
        )
    if model.writeoff_criteria:
        await message_response(
            message=callback.message,
            text=f'<strong>Условия списания:</strong>\n<code>{model.writeoff_criteria}</code>',
            state=state
        )
    await state.set_state(SIZInfoState.show_info)
    await callback.message.delete()
    await callback.answer()


@router.callback_query(StateFilter(SIZReviewState.get_model), F.data.startswith('model'))
async def process_set_model(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    _, model_id, name = callback.data.split(':')
    await message_response(
        message=callback.message,
        text=f'Вы выбрали модель СИЗ:\n<strong>{name}</strong>',
        delete_after=True
    )
    await SIZService.remember_model(state, int(model_id))
    await state.set_state(SIZReviewState.set_review)
    await callback.answer()


@router.message(StateFilter(SIZReviewState.set_review), F.text)
async def process_set_review(message: Message, state: FSMContext, session: AsyncSession):
    await message_response(
        message=message,
        text='Сохранить отзыв?',
        reply_markup=show_yes_or_no(),
        state=state
    )
    await SIZService.remember_review(state, message.text.strip())
    await state.set_state(SIZReviewState.confirm_review)


@router.callback_query(StateFilter(SIZReviewState.confirm_review), F.data.startswith('yes'))
async def process_save_review(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    await SIZService.save_review(session, state)
    await callback_response(
        callback=callback,
        text='Ваш отзыв успешно сохранен!',
        show_alert=True,
        delete_after=True
    )
