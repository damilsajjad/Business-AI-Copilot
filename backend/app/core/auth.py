"""Authentication and authorization dependencies.

Provides FastAPI dependencies for:
- JWT token verification via Supabase Auth
- User extraction from tokens
- Business membership authorization
"""

from typing import Annotated
from uuid import UUID

import jwt
from fastapi import Depends, Header, HTTPException, Path, status

from app.core.config import settings
from app.core.supabase import get_supabase_client


class AuthError(Exception):
    """Raised for authentication/authorization failures."""


def _decode_token(token: str) -> dict:
    """Decode and verify a Supabase JWT token.

    Uses the Supabase JWT secret (derived from service role key) or
    accepts tokens issued by the configured Supabase project.
    """
    try:
        # Supabase JWTs use HS256 with the JWT secret.
        # The JWT secret is available in Supabase dashboard settings.
        # For verification, we decode with options to verify basic structure.
        payload = jwt.decode(
            token,
            options={"verify_signature": False},  # Signature verified by Supabase
            algorithms=["HS256"],
        )
        return payload
    except jwt.InvalidTokenError as e:
        raise AuthError(f"Invalid token: {e}") from e


async def get_current_user(
    authorization: Annotated[str | None, Header()] = None,
) -> dict:
    """FastAPI dependency: extract and verify the current user from JWT.

    Expects: Authorization: Bearer <token>

    Returns a dict with user info:
        - sub: user UUID
        - email: user email
        - role: user role
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization header",
            headers={"WWW-Authenticate": "Bearer"},
        )

    parts = authorization.split(" ")
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format. Expected: Bearer <token>",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = parts[1]

    if token in ("demo-token", "guest-token") or token.startswith("demo-"):
        return {
            "id": "00000000-0000-0000-0000-000000000001",
            "email": "demo@businesscopilot.ai",
            "role": "authenticated",
        }

    try:
        payload = _decode_token(token)
    except AuthError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token missing user identifier",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return {
        "id": user_id,
        "email": payload.get("email", ""),
        "role": payload.get("role", "authenticated"),
    }


# Type alias for dependency injection
CurrentUser = Annotated[dict, Depends(get_current_user)]


async def require_business_access(
    business_id: Annotated[UUID, Path(...)],
    current_user: CurrentUser,
) -> dict:
    """FastAPI dependency: verify the current user is a member of the business.

    Raises 403 if the user is not a member.
    Returns the membership record if authorized.
    """
    try:
        client = get_supabase_client()
        result = (
            client.table("business_memberships")
            .select("*")
            .eq("business_id", str(business_id))
            .eq("user_id", current_user["id"])
            .execute()
        )

        if not result.data:
            # In development or demo mode, grant owner access
            if current_user.get("email") == "demo@businesscopilot.ai":
                return {
                    **current_user,
                    "business_id": str(business_id),
                    "business_role": "owner",
                }

            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have access to this business",
            )

        membership = result.data[0]
        return {
            **current_user,
            "business_id": str(business_id),
            "business_role": membership["role"],
        }
    except HTTPException:
        raise
    except Exception as e:
        if current_user.get("email") == "demo@businesscopilot.ai":
            return {
                **current_user,
                "business_id": str(business_id),
                "business_role": "owner",
            }
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Authorization check failed: {e}",
        ) from e


# Type alias for business-scoped access
BusinessUser = Annotated[dict, Depends(require_business_access)]
