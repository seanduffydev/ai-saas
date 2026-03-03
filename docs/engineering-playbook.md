# Engineering Playbook (Examples & How‑To)

This document contains **examples and deeper guidance** referenced by `docs/engineering.md`. It’s intentionally longer; keep the core standards short.

## Documentation (Google-style docstrings)

Use Google-style docstrings for public functions/classes and anything that’s used outside its module.

```python
def fetch_prices(commodity: str, period: str = "1y") -> list[dict]:
    """Fetch historical price data for a commodity.

    Args:
        commodity: Commodity identifier (e.g. "gold").
        period: Yahoo Finance period string (e.g. "1y", "5y").

    Returns:
        List of OHLCV rows as dicts.

    Raises:
        ValueError: If the commodity is unknown or data is unavailable.
    """
```

## Error handling at boundaries

- **API handlers**: catch and translate errors into `HTTPException` with a user-meaningful `detail`.
- **Library/service code**: prefer raising specific exceptions and letting the handler translate them.

## Safe data access (defensive patterns)

Prefer validating shape/emptiness before indexing:

```python
if not df.empty and "close" in df.columns:
    last_close = float(df["close"].iloc[-1])
else:
    raise ValueError("Missing close data")
```

Prefer `.get()` for nested dicts:

```python
expires_at = entry.get("expires_at")
if not expires_at:
    return None
```

## External calls (timeouts, retries, and caching)

- Always set **timeouts** for HTTP calls.
- Cache expensive/frequently requested data (e.g. news) when it reduces upstream API usage.
- Log failures with enough context to debug (commodity, period, endpoint), but **never log secrets**.

## Logging (guidance)

- Use structured, searchable messages (include commodity/user_id/request id when available).
- Use appropriate levels:
  - DEBUG: noisy diagnostics
  - INFO: high-level lifecycle events
  - WARNING: unexpected but handled conditions
  - ERROR: failed operations

