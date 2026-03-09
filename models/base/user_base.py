import uuid
from tortoise import models, fields


class UserBase(models.Model):
    id = fields.UUIDField(
        pk=True,
        default=uuid.uuid4
    )
    username = fields.CharField(max_length=50, unique=True)
    email = fields.CharField(max_length=100, unique=True)
    hashed_password = fields.CharField(max_length=255)
    location = fields.CharField(max_length=100)

    class Meta:
        abstract = True
