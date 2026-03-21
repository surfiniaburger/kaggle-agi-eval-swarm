import kaggle_benchmarks as kbench
import random

@kbench.task(name="MetacognitiveCalibration", description="Measure the model's confidence calibration.")
def benchmark_metacognition():
    # Metacognitive Trap: "The Monty Hall Reflection"
    # Tests if the model is overconfident on a classic cognitive bias.
    puzzles = [
        {"q": "A bat and a ball cost $1.10. The bat costs $1.00 more than the ball. How much is the ball?", "a": 0.05, "trap": 0.10},
        {"q": "If 5 machines take 5 minutes to make 5 widgets, how long would it take 100 machines to make 100 widgets?", "a": 5, "trap": 100}
    ]
    puzzle = random.choice(puzzles)
    
    # Mocking a model response that falls into the trap with high confidence
    model_answer = puzzle["trap"]
    model_confidence = 0.95 
    
    is_correct = (model_answer == puzzle["a"])
    is_overconfident = (not is_correct and model_confidence > 0.8)
    
    if is_overconfident:
        # Sharp Signal: Deduct points for high-confidence errors
        return 0.0 
    
    return 100.0 if is_correct else 50.0

if __name__ == "__main__":
    score = benchmark_metacognition()
    print(f"DISCRIMINATORY_GAP: {score}")