import logging
import asyncio
import os
import ast
import subprocess
from datetime import datetime
from typing import AsyncGenerator, Any
from google.adk.agents import BaseAgent, LlmAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event
from .agents import ResearchAgent, SkillWriterAgent, CriticAgent, ManagerAgent
from .drivers import ResearchProtocolDriver, SkillWriterProtocolDriver, ResearchResult
from .telemetry import get_mac_hardware_stats, log_telemetry

def _apply_patch(validated_code: str, target_node: str, benchmark_path: str) -> bool:
    """AST-based engine to replace a specific task function in benchmark.py"""
    try:
        new_tree = ast.parse(validated_code)
        # Verify the target node exists in the new code
        if not any(isinstance(n, ast.FunctionDef) and n.name == target_node for n in new_tree.body):
            logger.error(f"Validated code does NOT contain function '{target_node}'!")
            return False
    except SyntaxError:
        return False

    with open(benchmark_path, "r") as f:
        source_code = f.read()
    
    tree = ast.parse(source_code)
    lines = source_code.splitlines()
    
    start_idx = -1
    end_idx = -1
    
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name == target_node:
            start_line = node.decorator_list[0].lineno if node.decorator_list else node.lineno
            end_line = getattr(node, "end_lineno", node.lineno)
            
            start_idx = start_line - 1
            end_idx = end_line
            break
            
    if start_idx == -1:
        return False
        
    new_lines = lines[:start_idx] + validated_code.splitlines() + lines[end_idx:]
    
    with open(benchmark_path, "w") as f:
        f.write("\n".join(new_lines) + "\n")
        
    return True

logger = logging.getLogger("swarm.coordinator")


