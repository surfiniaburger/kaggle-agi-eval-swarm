import logging
import os
import asyncio
from typing import Optional, List, Dict, Any
from litellm import acompletion
from .prompt_boundary import PromptEnvelope, build_prompt_messages
from .skill_writer_driver import SkillWriterProtocolDriver

logger = logging.getLogger(__name__)

class SkillWriterAgent:
    """
    Layer 1/2: Skill Writer Agent.
    Analyzes project output and refines the 'skill' (program.md).
    Standalone version.
    """
    def __init__(self, driver: Optional[SkillWriterProtocolDriver] = None):
        self.driver = driver
        self.model = os.environ.get("SKILL_WRITER_MODEL") or "ollama/gemini-3-flash-preview:cloud"

    async def analyze_and_refine_skill(self, updater: Any = None) -> None:
        """
        The core logic for analyzing results and updating program.md.
        """
        logger.info("🧠 SkillWriter: Analyzing latest results...")
        
        # 1. Collect Context
        results_tsv = await self.driver.get_latest_results()
        run_log = await self.driver.get_latest_log()
        
        if not results_tsv or "val_bpb" not in results_tsv:
            logger.info("No substantial results to analyze yet.")
            return

        # 2. Consult the 'Brain' (LLM)
        system_instruction = (
            "You are a Senior AI Research Scientist. "
            "Your task is to analyze LLM training logs and metrics to propose the next architectural experiment. "
            "Focus on validation BPB and training efficiency. "
            "Return ONLY a concise markdown list of technical insights and the proposed next step."
        )
        
        prompt = f"""
        LATEST METRICS (results.tsv):
        {results_tsv}
        
        LATEST TRAINING LOG (run.log):
        {run_log}
        
        TASK:
        Based on these results, what have we learned and what should be the next experiment?
        Be specific about hyperparameters or architectural changes.
        """
        
        try:
            envelope = PromptEnvelope(
                verified_context=system_instruction,
                supplemental_context="Target: program.md (Insights Section)",
                user_query=prompt,
                persona="a professional Senior AI Research Scientist"
            )
            messages = build_prompt_messages(envelope)
            
            response = await acompletion(
                model=self.model,
                messages=messages,
                temperature=0.2
            )
            
            new_insights = response.choices[0].message.content
            
            # 3. Update the 'Skill' (program.md)
            logger.info("📝 Updating program.md with new insights...")
            await self.driver.update_skill(new_insights)
            
            logger.info("✅ program.md updated successfully.")
            
        except Exception as e:
            logger.error(f"SkillWriter analysis failed: {e}")
