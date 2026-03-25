"""
cnn_trainer.py — Builds and evaluates a CNN with given hyperparameters.

CUDA ACCELERATION EXPLAINED
────────────────────────────
• device = torch.device("cuda") when a GPU is available.
• model.to(device)     → model weights live in GPU VRAM.
• x.to(device)         → input tensors transferred to GPU via PCIe.
• torch.amp.autocast() → mixed precision (FP16) for Conv2d / Linear ops —
                          halves VRAM usage and doubles throughput on GTX 1050 Ti.
• GradScaler           → prevents FP16 underflow during backward pass.
• torch.cuda.empty_cache() → releases GPU memory back to CUDA allocator
                              after each candidate, preventing OOM on
                              4 GB VRAM cards.

WHY CUDA SPEEDS THIS UP
────────────────────────
A Conv2d on 32×32 images with 64 filters involves millions of MACs per batch.
A GPU executes these in parallel across thousands of CUDA cores; a CPU
would serialise them over 1–8 cores.  Even a GTX 1050 Ti delivers ~2 TFLOPS
vs ~0.1 TFLOPS for a modern laptop CPU — ~20× faster for convolutions.

CPU CONTROL
────────────
torch.set_num_threads(1) prevents PyTorch from spawning worker threads that
would compete with FastAPI's event loop thread.  DataLoader num_workers=0
avoids subprocess overhead on a constrained machine.
"""

import torch
import torch.nn as nn
import torch.optim as optim
from torch.cuda.amp import GradScaler
from torchvision import datasets, transforms
from torch.utils.data import DataLoader, Subset
import numpy as np

# ── CPU constraint ────────────────────────────────────────────────────────────
torch.set_num_threads(1)

# ── Device selection ──────────────────────────────────────────────────────────
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# ── Dataset (loaded once, shared across all evaluations) ─────────────────────
_DATASET_SIZE = 2000   # subset keeps training fast on constrained hardware

# CIFAR-10: 32×32 RGB images, 10 classes (airplane, car, bird, cat, ...)
# Normalize with CIFAR-10 per-channel mean/std (pre-computed from full train set)
_transform = transforms.Compose([
    transforms.ToTensor(),
    transforms.Normalize(
        mean=(0.4914, 0.4822, 0.4465),   # CIFAR-10 RGB channel means
        std =(0.2470, 0.2435, 0.2616),   # CIFAR-10 RGB channel stds
    ),
])

# Download on first call; cached thereafter (~170 MB)
_full_train = datasets.CIFAR10(root="./data", train=True,  download=True, transform=_transform)
_full_val   = datasets.CIFAR10(root="./data", train=False, download=True, transform=_transform)

# Fixed subset indices so every candidate is evaluated on the same split
_rng_idx  = np.random.default_rng(seed=0)
_train_idx = _rng_idx.choice(len(_full_train), size=_DATASET_SIZE, replace=False)
_val_idx   = _rng_idx.choice(len(_full_val),   size=500,           replace=False)

_train_subset = Subset(_full_train, _train_idx)
_val_subset   = Subset(_full_val,   _val_idx)


