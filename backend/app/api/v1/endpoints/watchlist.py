"""Watchlist management endpoints."""

from fastapi import APIRouter, Depends, HTTPException
from supabase import Client

from app.api.v1.deps import get_current_user, get_supabase, get_user_id_from_token
from app.schemas.common import MessageResponse
from app.schemas.watchlist import (
    WatchlistAddResponse,
    WatchlistInitializeResponse,
    WatchlistItem,
    WatchlistItemCreate,
)

router = APIRouter()


@router.get("/api/watchlist", response_model=list[WatchlistItem])
async def get_watchlist(
    current_user=Depends(get_current_user),
    supabase: Client = Depends(get_supabase),
):
    """Get user's watchlist commodities ordered by preference.

    Returns the user's customized watchlist with commodities in the order
    they specified. New users will have an empty list until initialization.

    Args:
        current_user: Authenticated user (injected by dependency)
        supabase: Database client (injected by dependency)

    Returns:
        List of watchlist items ordered by order_index

    Raises:
        HTTPException: 500 if data fetching fails
    """
    user_id = get_user_id_from_token(current_user)
    try:
        response = (
            supabase.table("watchlist_preferences")
            .select("*")
            .eq("user_id", user_id)
            .order("order_index")
            .execute()
        )

        return response.data

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to fetch watchlist: {str(e)}"
        )


@router.post("/api/watchlist", response_model=WatchlistAddResponse)
async def add_to_watchlist(
    item: WatchlistItemCreate,
    current_user=Depends(get_current_user),
    supabase: Client = Depends(get_supabase),
):
    """Add a commodity to user's watchlist.

    The commodity will be appended to the end of the user's watchlist
    with an automatically calculated order_index.

    Args:
        item: Watchlist item with commodity_id
        current_user: Authenticated user (injected by dependency)
        supabase: Database client (injected by dependency)

    Returns:
        Success message with created item data

    Raises:
        HTTPException: 400 if commodity already in watchlist, 500 for other errors
    """
    user_id = get_user_id_from_token(current_user)
    try:
        # Get current max order_index for this user
        existing = (
            supabase.table("watchlist_preferences")
            .select("order_index")
            .eq("user_id", user_id)
            .order("order_index", desc=True)
            .limit(1)
            .execute()
        )

        # Calculate next order_index
        next_order = 0
        if existing.data and len(existing.data) > 0:
            next_order = existing.data[0]["order_index"] + 1

        data = {
            "user_id": user_id,
            "commodity_id": item.commodity_id,
            "order_index": next_order,
        }

        response = supabase.table("watchlist_preferences").insert(data).execute()

        return {"message": "Commodity added to watchlist", "data": response.data}

    except Exception as e:
        # Handle duplicate commodity error
        if "duplicate" in str(e).lower() or "unique" in str(e).lower():
            raise HTTPException(
                status_code=400,
                detail=f"Commodity '{item.commodity_id}' is already in your watchlist",
            )
        raise HTTPException(
            status_code=500, detail=f"Failed to add to watchlist: {str(e)}"
        )


@router.delete("/api/watchlist/{commodity_id}", response_model=MessageResponse)
async def remove_from_watchlist(
    commodity_id: str,
    current_user=Depends(get_current_user),
    supabase: Client = Depends(get_supabase),
):
    """Remove a commodity from user's watchlist.

    Deletes the specified commodity from the user's watchlist. Only the owner
    can remove items (enforced by user_id from token).

    Args:
        commodity_id: Commodity identifier to remove
        current_user: Authenticated user (injected by dependency)
        supabase: Database client (injected by dependency)

    Returns:
        Success message

    Raises:
        HTTPException: 500 if deletion fails
    """
    user_id = get_user_id_from_token(current_user)
    try:
        supabase.table("watchlist_preferences").delete().eq(
            "commodity_id", commodity_id
        ).eq("user_id", user_id).execute()

        return {"message": "Commodity removed from watchlist"}

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to remove from watchlist: {str(e)}"
        )


@router.post("/api/watchlist/initialize", response_model=WatchlistInitializeResponse)
async def initialize_watchlist(
    current_user=Depends(get_current_user),
    supabase: Client = Depends(get_supabase),
):
    """Initialize default watchlist for new user.

    Creates a default watchlist with three commodities: Gold, Silver, and Crude Oil.
    If the user already has items, this endpoint returns the existing items.

    Note: This is NOT automatically called. Users start with empty watchlists
    and manually add commodities as needed.

    Args:
        current_user: Authenticated user (injected by dependency)
        supabase: Database client (injected by dependency)

    Returns:
        Success message with initialized or existing watchlist items

    Raises:
        HTTPException: 500 if initialization fails
    """
    user_id = get_user_id_from_token(current_user)
    try:
        # Check if user already has watchlist items
        existing = (
            supabase.table("watchlist_preferences")
            .select("*")
            .eq("user_id", user_id)
            .execute()
        )

        if existing.data and len(existing.data) > 0:
            return {"message": "Watchlist already initialized", "data": existing.data}

        # Insert default items (Gold, Silver, Crude Oil)
        default_items = [
            {"user_id": user_id, "commodity_id": "gold", "order_index": 0},
            {"user_id": user_id, "commodity_id": "silver", "order_index": 1},
            {"user_id": user_id, "commodity_id": "crude_oil", "order_index": 2},
        ]

        response = (
            supabase.table("watchlist_preferences").insert(default_items).execute()
        )

        return {"message": "Default watchlist initialized", "data": response.data}

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to initialize watchlist: {str(e)}"
        )
