import uuid

from tortoise import fields, models
from tortoise.migrations.constraints import CheckConstraint


class Changes(models.Model):
    id = fields.UUIDField(
        pk=True,
        default=uuid.uuid4
    )
    change_type = fields.CharField(max_length=6)
    payload = fields.JSONField()
    model = fields.CharField(max_length=100)
    user = fields.ForeignKeyField(
        "local_models.LocalUser",
        related_name="changes"
    )
    used = fields.BooleanField(default=False)
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        app = "local_models"
        table = "changes"

        constraints = [
            CheckConstraint(
                check="change_type IN (CREATE, UPDATE, DELETE)", name="chk_change_type_crud"
            )
        ]
