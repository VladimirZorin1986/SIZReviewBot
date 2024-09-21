from aiogram.fsm.state import State, StatesGroup


class AuthState(StatesGroup):
    get_contact = State()
