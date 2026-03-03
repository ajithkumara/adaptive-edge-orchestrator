"""
context_monitor.py — AdaptiveOrchestrator Sprint 2
Measures RTT and CPU every 500ms, decides operational mode,
writes structured JSONL logs as thesis evidence.
"""

import asyncio
import json
import os
import subprocess
import time
from datetime import datetime, timezone

import psutil

# ── Configuration ─────────────────────────────────────────────
CLOUD_HOST        = "cloud_node"
SAMPLE_INTERVAL_S = 0.5
LATENCY_THRESHOLD = 500.0   # ms — above this → EDGE_ONLY
CPU_THRESHOLD     = 80.0    # %  — above this → EDGE_ONLY
HYSTERESIS_COUNT  = 3       # consecutive breaches before switching
LOG_PATH          = "/logs/context_monitor.jsonl"

MODE_CLOUD      = "CLOUD_OPTIMISED"
MODE_EDGE       = "EDGE_ONLY"
MODE_AUTONOMOUS = "EDGE_AUTONOMOUS"

os.makedirs("/logs", exist_ok=True)

# ── Measurement ───────────────────────────────────────────────
def measure_rtt_ms(host: str) -> float:
    try:
        result = subprocess.run(
            ["ping", "-c", "1", "-W", "2", host],
            capture_output=True, text=True, timeout=3
        )
        for line in result.stdout.split("\n"):
            if "time=" in line:
                return float(line.split("time=")[1].split(" ")[0])
        return -1.0
    except Exception:
        return -1.0

def measure_cpu_pct() -> float:
    return psutil.cpu_percent(interval=None)

# ── Mode decision ─────────────────────────────────────────────
def decide_mode(rtt_ms: float, cpu_pct: float) -> str:
    if rtt_ms < 0:
        return MODE_AUTONOMOUS
    if rtt_ms > LATENCY_THRESHOLD or cpu_pct > CPU_THRESHOLD:
        return MODE_EDGE
    return MODE_CLOUD

# ── Output ────────────────────────────────────────────────────
def write_log(entry: dict):
    with open(LOG_PATH, "a") as f:
        f.write(json.dumps(entry) + "\n")

def print_status(e: dict):
    rtt = f"{e['rtt_ms']:.1f}ms" if e['rtt_ms'] >= 0 else "UNREACHABLE"
    breach = ""
    if e['latency_breach']: breach += "  ⚠ LATENCY"
    if e['cpu_breach']:     breach += "  ⚠ CPU"
    print(f"[{e['ts'][11:19]}]  RTT={rtt:>12}  CPU={e['cpu_pct']:>5.1f}%  "
          f"mode={e['mode']:<20}{breach}")

# ── Main loop ─────────────────────────────────────────────────
async def run():
    print("=" * 62)
    print(" AdaptiveOrchestrator — Context Monitor  (Sprint 2)")
    print(f" Thresholds: latency>{LATENCY_THRESHOLD}ms | CPU>{CPU_THRESHOLD}%")
    print(f" Log: {LOG_PATH}")
    print("=" * 62)

    psutil.cpu_percent(interval=None)   # warm up
    await asyncio.sleep(0.5)

    current_mode  = MODE_CLOUD
    breach_count  = 0
    sample_number = 0

    while True:
        t0 = time.monotonic()

        rtt_ms  = measure_rtt_ms(CLOUD_HOST)
        cpu_pct = measure_cpu_pct()
        raw     = decide_mode(rtt_ms, cpu_pct)

        # hysteresis — prevent flapping on transient spikes
        if raw != MODE_CLOUD:
            breach_count += 1
        else:
            breach_count = 0

        if breach_count >= HYSTERESIS_COUNT or raw == MODE_CLOUD:
            if raw != current_mode:
                print(f"\n{'─'*62}")
                print(f"  *** MODE SWITCH: {current_mode} → {raw} ***")
                print(f"{'─'*62}\n")
            current_mode = raw

        entry = {
            "ts":              datetime.now(timezone.utc).isoformat(),
            "sample":          sample_number,
            "rtt_ms":          round(rtt_ms, 3),
            "cpu_pct":         round(cpu_pct, 1),
            "cloud_reachable": rtt_ms >= 0,
            "latency_breach":  rtt_ms > LATENCY_THRESHOLD,
            "cpu_breach":      cpu_pct > CPU_THRESHOLD,
            "mode":            current_mode,
            "breach_count":    breach_count,
        }
        write_log(entry)
        print_status(entry)

        sample_number += 1
        await asyncio.sleep(max(0, SAMPLE_INTERVAL_S - (time.monotonic() - t0)))

if __name__ == "__main__":
    asyncio.run(run())
