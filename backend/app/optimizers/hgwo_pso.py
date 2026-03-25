"""
hgwo_pso.py — Hybrid Grey Wolf Optimizer + Particle Swarm Optimization.

ALGORITHM OVERVIEW
──────────────────
Optimizes 7 DNN hyperparameters simultaneously:
  [lr, batch_size, dropout, filters1, filters2, filters3, dense_units]

PSO velocity update:
  V = w*V + c1*r1*(pbest - X) + c2*r2*(gbest - X)

GWO position update:
  X_GWO = mean(X_alpha, X_beta, X_delta)  — standard GWO step

Hybrid blend:
  X(t+1) = (1 - λ)*X_GWO + λ*(X + V),   λ = 0.5

PERFORMANCE NOTES
─────────────────
• All CNN training runs on CUDA GPU (if available).
• This optimizer itself runs on CPU (numpy) — no benefit to GPU-side
  meta-heuristics at this population size.
• GPU memory is freed after each candidate evaluation.
• No multiprocessing / threading — sequential evaluation to stay stable
  on low-VRAM cards (GTX 1050 Ti, 4 GB).
"""

import numpy as np
import time
import torch

from app.optimizers.cnn_trainer import evaluate_candidate
from app.services.run_store import run_store

# ── Hyperparameter search space ──────────────────────────────────────────────
# Dimension = 7
# [lr, batch_size, dropout, filters1, filters2, filters3, dense_units]

BOUNDS_LOW  = np.array([1e-4,  8,  0.1,  16,  16,  16,  64], dtype=np.float64)
BOUNDS_HIGH = np.array([1e-2, 32,  0.5,  64,  64,  64, 256], dtype=np.float64)
DIM = 7          # MUST match len(BOUNDS_LOW) == len(BOUNDS_HIGH)

# ── Algorithm hyper-parameters ────────────────────────────────────────────────
LAMBDA   = 0.5   # hybrid blend weight
W        = 0.7   # PSO inertia weight
C1       = 1.5   # cognitive coefficient
C2       = 1.5   # social coefficient


def _clip(X: np.ndarray) -> np.ndarray:
    """Clip positions to search bounds."""
    return np.clip(X, BOUNDS_LOW, BOUNDS_HIGH)


def _decode(x: np.ndarray) -> dict:
    """
    Decode a continuous position vector into integer/float hyperparameters.
    batch_size and filter counts are integers; lr and dropout are floats.
    """
    return {
        "lr":          float(x[0]),
        "batch_size":  int(round(x[1])),
        "dropout":     float(x[2]),
        "filters1":    int(round(x[3])),
        "filters2":    int(round(x[4])),
        "filters3":    int(round(x[5])),
        "dense_units": int(round(x[6])),
    }


def run_hgwo_pso(run_id: str, config: dict) -> None:
    """
    Entry point called from asyncio.to_thread — runs in a worker thread so
    it does NOT block the FastAPI event loop.

    Updates run_store[run_id] in-place for the polling endpoint to read.
    """
    state = run_store[run_id]
    state["status"] = "running"
    t_start = time.time()

    n_pop  = config["population"]
    n_iter = config["iterations"]
    epochs = config["epochs"]

    # ── Initialise population positions & velocities (CPU numpy) ─────────────
    rng = np.random.default_rng(seed=42)
    X = rng.uniform(BOUNDS_LOW, BOUNDS_HIGH, size=(n_pop, DIM))  # positions
    V = np.zeros((n_pop, DIM))                                    # velocities

    # Personal bests (PSO)
    pbest      = X.copy()
    pbest_fit  = np.full(n_pop, -np.inf)

    # Global best
    gbest      = X[0].copy()
    gbest_fit  = -np.inf

    # GWO leaders
    alpha_pos, alpha_score = np.zeros(DIM), -np.inf
    beta_pos,  beta_score  = np.zeros(DIM), -np.inf
    delta_pos, delta_score = np.zeros(DIM), -np.inf

    convergence_curve = []

    # ── Main optimisation loop ────────────────────────────────────────────────
    for iteration in range(n_iter):

        iter_accuracies = []

        # Evaluate every candidate sequentially
        for i in range(n_pop):
            hp = _decode(X[i])
            acc = evaluate_candidate(hp, epochs=epochs)   # runs on CUDA GPU
            iter_accuracies.append(acc)

            # Update personal best
            if acc > pbest_fit[i]:
                pbest_fit[i] = acc
                pbest[i]     = X[i].copy()

            # Update global best
            if acc > gbest_fit:
                gbest_fit = acc
                gbest     = X[i].copy()

            # Update GWO leaders  (α > β > δ)
            if acc > alpha_score:
                delta_pos, delta_score = beta_pos.copy(),  beta_score
                beta_pos,  beta_score  = alpha_pos.copy(), alpha_score
                alpha_pos, alpha_score = X[i].copy(),      acc
            elif acc > beta_score:
                delta_pos, delta_score = beta_pos.copy(), beta_score
                beta_pos,  beta_score  = X[i].copy(),     acc
            elif acc > delta_score:
                delta_pos, delta_score = X[i].copy(), acc

        # ── GWO position update ──────────────────────────────────────────────
        # a decreases linearly from 2 → 0 over iterations
        a = 2.0 - iteration * (2.0 / n_iter)

        X_new = np.zeros_like(X)
        for i in range(n_pop):
            # GWO encircling for each of the three leaders
            def gwo_step(leader):
                r1, r2 = rng.random(DIM), rng.random(DIM)
                A = 2 * a * r1 - a
                C = 2 * r2
                D = np.abs(C * leader - X[i])
                return leader - A * D

            X1 = gwo_step(alpha_pos)
            X2 = gwo_step(beta_pos)
            X3 = gwo_step(delta_pos)
            X_GWO = (X1 + X2 + X3) / 3.0   # GWO candidate position

            # ── PSO velocity + position ──────────────────────────────────────
            r1_pso, r2_pso = rng.random(DIM), rng.random(DIM)
            V[i] = (W * V[i]
                    + C1 * r1_pso * (pbest[i] - X[i])
                    + C2 * r2_pso * (gbest    - X[i]))
            X_PSO = X[i] + V[i]

            # ── Hybrid blend ─────────────────────────────────────────────────
            # X(t+1) = (1 - λ)*X_GWO + λ*X_PSO
            X_new[i] = (1 - LAMBDA) * X_GWO + LAMBDA * X_PSO

        X = _clip(X_new)

        # ── Update shared state (read by polling endpoint) ───────────────────
        convergence_curve.append(float(gbest_fit))
        state["convergence"]      = convergence_curve.copy()
        state["all_accuracies"]  += iter_accuracies
        state["best_accuracy"]    = float(gbest_fit)
        state["iteration"]        = iteration + 1
        state["progress"]         = int(((iteration + 1) / n_iter) * 100)
        state["elapsed_seconds"]  = round(time.time() - t_start, 1)

    # ── Generate figures ──────────────────────────────────────────────────────
    from app.utils.plotter import save_convergence, save_boxplot
    conv_path = save_convergence(run_id, convergence_curve)
    box_path  = save_boxplot(run_id, state["all_accuracies"])

    state["figures"]["convergence"] = f"/figures/{run_id}_convergence.png"
    state["figures"]["boxplot"]     = f"/figures/{run_id}_boxplot.png"
    state["status"]                 = "completed"
    state["elapsed_seconds"]        = round(time.time() - t_start, 1)
