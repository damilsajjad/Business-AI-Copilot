"""Authentication-related Pydantic schemas."""

from pydantic import BaseModel


class UserProfile(BaseModel):
    """User profile data."""

    id: str
    email: str
    full_name: str = ""
    avatar_url: str = ""


class TokenPayload(BaseModel):
    """Decoded JWT token payload."""

    sub: str  # User UUID
    email: str = ""
    role: str = "authenticated"
    exp: int | None = None
    iat: int | None = None
