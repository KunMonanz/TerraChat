from uuid import UUID
from models.local.question_local import QuestionLocal
from models.cloud.question_cloud import QuestionCloud
from models.local.user_local import LocalUser
from questions.schemas import UserEditQuestion

class QuestionRepository:

    async def create_local_question(
        self,
        user: LocalUser,
        question_text: str
    ) -> QuestionLocal:

        question_local = await QuestionLocal.create(
            question_text=question_text,
            user=user
        )

        return question_local

    async def get_local_question(
        self,
        question_id: UUID,
        user: LocalUser
    ) -> QuestionLocal | None:

        question_local = await QuestionLocal.get_or_none(id=question_id, user=user)
        return question_local

    async def edit_local_question(
        self,
        question_id: UUID,
        user: LocalUser,
        edit_question: UserEditQuestion
    ) -> QuestionLocal | None:

        rows_affected = await QuestionLocal.filter(id=question_id, user=user).update(question_text=edit_question.question_text)

        if rows_affected > 0:
            return await QuestionLocal.get_or_none(id=question_id)

        return None

    async def delete_local_question(
        self,
        question_id: UUID,
        user: LocalUser
    ) -> bool:

        deleted_count = await QuestionLocal.filter(
            id=question_id,
            user=user
        ).delete()

        return deleted_count > 1
