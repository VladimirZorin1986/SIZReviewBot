from typing import List
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from states.callbacks import (QuestionCallbackFactory, PickPointCallbackFactory,
                              TypeCallbackFactory, ModelCallbackFactory)
from services.models import SQuestion, SPickPoint, SType, SModel


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
            text=score,
            callback_data=score
        )
    return builder.adjust(5).as_markup()


def show_yes_or_no() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='Да', callback_data='yes'),
             InlineKeyboardButton(text='Нет', callback_data='no'),
             InlineKeyboardButton(text='Отмена', callback_data='cancel_comment')]
        ]
    )


def show_siz_types(siz_types: List[SType]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for siz_type in siz_types:
        builder.button(
            text=siz_type.name,
            callback_data=TypeCallbackFactory(
                type_id=siz_type.id,
                name=siz_type.name
            ).pack()
        )
    return builder.adjust(1).as_markup()


def show_siz_models(siz_models: List[SModel]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for siz_model in siz_models:
        builder.button(
            text=siz_model.name,
            callback_data=ModelCallbackFactory(
                sizmodel_id=siz_model.id,
                name=siz_model.name
            ).pack()
        )
    return builder.adjust(1).as_markup()

