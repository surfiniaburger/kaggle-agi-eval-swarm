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
            "You are a specialized Code Surgeon (The Hands). "
            "Your job is to provide the NEW implementation of a SINGLE class or function based on documented strategy. "
            "Context available in session state: `strategy_packet`, `target_snippet`, `correction_prompt`. "
            "Return ONLY the code for that specific node within a ```python block. "
            "Do not return the whole file."
        )
        super().__init__(name=name, model=model, instruction=instruction, driver=driver)

    async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        logger.info(f"[{self.name}] Beginning code surgery...")
        
        # We no longer mutate self.instruction to preserve KV Cache.
        # Instead, we rely on ADK's built-in templating for the prompt tail.
        # Ensure we use double braces {{ }} if we were to use them in the init instruction,
        # but here we just pass the ctx.
        
        raw_result = ""
        try:
            async for event in super()._run_async_impl(ctx):
                if hasattr(event, 'content') and event.content and hasattr(event.content, 'parts'):
                    for part in event.content.parts:
                        if hasattr(part, 'text') and part.text:
                            raw_result += part.text
                yield event
        finally:
            if raw_result:
                new_code = raw_result
                if "```python" in new_code:
                    new_code = new_code.split("```python")[1].split("```")[0].strip()
                elif "```" in new_code:
                    new_code = new_code.split("```")[1].split("```")[0].strip()
                
                try:
                    ast.parse(new_code)
                    ctx.session.state["validated_code"] = new_code
                    ctx.session.state["ast_error"] = None
                    logger.info(f"[{self.name}] Code validation successful.")
                except Exception as e:
                    logger.error(f"[{self.name}] AST Validation failed: {e}")
                    ctx.session.state["validated_code"] = None
                    ctx.session.state["ast_error"] = str(e)
            
            ctx.session.state[self.output_key] = raw_result




class SkillWriterAgent(LlmAgent):
    """
    ADK-native Skill Writer (The Brain).
    Analyzes and updates program.md.
    """
    driver: SkillWriterProtocolDriver
    model_config = {"arbitrary_types_allowed": True}

    def __init__(self, name: str, model: str, driver: SkillWriterProtocolDriver):
        instruction = (
            "You are a Senior AI Research Scientist (The Brain). "
            "Analyze metrics and propose the next architectural experiment. "
            "Context available in session state: `strategy_packet`, `results_packet`. "
            "Return a markdown list of insights AND explicitly name the 'Target Node' (class/function) to modify. "
            "Format target node as: TARGET_NODE: [NodeName]"
        )
        super().__init__(name=name, model=model, instruction=instruction, driver=driver)

    async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        logger.info(f"[{self.name}] Analyzing results via shared documents...")
        
        raw_result = ""
        async for event in super()._run_async_impl(ctx):
            if hasattr(event, 'content') and event.content and hasattr(event.content, 'parts'):
                for part in event.content.parts:
                    if hasattr(part, 'text') and part.text:
                        raw_result += part.text
            yield event
            
        ctx.session.state[self.output_key] = raw_result


class CriticAgent(LlmAgent):
    """
    ADK-native Code Critic.
    Reviews train.py for logical errors and alignment with strategy.
    """
    model_config = {"arbitrary_types_allowed": True}

    def __init__(self, name: str, model: str):
        instruction = (
            "You are a Senior Code Reviewer (The Critic). "
            "Review the proposed changes against the strategy. "
            "Context available in session state: `program_md`, `target_snippet`, `validated_code`. "
            "Start your response with 'APPROVE' or 'REJECT'. "
            "If you 'REJECT', provide EXACT feedback."
        )
        super().__init__(name=name, model=model, instruction=instruction)

    async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        logger.info(f"[{self.name}] Reviewing surgical patch...")
        
        raw_result = ""
        async for event in super()._run_async_impl(ctx):
            if hasattr(event, 'content') and event.content and hasattr(event.content, 'parts'):
                for part in event.content.parts:
                    if hasattr(part, 'text') and part.text:
                        raw_result += part.text
            yield event
            
        ctx.session.state[self.output_key] = raw_result


