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


