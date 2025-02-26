from datetime import date, datetime
from pydantic import BaseModel, EmailStr, Field, HttpUrl
from typing import Optional

class UserCreate(BaseModel):
    full_name: str
    email: EmailStr
    password: str
    phone_number: str
    # role: str  # "admin", "landlord", "tenant"

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
    id: int  
    full_name:str

class TokenData(BaseModel):
    email: Optional[str] = None
    user_id:str


class PropertyCreate(BaseModel):
    name: str
    location: str
    description: Optional[str] = ""
    image_url: str 

class PropertyResponse(BaseModel):
    id: int
    name: str
    location:str 
    description: Optional[str] = "" 
    image_url: str 
  

    class Config:
        from_attributes = True

# 🚀 Schema for creating a unit
class UnitCreate(BaseModel):
    name: str
    status: Optional[str] = "available"  # Defaults to "available"
    # property_id: Optional[int] = None  # Add property_id here

# 🔄 Schema for returning unit data
class UnitResponse(UnitCreate):
    id: int
    # property_id: int  # Will be automatically assigned in the service logic

    class Config:
        from_attributes = True

class TenantCreate(BaseModel):
    # Exclude user_id from the schema; it will be automatically set
    full_name: str
    email: str
    phone_number: str

    class Config:
        orm_mode = True    


# Tenant response schema
from pydantic import BaseModel

class TenantResponse(BaseModel):
    id: int
    full_name: str
    email: str
    phone_number: str
    user_id: int

    class Config:
        orm_mode = True


# Lease creation schema
class LeaseCreate(BaseModel):
    start_date: date
    end_date: date
    rent_amount: float
    deposit_amount: float

    class Config:
        orm_mode = True  

# Lease response schema
class LeaseResponse(BaseModel):
    id: int
    tenant_id: int
    unit_id: int
    start_date: date
    end_date: date
    rent_amount: float
    deposit_amount: float
    lease_status: str  # Simple string for lease status
    created_at: date
    updated_at: date

    class Config:
        orm_mode = True


class PaymentCreate(BaseModel):
    amount_paid: float  # Only the amount paid will be included in the request
    class Config:
        orm_mode = True
class PaymentUpdate(BaseModel):
    amount_paid: Optional[float] = None
    payment_status: Optional[str] = None        


class PaymentResponse(BaseModel):
    payment_id: str
    checkout_url: str
    amount_paid: float
    payment_status: str

    class Config:
        orm_mode = True





class TicketCreate(BaseModel):
   
    subject: str
    description: str

class TicketUpdate(BaseModel):
    subject: Optional[str]
    description: Optional[str]
    status: Optional[str]  # Open, In Progress, Closed

class TicketResponse(BaseModel):
    id: int
    tenant_id: int
    subject: str
    description: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True
