from pydantic import BaseModel, EmailStr, Field
import uuid


class UserBase(BaseModel):
    username: str
    email: EmailStr


class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=72)


class UserRead(UserBase):
    id: uuid.UUID

    class Config:
        from_attribute = True
