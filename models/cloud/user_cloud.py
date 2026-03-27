from models.base.user_base import UserBase


class CloudUser(UserBase):

    class Meta:  # type: ignore
        app = "cloud_models"
        table = "users"
