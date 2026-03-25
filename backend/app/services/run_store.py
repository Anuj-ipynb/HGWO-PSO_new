"""
run_store.py — In-memory store for active optimization run state.
No external DB needed; single-process, no multiprocessing.
Thread-safe enough for asyncio + background thread via asyncio.to_thread.
"""

from typing import Dict, Any

# Global dict: run_id (str) → run state dict
run_store: Dict[str, Dict[str, Any]] = {}


def create_run(run_id: str, config: dict) -> None:
    run_store[run_id] = {
        "status": "queued",       # queued | running | completed | error
        "progress": 0,            # 0–100
        "iteration": 0,
        "total_iterations": config["iterations"],
        "best_accuracy": 0.0,
        "convergence": [],        # list of best_accuracy per iteration
        "all_accuracies": [],     # all eval accuracies across iterations (for boxplot)
        "figures": {
            "convergence": None,
            "boxplot": None,
        },
        "elapsed_seconds": 0.0,
        "error": None,
    }


def get_run(run_id: str) -> dict | None:
    return run_store.get(run_id)
