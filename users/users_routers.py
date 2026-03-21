from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, Request, Depends, status
from fastapi.security import OAuth2PasswordBearer
import jwt

from core.config import create_token, decode_access_token, get_current_user
from core.security import verify_password

from models.local.black_listed_token_model import BlackListedToken
from models.local.user_local import LocalUser

from utils.geolocation import get_location_from_ip

from .schemas import EditUsernameSchema, LoginSchema, UserCreate, UserResponse, ProfileSchema

from repositories.user_repositories import UserRepository

router = APIRouter(prefix="/users", tags=["Users"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@router.post("/", response_model=UserResponse)
async def create_user(user: UserCreate, request: Request):
    location = get_location_from_ip(request)
    user_repository = UserRepository()

    cloud_user = await user_repository.create_user(user, location)

    return UserResponse(
        id=cloud_user.id,
        username=cloud_user.username,
        email=cloud_user.email,
    )


@router.post("/login")
async def login(data: LoginSchema):
    user = await LocalUser.get_or_none(username=data.username)
    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = await create_token(user.id)
    return {"access_token": token, "token_type": "bearer"}


@router.post("/logout")
async def logout(token: str = Depends(oauth2_scheme)):
    try:
        payload = decode_access_token(token)
        jti = payload.get("jti")
        exp = payload.get("exp")

        if not jti:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid token identifier"
            )

        await BlackListedToken.get_or_create(
            token_jti=jti,
            defaults={
                "expires_at": datetime.fromtimestamp(exp, tz=timezone.utc)
            }
        )

        return {
            "detail": "Successfully logged out"
        }
    except jwt.PyJWKError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )


@router.get("/me", response_model=ProfileSchema)
async def get_profile(current_user=Depends(get_current_user)):
    return current_user


@router.patch("/username", response_model=UserResponse)
async def edit_username(
    username_edit: EditUsernameSchema,
    current_user=Depends(get_current_user)
):
    user_repository = UserRepository()
    username_edit_user = await user_repository.edit_username(
        user=current_user,
        username_edit=username_edit
    )
    return username_edit_user
