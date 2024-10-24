from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def authorization_kb() -> ReplyKeyboardMarkup:
    kb = [[KeyboardButton(text='🚶‍➡️ Авторизоваться', request_contact=True)]]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, one_time_keyboard=True)


def initial_kb(is_admin: bool = False) -> ReplyKeyboardMarkup:
    kb = [
        [KeyboardButton(text='🏬 Оценить работу пункта выдачи')],
        [KeyboardButton(text='📖 Оставить отзыв о СИЗ')],
        [KeyboardButton(text='🦺 Информация о СИЗ')],
        [KeyboardButton(text='🔎 Ответы на вопросы')]
    ]
    # if is_admin:
    #     kb.extend(
    #         (
    #             [KeyboardButton(text='Массовая рассылка')],
    #             [KeyboardButton(text='Выполнить обработку уведомлений')]
    #         )
    #     )
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, one_time_keyboard=True)


def return_kb(main_only: bool = True) -> ReplyKeyboardMarkup:
    kb = []
    if not main_only:
        kb.append([KeyboardButton(text='↩ Назад')])
    kb.append([KeyboardButton(text='🔙 Вернуться в главное меню')])
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

