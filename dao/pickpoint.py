from dao.base import BaseDAO
from database.models import PickPoint, PickPointRating


class PickPointDAO(BaseDAO):
    model = PickPoint


class PickPointRatingDAO(BaseDAO):
    model = PickPointRating
