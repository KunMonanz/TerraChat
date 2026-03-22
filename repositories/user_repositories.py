from datetime import datetime, timezone

from fastapi import HTTPException, status

from core.config import decode_access_token
from models.base.user_base import UserBase
from models.cloud.user_cloud import CloudUser
from models.local.black_listed_token_model import BlackListedToken
from models.local.changes_model import Changes
from models.local.user_local import LocalUser

from tortoise.transactions import in_transaction
from tortoise.exceptions import IntegrityError

from core.security import hash_password
from services.token_decode import derive_from_decode
from users.schemas import EditUsernameSchema, UserCreate


class UserRepository:

    async def create_user(
        self,
        user: UserCreate,
        location,
    ) -> CloudUser:

        cloud_user = None

        try:
            async with in_transaction("postgres") as cloud_conn:
                cloud_user = await CloudUser.create(
                    username=user.username.lower().strip(),
                    email=user.email,
                    hashed_password=hash_password(user.password),
                    location=location,
                    using_db=cloud_conn,
                )

        except IntegrityError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username or email already exists",
            )

        try:
            async with in_transaction("sqlite") as local_conn:
                await LocalUser.create(
                    id=cloud_user.id,
                    username=cloud_user.username,
                    hashed_password=cloud_user.hashed_password,
                    email=cloud_user.email,
                    location=cloud_user.location,
                    using_db=local_conn,
                )

        except Exception:
            async with in_transaction("postgres") as cloud_conn:
                await CloudUser.filter(id=cloud_user.id)\
                    .using_db(cloud_conn)\
                    .delete()

            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to sync user to local database",
            )

        return cloud_user

    async def edit_username(
        self,
        user: UserBase,
        username_edit: EditUsernameSchema,
    ) -> UserBase | None:

        try:
            async with in_transaction("postgres") as cloud_conn:
                rows_affected = await CloudUser.filter(
                    id=user.id,
                ).using_db(cloud_conn).update(
                    username=username_edit.username,
                )

                if rows_affected == 0:
                    return None

        except IntegrityError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already exists",
            )

        try:
            async with in_transaction("sqlite") as local_conn:
                await LocalUser.filter(
                    id=user.id,
                ).using_db(local_conn).update(
                    username=username_edit.username,
                )

        except Exception:
            async with in_transaction("postgres") as cloud_conn:
                await CloudUser.filter(
                    id=user.id,
                ).using_db(cloud_conn).update(
                    username=user.username,
                )

            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to sync username edit to local database",
            )

        user.username = username_edit.username
        return user

    async def get_or_create_blacklisted_token(
        self,
        token: str,
    ):
        token_decode = await derive_from_decode(token)

        jti = token_decode.get("jti")
        expires_at = token_decode.get("exp")
        user = token_decode.get("user")

        async with in_transaction("sqlite") as local_conn:
            black_listed_token = await BlackListedToken.get_or_create(
                token_jti=jti,
                defaults={
                    "expires_at": expires_at
                },
                using_db=local_conn
            )

            payload = {
                "token_jti": jti,
                "expires_at": str(expires_at)
            }

            await Changes.create(
                change_type="CREATE",
                payload=payload,
                model="blacklisted_tokens",
                user=user,
                using_db=local_conn
            )
