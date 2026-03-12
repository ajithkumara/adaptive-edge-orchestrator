"""
inference_engine.py — AdaptiveOrchestrator Sprint 4
Subscribes to sensors.bearing via NATS.
Loads Isolation Forest model from config/isolation_forest.pkl
Runs inference on each event and logs results to logs/inference.jsonl
"""
import asyncio, json, pickle, time, logging
from pathlib import Path
from datetime import datetime, timezone
import numpy as np

NATS_URL    = "nats://172.28.0.30:4222"
SUBJECT     = "sensors.bearing"
MODEL_PATH  = Path("/app/config/isolation_forest.pkl")
LOG_PATH    = Path("/logs/inference.jsonl")
CAL_PATH    = Path("/app/config/calibration.json")

# ── Logging ───────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [inference_engine] %(message)s",
    datefmt="%H:%M:%S"
)
log = logging.getLogger(__name__)

# ── Load calibration for current mode ─────────────────────────
def load_mode() -> str:
    try:
        cal = json.loads(CAL_PATH.read_text())
        return cal.get("current_mode", "UNKNOWN")
    except:
        return "UNKNOWN"

# ── Load model ────────────────────────────────────────────────
def load_model():
    if not MODEL_PATH.exists():
        raise FileNotFoundError(f"Model not found at {MODEL_PATH}. Run train_model.py first.")
    with open(MODEL_PATH, "rb") as f:
        model = pickle.load(f)
    log.info(f"Model loaded from {MODEL_PATH}")
    return model

# ── Feature extraction (must match train_model.py exactly) ────
def extract_features(feat_dict: dict) -> np.ndarray:
    return np.array([[
        feat_dict["rms"],
        feat_dict["peak"],
        feat_dict["crest"],
        feat_dict["kurtosis"],
        feat_dict["skew"],
        feat_dict["variance"],
        feat_dict["mean_abs"],
    ]])

# ── Stats tracker ─────────────────────────────────────────────
class Stats:
    def __init__(self):
        self.total     = 0
        self.anomalies = 0
        self.correct   = 0   # prediction matches ground truth
        self.t0        = time.time()

    def update(self, predicted_anomaly: bool, true_label: str):
        self.total += 1
        is_fault = true_label != "normal"
        if predicted_anomaly:
            self.anomalies += 1
        if predicted_anomaly == is_fault:
            self.correct += 1

    def accuracy(self):
        return self.correct / self.total if self.total > 0 else 0

    def elapsed(self):
        return time.time() - self.t0

async def run():
    import nats

    model = load_model()
    stats = Stats()
    log_file = open(LOG_PATH, "a")

    log.info(f"Connecting to NATS at {NATS_URL}...")
    nc = await nats.connect(NATS_URL)
    log.info(f"Subscribed to {SUBJECT}")
    log.info("Inference engine running. Ctrl+C to stop.\n")

    async def handler(msg):
        t_recv = time.monotonic()
        try:
            event = json.loads(msg.data)
        except Exception as e:
            log.warning(f"Bad message: {e}")
            return

        # ── Run inference ──────────────────────────────────────
        features   = extract_features(event["features"])
        raw_pred   = model.predict(features)[0]   # 1=normal -1=anomaly
        score      = model.score_samples(features)[0]
        is_anomaly = bool(raw_pred == -1)
        t_infer    = (time.monotonic() - t_recv) * 1000  # ms

        true_label = event.get("label", "unknown")
        stats.update(is_anomaly, true_label)

        # ── Build result ───────────────────────────────────────
        result = {
            "ts":            datetime.now(timezone.utc).isoformat(),
            "seq":           event.get("seq"),
            "sensor_id":     event.get("sensor_id"),
            "label":         true_label,
            "anomaly":       is_anomaly,
            "anomaly_score": round(float(score), 6),
            "infer_ms":      round(t_infer, 3),
            "mode":          load_mode(),
            "stats": {
                "total":     stats.total,
                "anomalies": stats.anomalies,
                "accuracy":  round(stats.accuracy(), 4),
                "elapsed_s": round(stats.elapsed(), 1),
            }
        }

        # ── Log to file ────────────────────────────────────────
        log_file.write(json.dumps(result) + "\n")
        log_file.flush()

        # ── Console output every 10 events ────────────────────
        if stats.total % 10 == 0:
            flag = "⚠ ANOMALY" if is_anomaly else "  normal "
            log.info(
                f"seq={event.get('seq'):>6}  {flag}  "
                f"label={true_label:<12}  "
                f"score={score:>8.4f}  "
                f"infer={t_infer:.1f}ms  "
                f"acc={stats.accuracy():.3f}  "
                f"total={stats.total}"
            )

    await nc.subscribe(SUBJECT, cb=handler)

    try:
        while True:
            await asyncio.sleep(1)
    except asyncio.CancelledError:
        pass
    finally:
        log_file.close()
        await nc.close()
        log.info(f"\nStopped. Total={stats.total}  "
                 f"Anomalies={stats.anomalies}  "
                 f"Accuracy={stats.accuracy():.4f}")

if __name__ == "__main__":
    asyncio.run(run())
