from fastapi import HTTPException, status

from models.base.user_base import UserBase
from models.cloud.user_cloud import CloudUser
from models.local.user_local import LocalUser

from tortoise.transactions import in_transaction
from tortoise.exceptions import IntegrityError

from core.security import hash_password
from users.schemas import EditUsernameSchema, UserCreate


class UserRepository:

    async def create_user(
        self,
        user: UserCreate,
        location
    ) -> CloudUser:

        cloud_user = None

        try:
            async with in_transaction("postgres") as cloud_conn:
                cloud_user = await CloudUser.create(
                    username=user.username.lower().strip(),
                    email=user.email,
                    hashed_password=hash_password(user.password),
                    location=location,
                    using_db=cloud_conn
                )

            async with in_transaction("sqlite") as local_conn:
                await LocalUser.create(
                    id=cloud_user.id,
                    username=cloud_user.username,
                    hashed_password=cloud_user.hashed_password,
                    email=cloud_user.email,
                    location=cloud_user.location,
                    using_db=local_conn
                )

        except IntegrityError:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                "Username or email already exists"
            )

        except Exception as e:
            if cloud_user:
                async with in_transaction("postgres") as cloud_conn:
                    await CloudUser.filter(id=cloud_user.id).using_db(cloud_conn).delete()

            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to sync user to local database"
            )

        return cloud_user

    async def edit_username(
        self,
        user: UserBase,
        username_edit: EditUsernameSchema
    ) -> UserBase | None:
        rows_affected = 0

        try:
            async with in_transaction("postgres") as cloud_conn:
                rows_affected = await CloudUser.filter(id=user.id)\
                    .update(
                    username=username_edit.username
                )
                if rows_affected < 1:
                    return None

            async with in_transaction("sqlite") as local_conn:
                await LocalUser.filter(id=user.id)\
                    .update(
                        username=username_edit.username
                )

            return user

        except IntegrityError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already exists"
            )

        except Exception as e:
            if rows_affected > 1:
                async with in_transaction("postgres") as cloud_conn:
                    await CloudUser.filter(id=user.id)\
                        .using_db(cloud_conn)\
                        .delete()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to sync username edit to local database"
            )
