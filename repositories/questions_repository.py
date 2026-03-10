from models.local.question_local import QuestionLocal
from models.cloud.question_cloud import QuestionCloud
from models.local.user_local import LocalUser


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
