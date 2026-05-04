from typing import Optional

from pydantic import BaseModel, Field


class UserRegisterSchema(BaseModel):
    email: str = Field(..., max_length=255)
    password: str = Field(..., min_length=6, max_length=128)


class UserLoginSchema(BaseModel):
    email: str = Field(..., max_length=255)
    password: str = Field(..., max_length=128)


class AdvertisementCreateSchema(BaseModel):
    title: str = Field(..., max_length=100)
    description: str


class AdvertisementUpdateSchema(BaseModel):
    title: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
