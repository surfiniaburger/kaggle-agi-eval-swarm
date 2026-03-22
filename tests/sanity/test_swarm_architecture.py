import os
import ast

def test_benchmark_imports_kbench():
    """Sanity Check: Ensure the benchmark.py file hasn't lost the core kbench SDK import."""
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    benchmark_path = os.path.join(base_dir, "research_env", "benchmark.py")
    
    assert os.path.exists(benchmark_path), "benchmark.py is missing!"
    
    with open(benchmark_path, "r") as f:
        code = f.read()
    
    tree = ast.parse(code)
    kbench_imported = False
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name == "kaggle_benchmarks":
                    kbench_imported = True
        elif isinstance(node, ast.ImportFrom):
            if node.module == "kaggle_benchmarks":
                kbench_imported = True
                
    assert kbench_imported, "benchmark.py LOST the kaggle_benchmarks import! Architectural Regression!"

def test_program_md_intact():
    """Sanity Check: program.md taxonomy must exist to feed the JSON Optimizer."""
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    program_path = os.path.join(base_dir, "research_env", "program.md")
    
    assert os.path.exists(program_path), "program.md is missing! Strategic context collapse pending!"
    with open(program_path, "r") as f:
        content = f.read()
    assert len(content) > 500, "program.md is too short, taxonomy has been corrupted."
