from datetime import datetime

from pydantic import BaseModel, EmailStr


class UserRead(BaseModel):
    id: int
    email: EmailStr
    full_name: str
    is_active: bool
    created_at: datetime


class UserPublicRead(BaseModel):
    id: int
    email: EmailStr
    full_name: str
