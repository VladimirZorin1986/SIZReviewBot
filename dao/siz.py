from dao.base import BaseDAO
from database.models import SIZType, SIZModel, SIZModelReview


class SIZTypeDAO(BaseDAO):
    model = SIZType


class SIZModelDAO(BaseDAO):
    model = SIZModel


class SIZReviewDAO(BaseDAO):
    model = SIZModelReview
