from pydantic import BaseModel, EmailStr
from uuid import UUID


class QuestionResponse(BaseModel):
    id: UUID
    question_text: str
    answer_text: str


class CreateQuestion(BaseModel):
    question_text: str
