from aiogram.fsm.state import State, StatesGroup


class QuestionState(StatesGroup):
    get_question = State()
