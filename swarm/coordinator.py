import logging
import asyncio
from datetime import datetime
from typing import AsyncGenerator, List, Any
from google.adk.agents import BaseAgent, LoopAgent, SequentialAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event
from .agents import ResearchAgent, SkillWriterAgent

logger = logging.getLogger("swarm.coordinator")

class SwarmCoordinator(BaseAgent):
    """
    The High-Level Orchestrator for the Research Swarm.
    Uses ADK's LoopAgent to drive continuous improvement.
    Now includes lifecycle event logging for full observability.
    """
    research_agent: ResearchAgent
    skill_writer: SkillWriterAgent
    loop_agent: LoopAgent
    model_config = {"arbitrary_types_allowed": True}

    def __init__(
        self,
        name: str,
        research_agent: ResearchAgent,
        skill_writer: SkillWriterAgent,
        max_iterations: int = 100
    ):
        loop_agent = LoopAgent(
            name="ResearchLoop",
            sub_agents=[skill_writer, research_agent],
            max_iterations=max_iterations
        )

        super().__init__(
            name=name,
            sub_agents=[loop_agent],
            research_agent=research_agent,
            skill_writer=skill_writer,
            loop_agent=loop_agent
        )

    async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        logger.info("═" * 60)
        logger.info("  PHASE 1: ENVIRONMENT SETUP")
        logger.info("═" * 60)
        
        success = await self.research_agent.driver.ensure_setup()
        if not success:
            logger.error("❌ Environment initialization FAILED.")
            return

        logger.info("✅ Environment initialized.")

        # ── Phase 2: Baseline ────────────────────────────────────
        logger.info("═" * 60)
        logger.info("  PHASE 2: BASELINE EXPERIMENT")
        logger.info("═" * 60)
        
        baseline = await self.research_agent.driver.run_experiment("baseline-reset")
        await self.research_agent.driver.log_result(baseline)
        
        logger.info(f"📊 Baseline result: val_bpb={baseline.val_bpb} | status={baseline.status}")
        
        # Populate session state
        ctx.session.state["latest_bpb"] = baseline.val_bpb
        ctx.session.state["iteration"] = 0
        ctx.session.state["program_md"] = await self.research_agent.driver.mcp.call_tool(
            "read_research_file", {"path": "program.md"}
        )
        ctx.session.state["train_py"] = await self.research_agent.driver.mcp.call_tool(
            "read_research_file", {"path": "train.py"}
        )

        # ── Phase 3: Autonomous Loop ─────────────────────────────
        logger.info("═" * 60)
        logger.info("  PHASE 3: ENTERING AUTONOMOUS LOOP")
        logger.info(f"  Max iterations: {self.loop_agent.max_iterations}")
        logger.info("═" * 60)
        
        iteration = 0
        async for event in self.loop_agent.run_async(ctx):
            # Track iteration transitions by watching for author changes
            author = getattr(event, 'author', '')
            
            if author == self.skill_writer.name and ctx.session.state.get("_last_author") != author:
                iteration += 1
                ctx.session.state["iteration"] = iteration
                logger.info("─" * 60)
                logger.info(f"  🔄 ITERATION {iteration} — TheBrain (SkillWriter) analyzing...")
                logger.info("─" * 60)
            
            elif author == self.research_agent.name and ctx.session.state.get("_last_author") != author:
                logger.info("─" * 60)
                logger.info(f"  🔧 ITERATION {iteration} — TheHands (ResearchAgent) hacking...")
                logger.info("─" * 60)
            
            ctx.session.state["_last_author"] = author
            yield event
            
        logger.info("═" * 60)
        logger.info("  🏁 SWARM ORCHESTRATION CONCLUDED")
        logger.info(f"  Total iterations: {iteration}")
        logger.info("═" * 60)
