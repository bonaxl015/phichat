from pydantic import BaseModel, EmailStr, Field, ConfigDict, UUID4
from datetime import datetime


class UserBase(BaseModel):
    username: str
    email: EmailStr


class UserCreate(UserBase):
    password: str = Field(min_length=8)


class UserRead(UserBase):
    id: UUID4
    last_seen: datetime | None = None

    model_config = ConfigDict(from_attributes=True)
