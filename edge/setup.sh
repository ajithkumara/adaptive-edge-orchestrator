#!/bin/bash
# ─────────────────────────────────────────────────────────
# AdaptiveOrchestrator — Environment Setup Script
# Run this once to set up everything from scratch
# Usage: bash setup.sh
# ─────────────────────────────────────────────────────────

set -e  # exit immediately if any command fails

PROJECT_DIR="$HOME/adaptive_orchestrator"
VENV_DIR="$PROJECT_DIR/venv"

echo "=================================================="
echo " AdaptiveOrchestrator Environment Setup"
echo "=================================================="

# ── Step 1: System dependencies ───────────────────────
echo ""
echo "[1/5] Installing system dependencies..."
sudo apt update -y -q
sudo apt install -y -q \
    python3-pip \
    python3-venv \
    python3-dev \
    build-essential \
    net-tools \
    iputils-ping \
    htop \
    curl \
    git
echo "      DONE"

# ── Step 2: Create virtual environment ────────────────
echo ""
echo "[2/5] Creating virtual environment..."
cd "$PROJECT_DIR"
python3 -m venv venv
echo "      DONE: venv created at $VENV_DIR"

# ── Step 3: Install Python packages ───────────────────
echo ""
echo "[3/5] Installing Python packages..."
source "$VENV_DIR/bin/activate"
pip install --upgrade pip -q
pip install -r requirements.txt -q
echo "      DONE: all packages installed"

# ── Step 4: Verify tc netem ────────────────────────────
echo ""
echo "[4/5] Verifying tc netem..."
sudo modprobe sch_netem && echo "      DONE: tc netem available" \
                        || echo "      WARN: tc netem not available"

# ── Step 5: Create folder structure ───────────────────
echo ""
echo "[5/5] Creating project folder structure..."
mkdir -p "$PROJECT_DIR"/{edge,cloud,tests,logs,data,scripts,config}
echo "      DONE"

# ── Summary ───────────────────────────────────────────
echo ""
echo "=================================================="
echo " Setup Complete"
echo "=================================================="
echo ""
echo " To activate the environment next time, run:"
echo "   cd ~/adaptive_orchestrator"
echo "   source venv/bin/activate"
echo ""
echo " To run Sprint 0 test:"
echo "   python3 tests/sprint0_baseline.py"
echo "=================================================="
