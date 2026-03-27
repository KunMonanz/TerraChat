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
from users.schemas import EditLocationSchema, EditUsernameSchema, UserCreate


class UserRepository:

    async def create_user(self, user: UserCreate, location) -> CloudUser:
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
                status_code=400,
                detail="Username or email already exists",
            )

        # Log change instead of writing to local immediately
        async with in_transaction("sqlite") as local_conn:
            await Changes.create(
                change_type="CREATE",
                model="users",
                payload={
                    "id": str(cloud_user.id),
                    "username": cloud_user.username,
                    "email": cloud_user.email,
                    "hashed_password": cloud_user.hashed_password,
                    "location": cloud_user.location,
                    "is_deleted": False,
                },
                user=str(cloud_user.id),
                using_db=local_conn,
            )

        return cloud_user

    async def edit_username(
        self,
        user: UserBase,
        username_edit: EditUsernameSchema,
    ):
        new_username = username_edit.username.lower().strip()

        try:
            async with in_transaction("postgres") as cloud_conn:
                rows = await CloudUser.filter(id=user.id).using_db(cloud_conn).update(
                    username=new_username
                )

                if rows == 0:
                    return None

        except IntegrityError:
            raise HTTPException(
                status_code=400,
                detail="Username already exists",
            )

        # Log change
        async with in_transaction("sqlite") as local_conn:
            await Changes.create(
                change_type="UPDATE",
                model="users",
                payload={
                    "id": str(user.id),
                    "username": new_username,
                },
                user=str(user.id),
                using_db=local_conn,
            )

        user.username = new_username
        return user

    async def edit_location(self, location_edit: EditLocationSchema, user):
        location = location_edit.location.strip().title()

        async with in_transaction("postgres") as cloud_conn:
            rows = await CloudUser.filter(id=user.id).using_db(cloud_conn).update(
                location=location
            )

            if rows == 0:
                return None

        async with in_transaction("sqlite") as local_conn:
            await Changes.create(
                change_type="UPDATE",
                model="users",
                payload={
                    "id": str(user.id),
                    "location": location,
                },
                user=str(user.id),
                using_db=local_conn,
            )

        user.location = location
        return user

    async def delete_account(self, user: UserBase):
        cloud_conn = None
        local_conn = None

        try:
            async with in_transaction("sqlite") as local_conn:
                local_user = await LocalUser.get_or_none(
                    id=user.id,
                    using_db=local_conn
                )

                if local_user:
                    await LocalUser.filter(id=user.id)\
                        .using_db(local_conn)\
                        .update(is_deleted=True)
                else:
                    local_user = await LocalUser.create(
                        id=user.id,
                        username=user.username,
                        email=user.email,
                        hashed_password=user.hashed_password,
                        location=user.location,
                        is_deleted=True,
                        using_db=local_conn
                    )

                await Changes.create(
                    change_type="DELETE",
                    payload={"id": str(user.id), "is_deleted": True},
                    model="users",
                    user=local_user,
                    using_db=local_conn
                )

            async with in_transaction("postgres") as cloud_conn:
                rows_affected = await CloudUser.filter(id=user.id)\
                    .using_db(cloud_conn)\
                    .update(is_deleted=True)
                if rows_affected == 0:
                    raise Exception("Failed to delete user in cloud")

            return True

        except Exception as e:
            if local_conn:
                await LocalUser.filter(id=user.id)\
                    .using_db(local_conn)\
                    .update(is_deleted=False)

                await Changes.filter(payload__id=str(user.id), model="users")\
                    .using_db(local_conn)\
                    .delete()
            raise e

    async def undelete_account(self, user_login: UserCreate):
        """Atomically restore a soft-deleted user in local + cloud."""

        user = await CloudUser.get_or_none(
            username=user_login.username,
            email=user_login.email
        )

        if not user:
            return False

        cloud_updated = False
        try:
            async with in_transaction("postgres") as cloud_conn:
                user.is_deleted = False
                await user.save(using_db=cloud_conn)
                cloud_updated = True

            async with in_transaction("sqlite") as local_conn:
                local_user_instance = await LocalUser.get_or_none(
                    id=user.id,
                    using_db=local_conn
                )

                if not local_user_instance:
                    await LocalUser.create(
                        id=user.id,
                        username=user.username,
                        email=user.email,
                        hashed_password=user.hashed_password,
                        location=user.location,
                        is_deleted=False,
                        using_db=local_conn
                    )
                else:
                    await LocalUser.filter(id=user.id).using_db(local_conn).update(
                        is_deleted=False
                    )

            return True

        except Exception as e:
            if cloud_updated:
                async with in_transaction("postgres") as cloud_conn:
                    await CloudUser.filter(id=user.id).using_db(cloud_conn).update(is_deleted=True)
            raise e

    async def get_or_create_blacklisted_token(self, token: str):
        token_decode = await derive_from_decode(token)

        jti = token_decode.get("jti")
        expires_at = token_decode.get("exp")
        user = token_decode.get("user")

        async with in_transaction("sqlite") as local_conn:
            black_listed_token, created = await BlackListedToken.get_or_create(
                token_jti=jti,
                defaults={"expires_at": expires_at},
                using_db=local_conn,
            )

            if created:
                await Changes.create(
                    change_type="CREATE",
                    payload={
                        "id": str(black_listed_token.id),
                        "token_jti": jti,
                        "expires_at": str(expires_at),
                    },
                    model="blacklisted_tokens",
                    user=user,
                    using_db=local_conn,
                )
