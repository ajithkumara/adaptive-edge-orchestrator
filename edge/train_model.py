"""
train_model.py — AdaptiveOrchestrator Sprint 4
Trains Isolation Forest on CWRU normal data only (70% train split).
Saves model to /app/config/isolation_forest.pkl
Saves training report to /logs/sprint4_training_report.json
"""
import json, pickle, time
from pathlib import Path
from datetime import datetime, timezone
import numpy as np
import scipy.io
from sklearn.ensemble import IsolationForest
from sklearn.metrics import f1_score, precision_score, recall_score

RANDOM_STATE = 42
WINDOW_SIZE  = 1024
TRAIN_SPLIT  = 0.70
DATA_DIR     = Path("/app/data/cwru")

FILE_LABELS = {
    "normal_0hp.mat":     "normal",
    "normal_1hp.mat":     "normal",
    "ball_0hp.mat":       "ball",
    "ball_1hp.mat":       "ball",
    "inner_race_0hp.mat": "inner_race",
    "inner_race_1hp.mat": "inner_race",
    "outer_race_0hp.mat": "outer_race",
    "outer_race_1hp.mat": "outer_race",
}

def load_signal(path):
    mat = scipy.io.loadmat(str(path))
    for key in mat:
        if "DE_time" in key:
            return mat[key].flatten().astype(np.float32)
    for key in mat:
        if not key.startswith("_"):
            arr = np.array(mat[key]).flatten()
            if len(arr) > 1000:
                return arr.astype(np.float32)
    raise ValueError(f"No signal in {path.name}")

def extract_features(window):
    rms      = np.sqrt(np.mean(window ** 2))
    peak     = np.max(np.abs(window))
    crest    = peak / (rms + 1e-9)
    kurtosis = np.mean((window - window.mean()) ** 4) / (window.std() + 1e-9) ** 4
    skew     = np.mean((window - window.mean()) ** 3) / (window.std() + 1e-9) ** 3
    variance = np.var(window)
    mean_abs = np.mean(np.abs(window))
    return [rms, peak, crest, kurtosis, skew, variance, mean_abs]

def windows_from_file(path):
    signal = load_signal(path)
    n = len(signal) // WINDOW_SIZE
    return np.array([
        extract_features(signal[i*WINDOW_SIZE:(i+1)*WINDOW_SIZE])
        for i in range(n)
    ])

print("=" * 55)
print("  AdaptiveOrchestrator — Isolation Forest Training")
print("  Sprint 4 — S4-T3")
print("=" * 55)

# ── Load all data ─────────────────────────────────────────────
print("\n[1/4] Loading CWRU windows...")
X_normal, X_fault = [], []
fault_labels = []

for fname, label in FILE_LABELS.items():
    fpath = DATA_DIR / fname
    print(f"  {fname} ({label})...", end=" ")
    windows = windows_from_file(fpath)
    print(f"{len(windows)} windows")
    if label == "normal":
        X_normal.append(windows)
    else:
        X_fault.append(windows)
        fault_labels.extend([label] * len(windows))

X_normal = np.vstack(X_normal)
X_fault  = np.vstack(X_fault)
print(f"\n  Normal windows : {len(X_normal)}")
print(f"  Fault windows  : {len(X_fault)}")

# ── Train / test split ────────────────────────────────────────
print(f"\n[2/4] Splitting — {int(TRAIN_SPLIT*100)}% train / {int((1-TRAIN_SPLIT)*100)}% test...")
np.random.seed(RANDOM_STATE)
idx           = np.random.permutation(len(X_normal))
split         = int(len(X_normal) * TRAIN_SPLIT)
X_train       = X_normal[idx[:split]]
X_normal_test = X_normal[idx[split:]]

print(f"  Train (normal only) : {len(X_train)} windows")
print(f"  Test  (normal)      : {len(X_normal_test)} windows")
print(f"  Test  (fault)       : {len(X_fault)} windows")

# ── Train model ───────────────────────────────────────────────
print(f"\n[3/4] Training Isolation Forest...")
print(f"  contamination=0.1  n_estimators=100  random_state={RANDOM_STATE}")
t0 = time.time()
model = IsolationForest(
    n_estimators=100,
    contamination=0.1,
    random_state=RANDOM_STATE,
    n_jobs=-1
)
model.fit(X_train)
train_time = time.time() - t0
print(f"  Training time: {train_time:.2f}s")

# ── Evaluate ──────────────────────────────────────────────────
print(f"\n[4/4] Evaluating on test set...")
y_true    = np.array([0] * len(X_normal_test) + [1] * len(X_fault))
X_test    = np.vstack([X_normal_test, X_fault])
preds_raw = model.predict(X_test)
y_pred    = (preds_raw == -1).astype(int)

precision = precision_score(y_true, y_pred, zero_division=0)
recall    = recall_score(y_true, y_pred, zero_division=0)
f1        = f1_score(y_true, y_pred, zero_division=0)

tp = int(np.sum((y_true == 1) & (y_pred == 1)))
tn = int(np.sum((y_true == 0) & (y_pred == 0)))
fp = int(np.sum((y_true == 0) & (y_pred == 1)))
fn = int(np.sum((y_true == 1) & (y_pred == 0)))

print(f"\n  {'Metric':<12} {'Value':>8}")
print(f"  {'-'*22}")
print(f"  {'Precision':<12} {precision:>8.4f}")
print(f"  {'Recall':<12} {recall:>8.4f}")
print(f"  {'F1 Score':<12} {f1:>8.4f}  {'✔ PASS' if f1 >= 0.80 else '✗ BELOW TARGET'}")
print(f"\n  Confusion Matrix:")
print(f"  TP={tp}  TN={tn}  FP={fp}  FN={fn}")

# ── Save model ────────────────────────────────────────────────
model_path = Path("/app/config/isolation_forest.pkl")
with open(model_path, "wb") as f:
    pickle.dump(model, f)
print(f"\n  Model saved → {model_path}")

# ── Save report ───────────────────────────────────────────────
report = {
    "sprint": "S4-T3",
    "trained_at": datetime.now(timezone.utc).isoformat(),
    "model": "IsolationForest",
    "params": {"n_estimators": 100, "contamination": 0.1, "random_state": RANDOM_STATE},
    "data": {
        "train_windows": len(X_train),
        "test_normal":   len(X_normal_test),
        "test_fault":    len(X_fault),
        "train_split":   TRAIN_SPLIT,
        "features":      ["rms","peak","crest","kurtosis","skew","variance","mean_abs"],
    },
    "results": {
        "precision": round(precision, 4),
        "recall":    round(recall, 4),
        "f1":        round(f1, 4),
        "tp": tp, "tn": tn, "fp": fp, "fn": fn,
        "train_time_s": round(train_time, 2),
        "target_met": f1 >= 0.80,
    }
}

report_path = Path("/logs/sprint4_training_report.json")
with open(report_path, "w") as f:
    json.dump(report, f, indent=2)
print(f"  Report saved → {report_path}")

print("\n" + "=" * 55)
print(f"  F1 = {f1:.4f}  |  Target >= 0.80  |  {'✔ S4-T3 PASS' if f1 >= 0.80 else '✗ NEEDS TUNING'}")
print("=" * 55)
