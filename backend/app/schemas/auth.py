from pydantic import BaseModel, EmailStr
from typing import Optional


class SignupRequest(BaseModel):
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class ResendRequest(BaseModel):
    email: EmailStr


class ResetRequest(BaseModel):
    email: EmailStr


class ResetConfirmRequest(BaseModel):
    token: str
    new_password: str


class MeResponse(BaseModel):
    user_id: int
    org_id: Optional[int] = None
    role: str
    verified: bool
    needs_onboarding: bool = False

