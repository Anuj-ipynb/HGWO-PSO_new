"""
hgwo_pso.py — Hybrid Grey Wolf Optimizer + Particle Swarm Optimization.
"""

import numpy as np
from app.optimizers.cnn_trainer import evaluate_candidate
from app.services.run_store import run_store
from app.utils.plotter import (
    save_convergence,
    save_boxplot,
    save_comparison,
    save_loss_curve
)

BOUNDS_LOW = np.array([1e-5, 16, 0.1, 32, 32, 32, 128])
BOUNDS_HIGH = np.array([1e-2, 128, 0.5, 96, 96, 96, 384])

DIM = 7

LAMBDA = 0.5
W = 0.5
C1 = 1.5
C2 = 1.5


def _clip(X):
    return np.clip(X, BOUNDS_LOW, BOUNDS_HIGH)


def _decode(x):
    return {
        "lr": float(x[0]),
        "batch_size": int(np.round(x[1])),
        "dropout": float(x[2]),
        "filters1": int(np.round(x[3])),
        "filters2": int(np.round(x[4])),
        "filters3": int(np.round(x[5])),
        "dense_units": int(np.round(x[6])),
    }


def run_hgwo_pso(run_id, config):
    state = run_store[run_id]
    state["status"] = "running"

    n_pop = config["population"]
    n_iter = config["iterations"]
    epochs = config["epochs"]

    rng = np.random.default_rng(42)

    X = rng.uniform(BOUNDS_LOW, BOUNDS_HIGH, (n_pop, DIM))
    V = np.zeros_like(X)

    gbest = X[0].copy()
    gbest_fit = -1

    convergence = []

    # 🔁 OPTIMIZATION LOOP
    for it in range(n_iter):
        fitness = np.zeros(n_pop)

        for i in range(n_pop):
            hp = _decode(X[i])
            acc = evaluate_candidate(hp, epochs)
            fitness[i] = acc

        # 🐺 GWO hierarchy
        idx = np.argsort(-fitness)
        alpha = X[idx[0]]
        beta  = X[idx[1]]
        delta = X[idx[2]]

        # 🌍 Global best update
        if fitness[idx[0]] > gbest_fit:
            gbest_fit = fitness[idx[0]]
            gbest = alpha.copy()

        # 🔄 Position update (Hybrid PSO + GWO)
        for i in range(n_pop):
            r1, r2 = rng.random(DIM), rng.random(DIM)

            # PSO velocity
            V[i] = W * V[i] + C1 * r1 * (gbest - X[i]) + C2 * r2 * (gbest - X[i])

            # GWO position
            X_gwo = (alpha + beta + delta) / 3

            # Hybrid update
            X[i] = (1 - LAMBDA) * X_gwo + LAMBDA * (X[i] + V[i])

        X = _clip(X)

        convergence.append(float(gbest_fit))

        # 🔄 Update state for UI
        state["best_accuracy"] = float(gbest_fit)
        state["best_params"] = _decode(gbest)
        state["convergence"] = convergence
        state["iteration"] = it + 1
        state["progress"] = int((it + 1) / n_iter * 100)

    # 🔥 FINAL TRAINING
    best_hp = _decode(gbest)
    final_acc = evaluate_candidate(best_hp, epochs=30)

    # 📊 GENERATE PLOTS
    conv_path = save_convergence(run_id, convergence)
    box_path = save_boxplot(run_id, convergence)
    comp_path = save_comparison(run_id, gbest_fit, final_acc)
    loss_path = save_loss_curve(run_id)

    # 🔥 FINAL STATE UPDATE
    state["best_accuracy"] = float(final_acc)
    state["best_params"] = best_hp
    state["convergence"].append(float(final_acc))

    state["figures"] = {
        "convergence": conv_path,
        "boxplot": box_path,
        "comparison": comp_path,
        "loss": loss_path
    }

    state["status"] = "completed"