"""
schemas.py — Pydantic request/response models.
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, List


class OptimizeRequest(BaseModel):
    epochs: int = Field(default=2, ge=1, le=5, description="Training epochs per candidate")
    population: int = Field(default=6, ge=4, le=20, description="Swarm / pack size")
    iterations: int = Field(default=10, ge=3, le=30, description="Optimization iterations")


class OptimizeResponse(BaseModel):
    run_id: str
    message: str


class RunStatus(BaseModel):
    status: str
    progress: int
    iteration: int
    total_iterations: int
    best_accuracy: float
    convergence: List[float]
    all_accuracies: List[float]
    figures: Dict[str, Optional[str]]
    elapsed_seconds: float
    error: Optional[str]
