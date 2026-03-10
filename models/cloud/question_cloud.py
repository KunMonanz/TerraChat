from models.base.question_base import QuestionBase
from tortoise import fields


class QuestionCloud(QuestionBase):
    user = fields.ForeignKeyField(
        "cloud_models.CloudUser",
        related_name="questions"
    )

    class Meta:
        app = "cloud_models"
        table = "questions"
