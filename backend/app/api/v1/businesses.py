"""Business CRUD API endpoints.

All endpoints require authentication. Business-scoped endpoints
additionally verify membership via the BusinessUser dependency.
"""


from fastapi import APIRouter, HTTPException, status

from app.core.auth import BusinessUser, CurrentUser
from app.core.supabase import SupabaseClientError, get_supabase_client
from app.schemas.business import (
    BusinessCreate,
    BusinessResponse,
    BusinessWithRole,
)

router = APIRouter(prefix="/businesses", tags=["businesses"])


@router.post("", response_model=BusinessResponse, status_code=status.HTTP_201_CREATED)
async def create_business(
    body: BusinessCreate,
    current_user: CurrentUser,
) -> BusinessResponse:
    """Create a new business and assign the current user as owner."""
    try:
        client = get_supabase_client()

        # Create business
        biz_result = (
            client.table("businesses")
            .insert(
                {
                    "name": body.name,
                    "industry": body.industry,
                    "description": body.description,
                }
            )
            .execute()
        )

        if not biz_result.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create business",
            )

        business = biz_result.data[0]

        # Create owner membership
        client.table("business_memberships").insert(
            {
                "business_id": business["id"],
                "user_id": current_user["id"],
                "role": "owner",
            }
        ).execute()

        return BusinessResponse(**business)

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
            detail=f"Failed to create business: {e}",
        ) from e


@router.get("", response_model=list[BusinessWithRole])
async def list_businesses(current_user: CurrentUser) -> list[BusinessWithRole]:
    """List all businesses the current user is a member of."""
    try:
        client = get_supabase_client()

        # Get user's memberships with business data
        result = (
            client.table("business_memberships")
            .select("role, businesses(*)")
            .eq("user_id", current_user["id"])
            .execute()
        )

        businesses = []
        for membership in result.data or []:
            biz = membership.get("businesses", {})
            if biz:
                businesses.append(
                    BusinessWithRole(
                        id=biz["id"],
                        name=biz["name"],
                        industry=biz.get("industry", ""),
                        description=biz.get("description", ""),
                        created_at=biz["created_at"],
                        updated_at=biz["updated_at"],
                        role=membership["role"],
                    )
                )

        return businesses

    except SupabaseClientError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database service not configured",
        ) from exc
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list businesses: {e}",
        ) from e


@router.get("/{business_id}", response_model=BusinessWithRole)
async def get_business(
    business_user: BusinessUser,
) -> BusinessWithRole:
    """Get a single business by ID. Requires membership."""
    try:
        client = get_supabase_client()

        result = (
            client.table("businesses")
            .select("*")
            .eq("id", business_user["business_id"])
            .single()
            .execute()
        )

        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Business not found",
            )

        return BusinessWithRole(
            **result.data,
            role=business_user["business_role"],
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get business: {e}",
        ) from e


@router.put("/{business_id}", response_model=BusinessResponse)
async def update_business(
    body: BusinessCreate,
    business_user: BusinessUser,
) -> BusinessResponse:
    """Update a business. Requires owner role."""
    if business_user["business_role"] != "owner":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only business owners can update business details",
        )

    try:
        client = get_supabase_client()

        result = (
            client.table("businesses")
            .update(
                {
                    "name": body.name,
                    "industry": body.industry,
                    "description": body.description,
                }
            )
            .eq("id", business_user["business_id"])
            .execute()
        )

        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Business not found",
            )

        return BusinessResponse(**result.data[0])

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update business: {e}",
        ) from e


@router.delete("/{business_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_business(
    business_user: BusinessUser,
) -> None:
    """Delete a business. Requires owner role."""
    if business_user["business_role"] != "owner":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only business owners can delete a business",
        )

    try:
        client = get_supabase_client()

        client.table("businesses").delete().eq(
            "id", business_user["business_id"]
        ).execute()

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete business: {e}",
        ) from e
