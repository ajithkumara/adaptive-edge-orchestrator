#!/usr/bin/env python3
"""
calibrate.py — Sprint 3: Adaptive Threshold Calibration
AdaptiveOrchestrator — MSc AI Thesis, University of Moratuwa

Runs a 5-minute baseline profiling phase, computes P95-based thresholds,
and saves the result to config/calibration.json.

Usage:
    python3 calibrate.py                        # default 5-minute profile
    python3 calibrate.py --duration 300         # explicit duration in seconds
    python3 calibrate.py --dry-run              # print thresholds, do not save

Outputs:
    config/calibration.json                     # loaded by context_monitor.py at startup

Algorithm:
    latency_threshold = max(LATENCY_FLOOR_MS,  P95_RTT  * LATENCY_MULTIPLIER)
    cpu_threshold     = max(CPU_FLOOR_PCT,      P95_CPU  * CPU_MULTIPLIER)

    LATENCY_FLOOR_MS  = 50.0   — prevents Docker LAN noise from triggering switches
    CPU_FLOOR_PCT     = 40.0   — reachable under real workload (R1 finding: 80% was not)
    LATENCY_MULTIPLIER = 2.0   — validated: 0 false positives in Sprint 3 stability test
    CPU_MULTIPLIER    = 2.5    — conservative buffer above P95 noise floor

Evidence:
    S3-T1 sweep (2026-03-08):
        Baseline P95 RTT = 0.16ms  →  max(50ms, 0.3ms) = 50.0ms
        Baseline P95 CPU = 5.3%    →  max(40%,  13.2%) = 40.0%
"""

import json
import os
import sys
import time
import argparse
import subprocess
import statistics
from datetime import datetime, timezone
from pathlib import Path

# ── Configuration ──────────────────────────────────────────────────────────
CLOUD_HOST          = "172.28.0.20"
SAMPLE_INTERVAL_S   = 0.5           # seconds between samples
DEFAULT_DURATION_S  = 300           # 5-minute profiling window
LATENCY_MULTIPLIER  = 2.0
CPU_MULTIPLIER      = 2.5
LATENCY_FLOOR_MS    = 50.0          # minimum meaningful latency threshold
CPU_FLOOR_PCT       = 40.0          # minimum meaningful CPU threshold
MIN_SAMPLES         = 100           # abort if fewer samples collected

# ── Output path ────────────────────────────────────────────────────────────
SCRIPT_DIR   = Path(__file__).parent
CONFIG_DIR   = SCRIPT_DIR.parent / "config"
OUTPUT_FILE  = CONFIG_DIR / "calibration.json"


# ── Measurement helpers ────────────────────────────────────────────────────
def measure_rtt(host: str) -> float:
    """
    Ping host once. Returns RTT in ms, or -1.0 if unreachable.
    """
    try:
        result = subprocess.run(
            ["ping", "-c", "1", "-W", "1", host],
            capture_output=True, text=True, timeout=2
        )
        if result.returncode != 0:
            return -1.0
        for line in result.stdout.split("\n"):
            if "time=" in line:
                return float(line.split("time=")[1].split(" ")[0])
        return -1.0
    except Exception:
        return -1.0


def measure_cpu() -> float:
    """
    Measure system-wide CPU usage via psutil.
    Returns percentage 0.0–100.0.
    """
    try:
        import psutil
        return psutil.cpu_percent(interval=0.5)
    except ImportError:
        print("[ERROR] psutil not installed. Run: pip install psutil")
        sys.exit(1)


def percentile(data: list, p: float) -> float:
    """
    Compute the p-th percentile of data (0–100).
    """
    if not data:
        return 0.0
    data = sorted(data)
    idx  = (len(data) - 1) * p / 100.0
    lo   = int(idx)
    hi   = min(lo + 1, len(data) - 1)
    return data[lo] + (data[hi] - data[lo]) * (idx - lo)


