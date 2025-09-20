from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, constr


class CreateOrganizationRequest(BaseModel):
    """Request schema for creating a new organization."""
    name: constr(min_length=1, max_length=255) = Field(..., description="Organization name")
    billing_email: Optional[EmailStr] = Field(None, description="Billing email address")
    billing_address: Optional[constr(max_length=500)] = Field(None, description="Billing address")
    timezone: constr(min_length=1, max_length=100) = Field(default="UTC", description="Organization timezone")


class OrganizationResponse(BaseModel):
    """Response schema for organization data."""
    id: int = Field(..., description="Organization ID")
    name: str = Field(..., description="Organization name")
    code: str = Field(..., description="Organization code")
    is_active: bool = Field(..., description="Whether organization is active")
    created_at: datetime = Field(..., description="Creation timestamp")
    created_by: str = Field(..., description="User who created the organization")
    slug: str = Field(..., description="Organization slug")
    email: str = Field(..., description="Organization email")
    phone: Optional[str] = Field(None, description="Organization phone")
    billing_address: Optional[str] = Field(None, description="Billing address")
    billing_email: Optional[str] = Field(None, description="Billing email")
    timezone: str = Field(..., description="Organization timezone")
    subscription_tier: str = Field(..., description="Subscription tier")
    subscription_status: str = Field(..., description="Subscription status")
    max_users: int = Field(..., description="Maximum users allowed")
    max_events: int = Field(..., description="Maximum events allowed")

    class Config:
        from_attributes = True


class OrganizationSummary(BaseModel):
    """Summary schema for organization data (used in onboarding wizard)."""
    id: int = Field(..., description="Organization ID")
    name: str = Field(..., description="Organization name")
    timezone: str = Field(..., description="Organization timezone")
    created_at: datetime = Field(..., description="Creation timestamp")

    class Config:
        from_attributes = True




