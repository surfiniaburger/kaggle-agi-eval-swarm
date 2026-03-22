#!/bin/bash
# Launch script for Resuming the Metacognitive Research Swarm
SWARM_DIR="/Users/surfiniaburger/Desktop/kaggle-agi-eval-swarm"
cd "$SWARM_DIR"

pkill -9 -f "run_swarm.py" 2>/dev/null || true
sleep 1

# Purge cache to ensure new coordinator.py logic runs
rm -rf swarm/__pycache__ __pycache__ 2>/dev/null || true

# We do NOT wipe session_state.json here.
# We also append to swarm_run.log and swarm.log instead of overwriting.

export KBENCH_SKIP_INIT=1

echo "" >> swarm.log
echo "=== RESUMING SWARM at $(date) ===" >> swarm.log

echo "=== Resuming Swarm from: $(pwd) at $(date) ==="
uv run python run_swarm.py
