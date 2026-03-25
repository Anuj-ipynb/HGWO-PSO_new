"""
plotter.py — Generates and saves matplotlib figures to static/figures/.
Dark-themed charts to match the futuristic UI.
"""

import os
import matplotlib
matplotlib.use("Agg")          # Non-interactive backend — safe for server use
import matplotlib.pyplot as plt
import numpy as np

FIGURES_DIR = "static/figures"
os.makedirs(FIGURES_DIR, exist_ok=True)

DARK_BG    = "#0B0F14"
CARD_BG    = "#111827"
NEON_CYAN  = "#00E5FF"
PURPLE     = "#7C3AED"
TEXT_COLOR = "#E5E7EB"
GRID_COLOR = "#1F2937"


def _apply_dark_style(fig, ax):
    fig.patch.set_facecolor(DARK_BG)
    ax.set_facecolor(CARD_BG)
    ax.tick_params(colors=TEXT_COLOR, labelsize=9)
    ax.xaxis.label.set_color(TEXT_COLOR)
    ax.yaxis.label.set_color(TEXT_COLOR)
    ax.title.set_color(TEXT_COLOR)
    ax.grid(True, color=GRID_COLOR, linewidth=0.6)
    for spine in ax.spines.values():
        spine.set_edgecolor(GRID_COLOR)


def save_convergence(run_id: str, convergence: list) -> str:
    path = os.path.join(FIGURES_DIR, f"{run_id}_convergence.png")
    fig, ax = plt.subplots(figsize=(7, 3.5), dpi=110)
    _apply_dark_style(fig, ax)

    iters = list(range(1, len(convergence) + 1))
    ax.plot(iters, convergence, color=NEON_CYAN, linewidth=2.2, marker="o",
            markersize=4, markerfacecolor=PURPLE)
    ax.fill_between(iters, convergence, alpha=0.12, color=NEON_CYAN)
    ax.set_xlabel("Iteration", fontsize=10)
    ax.set_ylabel("Best Accuracy", fontsize=10)
    ax.set_title("HGWO-PSO Convergence Curve", fontsize=12, pad=10)
    ax.set_ylim(0, 1)
    fig.tight_layout()
    fig.savefig(path, dpi=110, bbox_inches="tight", facecolor=DARK_BG)
    plt.close(fig)
    return path


def save_boxplot(run_id: str, all_accuracies: list) -> str:
    path = os.path.join(FIGURES_DIR, f"{run_id}_boxplot.png")
    fig, ax = plt.subplots(figsize=(5, 3.5), dpi=110)
    _apply_dark_style(fig, ax)

    bp = ax.boxplot(
        all_accuracies,
        patch_artist=True,
        medianprops=dict(color=NEON_CYAN, linewidth=2),
        boxprops=dict(facecolor=CARD_BG, color=PURPLE),
        whiskerprops=dict(color=PURPLE),
        capprops=dict(color=PURPLE),
        flierprops=dict(marker="o", color=PURPLE, markersize=4),
    )
    ax.set_ylabel("Accuracy", fontsize=10)
    ax.set_title("Accuracy Distribution (all evaluations)", fontsize=11, pad=10)
    ax.set_xticklabels(["All Candidates"])
    fig.tight_layout()
    fig.savefig(path, dpi=110, bbox_inches="tight", facecolor=DARK_BG)
    plt.close(fig)
    return path
