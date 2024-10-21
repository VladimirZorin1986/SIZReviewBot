from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from services.models import SQuestion, SAnswer
from dao.faq import FaqDAO
from services.base import BaseService


class FAQService(BaseService):

    @classmethod
    async def get_questions(cls, async_session: AsyncSession) -> List[SQuestion]:
        raw_questions = await FaqDAO.find_all_sort_by_priority(async_session)
        return [
            SQuestion(
                id=question.id,
                text=question.question_text
            ) for question in raw_questions
        ]

    @classmethod
    async def get_answer(cls, async_session: AsyncSession, question_id: int) -> SAnswer:
        faq_row = await FaqDAO.find_by_id(question_id, async_session)
        return SAnswer(
            question_text=faq_row.question_text,
            answer_text=faq_row.answer_text
        )


