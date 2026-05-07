from app.optimizers.cnn_trainer import evaluate_candidate
from app.services.run_store import run_store

best_hp = {
    "lr": 0.0036,
    "batch_size": 32,
    "dropout": 0.29,
    "filters1": 32,
    "filters2": 96,
    "filters3": 64,
    "dense_units": 304
}

# 🔥 FIRST: RUN TRAINING
acc = evaluate_candidate(best_hp, epochs=30)

print("🔥 FINAL ACCURACY:", acc)

# 🔥 THEN: STORE RESULT
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

print("Run ID:", run_id)