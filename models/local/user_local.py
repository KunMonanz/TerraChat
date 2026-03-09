from models.base.user_base import UserBase


class LocalUser(UserBase):

    class Meta:
        app = "local_models"
        table = "users"
