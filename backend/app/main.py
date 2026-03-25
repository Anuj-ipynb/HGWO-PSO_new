"""
main.py — FastAPI entrypoint for HGWO-PSO optimization engine.
Serves REST API + static figure files.
"""

import uuid
import asyncio
from fastapi import FastAPI, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.routers import optimize
from app.services.run_store import run_store


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: nothing heavy here — we do not pre-load the model
    yield
    # Shutdown cleanup
    run_store.clear()


app = FastAPI(
    title="HGWO-PSO Optimization Engine",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # Dev-only; tighten in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve generated figures as static files
app.mount("/figures", StaticFiles(directory="static/figures"), name="figures")

app.include_router(optimize.router, prefix="/api/v1")
