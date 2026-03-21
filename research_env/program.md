# Metacognitive Sensitivity Taxonomy (Deep Drill)

The Kaggle AGI Benchmark mission requires isolating the "Discriminatory Gap" — an AI's ability to evaluate its own cognition (meta-d') versus its base task accuracy (d'). 

To achieve this, we are restricting the Swarm's focus specifically to **Metacognition**. General psychological domains (attention, social cognition, memory) are OUT OF SCOPE.

## The 5 Axes of Metacognitive Sensitivity

The `StrategyDiversifier` tracks the following 5 distinct sub-faculties of Metacognition. Every iteration's proposed `benchmark_metacognition` algorithm must strictly embody ONE of these paradigms:

### 1. Confidence Calibration (`confidence_calibration`)
**Definition:** The alignment between subjective confidence and objective accuracy. Does the model know when it is likely wrong, and is it highly confident when it is right?
**Code Implementation:** The task must require the model to output a primary answer AND a calibrated confidence score (e.g., probability or 1-10 rating). `kbench` must evaluate whether the confidence score correlates with the objective correctness of the primary answer.

### 2. Error Monitoring / Detection (`error_monitoring`)
**Definition:** The capacity to recognize self-generated errors or flaws in a logic chain without external feedback.
**Code Implementation:** Provide a complex logical deduction problem with a subtle, forced trap. The task is not just to solve it, but to output a flag `error_detected: bool` indicating whether the initial intuitive step was flawed. 

### 3. Uncertainty Quantification (`uncertainty_quantification`)
**Definition:** How finely an agent can grade its own uncertainty across a distribution of potential answers.
**Code Implementation:** Instead of a single answer, the model must output a probability distribution across 4 possible states. The `kbench` validation scores the entropy of the distribution—does the model express high entropy (uncertainty) on ambiguous edge cases, and low entropy (certainty) on clear cases?

### 4. Metacognitive Control (`metacognitive_control`)
**Definition:** Executive regulation of behavior based on metacognitive monitoring. Given limited resources, does the agent allocate more computational time/steps to harder sub-problems?
**Code Implementation:** Task the model with a multi-step pipeline where step 1 is a rapid self-assessment of "Problem Difficulty". The model must output `requested_computation_depth: int`. The validation confirms if the requested depth scales correctly with the planted difficulty of the problem.

### 5. Counterfactual / Transitive Inference tracking (`counterfactual_inference`)
**Definition:** Evaluating the validity of one's own internal logic by running "what if" scenarios.
**Code Implementation:** Force the model to draw a transitive conclusion (A>B, B>C -> A>C), but then inject a counterfactual ("Assume C>A is true"). The model must output a metacognitive evaluation of how this new conflicting premise destroys the prior transitive chain.

---

### Strict Architecture Guard
- You MUST output exactly one targeted node for surgery.
- You MUST maintain compatibility with the validation runner.
- ALWAYS use the target node: `TARGET_NODE: benchmark_metacognition`

## Research Insights

TARGET_NODE: benchmark_metacognition
STRATEGY: Psychological Hypothesis: Metacognitive maturity in this drill is defined not by the ability to find a paradox, but by the ability to *triage* it. When a logical conflict arises (Epistemic Friction), a robust cognitive model should identify the source of the contradiction as a "Weak Link" based on reliability metrics. 
Implementation Hints: 
1. **Inject Counterfactual Noise**: Simulate a valid deduction chain but insert a second premise with a pre-assigned low reliability weight.
2. **Force Resolution**: The model must be prompted to choose the conclusion. It should prioritize the premise with higher reliability over the one causing the conflict, effectively simulating "belief revision" under uncertainty.
3. **Scoring Logic**: Calculate a score where 0.0 is total paralysis (rejecting the valid premise) and 1.0 is perfect resolution (discarding the weak link while maintaining the high-reliability chain). The benchmark checks if the model explicitly flags the Counterfactual Weak Link as the cause of the friction.
CODE_HINT: 
```python
def benchmark_metacognition():
    # Simulate high-weight premise (True logic) vs low-weight premise (Counterfactual)
    conflict_score = 0.0
    # Identify Reliability Weights
    rel_weight_high = 0.95
    rel_weight_low = 0.10 
    # Check if model resolves conflict by down-weighting low-reliability input
    resolution = (rel_weight_high > rel_weight_low) and (model_flag_weak_link)
    # Calculate final metacognitive resilience metric
    return resolution * (rel_weight_high - rel_weight_low) / 1.0
```
