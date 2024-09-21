from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def help_chapters_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='Авторизация', callback_data='auth_help')],
            [InlineKeyboardButton(text='Оценка пунктов выдачи', callback_data='pickpoint_help')],
            [InlineKeyboardButton(text='Работа с СИЗ', callback_data='siz_help')],
            [InlineKeyboardButton(text='Работа с F.A.Q.', callback_data='faq_help')]
        ]
    )