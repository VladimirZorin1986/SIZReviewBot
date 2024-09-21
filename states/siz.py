from aiogram.fsm.state import State, StatesGroup


class SIZInfoState(StatesGroup):
    get_type = State()
    get_model = State()
    show_info = State()


class SIZReviewState(StatesGroup):
    get_type = State()
    get_model = State()
    set_review = State()
