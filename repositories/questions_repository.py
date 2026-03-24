from uuid import UUID

from models.local.changes_model import Changes
from models.local.question_local import QuestionLocal
from models.local.user_local import LocalUser
from questions.schemas import UserEditQuestion
from tortoise.transactions import in_transaction


class QuestionRepository:

    async def create_local_question(
        self,
        user: LocalUser,
        question_text: str,
    ) -> QuestionLocal:

        async with in_transaction("sqlite") as local_conn:
            question_local = await QuestionLocal.create(
                question_text=question_text,
                user=user,
                using_db=local_conn,
            )

            await Changes.create(
                change_type="CREATE",
                payload={
                    "id": str(question_local.id),       # ← PK for upsert
                    "question_text": question_text,
                    # ← remapped to cloud user_id at sync time
                    "user_id": str(user.id),
                },
                model="questions",
                user=user,
                using_db=local_conn,
            )

        return question_local

    async def get_local_question(
        self,
        question_id: UUID,
        user: LocalUser,
    ) -> QuestionLocal | None:
        return await QuestionLocal.get_or_none(id=question_id, user=user)

    async def edit_local_question(
        self,
        question_id: UUID,
        user: LocalUser,
        edit_question: UserEditQuestion,
    ) -> QuestionLocal | None:

        async with in_transaction("sqlite") as local_conn:
            rows_affected = await QuestionLocal.filter(
                id=question_id,
                user=user,
            ).using_db(local_conn).update(
                question_text=edit_question.question_text
            )

            if rows_affected == 0:
                return None

            await Changes.create(
                change_type="UPDATE",
                payload={
                    "id": str(question_id),
                    "question_text": edit_question.question_text,
                },
                model="questions",
                user=user,
                using_db=local_conn,
            )

            question = await QuestionLocal.get_or_none(
                id=question_id,
                using_db=local_conn,        # ← same connection
            )

            if question is None:
                return None

            await QuestionLocal.filter(id=question_id).using_db(local_conn).update(
                is_synced=False             # ← update via filter, not instance.save()
            )

            # Re-fetch with is_synced updated
            return await QuestionLocal.get_or_none(
                id=question_id,
                using_db=local_conn,
            )

    async def delete_local_question(
        self,
        question_id: UUID,
        user: LocalUser,
    ) -> bool:

        async with in_transaction("sqlite") as local_conn:
            deleted_count = await QuestionLocal.filter(
                id=question_id,
                user=user,
            ).using_db(local_conn).delete()

            if deleted_count == 0:
                return False

            await Changes.create(
                change_type="DELETE",
                payload={
                    # ← was "question_id", wrong key
                    "id": str(question_id),
                },
                model="questions",
                user=user,
                using_db=local_conn,
            )

        return True
