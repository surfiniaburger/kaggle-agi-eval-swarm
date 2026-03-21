import os
import kaggle_benchmarks as kbench
from dataclasses import dataclass

# The Brain will instruct The Hands to implement a specific cognitive trap here.
# TARGET_NODE: generate_cognitive_task
@kbench.task(name="cognitive_evaluation")
def generate_cognitive_task(llm):
    """
    Template function for the swarm to implement a specific cognitive evaluation.
    Evaluate the LLM's capability on the requested track (e.g. Metacognition).
    """
    prompt = "Reply with 'ready'."
    response = llm.prompt(prompt)
    kbench.assertions.assert_contains_regex("ready", response.lower(), expectation="LLM should be ready.")
    

if __name__ == "__main__":
    # We evaluate the task using the Kaggle SDK.
    # To determine Discriminatory Gap, the Hands can evaluate two models:
    # 1. A Frontier Model (e.g. gemini-2.5-pro or gpt-4o)
    # 2. A Weak Model (e.g. gemini-2.5-flash)
    
    # In this baseline stub, we just pretend the gap is 0.0
    # The Swarm will write the logic to calculate the real gap.
    print("DISCRIMINATORY_GAP: 0.0")