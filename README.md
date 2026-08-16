# AfterTake

AfterTake is a personalized, self-improving content decision engine. It learns a
specific creator's actual voice, thumbnail style, and title formula from their
own catalog and real performance data, then acts as their editorial brain:
deciding what to make next, generating it in their established style, gating
every asset through a style-fit quality check that can reject and regenerate,
and presenting the full decision log alongside the output before publishing.

Where comparable tools take a topic as input and produce generic content,
AfterTake conditions every decision and every generated asset on the creator's
own learned profile — the innovation is the decision layer, not the generation
mechanics.

## Run Instructions

### Database (Phase 0)

Everything runs from the repo root with the backend venv's python:

```bash
# Create tables from backend/db/sql/*.sql (idempotent — safe to rerun)
backend/.venv/Scripts/python -m backend.db.manage init

# Wipe all tables, then re-create them from the schema files
backend/.venv/Scripts/python -m backend.db.manage reset

# List tables + row counts
backend/.venv/Scripts/python -m backend.db.manage inspect

# Print the resolved DB file path (DATABASE_PATH from .env, default ./aftertake.db)
backend/.venv/Scripts/python -m backend.db.manage path

# Load the 8-video seed catalog (data/seed/catalog.json) for creator_001
# Mirrors POST /catalog/ingest; idempotent (safe to re-run)
backend/.venv/Scripts/python -m backend.db.seed
```

The schema is one SQL file per table in `backend/db/sql/` — applied in sorted
filename order on `init` and on backend startup.

### Backend (Phase 1+)

*Placeholder — once dependencies are installed: `uvicorn backend.main:app --reload`.*

## What Is Real vs Mocked

*Placeholder — updated as each stage is built. The rule: be honest about mocked
parts. Judges respect transparency.*
