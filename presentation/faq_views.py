from services.models import SAnswer


def answer_view(answer: SAnswer) -> str:
    return f'<b>Вопрос:</b>\n<code>{answer.question_text}</code>\n\n<b>Ответ:</b>\n<code>{answer.answer_text}</code>'
