from fastapi import (
    APIRouter,
    HTTPException,
    Request,
    Depends,
    status
)

from fastapi.security import OAuth2PasswordBearer

from core.config import create_token, get_current_user
from core.security import verify_password

from models.local.changes_model import Changes
from models.local.user_local import LocalUser

from services.sync_changes_services import SyncService
from utils.geolocation import get_location_from_ip

from .schemas import (
    EditLocationSchema,
    EditUsernameSchema,
    LoginSchema,
    UserCreate,
    UserResponse,
    ProfileSchema
)

from repositories.user_repositories import UserRepository

router = APIRouter(prefix="/users", tags=["Users"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

user_repository = UserRepository()


@router.post("/", response_model=UserResponse)
async def create_user(user: UserCreate, request: Request):
    location = get_location_from_ip(request)
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
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials"
        )

    token = await create_token(user.id)
    return {"access_token": token, "token_type": "bearer"}


@router.post("/logout")
async def logout(token: str = Depends(oauth2_scheme)):
    await user_repository.get_or_create_blacklisted_token(token)
    return {
        "detail": "Successfully logged out"
    }


@router.get("/me", response_model=ProfileSchema)
async def get_profile(current_user=Depends(get_current_user)):
    return current_user


@router.patch("/username", response_model=UserResponse)
async def edit_username(
    username_edit: EditUsernameSchema,
    current_user=Depends(get_current_user)
):
    """
        Edit username
    """
    username_edit_user = await user_repository.edit_username(
        user=current_user,
        username_edit=username_edit
    )
    return username_edit_user


@router.patch("/location", response_model=UserResponse)
async def edit_location(
    location_edit: EditLocationSchema,
    current_user=Depends(get_current_user)
):
    user_with_edited_location = await user_repository.edit_location(
        location_edit=location_edit,
        user=current_user
    )
    return user_with_edited_location


@router.post("/sync")
async def trigger_sync(
    current_user: LocalUser = Depends(get_current_user)
):
    service = SyncService()
    stats = await service.sync(
        user_id=str(current_user.id),
        cloud_user_id=str(current_user.id),
    )
    return {
        "status": "ok",
        "stats": stats
    }


# @router.post("/purge-bad-changes")
# async def purge_bad_changes():
#     bad_user_updates = await Changes.filter(
#         model="users",
#         change_type="UPDATE",
#         used=False,
#     )
#     deleted = 0
#     for change in bad_user_updates:
#         if "id" not in change.payload:
#             await change.delete()
#             deleted += 1

#     bad_question_creates = await Changes.filter(
#         model="questions",
#         change_type="CREATE",
#         used=False,
#     )
#     for change in bad_question_creates:
#         if "user_id" not in change.payload:
#             await change.delete()
#             deleted += 1

#     return {"deleted": deleted}
