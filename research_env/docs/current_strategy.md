# Current Strategy

o harder sub-problems?
**Code Implementation:** Task the model with a multi-step pipeline where step 1 is a rapid self-assessment of "Problem Difficulty". The model must output `requested_computation_depth: int`. The validation confirms if the requested depth scales correctly with the planted difficulty of the problem.

### 5. Counterfactual / Transitive Inference tracking (`counterfactual_inference`)
**Definition:** Evaluating the validity of one's own internal logic by running "what if" scenarios.
**Code Implementation:** Force the model to draw a transitive conclusion (A>B, B>C -> A>C), but then inject a counterfactual ("Assume C>A is true"). The model must output a metacognitive evaluation of how this new conflicting premise destroys the prior transitive chain.

---

### Strict Architecture Guard
- You MUST output exactly one targeted node for surgery.
- You MUST maintain compatibility with the validation runner.
- ALWAYS use the target node: `TARGET_NODE: benchmark_metacognition`
