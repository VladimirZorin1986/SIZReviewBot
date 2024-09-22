from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def authorization_kb() -> ReplyKeyboardMarkup:
    kb = [[KeyboardButton(text='🚶‍➡️ Авторизоваться', request_contact=True)]]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, one_time_keyboard=True)


def initial_kb() -> ReplyKeyboardMarkup:
    kb = [
        [KeyboardButton(text='🏬 Оценить пункт выдачи'),
         KeyboardButton(text='🦺 Информация по СИЗ')],
        [KeyboardButton(text='📖 Оставить отзыв на СИЗ'),
         KeyboardButton(text='🔎 F.A.Q.')]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, one_time_keyboard=True)


def return_kb(main_only: bool = True) -> ReplyKeyboardMarkup:
    kb = []
    if not main_only:
        kb.append([KeyboardButton(text='↩ Назад')])
    kb.append([KeyboardButton(text='🔙 Вернуться в главное меню')])
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

