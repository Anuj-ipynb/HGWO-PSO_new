"""
main.py — FastAPI entrypoint for HGWO-PSO optimization engine.
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
    yield
    run_store.clear()


app = FastAPI(
    title="HGWO-PSO Optimization Engine",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ FIXED STATIC MOUNT
app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(optimize.router, prefix="/api/v1")


@app.get("/")
def home():
    return {"message": "API is working 🚀"}