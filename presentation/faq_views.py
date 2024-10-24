from services.models import SAnswer


def answer_view(answer: SAnswer) -> str:
    return f'<b>Вопрос:</b>\n<i>{answer.question_text}</i>\n\n<b>Ответ:</b>\n{answer.answer_text}'
