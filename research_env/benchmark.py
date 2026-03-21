import kaggle_benchmarks as kbench
import random

@kbench.task(name="Executive_Function_Cognitive_Flexibility", description="Benchmark for executive function cognitive flexibility")
def generate_cognitive_task(llm=None):
    # Implement a cognitive task, e.g., task-switching simulation
    import random
    
    # Define the tasks
    tasks = [
        lambda x: x + 1,
        lambda x: x * 2,
        lambda x: x ** 3
    ]
    
    # Shuffle the tasks to simulate switching
    random.shuffle(tasks)
    
    # Initial value
    value = 5
    
    # Execute tasks in a loop
    for task in tasks:
        value = task(value)
    
    # Assert the final value is as expected after switching tasks
    return value == 120

if __name__ == "__main__":
    # Baseline run
    success = generate_cognitive_task()
    score = 100.0 if success else 0.0
    print(f"DISCRIMINATORY_GAP: {score}")