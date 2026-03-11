import logging
from typing import AsyncGenerator, List, Any
from google.adk.agents import BaseAgent, LoopAgent, SequentialAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event
from .agents import ResearchAgent, SkillWriterAgent

logger = logging.getLogger(__name__)

class SwarmCoordinator(BaseAgent):
    """
    The High-Level Orchestrator for the Research Swarm.
    Uses ADK's LoopAgent to drive continuous improvement.
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
        # Create sub-agents
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
        logger.info(f"[{self.name}] Starting Autonomous Research Swarm...")
        
        # 1. Prepare Environment (One-time)
        success = await self.research_agent.driver.ensure_setup()
        if not success:
            logger.error("Initialization failed.")
            return

        # 2. Get Initial Baseline
        logger.info("Establishing initial baseline...")
        baseline = await self.research_agent.driver.run_experiment("baseline-reset")
        await self.research_agent.driver.log_result(baseline)
        
        # Populate initial state for the loop
        ctx.session.state["latest_bpb"] = baseline.val_bpb
        ctx.session.state["program_md"] = await self.research_agent.driver.mcp.call_tool("read_research_file", {"path": "program.md"})
        ctx.session.state["train_py"] = await self.research_agent.driver.mcp.call_tool("read_research_file", {"path": "train.py"})

        # 3. Start the LoopAgent
        async for event in self.loop_agent.run_async(ctx):
            yield event
            
        logger.info("Swarm orchestration concluded.")
