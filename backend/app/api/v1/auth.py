"""Authentication API endpoints.

Signup/login is handled client-side via Supabase Auth JS SDK.
These endpoints verify JWT tokens and return user data.
"""

from fastapi import APIRouter, HTTPException, status

from app.core.auth import CurrentUser
from app.core.supabase import SupabaseClientError, get_supabase_client
from app.schemas.auth import SignupRequest, SignupResponse, UserProfile

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup", response_model=SignupResponse, status_code=status.HTTP_201_CREATED)
async def signup(body: SignupRequest) -> SignupResponse:
    """Create a new user account with pre-confirmed email to avoid SMTP rate limits."""
    try:
        client = get_supabase_client()
        res = client.auth.admin.create_user(
            {
                "email": body.email,
                "password": body.password,
                "email_confirm": True,
                "user_metadata": {"full_name": body.full_name},
            }
        )
        if not res or not res.user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create account",
            )
        return SignupResponse(
            id=str(res.user.id),
            email=res.user.email or body.email,
            message="Account created successfully",
        )
    except HTTPException:
        raise
    except Exception as e:
        err_msg = str(e)
        if "already been registered" in err_msg or "already exists" in err_msg:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="An account with this email address already exists. Please sign in.",
            ) from e
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Could not create account: {err_msg}",
        ) from e


@router.get("/me")
async def get_me(current_user: CurrentUser) -> dict:
    """Return the current authenticated user's basic info from the JWT token."""
    return {
        "id": current_user["id"],
        "email": current_user["email"],
        "role": current_user["role"],
    }


@router.get("/profile", response_model=UserProfile)
async def get_profile(current_user: CurrentUser) -> UserProfile:
    """Return the current user's full profile from the database."""
    try:
        client = get_supabase_client()
        result = (
            client.table("profiles")
            .select("*")
            .eq("id", current_user["id"])
            .single()
            .execute()
        )

        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Profile not found",
            )

        return UserProfile(
            id=result.data["id"],
            email=result.data["email"],
            full_name=result.data.get("full_name", ""),
            avatar_url=result.data.get("avatar_url", ""),
        )
    except SupabaseClientError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database service not configured",
        ) from exc
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch profile: {e}",
        ) from e
