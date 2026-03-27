import uuid
from tortoise import models, fields


class QuestionBase(models.Model):
    id = fields.UUIDField(
        pk=True,
        default=uuid.uuid4
    )
    question_text = fields.TextField()
    answer_text = fields.TextField(default="")
    answer_type = fields.CharField(max_length=10, default="")
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:  # type: ignore
        abstract = True
