from models.base.user_base import UserBase


class CloudUser(UserBase):

    class Meta:
        app = "cloud_models"
        table = "users"
