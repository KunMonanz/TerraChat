from models.base.question_base import QuestionBase
from tortoise import fields


class QuestionLocal(QuestionBase):
    user = fields.ForeignKeyField(
        "local_models.LocalUser",
        related_name="questions"
    )
    is_synced = fields.BooleanField(default=False)

    class Meta:
        app = "local_models"
        table = "questions"
