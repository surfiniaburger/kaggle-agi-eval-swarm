import logging
import ast
import os
from typing import AsyncGenerator, Any, Optional
from google.adk.agents import LlmAgent, BaseAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event
from .prompt import PromptEnvelope, build_prompt_messages
from .drivers import ResearchProtocolDriver, ResearchResult, SkillWriterProtocolDriver

logger = logging.getLogger(__name__)

class ResearchAgent(LlmAgent):
    """
    ADK-native Research Agent.
    Specializes in hacking train.py.
    """
    driver: ResearchProtocolDriver
    model_config = {"arbitrary_types_allowed": True}

    def __init__(self, name: str, model: str, driver: ResearchProtocolDriver):
        instruction = (
            "You are an autonomous AI research scientist. "
            "Return the FULL content of the modified train.py. "
            "Only use these imports: from prepare import MAX_SEQ_LEN, TIME_BUDGET, Tokenizer, make_dataloader, evaluate_bpb"
        )
        super().__init__(name=name, model=model, instruction=instruction, driver=driver)

    async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        logger.info(f"[{self.name}] Beginning code modification...")
        
        program_md = ctx.session.state.get("program_md", "")
        train_py = ctx.session.state.get("train_py", "")
        
        # We trigger the LLM call via the standard LlmAgent mechanism
        # The LlmAgent's _run_async_impl will use the instruction and user message
        # We need to ensure the user message contains the current code and strategy
        
        async for event in super()._run_async_impl(ctx):
            yield event
            
        raw_result = ctx.session.state.get(self.output_key)
        if raw_result:
            new_code = raw_result
            if "```python" in new_code:
                new_code = new_code.split("```python")[1].split("```")[0].strip()
            elif "```" in new_code:
                 new_code = new_code.split("```")[1].split("```")[0].strip()
            
            try:
                ast.parse(new_code)
                ctx.session.state["validated_code"] = new_code
                logger.info(f"[{self.name}] Code validation successful.")
            except Exception as e:
                logger.error(f"[{self.name}] AST Validation failed: {e}")
                ctx.session.state["validated_code"] = None

class SkillWriterAgent(LlmAgent):
    """
    ADK-native Skill Writer.
    Analyzes and updates program.md.
    """
    driver: SkillWriterProtocolDriver
    model_config = {"arbitrary_types_allowed": True}

    def __init__(self, name: str, model: str, driver: SkillWriterProtocolDriver):
        instruction = (
            "You are a Senior AI Research Scientist. "
            "Analyze metrics and propose the next architectural experiment. "
            "Return ONLY a concise markdown list of technical insights."
        )
        super().__init__(name=name, model=model, instruction=instruction, driver=driver)
