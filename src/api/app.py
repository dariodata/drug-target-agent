"""FastAPI application for the drug target explorer."""

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.neo4j_client import close_driver
from src.api.routes import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage Neo4j driver lifecycle."""
    yield
    await close_driver()


app = FastAPI(
    title="Drug Target Explorer API",
    description="REST API for exploring drug target reconnaissance data stored in Neo4j.",
    version="0.1.0",
    lifespan=lifespan,
)

_cors_origins = os.environ.get("CORS_ORIGINS", "*")
_origins = [o.strip() for o in _cors_origins.split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_origins,
    allow_methods=["GET"],
    allow_headers=["*"],
)

app.include_router(router)


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "ok"}
