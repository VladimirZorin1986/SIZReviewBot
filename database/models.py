import datetime
from typing import List, Optional
from sqlalchemy import ForeignKey, Identity, text
from sqlalchemy.types import BigInteger, String, SmallInteger, Integer, DateTime, Boolean, Text
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(AsyncAttrs, DeclarativeBase):
    pass


class PickPoint(Base):
    __tablename__ = 'pickpoint'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    last_modified_at: Mapped[datetime.datetime] = mapped_column(DateTime)

    ratings: Mapped[List['PickPointRating']] = relationship()


class SIZType(Base):
    __tablename__ = 'siz_type'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    last_modified_at: Mapped[datetime.datetime] = mapped_column(DateTime)

    models: Mapped[List['SIZModel']] = relationship()


class SIZUser(Base):
    __tablename__ = 'siz_user'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    tg_id: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    phone_number: Mapped[str] = mapped_column(String(12), unique=True, index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    last_modified_at: Mapped[datetime.datetime] = mapped_column(DateTime)

    reviews: Mapped[List['SIZModelReview']] = relationship()
    ratings: Mapped[List['PickPointRating']] = relationship()


class QuestionPriority(Base):
    __tablename__ = 'question_priority'

    id: Mapped[int] = mapped_column(SmallInteger, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    order_value: Mapped[int] = mapped_column(SmallInteger, unique=True, index=True)

    questions: Mapped[List['SIZFAQ']] = relationship()


class SIZFAQ(Base):
    __tablename__ = 'siz_faq'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    priority_id: Mapped[int] = mapped_column(
        SmallInteger,
        ForeignKey(column='question_priority.id', ondelete='RESTRICT')
    )
    question_text: Mapped[str] = mapped_column(Text)
    answer_text: Mapped[str] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    last_modified_at: Mapped[datetime.datetime] = mapped_column(DateTime)


class SIZModel(Base):
    __tablename__ = 'siz_model'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    type_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey(column='siz_type.id', ondelete='RESTRICT')
    )
    name: Mapped[str] = mapped_column(String(255))
    protect_props: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    care_procedure: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    writeoff_criteria: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    operating_rules: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    file_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    last_modified_at: Mapped[datetime.datetime] = mapped_column(DateTime)

    reviews: Mapped[List['SIZModelReview']] = relationship()


class PickPointRating(Base):
    __tablename__ = 'pickpoint_rating'

    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    pickpoint_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey(column='pickpoint.id', ondelete='CASCADE')
    )
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey(column='siz_user.id', ondelete='CASCADE')
    )
    rating_score: Mapped[int] = mapped_column(SmallInteger)
    score_comment: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=text('NOW()'))
    sent_to_eis: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, nullable=True)


class SIZModelReview(Base):
    __tablename__ = 'sizmodel_review'

    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    model_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey(column='siz_model.id', ondelete='CASCADE')
    )
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey(column='siz_user.id', ondelete='CASCADE')
    )
    review_text: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=text('NOW()'))
    sent_to_eis: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, nullable=True)


class AdminNotice(Base):
    __tablename__ = 'admin_notice'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    notice_text: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime)
    sent_from_eis: Mapped[datetime.datetime] = mapped_column(DateTime)
    delivered_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, nullable=True)
