from aiogram.fsm.state import State, StatesGroup


class PickPointState(StatesGroup):
    get_pickpoint = State()
    set_score = State()
    set_comment = State()
