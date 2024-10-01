from aiogram.fsm.state import State, StatesGroup


class NotificationState(StatesGroup):
    set_text = State()
    get_confirm = State()
