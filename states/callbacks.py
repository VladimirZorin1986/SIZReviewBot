from aiogram.filters.callback_data import CallbackData


class PickPointCallbackFactory(CallbackData, prefix='pickpoint'):
    pickpoint_id: int


class QuestionCallbackFactory(CallbackData, prefix='question'):
    question_id: int


class TypeCallbackFactory(CallbackData, prefix='type'):
    type_id: int


class ModelCallbackFactory(CallbackData, prefix='model'):
    model_id: int
