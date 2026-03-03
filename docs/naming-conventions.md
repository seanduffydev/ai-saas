# Naming Conventions (Repo-Specific)

This repo follows normal ecosystem conventions. Keep these rules simple; consistency beats perfection.

## Python (PEP 8)

- **Modules**: `snake_case.py`
- **Packages**: lowercase, no hyphens
- **Classes**: `CapWords`
- **Functions/vars**: `snake_case`
- **Constants**: `UPPER_SNAKE_CASE`
- **Booleans**: read like questions (`is_valid`, `has_session`, `should_refresh`)

## Frontend (React)

- **Components**: `PascalCase.jsx`
- **Hooks**: `useXyz`
- **Props/vars**: `camelCase`

## Files & docs in this repo

- Root docs: keep small and obvious (`README.md`, `WATCHLIST_SETUP.md`).
- `docs/`: use lowercase-with-hyphens (example: `code-review-checklist.md`).

## Data operation verbs (recommended)

Use verbs that communicate whether the operation hits the network or local storage:

- **fetch**: network call to external API (rate limits, auth, latency)
- **get**: general retrieval (may compute or read)
- **load**: bring data into memory/state (often from API/database)
- **save/store**: persist to database/cache
- **cache**: write/read through a caching layer

