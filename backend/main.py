"""AfterTake FastAPI entry point. Wiring only — no business logic lives here.

Run from the repo root (using the backend venv's python):

    .venv/Scripts/python -m uvicorn backend.main:app --reload

The DB schema is applied on startup via db/database.init_db(), which executes
backend/db/schema.sql (idempotent).
"""
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.db import database
from backend.routers import catalog, pipeline, profile


@asynccontextmanager
async def lifespan(_app: FastAPI):
    database.init_db()
    yield


app = FastAPI(title="AfterTake", version="0.1.0", lifespan=lifespan)

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


@app.get("/health")
def health():
    return {"status": "ok"}
