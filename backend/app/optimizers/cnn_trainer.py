import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import datasets, transforms
from torch.utils.data import DataLoader, Subset
import numpy as np

torch.backends.cudnn.benchmark = True

# ── Device ─────────────────────────────────────────
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# ── Data Augmentation ──────────────────────────────
_transform_train = transforms.Compose([
    transforms.RandomHorizontalFlip(),
    transforms.RandomCrop(32, padding=4),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=(0.4914, 0.4822, 0.4465),
        std =(0.2470, 0.2435, 0.2616),
    ),
])

_transform_val = transforms.Compose([
    transforms.ToTensor(),
    transforms.Normalize(
        mean=(0.4914, 0.4822, 0.4465),
        std =(0.2470, 0.2435, 0.2616),
    ),
])

# ── DATA ───────────────────────────────────────────
full_train = datasets.CIFAR10(root="./data", train=True, download=True, transform=_transform_train)
full_val   = datasets.CIFAR10(root="./data", train=False, download=True, transform=_transform_val)

train_dataset = Subset(full_train, range(20000))
val_dataset   = Subset(full_val, range(5000))

# ── MODEL ──────────────────────────────────────────
class CandidateCNN(nn.Module):
    def __init__(self, f1, f2, f3, dense, dropout):
        super().__init__()

        self.features = nn.Sequential(
            nn.Conv2d(3, f1, 3, padding=1),
            nn.BatchNorm2d(f1),
            nn.ReLU(),
            nn.MaxPool2d(2),

            nn.Conv2d(f1, f2, 3, padding=1),
            nn.BatchNorm2d(f2),
            nn.ReLU(),
            nn.MaxPool2d(2),

            nn.Conv2d(f2, f3, 3, padding=1),
            nn.BatchNorm2d(f3),
            nn.ReLU(),
            nn.AdaptiveAvgPool2d((4, 4)),
        )

        self.classifier = nn.Sequential(
            nn.Flatten(),
            nn.Linear(f3 * 16, dense),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(dense, 10),
        )

    def forward(self, x):
        x = self.features(x)
        return self.classifier(x)


# ── TRAIN + EVAL ───────────────────────────────────
def evaluate_candidate(hp: dict, epochs: int) -> float:

    FAST_EPOCHS = epochs
    hp["batch_size"] = max(16, min(128, int(hp["batch_size"])))

    train_loader = DataLoader(
        train_dataset,
        batch_size=hp["batch_size"],
        shuffle=True,
        num_workers=0,
        pin_memory=True,
    )

    val_loader = DataLoader(
        val_dataset,
        batch_size=128,
        shuffle=False,
        num_workers=0,
        pin_memory=True,
    )

    model = CandidateCNN(
        hp["filters1"],
        hp["filters2"],
        hp["filters3"],
        hp["dense_units"],
        hp["dropout"]
    ).to(device)

    optimizer = optim.Adam(model.parameters(), lr=hp["lr"])
    scheduler = optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=FAST_EPOCHS)
    criterion = nn.CrossEntropyLoss()

    # 🔥 SAFE AMP SETUP
    use_cuda = torch.cuda.is_available()
    scaler = torch.amp.GradScaler("cuda") if use_cuda else None

    # ── TRAIN ─────────────────────────────
    model.train()
    for _ in range(FAST_EPOCHS):
        for x, y in train_loader:
            x, y = x.to(device), y.to(device)

            optimizer.zero_grad()

            if use_cuda:
                with torch.amp.autocast("cuda"):
                    out = model(x)
                    loss = criterion(out, y)
                    loss = loss + 1e-6

                scaler.scale(loss).backward()
                scaler.step(optimizer)
                scaler.update()

            else:
                out = model(x)
                loss = criterion(out, y)
                loss = loss + 1e-6
                loss.backward()
                optimizer.step()

        scheduler.step()

    # ── VALIDATE ─────────────────────────
    model.eval()
    correct, total = 0, 0

    with torch.no_grad():
        for x, y in val_loader:
            x, y = x.to(device), y.to(device)

            if use_cuda:
                with torch.amp.autocast("cuda"):
                    out = model(x)
            else:
                out = model(x)

            pred = out.argmax(1)
            correct += (pred == y).sum().item()
            total += y.size(0)

    acc = correct / total

    # cleanup
    del model
    torch.cuda.empty_cache()

    return acc