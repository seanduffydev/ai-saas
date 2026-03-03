# Deployment (Vercel + Railway)

This repo is a **monorepo**: frontend (React) and backend (FastAPI) live in `frontend/` and `backend/`. Each platform must use the correct **root directory** or builds will fail.

## Vercel (frontend)

- **Root Directory:** Set to **`frontend`** in the Vercel project.
  - Project Settings → General → Root Directory → `frontend` (then Save).
- **Build:** Uses `frontend/vercel.json` (build command and output directory are set).
- **Environment variables:** Add in Vercel dashboard, e.g. `REACT_APP_API_URL`, `REACT_APP_SUPABASE_URL`, `REACT_APP_SUPABASE_ANON_KEY` (see `frontend/.env.example`).

If Root Directory is left at the repo root, Vercel will not find `package.json` and the build will fail.

## Railway (backend)

- **Root Directory:** Set to **`backend`** in the Railway service.
  - Service → Settings → Source → Root Directory → `backend`.
- **Start command:** Handled by `backend/Procfile` or `backend/railway.json` (`uvicorn app.main:app --host 0.0.0.0 --port $PORT`). Railway sets `PORT` automatically.
- **Environment variables:** Add in Railway dashboard, e.g. `SUPABASE_URL`, `SUPABASE_KEY`, `OPENAI_API_KEY`, `NEWS_API_KEY`, `ALPHA_VANTAGE_API_KEY` (see `backend/.env.example`).

If Root Directory is left at the repo root, Railway will not find `requirements.txt` or the `app` module and the build/deploy will fail.

**Note:** The backend depends on `torch`; the first build can be slow or hit memory limits. If the build times out, consider using a CPU-only PyTorch build in `requirements.txt` or increasing Railway build resources.

## After changing root directories

Redeploy (e.g. trigger a new deployment from the Vercel/Railway dashboard or push a commit) so the new settings apply.
