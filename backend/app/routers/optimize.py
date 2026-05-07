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

# 🔥 FINAL TRAINING ENDPOINT
from app.optimizers.cnn_trainer import evaluate_candidate

@router.get("/final-train")   # use GET for easy browser demo
async def final_train():
    best_hp = {
        "lr": 0.0036,
        "batch_size": 32,
        "dropout": 0.29,
        "filters1": 32,
        "filters2": 96,
        "filters3": 64,
        "dense_units": 304
    }

    acc = evaluate_candidate(best_hp, epochs=30)

    run_id = "final_run"

    run_store[run_id] = {
        "status": "completed",
        "progress": 100,
        "iteration": 1,
        "total_iterations": 1,
        "best_accuracy": acc,
        "convergence": [acc],
        "all_accuracies": [],
        "figures": {},
        "elapsed_seconds": 0,
        "error": None,
        "best_params": best_hp
    }

    return {"run_id": run_id, "accuracy": acc}