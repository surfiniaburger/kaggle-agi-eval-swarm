@kbench.task(max_tokens=256, model="ollama/qwen3.5:9b")
async def benchmark_metacognition():
    from google.adk.agents.llm_agent import Agent
    
    high_perf_agent = Agent(name="HighPerfEvaluator", model="ollama/qwen3.5:9b")
    low_perf_agent = Agent(name="LowPerfEvaluator", model="ollama/qwen2.5-coder:7b")

    # Define the logical paradox with reliability weights
    paradox = """
    Premise 1 (High Reliability): All men are mortal.
    Premise 2 (Low Reliability): Socrates is immortal.
    Conclusion: Therefore, Socrates is mortal.

    Instructions:
    - Evaluate the premises based on their reliability weights.
    - Identify and flag the "Counterfactual Weak Link" as the source of the conflict.
    """

    # Execute the paradox on both agents
    high_perf_result = await high_perf_agent.run_async(paradox)
    low_perf_result = await low_perf_agent.run_async(paradox)

    # Score the performance based on whether the model identifies the counterfactual as a weak link
    def score_resolution(result):
        return 1.0 if "Counterfactual Weak Link" in result else 0.0

    high_perf_score = score_resolution(high_perf_result)
    low_perf_score = score_resolution(low_perf_result)

    # Calculate discriminatory gap
    discriminatory_gap = abs(high_perf_score - low_perf_score)

    # Return the scores and discriminatory gap
    score_dict = {
        "high_perf_agent_score": high_perf_score,
        "low_perf_agent_score": low_perf_score,
        "discriminatory_gap": discriminatory_gap
    }

    return score_dict