# ── Profiling loop ─────────────────────────────────────────────────────────
def run_profiling(duration_s: int) -> dict:
    """
    Collect RTT and CPU samples for duration_s seconds.
    Returns dict with raw samples and computed statistics.
    """
    rtt_samples = []
    cpu_samples = []

    start_time   = time.time()
    end_time     = start_time + duration_s
    sample_count = 0

    print(f"\n[calibrate] Profiling for {duration_s}s ({duration_s//60}m {duration_s%60}s)...")
    print(f"[calibrate] Target host: {CLOUD_HOST}")
    print(f"[calibrate] Sample interval: {SAMPLE_INTERVAL_S}s\n")
    print(f"{'Sample':>8}  {'RTT (ms)':>10}  {'CPU (%)':>8}  {'Elapsed':>8}")
    print("-" * 45)

    while time.time() < end_time:
        rtt = measure_rtt(CLOUD_HOST)
        cpu = measure_cpu()

        # Only include reachable RTT samples in statistics
        if rtt > 0:
            rtt_samples.append(rtt)

        cpu_samples.append(cpu)
        sample_count += 1
        elapsed = time.time() - start_time

        # Print progress every 30 samples
        if sample_count % 30 == 1 or sample_count <= 3:
            rtt_disp = f"{rtt:.2f}" if rtt > 0 else "UNREACHABLE"
            print(f"{sample_count:>8}  {rtt_disp:>10}  {cpu:>7.1f}%  {elapsed:>6.0f}s")

        time.sleep(max(0, SAMPLE_INTERVAL_S - (time.time() % SAMPLE_INTERVAL_S)))

    print(f"\n[calibrate] Profiling complete. {sample_count} total samples collected.")
    print(f"[calibrate] Reachable RTT samples: {len(rtt_samples)}")

    if len(rtt_samples) < MIN_SAMPLES:
        print(f"\n[ERROR] Too few reachable RTT samples ({len(rtt_samples)} < {MIN_SAMPLES}).")
        print("[ERROR] Check that cloud_node is running and reachable.")
        print(f"[ERROR] Test with: ping -c 3 {CLOUD_HOST}")
        sys.exit(1)

    return {
        "rtt_samples": rtt_samples,
        "cpu_samples": cpu_samples,
        "sample_count": sample_count,
        "reachable_count": len(rtt_samples),
        "duration_s": duration_s,
    }


# ── Threshold computation ──────────────────────────────────────────────────
def compute_thresholds(profile: dict) -> dict:
    """
    Compute P50/P95/P99 statistics and derive thresholds.
    """
    rtts = profile["rtt_samples"]
    cpus = profile["cpu_samples"]

    rtt_p50 = percentile(rtts, 50)
    rtt_p95 = percentile(rtts, 95)
    rtt_p99 = percentile(rtts, 99)
    rtt_max = max(rtts)

    cpu_p50 = percentile(cpus, 50)
    cpu_p95 = percentile(cpus, 95)
    cpu_p99 = percentile(cpus, 99)
    cpu_max = max(cpus)

    # Core algorithm: floor-bounded P95 multiplier
    raw_latency_threshold = rtt_p95 * LATENCY_MULTIPLIER
    raw_cpu_threshold     = cpu_p95 * CPU_MULTIPLIER

    latency_threshold = max(LATENCY_FLOOR_MS, raw_latency_threshold)
    cpu_threshold     = max(CPU_FLOOR_PCT,    raw_cpu_threshold)

    latency_floor_active = raw_latency_threshold < LATENCY_FLOOR_MS
    cpu_floor_active     = raw_cpu_threshold     < CPU_FLOOR_PCT

    return {
        "rtt_p50_ms":  round(rtt_p50, 3),
        "rtt_p95_ms":  round(rtt_p95, 3),
        "rtt_p99_ms":  round(rtt_p99, 3),
        "rtt_max_ms":  round(rtt_max, 3),
        "cpu_p50_pct": round(cpu_p50, 2),
        "cpu_p95_pct": round(cpu_p95, 2),
        "cpu_p99_pct": round(cpu_p99, 2),
        "cpu_max_pct": round(cpu_max, 2),
        "latency_multiplier":     LATENCY_MULTIPLIER,
        "cpu_multiplier":         CPU_MULTIPLIER,
        "latency_floor_ms":       LATENCY_FLOOR_MS,
        "cpu_floor_pct":          CPU_FLOOR_PCT,
        "latency_floor_active":   latency_floor_active,
        "cpu_floor_active":       cpu_floor_active,
        "latency_threshold_ms":   round(latency_threshold, 2),
        "cpu_threshold_pct":      round(cpu_threshold, 2),
    }