class ManagerAgent(BaseAgent):
    """
    Mid-Level Manager.
    Orchestrates the Brain, Hands, and Critic.
    Implements 'Contextual Packets' for efficient communication.
    """
    brain: BaseAgent
    hands: BaseAgent
    critic: BaseAgent
    model_config = {"arbitrary_types_allowed": True}

    def __init__(self, name: str, brain: BaseAgent, hands: BaseAgent, critic: BaseAgent):
        super().__init__(
            name=name,
            sub_agents=[brain, hands, critic],
            brain=brain,
            hands=hands,
            critic=critic
        )
        self._fibonacci_cache = [1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144]

    def _is_fibonacci(self, n: int) -> bool:
        return n in self._fibonacci_cache

    def _prepare_contextual_packets(self, ctx: InvocationContext):
        """Summarizes full files into contextual packets and writes to docs/."""
        research_dir = ctx.session.state.get("research_dir", "research_env")
        docs_dir = os.path.join(research_dir, "docs")
        os.makedirs(docs_dir, exist_ok=True)

        # 1. Summarize Results (last 5 entries)
        results = ctx.session.state.get("results_tsv", "")
        if results:
            lines = results.strip().split("\n")
            header = lines[0]
            last_entries = lines[-5:]
            results_packet = f"{header}\n" + "\n".join(last_entries)
            ctx.session.state["results_packet"] = results_packet
            with open(os.path.join(docs_dir, "results_summary.md"), "w") as f:
                f.write(f"# Results Summary\n\n{results_packet}")
        
        # 2. Summarize Strategy
        program = ctx.session.state.get("program_md", "")
        if program:
            strategy_packet = program[-1000:]
            ctx.session.state["strategy_packet"] = strategy_packet
            with open(os.path.join(docs_dir, "current_strategy.md"), "w") as f:
                f.write(f"# Current Strategy\n\n{strategy_packet}")

        # 3. Load Last Critique (Cross-Iteration Memory)
        critique_path = os.path.join(docs_dir, "last_critique.md")
        if os.path.exists(critique_path):
            with open(critique_path, "r") as f:
                last_critique = f.read()
                ctx.session.state["critic_feedback"] = last_critique # Seed it for Attempt 1

    async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        logger.info(f"[{self.name}] Orchestrating research loop with Contextual Packets...")
        
        self._prepare_contextual_packets(ctx)
        
        # 1. Ask Brain for strategy (Uses results_packet)
        logger.info(f"[{self.name}] Step 1: Brain (Strategy Update)")
        async for event in self.brain.run_async(ctx):
            yield event
            
        brain_out = ctx.session.state.get(self.brain.output_key, "")
        if brain_out:
            await self.brain.driver.update_skill(brain_out)
            ctx.session.state["strategy_summary"] = brain_out[:200] + "..."
            
            # Extract Target Node for snippet-based editing
            if "TARGET_NODE:" in brain_out:
                target = brain_out.split("TARGET_NODE:")[1].split("\n")[0].strip()
                ctx.session.state["target_node"] = target
                logger.info(f"[{self.name}] Surgery Target identified: {target}")
            else:
                ctx.session.state["target_node"] = "Transformer" # Default
            
            # Extract reference snippet from train.py
            train_py = ctx.session.state.get("train_py", "")
            if train_py and ctx.session.state.get("target_node"):
                node_name = ctx.session.state["target_node"]
                # Basic snippet extraction: find node and try to get a reasonable chunk
                # In a real app we'd use AST here too, but for prompt we just need the text
                try:
                    import ast
                    tree = ast.parse(train_py)
                    lines = train_py.splitlines()
                    for node in ast.walk(tree):
                        if isinstance(node, (ast.FunctionDef, ast.ClassDef)) and node.name == node_name:
                            snippet = "\n".join(lines[node.lineno-1:node.end_lineno])
                            ctx.session.state["target_snippet"] = snippet
                            break
                    else:
                        ctx.session.state["target_snippet"] = "Node not found in source."
                except:
                    ctx.session.state["target_snippet"] = "Error extracting snippet."
            
        # 2. Ask Hands for code implementation
        max_correction_attempts = 2
        for attempt in range(max_correction_attempts):
            logger.info(f"[{self.name}] Step 2: Hands (Implementation - Attempt {attempt+1})")
            
            # If this is a correction, or we have residual feedback from last iteration
            ast_err = ctx.session.state.get("ast_error")
            critic_feedback = ctx.session.state.get("critic_feedback")
            
            if ast_err:
                ctx.session.state["correction_prompt"] = f"SYNTAX ERROR: {ast_err}\nPlease fix the syntax and return the full code."
            elif critic_feedback:
                ctx.session.state["correction_prompt"] = f"PREVIOUS FEEDBACK: {critic_feedback}\nPlease ensure your NEW implementation addresses these concerns."
            else:
                ctx.session.state["correction_prompt"] = ""

            async for event in self.hands.run_async(ctx):
                yield event
            
            # AST Validation Check
            validated_code = ctx.session.state.get("validated_code")
            if not validated_code:
                logger.warning(f"[{self.name}] Hands failed AST validation. Attempting correction...")
                continue
            
            # Write proposed patch to disk for persistent audit trail/critic review
            research_dir = ctx.session.state.get("research_dir", "research_env")
            with open(os.path.join(research_dir, "docs", "proposed_patch.py"), "w") as f:
                f.write(validated_code)
                
            # 3. Ask Critic for review
            logger.info(f"[{self.name}] Step 3: Critic (Review)")
            async for event in self.critic.run_async(ctx):
                yield event
                
            critic_out = ctx.session.state.get(self.critic.output_key, "")
            if "REJECT" in critic_out:
                logger.warning(f"[{self.name}] Code REJECTED by Critic. Attempting correction...")
                ctx.session.state["critic_feedback"] = critic_out
                # Shared Memory: Critique
                docs_dir = os.path.join(research_dir, "docs") # Ensure docs_dir is defined here
                critique_path = os.path.join(docs_dir, "last_critique.md")
                with open(critique_path, "w") as f:
                    f.write(critic_out)
                ctx.session.state["validated_code"] = None
                ctx.session.state["ast_error"] = None # Clear to prioritize critic
                continue
            else:
                logger.info(f"[{self.name}] Code APPROVED by Critic.")
                break
