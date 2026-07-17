from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    full_name: str
    email: EmailStr
    age_group: str
    state: str


class UserCreate(UserBase):
    password: str = Field(min_length=6)


class UserOut(UserBase):
    id: str = Field(alias="_id")
    created_at: datetime

    class Config:
        populate_by_name = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    user_id: Optional[str] = None

