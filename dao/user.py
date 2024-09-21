from dao.base import BaseDAO
from database.models import SIZUser


class UserDAO(BaseDAO):
    model = SIZUser
