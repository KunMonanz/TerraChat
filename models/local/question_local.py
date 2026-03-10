from models.base.question_base import QuestionBase
from tortoise import fields


class QuestionLocal(QuestionBase):
    user = fields.ForeignKeyField(
        "local_models.LocalUser",
        related_name="questions"
    )

    class Meta:
        app = "local_models"
        table = "questions"
