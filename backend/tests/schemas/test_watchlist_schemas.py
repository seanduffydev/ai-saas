"""Tests for watchlist schemas."""

from app.schemas.watchlist import WatchlistItemCreate, WatchlistItem, WatchlistInitializeResponse


def test_watchlist_item_create():
    w = WatchlistItemCreate(commodity_id="gold")
    assert w.commodity_id == "gold"


def test_watchlist_item():
    w = WatchlistItem(
        id="1",
        user_id="u1",
        commodity_id="gold",
        order_index=0,
        added_at="2024-01-01T00:00:00",
    )
    assert w.order_index == 0


def test_watchlist_initialize_response():
    r = WatchlistInitializeResponse(message="OK", data=[])
    assert r.message == "OK"
    assert r.data == []
