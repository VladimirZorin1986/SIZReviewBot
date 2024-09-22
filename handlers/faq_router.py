from aiogram import Router, F
from aiogram.fsm.state import default_state
from aiogram.types import Message, CallbackQuery
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from presentation.faq_views import answer_view
from presentation.keyboards.inline import show_questions
from presentation.keyboards.reply import return_kb
from states.faq import QuestionState
from presentation.responses import message_response, callback_response
from services.faq import FAQService


router = Router()


@router.message(F.text.endswith('F.A.Q.'), StateFilter(default_state))
async def process_show_questions(message: Message, state: FSMContext, session: AsyncSession):
    questions = await FAQService.get_questions(session)
    await state.set_state(QuestionState.get_question)
    await message_response(
        message=message,
        text='Выберите интересующий вопрос из списка:',
        reply_markup=show_questions(questions),
        state=state
    )
    await message_response(
        message=message,
        text='Для возврата нажмите на кнопку "Вернуться в главное меню"',
        reply_markup=return_kb(),
        state=state
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
