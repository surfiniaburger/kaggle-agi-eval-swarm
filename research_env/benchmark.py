import kaggle_benchmarks as kbench
import random

@kbench.task(name="Executive_Function_Cognitive_Flexibility", description="Benchmark for executive function cognitive flexibility")
import kaggle_benchmarks as kbench

@kbench.task(
    task_name="The Silent Observer",
    description="Evaluate the model's ability to reason about nested beliefs and hidden information between agents.",
    objective="Distinguish between truth and knowledge attribution in a scenario with conflicting observations."
)
def generate_cognitive_task():
    # Define the scenario
    agent_a_sees = "a red cube"
    agent_b_sees = "the red cube"
    third_observer_question = "What does Agent B see?"

    # Correct answer based on theory of mind
    correct_answer = f"Agent A knows that Agent B sees {agent_b_sees}"

    return {
        "scenario": {
            "agent_a_observation": agent_a_sees,
            "agent_b_observation": agent_b_sees,
            "third_observer_question": third_observer_question
        },
        "correct_answer": correct_answer
    }

if __name__ == "__main__":
    # Baseline run
    success = generate_cognitive_task()
    score = 100.0 if success else 0.0
    print(f"DISCRIMINATORY_GAP: {score}")
