from datetime import datetime, timezone

from fastapi import HTTPException, status
import jwt

from core.config import decode_access_token
from models.local.user_local import LocalUser


async def derive_from_decode(token: str) -> dict:

    try:
        payload = decode_access_token(token)
        user_id = payload.get("sub")
        jti = payload.get("jti")
        exp = payload.get("exp")

        if jti is None or exp is None or user_id is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid token identifier"
            )

        expires_at = datetime.fromtimestamp(
            exp,
            tz=timezone.utc
        )

        user: LocalUser | None = await LocalUser.get_or_none(id=user_id)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User does not exist"
            )

        return {
            "jti": jti,
            "exp": expires_at,
            "user": user
        }

    except jwt.PyJWKError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
