from services.models import SAnswer


def answer_view(answer: SAnswer) -> str:
    return f'Вопрос: {answer.question_text}\nОтвет: {answer.answer_text}'
