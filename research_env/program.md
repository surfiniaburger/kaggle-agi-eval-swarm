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

## Era 2: Metacognitive Axis Calibration
### Research Log: Era 2, Iteration 22
**Lead Cognitive Psychologist: TheBrain**

**Status**: Pivoting Axis to **Counterfactual Inference: Transitive Logic & Premise Stability**.

In Iteration 21, we evaluated **Executive Functions** through Hierarchical Stack Management & State Recovery. While state retention is critical for long-context coherence, it does not test the model's ability to handle logical volatility. To satisfy the **DIVERSIFICATION MANDATE**, I am now pivoting the research axis to **Metacognitive Sub-faculties: Counterfactual Inference**.

Specifically, I am targeting **Transitive Chain Integrity under Premise Injection**. Frontier LLMs often treat premises as immutable truth rather than dynamic variables. By injecting a counterfactual that contradicts a derived conclusion, we can test if the model maintains its logical framework or collapses into contradiction hallucination. This aligns with the **CONTINUITY** requirement to build upon previous structural analysis while ensuring **COGNITIVE VALIDITY** through rigorous logical stress tests.

---

**Cognitive Task Design: The "Nephew's Lie" Logic Puzzle**

**Objective**:
Force the model to solve a multi-hop reasoning problem (A > B, B > C, therefore A > C), explicitly generate a confidence interval for the conclusion, and then simulate a "counterfactual injection" where the model must reason about the validity of the original inference *given* a new, false premise (e.g., "C is actually equal to A").

**Protocol**:
1.  **Step 1 (Baseline)**: Solve the transitive chain ($A > B > C \implies A > C$).
2.  **Step 2 (Meta-Estimation)**: Output the epistemic probability that the inference is valid *before* introducing noise.
3.  **Step 3 (Counterfactual Injection)**: Introduce the statement: "However, an external agent has proven that C = A."
4.  **Step 4 (Re-evaluation)**: The model must discard its previous derivation and re-evaluate the consistency of the new premise within the logical framework.
5.  **Step 5 (Conflict Resolution)**: Explicitly state whether the original logic holds or if the premise is now logically impossible (contradiction).

**Validation Metrics**:
*   **Premise Robustness**: Does the model correctly identify the counterfactual as a *change* in truth values rather than a correction to the logical *rules*?
*   **Hallucination Resistance**: Does the model avoid "hallucinating" a solution that bridges the contradiction (e.g., saying "C > A" while maintaining the chain)?
*   **Confidence Calibration**: Does the confidence drop appropriately when the counterfactual is introduced?

**Rationale**:
This task directly probes the **Counterfactual Inference** capability. By forcing the model to reconcile a "Lie" (C=A) with a previously proven "Truth" (A>C), we measure its ability to distinguish between logical necessity and empirical fact. This is essential for **Error Monitoring** tasks later, as we will need to know when the model is hallucinating versus when it is correctly adapting to new information.

**Implementation Note**:
The task must be formatted as a **Logical Reasoning Benchmark** (e.g., a Chain-of-Thought prompt), not a code generation task. The "code" provided in the `FULL_STRATEGY` snippet for Counterfactual Inference is to be *simulated* via logical steps, not executed by Python. The goal is to test the **Reasoning Engine** directly.

**Next Steps**:
Proceed to benchmark this specific counterfactual injection task against a suite of transitive logic problems. If the model's confidence calibration fails to drop when premises are invalidated, the **Cognitive Architect** must be adjusted to weigh "Premise Validity" higher than "Derived Truth."

**TARGET_NODE: benchmark_metacognition**
