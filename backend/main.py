"""AfterTake FastAPI entry point. Wiring only — no business logic lives here.

Run from the repo root (using the backend venv's python):

    backend/.venv/Scripts/python -m uvicorn backend.main:app --reload

The DB schema is applied on startup via db/database.init_db(), which executes
every *.sql file in backend/db/sql/ (idempotent).
"""
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.db import database
from backend.routers import catalog, content, output, pipeline, profile


@asynccontextmanager
async def lifespan(_app: FastAPI):
    database.init_db()
    yield


app = FastAPI(title="AfterTake", version="0.1.0", lifespan=lifespan)

# CORS: wide open for local development (Phase 1 Step 4). Vite dev server runs
# on http://localhost:5173; the allowed origins come from CORS_ORIGINS.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(catalog.router)
app.include_router(profile.router)
app.include_router(pipeline.router)
app.include_router(content.router)
app.include_router(output.router)


# --- Consistent error shape (Phase 1 Step 4) --------------------------------
# Every error response follows {status: "error", message, detail} so the
# frontend always knows what broke, from the response, without reading logs.


@app.exception_handler(RequestValidationError)
async def validation_error_handler(_request: Request, exc: RequestValidationError):
    first = exc.errors()[0] if exc.errors() else {}
    loc = ".".join(str(p) for p in first.get("loc", []) if p != "body")
    msg = f"Validation error at {loc}: {first.get('msg', 'invalid input')}"
    return JSONResponse(
        status_code=422,
        content={
            "status": "error",
            "message": msg,
            "detail": jsonable_encoder(exc.errors()),
        },
    )


@app.exception_handler(HTTPException)
async def http_error_handler(_request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": "error",
            "message": str(exc.detail),
            "detail": None,
        },
    )


@app.exception_handler(Exception)
async def unhandled_error_handler(_request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "message": f"Internal error: {exc}",
            "detail": None,
        },
    )


@app.get("/health")
def health():
    return {"status": "ok"}


# Catch-all — registered LAST so it never shadows a real route. Unknown paths
# return the consistent {status, message} shape instead of Starlette's plain
# "Not Found" text.
@app.api_route("/{full_path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE", "HEAD"])
async def not_found(full_path: str):
    raise HTTPException(status_code=404, detail=f"Not found: /{full_path}")
