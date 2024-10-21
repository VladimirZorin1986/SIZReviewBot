from typing import List
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from states.callbacks import (QuestionCallbackFactory, PickPointCallbackFactory,
                              TypeCallbackFactory, ModelCallbackFactory)
from services.models import SQuestion, SPickPoint


emoji_dict = {
    '1': '1️⃣',
    '2': '2️⃣',
    '3': '3️⃣',
    '4': '4️⃣',
    '5': '5️⃣'
}


def help_chapters_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='Авторизация', callback_data='auth_help')],
            [InlineKeyboardButton(text='Оценка пунктов выдачи', callback_data='pickpoint_help')],
            [InlineKeyboardButton(text='Работа с СИЗ', callback_data='siz_help')],
            [InlineKeyboardButton(text='Работа с F.A.Q.', callback_data='faq_help')]
        ]
    )


def show_questions(questions: List[SQuestion]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for question in questions:
        builder.button(
            text=question.text,
            callback_data=QuestionCallbackFactory(
                question_id=question.id
            ).pack()
        )
    return builder.adjust(1).as_markup()


def show_pickpoints(pickpoints: List[SPickPoint]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for pickpoint in pickpoints:
        builder.button(
            text=pickpoint.name,
            callback_data=PickPointCallbackFactory(
                pickpoint_id=pickpoint.id,
                name=pickpoint.name
            ).pack()
        )
    return builder.adjust(1).as_markup()


def show_potential_score() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for score in '12345':
        builder.button(
            text=emoji_dict.get(score),
            callback_data=score
        )
    return builder.adjust(5).as_markup()


def show_yes_or_no() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='👍 Да', callback_data='yes'),
             InlineKeyboardButton(text='👎 Нет', callback_data='no'),
             InlineKeyboardButton(text='❌ Отмена', callback_data='cancel')]
        ]
    )


def show_siz_types(siz_types: dict[int, str]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for type_id, type_name in siz_types.items():
        builder.button(
            text=type_name,
            callback_data=TypeCallbackFactory(
                siztype_id=type_id
            ).pack()
        )
    return builder.adjust(1).as_markup()


def show_siz_models(siz_models: dict[int, str]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for model_id, model_name in siz_models.items():
        builder.button(
            text=model_name,
            callback_data=ModelCallbackFactory(
                sizmodel_id=model_id
            ).pack()
        )
    return builder.adjust(1).as_markup()
