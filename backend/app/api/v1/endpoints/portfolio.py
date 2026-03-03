"""Portfolio management endpoints."""

from fastapi import APIRouter, Depends, HTTPException
from supabase import Client

from app.api.v1.deps import get_current_user, get_supabase, get_user_id_from_token
from app.schemas.common import MessageResponse
from app.schemas.portfolio import (
    PortfolioAddResponse,
    PortfolioPosition,
    PortfolioPositionCreate,
)
from app.services.portfolio_service import PortfolioService

router = APIRouter()


@router.get("/api/portfolio", response_model=list[PortfolioPosition])
async def get_portfolio(
    current_user=Depends(get_current_user),
    supabase: Client = Depends(get_supabase),
):
    """Get all portfolio positions for a user with current market data.

    Fetches user's positions from database and enriches each with:
    - Current market price
    - Current total value
    - Profit/loss amount
    - Profit/loss percentage

    Args:
        current_user: Authenticated user (injected by dependency)
        supabase: Database client (injected by dependency)

    Returns:
        List of portfolio positions with calculated metrics

    Raises:
        HTTPException: 500 if data fetching fails
    """
    user_id = get_user_id_from_token(current_user)
    try:
        # Fetch positions from database
        response = (
            supabase.table("portfolio_positions")
            .select("*")
            .eq("user_id", user_id)
            .execute()
        )

        positions = response.data

        # Enrich each position with current price data
        enriched_positions = []
        for position in positions:
            enriched = PortfolioService.enrich_position_with_current_data(position)
            enriched_positions.append(enriched)

        return enriched_positions

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to fetch portfolio: {str(e)}"
        )


@router.post("/api/portfolio", response_model=PortfolioAddResponse)
async def add_position(
    position: PortfolioPositionCreate,
    current_user=Depends(get_current_user),
    supabase: Client = Depends(get_supabase),
):
    """Add a new portfolio position.

    Creates a new position record with the provided details. The position
    will be associated with the authenticated user.

    Args:
        position: Position details (commodity, quantity, price, date, notes)
        current_user: Authenticated user (injected by dependency)
        supabase: Database client (injected by dependency)

    Returns:
        Success message with created position data

    Raises:
        HTTPException: 400 if validation fails, 500 if database operation fails
    """
    user_id = get_user_id_from_token(current_user)
    try:
        data = {
            "user_id": user_id,
            "commodity": position.commodity,
            "quantity": position.quantity,
            "purchase_price": position.purchase_price,
            "purchase_date": position.purchase_date.isoformat(),
            "notes": position.notes,
        }

        response = supabase.table("portfolio_positions").insert(data).execute()

        return {"message": "Position added successfully", "data": response.data}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add position: {str(e)}")


@router.delete("/api/portfolio/{position_id}", response_model=MessageResponse)
async def delete_position(
    position_id: str,
    current_user=Depends(get_current_user),
    supabase: Client = Depends(get_supabase),
):
    """Delete a portfolio position.

    Removes the specified position from the user's portfolio. Only the owner
    of the position can delete it (enforced by user_id from token).

    Args:
        position_id: Position identifier (UUID)
        current_user: Authenticated user (injected by dependency)
        supabase: Database client (injected by dependency)

    Returns:
        Success message

    Raises:
        HTTPException: 404 if position not found, 500 if deletion fails
    """
    user_id = get_user_id_from_token(current_user)
    try:
        response = (
            supabase.table("portfolio_positions")
            .delete()
            .eq("id", position_id)
            .eq("user_id", user_id)
            .execute()
        )

        if not response.data or len(response.data) == 0:
            raise HTTPException(
                status_code=404,
                detail="Position not found or you do not have permission to delete it",
            )

        return {"message": "Position deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to delete position: {str(e)}"
        )
