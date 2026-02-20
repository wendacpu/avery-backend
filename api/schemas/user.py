from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional


class UserBase(BaseModel):
    """Base user schema"""
    email: EmailStr
    name: Optional[str] = None
    linkedin_url: Optional[str] = None
    company_url: Optional[str] = None


class UserCreate(UserBase):
    """User creation schema"""
    password: Optional[str] = None  # For OAuth, password might not be required


class UserUpdate(BaseModel):
    """User update schema"""
    name: Optional[str] = None
    linkedin_url: Optional[str] = None
    company_url: Optional[str] = None


class UserResponse(UserBase):
    """User response schema"""
    id: str
    subscription_tier: str
    credits_remaining: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    """Token response schema"""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Token data schema"""
    email: Optional[str] = None
