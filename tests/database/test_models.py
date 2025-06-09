import pytest
from datetime import datetime
from contextlib import nullcontext as does_not_raise
from sqlalchemy import select, insert, delete, update
from sqlalchemy.exc import IntegrityError, StatementError
from database.models import (
                                PickPoint, SIZType, SIZUser,
                                QuestionPriority, SIZFAQ, SIZModel,
                                PickPointRating, SIZModelReview, AdminNotice
                            )

@pytest.mark.parametrize(
    "test_values,expectation",
    [
        # Good values
        ({"id": 1, "name": "text", "is_active": True, "last_modified_at": datetime.now()}, does_not_raise()),
        ({"name": "text", "last_modified_at": datetime.now()}, does_not_raise()),

        # Missing values
        ({"last_modified_at": datetime.now()}, pytest.raises(IntegrityError)),
        ({"name": "text"}, pytest.raises(IntegrityError)),

        # Bad values
        ({"id": "BAD", "name": "text", "is_active": True, "last_modified_at": datetime.now()}, pytest.raises(IntegrityError)),
        ({"name": "text", "is_active": "BAD", "last_modified_at": datetime.now()}, pytest.raises(StatementError)),
        ({"name": "text", "last_modified_at": "BAD"}, pytest.raises(StatementError)),
    ],
)
@pytest.mark.asyncio
async def test_pickpoint(db_session, test_values, expectation):
    async with db_session as session:
        query = insert(PickPoint).values(**test_values)
        with expectation:
            await session.execute(query)

@pytest.mark.parametrize(
    "test_values,expectation",
    [
        # Good values
        ({"id": 1, "name": "text", "is_active": True, "last_modified_at": datetime.now()}, does_not_raise()),
        ({"name": "text", "last_modified_at": datetime.now()}, does_not_raise()),

        # Missing values
        ({"last_modified_at": datetime.now()}, pytest.raises(IntegrityError)),
        ({"name": "text"}, pytest.raises(IntegrityError)),

        # Bad values
        ({"id": "BAD", "name": "text", "is_active": True, "last_modified_at": datetime.now()}, pytest.raises(IntegrityError)),
        ({"name": "text", "is_active": "BAD", "last_modified_at": datetime.now()}, pytest.raises(StatementError)),
        ({"name": "text", "last_modified_at": "BAD"}, pytest.raises(StatementError)),
    ],
)
@pytest.mark.asyncio
async def test_siz_type(db_session, test_values, expectation):
    async with db_session as session:
        query = insert(SIZType).values(**test_values)
        with expectation:
            await session.execute(query)

@pytest.mark.parametrize(
    "test_values,expectation",
    [
        # Good values
        ({"id": 1, "tg_id": 2, "phone_number": "text", "is_active": True, "last_modified_at": datetime.now(), "registered_at": datetime.now()}, does_not_raise()),
        ({"phone_number": "text", "last_modified_at": datetime.now()}, does_not_raise()),

        # Missing values
        ({"last_modified_at": datetime.now()}, pytest.raises(IntegrityError)),
        ({"phone_number": "text"}, pytest.raises(IntegrityError)),

        # Bad values
        ({"id": "BAD", "phone_number": "text", "last_modified_at": datetime.now()}, pytest.raises(IntegrityError)),
        ({"phone_number": "text", "is_active": "BAD", "last_modified_at": datetime.now(), "registered_at": datetime.now()}, pytest.raises(StatementError)),
        ({"phone_number": "text", "is_active": True, "last_modified_at": "BAD", "registered_at": datetime.now()}, pytest.raises(StatementError)),
        ({"phone_number": "text", "is_active": True, "last_modified_at": datetime.now(), "registered_at": "BAD"}, pytest.raises(StatementError)),
    ],
)
@pytest.mark.asyncio
async def test_siz_user(db_session, test_values, expectation):
    async with db_session as session:
        query = insert(SIZUser).values(**test_values)
        with expectation:
            await session.execute(query)

