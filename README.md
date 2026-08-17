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

## Phase 0 Lock

**MVP sentence** — A creator seeds their past content catalog, the system learns
their unique voice and style from real performance data, recommends what to make
next with a rationale tied to their actual best-performing content traits,
generates a script and thumbnail in that learned style, scores it against their
profile through a quality gate that can reject and regenerate, and presents the
full decision log alongside the output before publishing.

**Differentiation** — Every comparable tool takes a topic as input and generates
generic content. AfterTake takes a specific creator's own catalog and performance
history, learns what makes them distinctive and what has actually worked, and
uses that profile to decide what to make next and whether the output actually
sounds and looks like them — not like generic AI.

**Never cut** — the DNA agent producing a real profile from the seed catalog; the
opportunity recommendation with a rationale tied to the profile; the scorer's
live reject/regenerate cycle visible in the decision log; the decision log shown
in the UI with stage-by-stage reasoning.

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

### Backend (Phase 1)

```bash
# Install backend dependencies into backend/.venv
backend/.venv/Scripts/python -m pip install -r backend/requirements.txt

# Start the API (repo root). Auto-applies the DB schema on startup.
backend/.venv/Scripts/python -m uvicorn backend.main:app --reload
```

The API lives at http://localhost:8000 — interactive docs at `/docs`.

**LLM provider (Phase 2 dev default):** local **Ollama** (`llama3.2:1b`) via
`backend/agents/llm.py` — every agent call goes through `call_llm()`, the one
place that talks to a model. To switch to the Anthropic API (the production
stack): set `LLM_PROVIDER=anthropic` and fill `ANTHROPIC_API_KEY` in `.env`.
No code changes needed.

**Endpoints** (Phase 0 Step 10 contract, all verified live):

| Endpoint | Status | What it does today |
|---|---|---|---|
| `GET /health` | real | liveness check |
| `POST /catalog/ingest` | real | stores Source Video objects (storage only) |
| `POST /profile/build` | stub* | returns + stores a realistic DNA profile |
| `GET /profile/{creator_id}` | real | returns the stored profile or 404 |
| `POST /content/recommend` | stub* | 3 ranked opportunities (0.87 / 0.71 / 0.58) |
| `POST /content/generate` | stub* | full asset: script + 3 thumbnails + metadata |
| `POST /content/score` | stub* | alternates reject (0.62) / pass (0.81) |
| `POST /content/publish` | stub* | returns a fake YouTube post id + URL |
| `POST /pipeline/run` | stub* | full run + 8-entry decision log (persisted) |
| `GET /pipeline/{run_id}/status` | real | run status + progress % for the UI poll |
| `GET /pipeline/{run_id}/log` | real | the full decision log, oldest first |
| `GET /output/video/{filename}` | stub* | 404 until rendering exists (Phase 3) |
| `GET /output/thumbnail/{filename}` | stub* | real file, else a generated placeholder PNG |

*\*Stub* = realistic fake data (Phase 1 Step 3) shaped exactly like the real
response will be, built through the real Pydantic models. The frontend can build
against these today; real agents replace them in Phase 2+. The `POST /pipeline/run`
stub persists its run + decision-log rows, so the *real* status/log endpoints
serve the full demo timeline immediately.

Errors follow one shape everywhere: `{status: "error", message, detail}` —
422 validation (names the failing field), 404 not-found (names what was missing),
500 internal (describes what broke), consistent for unknown routes too.

### Demo flow (works end to end today, stubs only)

```bash
# Seed the 8-video catalog, then run the whole pipeline
backend/.venv/Scripts/python -m backend.db.seed
curl -X POST http://localhost:8000/pipeline/run -H "Content-Type: application/json" \
     -d '{"creator_id": "creator_001"}'
# -> complete run: selected opportunity, generated asset, 8 decision-log
#    entries incl. a live reject -> regenerate -> pass cycle
```

## What Is Real vs Mocked

Phase 1 = backend foundations only. Real: models + validation, SQLite storage,
all routing, CORS, error handling, seed catalog, benchmark math. **Mocked:** all
agent output (DNA profile, opportunities, script, thumbnails, metadata,
scoring, publishing) — served as realistic stubs until Phase 2+; video
rendering + TTS + captions are not built at all yet (Phase 3).

**SVG rendering note:** cairosvg (the plan's primary thumbnail renderer) needs
the native cairo DLL, which is missing on this Windows box. resvg-py — the
plan's named fallback — is installed and verified rendering the stub thumbnails
to valid PNGs. Phase 3 will use resvg-py.
