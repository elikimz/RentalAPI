from pydantic import BaseModel, EmailStr
from typing import Optional

class UserCreate(BaseModel):
    full_name: str
    email: EmailStr
    password: str
    role: str  # "admin", "landlord", "tenant"

class UserResponse(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    role: str
   

    class Config:
        from_attributes = True

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None


class PropertyCreate(BaseModel):
    name: str
    location: str

class PropertyResponse(BaseModel):
    id: int
    name: str
    location: str
    landlord_id: int

    class Config:
        from_attributes = True