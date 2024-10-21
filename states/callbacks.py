from aiogram.filters.callback_data import CallbackData


class PickPointCallbackFactory(CallbackData, prefix='pickpoint'):
    pickpoint_id: int
    name: str


class QuestionCallbackFactory(CallbackData, prefix='question'):
    question_id: int


class TypeCallbackFactory(CallbackData, prefix='type'):
    siztype_id: int


class ModelCallbackFactory(CallbackData, prefix='model'):
    sizmodel_id: int