# ── Model definition ──────────────────────────────────────────────────────────
class CandidateCNN(nn.Module):
    """
    Three-block CNN with configurable filter counts and a dense head.
    Architecture scales with the hyperparameters supplied by HGWO-PSO.
    """

    def __init__(self, filters1: int, filters2: int, filters3: int,
                 dense_units: int, dropout: float, num_classes: int = 10):
        super().__init__()

        self.features = nn.Sequential(
            # Block 1 — runs on GPU; each Conv2d is a batched matrix multiply
            # CIFAR-10 images are 32×32 RGB → in_channels=3
            nn.Conv2d(3, filters1, kernel_size=3, padding=1),
            nn.BatchNorm2d(filters1),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2),          # 32×32 → 16×16

            # Block 2
            nn.Conv2d(filters1, filters2, kernel_size=3, padding=1),
            nn.BatchNorm2d(filters2),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2),          # 16×16 → 8×8

            # Block 3
            nn.Conv2d(filters2, filters3, kernel_size=3, padding=1),
            nn.BatchNorm2d(filters3),
            nn.ReLU(inplace=True),
            nn.AdaptiveAvgPool2d((4, 4)),  # → 4×4 feature map (stable output size)
        )

        self.classifier = nn.Sequential(
            nn.Flatten(),
            nn.Linear(filters3 * 16, dense_units),
            nn.ReLU(inplace=True),
            nn.Dropout(p=dropout),
            nn.Linear(dense_units, num_classes),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = self.features(x)
        return self.classifier(x)


# ── Evaluation function ───────────────────────────────────────────────────────
def evaluate_candidate(hp: dict, epochs: int = 2) -> float:
    """
    Train a CandidateCNN with the given hyperparameters and return
    validation accuracy (0.0 – 1.0).

    All tensor operations run on `device` (CUDA when available).
    GPU memory is freed after this function returns.
    """

    # Build DataLoaders — num_workers=0 avoids subprocess spawning
    train_loader = DataLoader(
        _train_subset,
        batch_size=hp["batch_size"],
        shuffle=True,
        num_workers=0,
        pin_memory=(device.type == "cuda"),  # speeds up CPU→GPU transfers
    )
    val_loader = DataLoader(
        _val_subset,
        batch_size=64,
        shuffle=False,
        num_workers=0,
        pin_memory=(device.type == "cuda"),
    )

    # Instantiate model and move weights to GPU VRAM
    model = CandidateCNN(
        filters1=hp["filters1"],
        filters2=hp["filters2"],
        filters3=hp["filters3"],
        dense_units=hp["dense_units"],
        dropout=hp["dropout"],
    ).to(device)   # ← model lives on GPU from here on

    optimizer = optim.Adam(model.parameters(), lr=hp["lr"])
    criterion = nn.CrossEntropyLoss()

    # GradScaler for mixed-precision training (prevents FP16 underflow)
    scaler = GradScaler(enabled=(device.type == "cuda"))

    # ── Training loop ─────────────────────────────────────────────────────────
    model.train()
    for epoch in range(epochs):
        for x_batch, y_batch in train_loader:
            # Transfer batch to GPU — happens over PCIe bus
            x_batch = x_batch.to(device, non_blocking=True)
            y_batch = y_batch.to(device, non_blocking=True)

            optimizer.zero_grad()

            # autocast → Conv2d/Linear run in FP16 on GPU (2× faster, ½ VRAM)
            with torch.amp.autocast(device_type=device.type,
                                     enabled=(device.type == "cuda")):
                logits = model(x_batch)          # forward pass on GPU
                loss   = criterion(logits, y_batch)

            scaler.scale(loss).backward()        # scaled backward on GPU
            scaler.step(optimizer)
            scaler.update()

    # ── Validation loop ───────────────────────────────────────────────────────
    model.eval()
    correct = 0
    total   = 0

    with torch.no_grad():
        for x_batch, y_batch in val_loader:
            x_batch = x_batch.to(device, non_blocking=True)
            y_batch = y_batch.to(device, non_blocking=True)

            with torch.amp.autocast(device_type=device.type,
                                     enabled=(device.type == "cuda")):
                logits = model(x_batch)

            preds    = logits.argmax(dim=1)
            correct += (preds == y_batch).sum().item()
            total   += y_batch.size(0)

    accuracy = correct / total if total > 0 else 0.0

    # ── GPU memory cleanup ────────────────────────────────────────────────────
    # Explicitly delete tensors and model to release GPU VRAM allocations.
    # Critical on 4 GB VRAM cards to prevent OOM on next candidate.
    del model, optimizer, scaler
    if device.type == "cuda":
        torch.cuda.empty_cache()

    return accuracy
