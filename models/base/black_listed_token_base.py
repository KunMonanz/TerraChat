import uuid

from tortoise import fields, models


class BlackListedTokenBase(models.Model):
    id = fields.UUIDField(
        pk=True,
        default=uuid.uuid4
    )
    token_jti = fields.CharField(
        max_length=255,
        unique=True,
        index=True
    )
    expires_at = fields.DatetimeField()
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        abstract = True
