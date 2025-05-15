from pydantic import BaseModel, HttpUrl
from typing import Optional
from datetime import datetime

class SlideBase(BaseModel):
    url: str
    title: str
    description: Optional[str] = None
    duration: int = 60  # Duración en segundos
    is_active: bool = True
    expiry_date: Optional[datetime] = None

class SlideCreate(SlideBase):
    pass

class SlideUpdate(SlideBase):
    url: Optional[str] = None
    title: Optional[str] = None
    duration: Optional[int] = None
    is_active: Optional[bool] = None
    expiry_date: Optional[datetime] = None

class SlideInDB(SlideBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class UserBase(BaseModel):
    username: str
    email: str

class UserCreate(UserBase):
    password: str

class UserInDB(UserBase):
    id: int
    is_active: bool
    is_admin: bool
    created_at: datetime

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None