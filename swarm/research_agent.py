import logging
import os
import asyncio
import subprocess
import ast
from typing import Optional, Any
from litellm import acompletion
from .prompt_boundary import PromptEnvelope, build_prompt_messages
from .research_driver import ResearchProtocolDriver, ResearchResult

logger = logging.getLogger(__name__)

class ResearchAgent:
    """
    Layer 1/2: Research Agent.
    Orchestrates the autonomous research loop using the Protocol Driver.
    Standalone version.
    """
    def __init__(self, driver: Optional[ResearchProtocolDriver] = None):
        self.driver = driver
        self.is_running = False
        self.model = os.environ.get("USER_LLM_MODEL") or "ollama/gemma3:1b"

    async def start_autonomous_loop(self, updater: Any = None):
        """
        The 'LOOP FOREVER' from program.md.
        """
        if self.is_running:
            logger.info("Autonomous loop is already running.")
            return

        self.is_running = True
        logger.info("Initializing Research Environment...")
        
        success = await self.driver.ensure_setup()
        if not success:
            self.is_running = False
            logger.error("Failed to initialize research environment.")
            return

        logger.info("Environment ready. Establishing baseline...")
        
        # Establishing baseline
        baseline = await self.driver.run_experiment("baseline")
        await self.driver.log_result(baseline)
        
        logger.info(f"Baseline established: val_bpb={baseline.val_bpb}")

        # Autonomous loop
        while self.is_running:
            logger.info("Analyzing results and proposing next experiment...")
            
            # 1. Read latest insights and code
            program_md = await self.driver.mcp.call_tool("read_research_file", {"path": "program.md"})
            train_py = await self.driver.mcp.call_tool("read_research_file", {"path": "train.py"})
            
            # 2. Hack train.py using LLM
            logger.info("🤖 Hacking train.py based on program.md...")
            new_code = await self._hack_train_py(program_md, train_py)
            
            if "Error" in new_code:
                 logger.warning(f"⚠️ Code generation failed: {new_code}. Retrying...")
                 continue

            # 3. Write new code
            logger.info(f"📝 Writing hacked code to train.py (Length: {len(new_code)})")
            await self.driver.mcp.call_tool("write_research_file", {"path": "train.py", "content": new_code})
            
            # 4. Run experiment
            logger.info("🧪 Launching experiment...")
            exp_result = await self.driver.run_experiment("Autonomous iteration")
            logger.info(f"📊 Experiment result: {exp_result.val_bpb} ({exp_result.status})")
            await self.driver.log_result(exp_result)
            
            # Automatically update progress.png
            try:
                subprocess.run(["uv", "run", "python3", "plot_progress.py"], cwd=self.driver.repo_path)
                logger.info("📈 Progress plot updated.")
            except Exception as e:
                logger.error(f"Failed to update progress plot: {e}")
            
            logger.info(f"Iteration complete: val_bpb={exp_result.val_bpb}. Status: {exp_result.status}")
            
            # Wait a bit before next loop to avoid thrashing
            await asyncio.sleep(5)
        
        self.is_running = False
        logger.info("Research session concluded.")

    async def _hack_train_py(self, program_md: str, current_code: str) -> str:
        """
        Uses LLM to modify train.py based on the research protocol in program.md.
        Includes strict validation to ensure pure Python output.
        """
        system_instruction = (
            "You are an autonomous AI research scientist. "
            "Return the FULL content of the modified train.py. "
            "IMPORTANT: Only use these imports from prepare.py: "
            "from prepare import MAX_SEQ_LEN, TIME_BUDGET, Tokenizer, make_dataloader, evaluate_bpb"
        )
        
        prompt = f"""
        RESEARCH PROTOCOL (program.md):
        {program_md}
        
        CURRENT CODE (train.py):
        {current_code}
        
        TASK:
        Apply the next architectural or hyperparameter optimization from program.md to train.py.
        Return the COMPLETE new train.py file.
        """
        
        try:
            envelope = PromptEnvelope(
                verified_context=system_instruction,
                supplemental_context="Target: train.py",
                user_query=prompt,
                persona="a professional AI Research Scientist specializing in architecture search"
            )
            messages = build_prompt_messages(envelope)
            
            # Use lower temperature for consistency
            response = await acompletion(
                model=self.model,
                messages=messages,
                temperature=0.1,
                max_tokens=4096
            )
            
            raw_content = response.choices[0].message.content
            
            # Robust extraction
            new_code = raw_content
            if "```python" in new_code:
                new_code = new_code.split("```python")[1].split("```")[0].strip()
            elif "```" in new_code:
                 new_code = new_code.split("```")[1].split("```")[0].strip()
            
            # Syntax Validation (AST)
            try:
                ast.parse(new_code)
                logger.info("✅ Code validation passed: Valid Python syntax.")
                return new_code
            except SyntaxError as se:
                logger.error(f"❌ Code validation failed: {se}")
                logger.debug(f"Bad content generated: {new_code[:200]}...")
                return f"Error: LLM generated invalid Python syntax: {se}"
                
        except Exception as e:
            logger.error(f"Failed to hack train.py: {e}")
            return f"Error: {e}"

    async def shutdown(self):
        self.is_running = False
        logger.info("ResearchAgent shutting down.")
