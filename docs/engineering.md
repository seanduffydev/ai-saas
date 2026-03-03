# Engineering Standards (Repo Core)

This is the **canonical** engineering standards document for this repository (FastAPI backend + Create React App frontend + Supabase).

If you want “how-to” examples and longer rationale, see:
- `docs/engineering-playbook.md`
- `docs/code-review-checklist.md`
- `docs/naming-conventions.md`

## Scope

Applies to all code under:
- `backend/` (FastAPI, Supabase, forecasting models, pytest)
- `frontend/` (React, CRA tooling)

## Non‑negotiables (MUST)

- **Secrets**: never commit credentials. Use `.env` files locally and environment variables in deploys.
- **Docstrings/JSDoc**: new or changed public Python functions/classes must have **Google-style docstrings**; shared JS utilities/components should have **JSDoc**.
- **Errors**: return clear errors at API boundaries (FastAPI handlers) and don’t swallow exceptions silently.
- **External calls**: network I/O (news, prices) must have timeouts and error handling. Cache where it meaningfully reduces load.
- **Testing when changing behavior**: bug fixes and feature changes should include/adjust tests in `backend/tests/` when feasible.

## Code standards

### Python (backend)

- **Style**: follow PEP 8 conventions; prefer clarity over cleverness.
- **Types**: add type hints for new code and touched code when reasonable.
- **Structure**:
  - API routes: `backend/app/api/v1/endpoints/`
  - Business logic: `backend/app/services/`
  - Data fetchers/integration code: `backend/app/data/fetchers/`
  - Schemas: `backend/app/schemas/`
- **Logging**: use module loggers (`logging.getLogger(__name__)`) for new code; avoid printing from library code.

### JavaScript/React (frontend)

- **Tooling**: uses Create React App’s ESLint configuration (`react-app`, `react-app/jest`).
- **Components**: keep components focused; extract data fetching and non-UI logic when it starts dominating a component.
- **API base URL**: use `REACT_APP_API_URL` and keep backend endpoints consistent.

## API conventions (backend)

- **Auth**: endpoints that require auth should use the shared dependency (`get_current_user`) and return `401` when unauthenticated.
- **Responses**: response shapes should be explicit (Pydantic schemas where practical).
- **Errors**: use `HTTPException` with meaningful `detail` for client visibility; log internal stack traces on the server side.

## Running locally

### Backend

From `backend/`:

```bash
pip install -r requirements.txt -r requirements-dev.txt
./start.sh
```

### Frontend

From `frontend/`:

```bash
npm install
npm start
```

## Testing

### Backend

From `backend/`:

```bash
pytest
```

### Frontend

From `frontend/`:

```bash
npm test
```

## Enforcement (automated)

These checks run in **CI** (GitHub Actions) and, for backend Python, **locally via pre-commit**.

### Backend (Python)

- **Ruff lint** (`ruff check app tests`): style, imports, and docstrings (Google-style).
- **Ruff format** (`ruff format --check app tests`): formatting.
- **Pytest**: all tests in `backend/tests/`.

Config: `backend/pyproject.toml`.

### Frontend

- **Build**: `npm run build` (includes ESLint via Create React App).
- **Tests**: `npm test -- --watchAll=false`.

### Pre-commit (optional, recommended)

From repo root:

```bash
pip install pre-commit   # or use a global install
pre-commit install
```

Then each commit runs Ruff lint and format on changed backend Python files. To run manually: `pre-commit run --all-files`.

### Env templates

- `backend/.env.example` – copy to `backend/.env` and set Supabase/API keys.
- `frontend/.env.example` – copy to `frontend/.env.local` and set `REACT_APP_*` vars.
