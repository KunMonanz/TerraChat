from pydantic import BaseModel, EmailStr
from uuid import UUID


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: UUID
    username: str
    email: EmailStr


class LoginSchema(BaseModel):
    username: str
    email: str
    password: str


class ProfileSchema(BaseModel):
    username: str
    email: str
    location: str


class EditUsernameSchema(BaseModel):
    username: str


class EditLocationSchema(BaseModel):
    location: str
