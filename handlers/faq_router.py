from aiogram import Router, F
from aiogram.fsm.state import default_state
from aiogram.types import Message, CallbackQuery
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from presentation.faq_views import answer_view
from presentation.keyboards.inline import show_questions
from states.faq import QuestionState
from presentation.responses import message_response, callback_response
from services.faq import FAQService
from handlers.base_functions import navigate_to_auth, response_back


router = Router()


@router.message(F.text.endswith('Ответы на вопросы'), StateFilter(default_state))
async def process_show_questions(message: Message, state: FSMContext, session: AsyncSession):
    if not await FAQService.is_authorized_user(session, message.from_user.id):
        await navigate_to_auth(message, state)
    else:
        questions = await FAQService.get_questions(session)
        await state.set_state(QuestionState.get_question)
        await message_response(
            message=message,
            text='Выберите интересующий вопрос из списка:',
            reply_markup=show_questions(questions),
            state=state
        )
        await response_back(
            message=message,
            state=state,
            msg_text='Для возврата в главное меню нажмите на кнопку "Вернуться в главное меню"',
            delete_after=True,
            main_only=True
        )


@router.callback_query(StateFilter(QuestionState.get_question), F.data.startswith('question'))
async def process_show_answer(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    answer = await FAQService.get_answer(session, int(callback.data.split(':')[-1]))
    await message_response(
        message=callback.message,
        text=answer_view(answer),
        state=state
    )
    await callback_response(callback)
