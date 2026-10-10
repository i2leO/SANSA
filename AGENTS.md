# SANSA — Agent Working Context

## Start here

Read `docs/LIVE_DATA_CONTEXT.md` first for the compact live-site/SQL/Excel comparison (completed 2026-09-12). Read `docs/REWORK_CONTEXT.md` for the original source review at commit `8e034536cce40b00a3dee37af85d759dc2818ad5` on `main`.

Current facts: the SQL dump has 20 instrument columns absent from Git models; revised4 contains 200 populated participants plus 100 template rows; its Model 3 predicts Under/Normal/Over. Do not assume Git equals deployed code or match Excel record numbers to existing respondents without an approved identity crosswalk. The current authorization is inspection/documentation; implementation/import is pending the user's remaining requirements.

## Project intent

SANSA is a Thai nutrition research data collection application for older adults/caregivers and research staff. The stack is React 18 + TypeScript + Vite + Tailwind + Zustand, FastAPI + Pydantic + SQLAlchemy, and MySQL. The user plans a rework; its detailed scope has not yet been specified. Communicate with the user in Thai unless requested otherwise.

## Working conventions

- Treat active source code as the implementation baseline. README/architecture descriptions and `*_old.*` files do not reliably describe current behavior.
- Follow imports from `frontend/src/App.tsx` and `backend/app/main.py`. Legacy files are historical references, not automatic edit targets.
- Trace changes across UI, API schema, router, scoring service, model, and export/import mapping.
- Preserve respondent codes, visit associations, raw answers, recorded scores, scoring versions, and research export meanings. Distinguish numeric zero from missing data.
- Do not invent clinical scoring rules or silently recalculate historical results. Obtain the research instrument's approved specification when a requested change depends on it.
- Use synthetic data for verification. Do not copy participant records, workbook rows, credentials, tokens, or database dumps into documentation or logs.
- Do not run reset/recreate/import/seed scripts against an existing database as a routine setup step. Inspect their effects and select an appropriate isolated database first.
- The repository has Alembic configuration but no tracked migration revisions at the reviewed commit. Do not claim `alembic upgrade head` creates the schema.
- For frontend changes, use the lockfile and check `npm run build`; use lint when applicable. For backend behavior changes, add focused regression coverage and use an isolated test database where integration testing is needed.
- Report checks actually performed and any remaining limitations. Static syntax checks are not evidence that the application runs.
- Update `docs/REWORK_CONTEXT.md` when an architectural decision is made or a recorded issue is resolved.

## Entry points

- Frontend routing: `frontend/src/App.tsx`, `frontend/src/pages/admin/AdminRoutes.tsx`
- API client/auth state: `frontend/src/lib/api.ts`, `frontend/src/stores/authStore.ts`
- Backend routing/config: `backend/app/main.py`, `backend/app/config.py`
- Data contracts: `backend/app/models.py`, `backend/app/schemas.py`, `frontend/src/types/index.ts`
- Business logic: `backend/app/services/scoring_service.py`, `backend/app/services/export_service.py`

The initial review added documentation only. It did not approve or perform a redesign, database migration, deployment, or historical data correction.
