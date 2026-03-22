#!/bin/bash
# Launch script for the Metacognitive Research Swarm
SWARM_DIR="/Users/surfiniaburger/Desktop/kaggle-agi-eval-swarm"
cd "$SWARM_DIR"

pkill -9 -f "run_swarm.py" 2>/dev/null || true
sleep 1

rm -rf swarm/__pycache__ __pycache__ 2>/dev/null || true
rm -f swarm.log research_env/docs/session_state.json

export KBENCH_SKIP_INIT=1

echo "=== Launching Swarm from: $(pwd) at $(date) ==="
uv run python run_swarm.py
