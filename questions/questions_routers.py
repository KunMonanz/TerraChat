from uuid import UUID

from fastapi import APIRouter, HTTPException, Depends, status

from core.config import create_token, get_current_user
from repositories.questions_repository import QuestionRepository
from .schemas import QuestionResponse, CreateQuestion, UserEditQuestion

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


@router.get("/{question_id}", response_model=QuestionResponse)
async def get_local_question(question_id: UUID, current_user=Depends(get_current_user)):
    question_repository = QuestionRepository()
    question = await question_repository.get_local_question(question_id, current_user)

    if question is None:
        raise HTTPException(detail="question not found",
                            status_code=status.HTTP_401_UNAUTHORIZED)
    return question


@router.patch("/{question_id}", response_model=QuestionResponse)
async def edit_local_question(
    question_id: UUID,
    user_edit_question: UserEditQuestion,
    current_user=Depends(get_current_user)
):
    question_repository = QuestionRepository()

    question = await question_repository.edit_local_question(
        question_id=question_id,
        edit_question=user_edit_question,
        user=current_user
    )

    if question is None:
        raise HTTPException(detail="question not found",
                            status_code=status.HTTP_401_UNAUTHORIZED)