class SwarmCoordinator(BaseAgent):
    """
    Orchestrator that drives the FULL research lifecycle without Taipy UI.
    """
    manager_agent: ManagerAgent
    max_iterations: int = 100
    session_state_path: str = ""
    start_iteration: int = 1
    global_best_score: float = 0.0
    scenario_cfg: Any = None
    taipy_core: Any = None
    model_config = {"arbitrary_types_allowed": True}

    def __init__(
        self,
        name: str,
        manager_agent: ManagerAgent,
        max_iterations: int = 100
    ):
        super().__init__(
            name=name,
            sub_agents=[manager_agent],
            manager_agent=manager_agent,
            max_iterations=max_iterations
        )
        self.session_state_path = os.path.join(self.manager_agent.hands.driver.repo_path, "docs", "session_state.json")
        self._load_session_state()
        
        # UI Disabled to resolve dependency conflicts
        self.scenario_cfg = None
        self.taipy_core = None

    def _load_session_state(self):
        """Loads persistent session state from disk."""
        if os.path.exists(self.session_state_path):
            try:
                import json
                with open(self.session_state_path, "r") as f:
                    state = json.load(f)
                    self.start_iteration = state.get("iteration", 1)
                    self.global_best_score = state.get("global_best_score", 0.0)
                    logger.info(f"📂 Loaded session state: iteration={self.start_iteration}, best_gap={self.global_best_score}")
            except Exception as e:
                logger.error(f"⚠️ Failed to load session state: {e}")
                self.start_iteration = 1
                self.global_best_score = 0.0
        else:
            self.start_iteration = 1
            self.global_best_score = 0.0

    def _save_session_state(self, iteration: int, global_best_score: float):
        """Saves session state to disk."""
        try:
            import json
            state = {
                "iteration": iteration,
                "global_best_score": global_best_score,
                "timestamp": datetime.now().isoformat()
            }
            with open(self.session_state_path, "w") as f:
                json.dump(state, f, indent=2)
        except Exception as e:
            logger.error(f"⚠️ Failed to save session state: {e}")

    async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        # ── Phase 1: Environment Setup ───────────────────────────
        logger.info("═" * 60)
        logger.info("  PHASE 1: ENVIRONMENT SETUP")
        logger.info("═" * 60)
        
        success = await self.manager_agent.hands.driver.ensure_setup()
        if not success:
            logger.error("❌ Environment initialization FAILED.")
            return
        logger.info("✅ Environment initialized.")

        # Ensure docs directory exists
        repo_path = self.manager_agent.hands.driver.repo_path
        docs_dir = os.path.join(repo_path, "docs")
        os.makedirs(docs_dir, exist_ok=True)
        
        # Inject context for ManagerAgent
        ctx.session.state["research_dir"] = repo_path

        # Load initial files into session state
        ctx.session.state["program_md"] = await self.manager_agent.hands.driver.mcp.call_tool(
            "read_research_file", {"path": "program.md"}
        )
        ctx.session.state["benchmark_py"] = await self.manager_agent.hands.driver.mcp.call_tool(
            "read_research_file", {"path": "benchmark.py"}
        )

        # ── Phase 2: Baseline ────────────────────────────────────
        if self.global_best_score > 0.0:
            logger.info("═" * 60)
            logger.info(f"  PHASE 2: RESUMING SESSION (Best Gap: {self.global_best_score:.4f})")
            logger.info("═" * 60)
            ctx.session.state["global_best_score"] = self.global_best_score
        else:
            logger.info("═" * 60)
            logger.info("  PHASE 2: INITIAL BASECHMARK")
            logger.info("═" * 60)
            
            # Reset logs for baseline
            await self.manager_agent.hands.driver.mcp.call_tool("execute_command", {"command": "> run.log"})
            
            # Revert benchmark.py to baseline if it doesn't exist
            if not ctx.session.state["benchmark_py"]:
                logger.info("🆕 Initializing benchmark.py with Metacognitive Calibration baseline...")
                # The Hands usually do this, but for Phase 2 we want a fixed anchor.
            
            # Baseline is usually just running the current benchmark.py
            # But the SwarmCoordinator logic often expects a "Keep" or "Crash" status.
            
            res = await self.manager_agent.hands.driver.run_experiment("baseline-reset")
            if res.status == "crash":
                logger.error("❌ Baseline execution FAILED. Check run.log.")
                # Force a minimal valid benchmark.py to recover
            else:
                self.global_best_score = res.val_score
                logger.info(f"📊 Baseline: gap={res.val_score} | status={res.status}")
                self._save_session_state(1, self.global_best_score)

        # ── Phase 3: Autonomous Loop ─────────────────────────────
        logger.info("═" * 60)
        logger.info(f"  PHASE 3: AUTONOMOUS LOOP (max {self.max_iterations} iterations)")
        logger.info("═" * 60)
        
        current_iter = self.start_iteration
        while current_iter <= self.max_iterations:
            logger.info("─" * 60)
            logger.info(f"  🔄 ITERATION {current_iter}/{self.max_iterations}")
            logger.info("─" * 60)
            
            ctx.session.state["iteration"] = current_iter

            # ---- EMBEDDED SANITY CHECK ----
            logger.info("🛡️ Running Embedded BDD Sanity Checks...")
            sanity_res = subprocess.run(["uv", "run", "pytest", "tests/sanity/test_swarm_architecture.py", "-v"], capture_output=True, text=True)
            if sanity_res.returncode != 0:
                logger.error(f"🚨 SANITY CHECK FAILED! Bailing out of swarm loop to prevent hallucination:\n{sanity_res.stdout}")
                break
            logger.info("✅ Architecture is sane.")

            # Delegate to ManagerAgent
            # The Manager will run Brain -> Hands -> Critic
            try:
                async for event in self.manager_agent.run_async(ctx):
                    yield event
                
                # After the loop, the results is in docs/results_summary.md
                # We need to apply proposed_patch.py to benchmark.py, run it, and parse metrics.
                validated_code = ctx.session.state.get("validated_code")
                target_node = ctx.session.state.get("target_node", "benchmark_metacognition")
                research_dir = ctx.session.state.get("research_dir", "research_env")
                benchmark_path = os.path.join(research_dir, "benchmark.py")
                
                logger.info(f"[DEBUG] Target Node: {target_node}")
                logger.info(f"[DEBUG] Benchmark Path '{benchmark_path}' Exists? {os.path.exists(benchmark_path)}")
                logger.info(f"[DEBUG] Validated Code Length: {len(validated_code) if validated_code else 0}")
                
                if validated_code and os.path.exists(benchmark_path):
                    logger.info(f"🔨 Applying validated syntax patch to {target_node} via AST...")
                    success = _apply_patch(validated_code, target_node, benchmark_path)
                    if not success:
                        logger.error(f"Failed to find AST node {target_node} in benchmark.py to mutate!")
                    else:
                        logger.info("🚀 Running live benchmark execution...")
                        desc = f"Iteration {current_iter} Patch by TheHands"
                        result = await self.manager_agent.hands.driver.run_experiment(description=desc)
                        logger.info(f"📊 Live Benchmark Result -> {result.val_score}")
                        self.global_best_score = max(self.global_best_score, result.val_score)
                        
                        # Clear validated code so we don't apply it again next loop if next loop is empty
                        ctx.session.state["validated_code"] = None
                
            except Exception as e:
                error_str = str(e).lower()
                if "connection" in error_str or "timeout" in error_str or "no such host" in error_str:
                    logger.error(f"🌐 Network Error in Iteration {current_iter}: {e}")
                    logger.info("⏳ Sleeping for 60 seconds before retrying the same iteration due to network failure...")
                    await asyncio.sleep(60)
                    continue  # Retry without incrementing
                else:
                    logger.error(f"💥 Iteration {current_iter} failed: {e}")
                    logger.info(f"↩️ Continuing to next iteration...")
                
            # Periodic telemetry sampling (non-fatal)
            try:
                hw_stats = get_mac_hardware_stats()
                log_telemetry("iteration_checkpoint", {"iteration": current_iter, "role": "coordinator", "stats": hw_stats})
            except Exception as te:
                logger.warning(f"Telemetry sampling failed: {te}")
            
            # Save progress
            current_iter += 1
            self._save_session_state(current_iter, self.global_best_score)

            
        logger.info("🏁 Research Lifecycle Complete.")
