import pytest
import json
from swarm.agents import ContextOptimizerAgent

def test_context_optimizer_agent_initialization():
    """
    Test that the ContextOptimizerAgent initializes correctly
    and contains strict JSON formatting instructions in its prompt.
    """
    agent = ContextOptimizerAgent(name="ContextOptimizer", model="ollama/qwen2.5-coder:7b")
    
    assert agent.name == "ContextOptimizer"
    assert "Strict JSON output ONLY" in agent.instruction, "Missing JSON enforcement guardrail"
    
    # Assert all required keys are requested in the prompt
    required_keys = [
        "current_axis", 
        "last_action", 
        "failure_reason", 
        "historical_guardrails", 
        "recommended_surgery"
    ]
    for key in required_keys:
        assert f'"{key}"' in agent.instruction, f"Missing requested JSON key: {key}"