@pytest.mark.parametrize(
    "test_values,expectation",
    [
        # Good values
        ({"id": 1, "name": "text", "order_value": 1}, does_not_raise()),

        # Missing values
        ({"name": "text", "order_value": 1}, pytest.raises(IntegrityError)),
        ({"id": 1, "order_value": 1}, pytest.raises(IntegrityError)),
        ({"id": 1, "name": "text"}, pytest.raises(IntegrityError)),
    ],
)
@pytest.mark.asyncio
async def test_question_priority(db_session, test_values, expectation):
    async with db_session as session:
        query = insert(QuestionPriority).values(**test_values)
        with expectation:
            await session.execute(query)

@pytest.mark.parametrize(
    "test_values,expectation",
    [
        # Good values
        ({"id": 1, "priority_id": 2, "question_text": "text", "answer_text": "text", "is_active": True, "last_modified_at": datetime.now()}, does_not_raise()),
        ({"priority_id": 2, "question_text": "text", "answer_text": "text", "last_modified_at": datetime.now()}, does_not_raise()),

        # Missing values
        ({"question_text": "text", "answer_text": "text", "last_modified_at": datetime.now()}, pytest.raises(IntegrityError)),
        ({"priority_id": 2, "answer_text": "text", "last_modified_at": datetime.now()}, pytest.raises(IntegrityError)),
        ({"priority_id": 2, "question_text": "text", "last_modified_at": datetime.now()}, pytest.raises(IntegrityError)),
        ({"priority_id": 2, "question_text": "text", "answer_text": "text"}, pytest.raises(IntegrityError)),

        # Bad values
        ({"id": "BAD", "priority_id": 2, "question_text": "text", "answer_text": "text", "last_modified_at": datetime.now()}, pytest.raises(IntegrityError)),
        ({"priority_id": 2, "question_text": "text", "answer_text": "text", "is_active": "BAD", "last_modified_at": datetime.now()}, pytest.raises(StatementError)),
        ({"priority_id": 2, "question_text": "text", "answer_text": "text", "last_modified_at": "BAD"}, pytest.raises(StatementError)),
    ],
)
@pytest.mark.asyncio
async def test_siz_faq(db_session, test_values, expectation):
    async with db_session as session:
        query = insert(SIZFAQ).values(**test_values)
        with expectation:
            await session.execute(query)

@pytest.mark.parametrize(
    "test_values,expectation",
    [
        # Good values
        ({"id": 1, "type_id": 2, "name": "text", "protect_props": "text", "care_procedure": "text", "writeoff_criteria": "text", "operating_rules": "text", "file_id": 3, "file_name": "text", "is_active": True, "last_modified_at": datetime.now()}, does_not_raise()),
        ({"type_id": 2, "name": "text", "last_modified_at": datetime.now()}, does_not_raise()),

        # Missing values
        ({"name": "text", "last_modified_at": datetime.now()}, pytest.raises(IntegrityError)),
        ({"type_id": 2, "last_modified_at": datetime.now()}, pytest.raises(IntegrityError)),
        ({"type_id": 2, "name": "text"}, pytest.raises(IntegrityError)),

        # Bad values
        ({"id": "BAD", "type_id": 2, "name": "text", "last_modified_at": datetime.now()}, pytest.raises(IntegrityError)),
        ({"type_id": 2, "name": "text", "is_active": "BAD", "last_modified_at": datetime.now()}, pytest.raises(StatementError)),
        ({"type_id": 2, "name": "text", "last_modified_at": "BAD"}, pytest.raises(StatementError)),
    ],
)
@pytest.mark.asyncio
async def test_siz_model(db_session, test_values, expectation):
    async with db_session as session:
        query = insert(SIZModel).values(**test_values)
        with expectation:
            await session.execute(query)

