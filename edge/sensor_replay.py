"""
sensor_replay.py — AdaptiveOrchestrator Sprint 4
Replays CWRU bearing dataset at configurable Hz via NATS.
Publishes to subject: sensors.bearing
Includes ground truth fault labels for F1 evaluation.
"""
import asyncio, json, time
from pathlib import Path
from datetime import datetime, timezone
import numpy as np
import scipy.io

NATS_URL     = "nats://172.28.0.30:4222"
SUBJECT      = "sensors.bearing"
REPLAY_HZ    = 10
WINDOW_SIZE  = 1024
RANDOM_STATE = 42
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

def load_cwru_signal(path: Path) -> np.ndarray:
    mat = scipy.io.loadmat(str(path))
    for key in mat:
        if "DE_time" in key:
            return mat[key].flatten().astype(np.float32)
    for key in mat:
        if not key.startswith("_"):
            arr = np.array(mat[key]).flatten()
            if len(arr) > 1000:
                return arr.astype(np.float32)
    raise ValueError(f"No signal found in {path.name}")

def extract_features(window: np.ndarray) -> dict:
    rms      = float(np.sqrt(np.mean(window ** 2)))
    peak     = float(np.max(np.abs(window)))
    crest    = peak / (rms + 1e-9)
    kurtosis = float(np.mean((window - window.mean()) ** 4) / (window.std() + 1e-9) ** 4)
    skew     = float(np.mean((window - window.mean()) ** 3) / (window.std() + 1e-9) ** 3)
    variance = float(np.var(window))
    mean_abs = float(np.mean(np.abs(window)))
    return {
        "rms":      round(rms, 6),
        "peak":     round(peak, 6),
        "crest":    round(crest, 6),
        "kurtosis": round(kurtosis, 6),
        "skew":     round(skew, 6),
        "variance": round(variance, 6),
        "mean_abs": round(mean_abs, 6),
    }

async def replay(hz: int = REPLAY_HZ, once: bool = False):
    import nats
    print(f"[sensor_replay] Connecting to NATS at {NATS_URL}...")
    nc = await nats.connect(NATS_URL)
    print(f"[sensor_replay] Connected. Replaying at {hz} Hz → {SUBJECT}")
    print(f"[sensor_replay] Window size: {WINDOW_SIZE} samples per event\n")

    interval  = 1.0 / hz
    seq       = 0
    file_list = sorted(FILE_LABELS.keys())
    np.random.seed(RANDOM_STATE)

    try:
        iterations = 1 if once else 999999
        for _ in range(iterations):
            for fname in file_list:
                fpath = DATA_DIR / fname
                if not fpath.exists():
                    print(f"[WARN] Missing: {fname} — skipping")
                    continue

                label     = FILE_LABELS[fname]
                signal    = load_cwru_signal(fpath)
                n_windows = len(signal) // WINDOW_SIZE

                print(f"[sensor_replay] Playing {fname} ({label}) — {n_windows} windows")

                for i in range(n_windows):
                    t0     = time.monotonic()
                    window = signal[i * WINDOW_SIZE:(i + 1) * WINDOW_SIZE]
                    feats  = extract_features(window)

                    event = {
                        "ts":         datetime.now(timezone.utc).isoformat(),
                        "seq":        seq,
                        "sensor_id":  "bearing.DE",
                        "file":       fname,
                        "label":      label,
                        "window_idx": i,
                        "features":   feats,
                    }

                    await nc.publish(SUBJECT, json.dumps(event).encode())

                    if seq % (hz * 10) == 0:
                        print(f"  [{datetime.now().strftime('%H:%M:%S')}] "
                              f"seq={seq:>6}  label={label:<12}  "
                              f"rms={feats['rms']:.4f}  kurtosis={feats['kurtosis']:.2f}")

                    seq += 1
                    elapsed = time.monotonic() - t0
                    await asyncio.sleep(max(0, interval - elapsed))

    except asyncio.CancelledError:
        pass
    finally:
        await nc.close()
        print(f"\n[sensor_replay] Stopped. Total events published: {seq}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--hz",   type=int,  default=REPLAY_HZ)
    parser.add_argument("--once", action="store_true",
                        help="Replay each file once then exit")
    args = parser.parse_args()
    asyncio.run(replay(args.hz, args.once))
