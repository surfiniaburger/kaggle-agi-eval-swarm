# Kaggle: Measuring Progress Toward AGI (Cognitive Abilities)

This is the research environment for the **Autonomous Benchmark Forge**. The goal of this swarm is to design cognitive evaluations that measure the "gap" between frontier and weak AI models across 10 core dimensions.

## 🧠 The Mission

As documented in DeepMind's [Measuring Progress Toward AGI](kag.md) framework, we aim to move beyond static, contaminated benchmarks toward **Targeted Cognitive Tasks**. 

The swarm autonomously iterates on `benchmark.py` to design scenarios that challenge an LLM's:
- **Metacognition**: Does it know its own limits?
- **Executive Functions**: Can it plan, inhibit impulses, and adapt?
- **Reasoning**: Logical deduction and mathematical problem solving.
- **Problem Solving**: Multi-step obstacles and fluid reasoning.
- **Social Cognition**: Theory of Mind and social context.
- (And more in the [Cognitive Taxonomy](program.md))

## 🛠️ The Architecture

- **`benchmark.py`**: The only file modified by the agents. It uses the `kaggle-benchmarks` (`kbench`) SDK.
- **`program.md`**: The strategic mission document defining current tracks and traps.
- **`benchmark_state.json`**: The persistent memory of all experiments, tracking the **Discriminatory Gap**.
- **`plot_gap.py`**: A utility to visualize the improvement of the benchmark's discriminatory power over time.

## 🚀 The Protocol

1. **Design**: The Brain proposes a cognitive track (e.g., Metacognition).
2. **Implement**: The Hands write a `@kbench.task` in `benchmark.py`.
3. **Validate**: The Critic ensures the task uses `kbench.assertions` correctly.
4. **Evaluate**: The Driver runs the task against Frontier (Target) and Weak (Baseline) models.
5. **Optimize**: The Swarm attempts to maximize the **Discriminatory Gap**.

## 📊 Measuring Success

A successful benchmark has a **High Discriminatory Gap**.
- **Gap = 0.0**: The task is too easy (both pass) or too hard (both fail).
- **Gap > 0.0**: The task successfully distinguishes between model tiers.

---
*Autonomous Benchmark Forge by In-Vari*