# ── Save / print ───────────────────────────────────────────────────────────
def build_output(profile: dict, thresholds: dict) -> dict:
    return {
        "calibrated_at":       datetime.now(timezone.utc).isoformat(),
        "environment_tag":     "docker-wsl2-dev",
        "cloud_host":          CLOUD_HOST,
        "profiling_duration_s": profile["duration_s"],
        "sample_count":        profile["sample_count"],
        "reachable_count":     profile["reachable_count"],
        "statistics":          thresholds,
        "thresholds": {
            "latency_ms":  thresholds["latency_threshold_ms"],
            "cpu_pct":     thresholds["cpu_threshold_pct"],
            "hysteresis":  3,
        },
        "algorithm": (
            f"latency = max({LATENCY_FLOOR_MS}ms, P95_RTT x {LATENCY_MULTIPLIER}) | "
            f"cpu = max({CPU_FLOOR_PCT}%, P95_CPU x {CPU_MULTIPLIER})"
        ),
        "notes": {
            "latency_floor_reason": (
                "Docker LAN baseline P95 RTT is <1ms. Raw multiplier would produce "
                "sub-millisecond thresholds triggering on any network noise. "
                "50ms floor ensures only real WAN degradation (>50ms) triggers a switch."
            ),
            "cpu_floor_reason": (
                "R1 stress test (2026-03-04) found psutil reads system-wide CPU across "
                "8 host cores. Single-core container stress produces ~12% system-wide. "
                "80% hardcoded threshold was unreachable. 40% floor is above normal "
                "noise (P95=5.3%) and reachable under real workload pressure."
            ),
        }
    }


def print_summary(output: dict):
    t  = output["thresholds"]
    st = output["statistics"]
    print("\n" + "="*60)
    print("  CALIBRATION RESULTS")
    print("="*60)
    print(f"  Samples collected : {output['sample_count']}")
    print(f"  Profile duration  : {output['profiling_duration_s']}s")
    print()
    print(f"  RTT   P50={st['rtt_p50_ms']:.2f}ms  P95={st['rtt_p95_ms']:.2f}ms  "
          f"P99={st['rtt_p99_ms']:.2f}ms  MAX={st['rtt_max_ms']:.2f}ms")
    print(f"  CPU   P50={st['cpu_p50_pct']:.1f}%   P95={st['cpu_p95_pct']:.1f}%   "
          f"P99={st['cpu_p99_pct']:.1f}%   MAX={st['cpu_max_pct']:.1f}%")
    print()
    print(f"  Algorithm : {output['algorithm']}")
    print()
    floor_note_lat = " [FLOOR ACTIVE]" if st["latency_floor_active"] else ""
    floor_note_cpu = " [FLOOR ACTIVE]" if st["cpu_floor_active"] else ""
    print(f"  ✔  latency_threshold = {t['latency_ms']} ms{floor_note_lat}")
    print(f"  ✔  cpu_threshold     = {t['cpu_pct']} %{floor_note_cpu}")
    print(f"  ✔  hysteresis        = {t['hysteresis']} consecutive breaches")
    print("="*60)


# ── Main ───────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(
        description="AdaptiveOrchestrator Sprint 3 — Threshold Calibration"
    )
    parser.add_argument(
        "--duration", type=int, default=DEFAULT_DURATION_S,
        help=f"Profiling duration in seconds (default: {DEFAULT_DURATION_S})"
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Compute and print thresholds without saving calibration.json"
    )
    args = parser.parse_args()

    print("\n╔══════════════════════════════════════════════╗")
    print("║  AdaptiveOrchestrator — calibrate.py         ║")
    print("║  Sprint 3 — Adaptive Threshold Calibration   ║")
    print("╚══════════════════════════════════════════════╝")

    # Quick connectivity check before wasting 5 minutes
    print(f"\n[calibrate] Pre-check: pinging {CLOUD_HOST}...")
    test_rtt = measure_rtt(CLOUD_HOST)
    if test_rtt < 0:
        print(f"[ERROR] Cannot reach {CLOUD_HOST}. Is cloud_node running?")
        print("[ERROR] Run: docker compose up -d")
        sys.exit(1)
    print(f"[calibrate] Pre-check OK — RTT {test_rtt:.2f}ms\n")

    # Run profiling
    profile    = run_profiling(args.duration)
    thresholds = compute_thresholds(profile)
    output     = build_output(profile, thresholds)

    print_summary(output)

    if args.dry_run:
        print("\n[calibrate] Dry-run mode — calibration.json NOT saved.")
        return

    # Save
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, "w") as f:
        json.dump(output, f, indent=2)

    print(f"\n[calibrate] Saved → {OUTPUT_FILE}")
    print("[calibrate] context_monitor.py will load these thresholds on next start.\n")


if __name__ == "__main__":
    main()