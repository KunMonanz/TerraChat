from models.base.user_base import UserBase
from tortoise import fields

class LocalUser(UserBase):
    is_synced = fields.BooleanField(default=False)
    class Meta:
        app = "local_models"
        table = "users"
