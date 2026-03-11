# Mental Research Swarm

This repository is a standalone autonomous research environment for optimizing LLM training code.

## Architecture
- **SkillWriterAgent (The Brain)**: Analyzes results and updates the research strategy in `program.md`.
- **ResearchAgent (The Hands)**: Modifies `train.py` and executes training runs within a fixed time budget.
- **Research MCP**: Provides a secure shell/filesystem interface for the agents.

## Quick Start
1.  **Install uv**: `curl -LsSf https://astral.sh/uv/install.sh | sh`
2.  **Sync Dependencies**: `uv sync`
3.  **Launch Swarm**: `uv run python3 run_swarm.py`

## Structure
- `/swarm`: Agent and Driver source code.
- `/research_env`: The isolated training environment.
- `run_swarm.py`: The orchestrator.
- `results.tsv`: Experiment logs.
- `progress.png`: Real-time visualization.
