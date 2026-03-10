from fastapi import APIRouter, HTTPException, Depends

from core.config import create_token, get_current_user
from repositories.questions_repository import QuestionRepository
from .schemas import QuestionResponse, CreateQuestion

router = APIRouter(prefix="/questions", tags=["Questions"])


@router.post("/", response_model=QuestionResponse)
async def create_local_question(
    question_create: CreateQuestion,
    current_user=Depends(get_current_user)
):
    question_repository = QuestionRepository()
    question = await question_repository.create_local_question(
        user=current_user,
        question_text=question_create.question_text
    )
    return question
