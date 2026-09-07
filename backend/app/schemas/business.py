"""Business-related Pydantic schemas."""

from datetime import datetime

from pydantic import BaseModel


class BusinessCreate(BaseModel):
    """Schema for creating a new business."""

    name: str
    industry: str = ""
    description: str = ""


class BusinessResponse(BaseModel):
    """Schema for business data in API responses."""

    id: str
    name: str
    industry: str = ""
    description: str = ""
    created_at: datetime
    updated_at: datetime


class BusinessMembershipResponse(BaseModel):
    """Schema for business membership data in API responses."""

    id: str
    business_id: str
    user_id: str
    role: str
    created_at: datetime


class BusinessWithRole(BaseModel):
    """Schema for business data with the user's role."""

    id: str
    name: str
    industry: str = ""
    description: str = ""
    created_at: datetime
    updated_at: datetime
    role: str  # The current user's role in this business
