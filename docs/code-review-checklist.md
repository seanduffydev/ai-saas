# Code Review Checklist

Use this as a lightweight PR review guide. Keep it practical for this repo.

## Before opening a PR

- [ ] **Build/run**: app starts locally (backend and/or frontend if you touched it)
- [ ] **Tests**: relevant tests added/updated
  - Backend: `pytest` (from `backend/`)
  - Frontend: `npm test` (from `frontend/`, when applicable)
- [ ] **Docs**: docstrings/JSDoc updated for public API changes
- [ ] **Secrets**: no API keys, tokens, or `.env` files committed

## PR quality

- [ ] **Scope**: PR is focused and not a “grab bag”
- [ ] **Error handling**: failures are explicit; API endpoints return useful messages
- [ ] **External calls**: timeouts + graceful degradation (especially news/prices)
- [ ] **Security**: auth checks are present where required; no sensitive logging
- [ ] **Performance**: no accidental N+1 network calls; caching considered where appropriate

## Merge readiness

- [ ] **Commit messages**: Conventional Commits preferred (`feat:`, `fix:`, `docs:`, `test:`, `refactor:`)
- [ ] **Changelog/release notes**: update if the change is user-facing

