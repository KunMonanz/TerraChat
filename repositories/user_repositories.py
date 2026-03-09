from dataclasses import dataclass

from fastapi import HTTPException

from models.cloud.user_cloud import CloudUser
from models.local.user_local import LocalUser

from tortoise.transactions import in_transaction
from tortoise.exceptions import IntegrityError

from core.security import hash_password
from users.schemas import UserCreate


class UserRepository:

    async def create_user(
        self,
        user: UserCreate,
        location
    ) -> CloudUser:

        try:
            async with in_transaction("postgres") as cloud_conn:
                cloud_user = await CloudUser.create(
                    username=user.username.lower().strip(),
                    email=user.email,
                    hashed_password=hash_password(user.password),
                    location=location,
                    using_db=cloud_conn
                )
        except IntegrityError:
            raise HTTPException(400, "Username or email already exists")

        async with in_transaction("sqlite") as local_conn:
            await LocalUser.create(
                id=cloud_user.id,
                username=cloud_user.username,
                hashed_password=cloud_user.hashed_password,
                email=cloud_user.email,
                location=cloud_user.location,
                using_db=local_conn
            )

        return cloud_user