@pytest.mark.parametrize(
    "test_values,expectation",
    [
        # Good values
        ({"id": 1, "pickpoint_id": 2, "user_id": 3, "rating_score": 4, "score_comment": "text", "created_at": datetime.now(), "sent_to_eis": datetime.now()}, does_not_raise()),
        ({"id": 1, "pickpoint_id": 2, "user_id": 3, "rating_score": 4, "score_comment": "text"}, does_not_raise()),

        # Missing values
        ({"pickpoint_id": 2, "user_id": 3, "rating_score": 4, "score_comment": "text"}, pytest.raises(IntegrityError)),
        ({"id": 1, "user_id": 3, "rating_score": 4, "score_comment": "text"}, pytest.raises(IntegrityError)),
        ({"id": 1, "pickpoint_id": 2, "rating_score": 4, "score_comment": "text"}, pytest.raises(IntegrityError)),
        ({"id": 1, "pickpoint_id": 2, "user_id": 3, "score_comment": "text"}, pytest.raises(IntegrityError)),
        ({"id": 1, "pickpoint_id": 2, "user_id": 3, "rating_score": 4}, pytest.raises(IntegrityError)),

        # Bad values
        ({"id": 1, "pickpoint_id": 2, "user_id": 3, "rating_score": 4, "score_comment": "text", "created_at": "BAD", "sent_to_eis": datetime.now()}, pytest.raises(StatementError)),
        ({"id": 1, "pickpoint_id": 2, "user_id": 3, "rating_score": 4, "score_comment": "text", "created_at": datetime.now(), "sent_to_eis": "BAD"}, pytest.raises(StatementError)),
    ],
)
@pytest.mark.asyncio
async def test_pickpoint_rating(db_session, test_values, expectation):
    async with db_session as session:
        query = insert(PickPointRating).values(**test_values)
        with expectation:
            await session.execute(query)

@pytest.mark.parametrize(
    "test_values,expectation",
    [
        # Good values
        ({"id": 1, "model_id": 2, "user_id": 3, "review_text": "text", "created_at": datetime.now(), "sent_to_eis": datetime.now()}, does_not_raise()),
        ({"id": 1, "model_id": 2, "user_id": 3, "review_text": "text"}, does_not_raise()),

        # Missing values
        ({"model_id": 2, "user_id": 3, "review_text": "text"}, pytest.raises(IntegrityError)),
        ({"id": 1, "user_id": 3, "review_text": "text"}, pytest.raises(IntegrityError)),
        ({"id": 1, "model_id": 2, "review_text": "text"}, pytest.raises(IntegrityError)),
        ({"id": 1, "model_id": 2, "user_id": 3}, pytest.raises(IntegrityError)),

        # Bad values
        ({"id": 1, "model_id": 2, "user_id": 3, "review_text": "text", "created_at": "BAD", "sent_to_eis": datetime.now()}, pytest.raises(StatementError)),
        ({"id": 1, "model_id": 2, "user_id": 3, "review_text": "text", "created_at": datetime.now(), "sent_to_eis": "BAD"}, pytest.raises(StatementError)),
    ],
)
@pytest.mark.asyncio
async def test_siz_model_review(db_session, test_values, expectation):
    async with db_session as session:
        query = insert(SIZModelReview).values(**test_values)
        with expectation:
            await session.execute(query)

@pytest.mark.parametrize(
    "test_values,expectation",
    [
        # Good values
        ({"id": "1", "notice_text": "text", "created_at": datetime.now(), "sent_from_eis": datetime.now(), "delivered_at": datetime.now()}, does_not_raise()),
        ({"notice_text": "text", "created_at": datetime.now(), "sent_from_eis": datetime.now()}, does_not_raise()),

        # Missing values
        ({"created_at": datetime.now(), "sent_from_eis": datetime.now()}, pytest.raises(IntegrityError)),
        ({"notice_text": "text", "sent_from_eis": datetime.now()}, pytest.raises(IntegrityError)),
        ({"notice_text": "text", "created_at": datetime.now()}, pytest.raises(IntegrityError)),

        # Bad values
        ({"id": "BAD", "notice_text": "text", "created_at": datetime.now(), "sent_from_eis": datetime.now()}, pytest.raises(IntegrityError)),
        ({"notice_text": "text", "created_at": "BAD", "sent_from_eis": datetime.now()}, pytest.raises(StatementError)),
        ({"notice_text": "text", "created_at": datetime.now(), "sent_from_eis": "BAD"}, pytest.raises(StatementError)),
        ({"notice_text": "text", "created_at": datetime.now(), "sent_from_eis": datetime.now(), "delivered_at": "BAD"}, pytest.raises(StatementError)),
    ],
)
@pytest.mark.asyncio
async def test_admin_notice(db_session, test_values, expectation):
    async with db_session as session:
        query = insert(AdminNotice).values(**test_values)
        with expectation:
            await session.execute(query)