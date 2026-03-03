"""Tests for portfolio schemas."""

from datetime import date

from app.schemas.portfolio import PortfolioPosition, PortfolioPositionCreate


def test_portfolio_position_create_valid():
    p = PortfolioPositionCreate(
        commodity="Gold",
        quantity=10.0,
        purchase_price=1900.0,
        purchase_date=date(2024, 1, 15),
        notes="Test",
    )
    assert p.commodity == "Gold"
    assert p.quantity == 10.0
    assert p.notes == "Test"


def test_portfolio_position_create_quantity_validation():
    from pydantic import ValidationError

    try:
        PortfolioPositionCreate(
            commodity="Gold",
            quantity=-1,
            purchase_price=1900.0,
            purchase_date=date(2024, 1, 15),
        )
        assert False
    except ValidationError:
        pass


def test_portfolio_position_model():
    p = PortfolioPosition(
        id="pos-1",
        user_id="u1",
        commodity="Gold",
        quantity=10.0,
        purchase_price=1900.0,
        purchase_date=date(2024, 1, 15),
        notes=None,
        current_price=1950.0,
        current_value=19500.0,
        profit_loss=500.0,
        profit_loss_percent=2.63,
    )
    assert p.current_value == 19500.0
