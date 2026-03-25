"""
routers/optimize.py — REST endpoints:
  POST /api/v1/optimize       → kick off background optimization
  GET  /api/v1/status/{run_id} → poll live status
"""

import uuid
import asyncio
from fastapi import APIRouter, BackgroundTasks, HTTPException

from app.models.schemas import OptimizeRequest, OptimizeResponse, RunStatus
from app.services.run_store import run_store, create_run, get_run
from app.optimizers.hgwo_pso import run_hgwo_pso

router = APIRouter()


@router.post("/optimize", response_model=OptimizeResponse)
async def start_optimization(req: OptimizeRequest, background_tasks: BackgroundTasks):
    """
    Validate request, create a run entry, then launch HGWO-PSO in a
    background thread via asyncio.to_thread (non-blocking — does NOT use
    asyncio.run inside an async function).
    """
    run_id = str(uuid.uuid4())[:8]
    config = {
        "epochs":     req.epochs,
        "population": req.population,
        "iterations": req.iterations,
    }
    create_run(run_id, config)

    # asyncio.to_thread runs the blocking optimizer in a thread pool
    # without blocking the event loop
    background_tasks.add_task(_run_in_thread, run_id, config)

    return OptimizeResponse(run_id=run_id, message="Optimization started")


async def _run_in_thread(run_id: str, config: dict):
    """Wraps the blocking optimizer so it runs in a thread pool."""
    try:
        await asyncio.to_thread(run_hgwo_pso, run_id, config)
    except Exception as exc:
        state = run_store.get(run_id)
        if state:
            state["status"] = "error"
            state["error"]  = str(exc)


@router.get("/status/{run_id}", response_model=RunStatus)
async def get_status(run_id: str):
    state = get_run(run_id)
    if state is None:
        raise HTTPException(status_code=404, detail="Run not found")
    return RunStatus(**state)
