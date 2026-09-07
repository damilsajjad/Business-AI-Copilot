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


class SignupRequest(BaseModel):
    """User signup payload."""

    email: str
    password: str
    full_name: str = ""


class SignupResponse(BaseModel):
    """User signup response."""

    id: str
    email: str
    message: str = "Account created successfully"
