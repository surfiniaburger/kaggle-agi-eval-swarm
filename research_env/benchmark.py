import kaggle_benchmarks as kbench

@kbench.task(name="Executive_Function_Cognitive_Flexibility", description="Benchmark for executive function cognitive flexibility")
def benchmark_executive_function_cognitive_flexibility():
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
    assert kbench.assertions.equals(value, 120), "Final value does not match the expected result"