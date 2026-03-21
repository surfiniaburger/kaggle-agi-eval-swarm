import asyncio
import subprocess
import os
import logging
from datetime import datetime
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from swarm.agents import ResearchAgent, SkillWriterAgent, CriticAgent, ManagerAgent, ContextOptimizerAgent
from swarm.drivers import ResearchProtocolDriver, SkillWriterProtocolDriver
from swarm.coordinator import SwarmCoordinator

# ─── Logging Setup ───────────────────────────────────────────────
# Console: INFO summary
# swarm.log: Full structured lifecycle events
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SWARM_LOG = os.path.join(BASE_DIR, "swarm.log")

root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)

# Console handler (concise)
console = logging.StreamHandler()
console.setLevel(logging.INFO)
console.setFormatter(logging.Formatter("[%(levelname)s] %(message)s"))
root_logger.addHandler(console)

# File handler (detailed, timestamped)
file_handler = logging.FileHandler(SWARM_LOG, mode="a")
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(logging.Formatter(
    "%(asctime)s | %(levelname)-7s | %(name)-25s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
))
root_logger.addHandler(file_handler)

logger = logging.getLogger("swarm.main")

REPO_PATH = os.path.join(BASE_DIR, "research_env")
APP_NAME = "mental_research_swarm"
USER_ID = "surfiniaburger"
SESSION_ID = "swarm_context_opt_001"


def load_env_file(env_path):
    """Manually load .env file to avoid extra dependencies."""
    if os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                if "=" in line and not line.startswith("#"):
                    key, value = line.strip().split("=", 1)
                    os.environ[key] = value.strip('"').strip("'")
        return True
    return False


def log_banner(msg: str):
    """Write a visible banner to swarm.log for phase changes."""
    border = "═" * 60
    logger.info(border)
    logger.info(f"  {msg}")
    logger.info(border)


async def main():
    log_banner("🚀 ADK RESEARCH SWARM — SESSION START")
    logger.info(f"Timestamp: {datetime.now().isoformat()}")
    logger.info(f"Log file:  {SWARM_LOG}")

    # 0. Load Environment
    if load_env_file(os.path.join(BASE_DIR, ".env")):
        logger.info("🔑 Loaded .env credentials.")
    else:
        logger.warning("⚠️ No .env file found. Cloud models may fail.")

    # 1. Start MCP Server
    logger.info("🧪 Starting Research MCP Server...")
    mcp_proc = subprocess.Popen(
        ["uv", "run", "python3", "swarm/mcp_server.py"],
        env={**os.environ, "SAFE_REPO_PATH": REPO_PATH},
        cwd=BASE_DIR,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    await asyncio.sleep(2)

    try:
        from swarm import mcp_server
        class LocalMCPClient:
            async def call_tool(self, name, args):
                if name == "execute_command": return await mcp_server.execute_command(**args)
                if name == "read_research_file": return await mcp_server.read_research_file(**args)
                if name == "write_research_file": return await mcp_server.write_research_file(**args)
                if name == "patch_research_file": return await mcp_server.patch_research_file(**args)
                raise ValueError(f"Unknown tool: {name}")

        mcp_client = LocalMCPClient()

        # 2. Component Setup
        r_driver = ResearchProtocolDriver(mcp_client)
        sw_driver = SkillWriterProtocolDriver(mcp_client)
        
        # Cloud tier exhausted. Reverting to local local models as requested.
        # Direct local local naming (no prefix for ADK native, prefix for LlmAgent).
        MODEL_BRAIN = os.environ.get("BRAIN_MODEL", "ollama/qwen3.5:9b")
        MODEL_MANAGER = os.environ.get("MANAGER_MODEL", "ollama/qwen2.5-coder:7b")
        MODEL_HANDS = os.environ.get("HANDS_MODEL", "ollama/qwen2.5-coder:7b")
        MODEL_CRITIC = os.environ.get("CRITIC_MODEL", "ollama/qwen3.5:9b")

        research_agent = ResearchAgent(
            name="TheHands", 
            model=MODEL_HANDS,
            driver=r_driver
        )
        skill_writer = SkillWriterAgent(
            name="TheBrain",
            model=MODEL_BRAIN,
            driver=sw_driver
        )
        critic_agent = CriticAgent(
            name="TheCritic",
            model=MODEL_CRITIC
        )
        context_optimizer = ContextOptimizerAgent(
            name="ContextOptimizer",
            model=MODEL_MANAGER
        )
        
        manager_agent = ManagerAgent(
            name="MidLevelManager",
            brain=skill_writer,
            hands=research_agent,
            critic=critic_agent,
            context_optimizer=context_optimizer
        )
        
        coordinator = SwarmCoordinator(
            name="SwarmCoordinator",
            manager_agent=manager_agent,
            max_iterations=30
        )

        # 3. ADK Runner & Session
        session_service = InMemorySessionService()
        await session_service.create_session(
            app_name=APP_NAME, 
            user_id=USER_ID, 
            session_id=SESSION_ID,
            state={
                "topic": "Generate and Evaluate AGI Benchmarks (Kaggle)",
                "benchmark_py": open(os.path.join(BASE_DIR, "research_env/benchmark.py")).read() if os.path.exists(os.path.join(BASE_DIR, "research_env/benchmark.py")) else "",
                "program_md": open(os.path.join(BASE_DIR, "research_env/program.md")).read() if os.path.exists(os.path.join(BASE_DIR, "research_env/program.md")) else "",
                "results_packet": "No iterations completed yet. Starting from baseline.",
                "strategy_packet": open(os.path.join(BASE_DIR, "research_env/program.md")).read() if os.path.exists(os.path.join(BASE_DIR, "research_env/program.md")) else "Establish a stable Metacognitive baseline...",
                "crash_feedback": "None"
            }
        )
        
        runner = Runner(
            agent=coordinator,
            app_name=APP_NAME,
            session_service=session_service
        )

        # 4. Execute Swarm with EVENT LOGGING
        content = types.Content(role='user', parts=[types.Part(text="Start autonomous research.")])
        log_banner("🤖 SWARM SESSION ACTIVE — ENTERING EVENT LOOP")
        
        event_count = 0
        async for event in runner.run_async(user_id=USER_ID, session_id=SESSION_ID, new_message=content):
            event_count += 1
            # Log every ADK event with its author and type
            author = getattr(event, 'author', 'unknown')
            is_final = event.is_final_response() if hasattr(event, 'is_final_response') else False
            
            # Extract text content if present
            text_preview = ""
            if hasattr(event, 'content') and event.content and hasattr(event.content, 'parts'):
                for part in event.content.parts:
                    if hasattr(part, 'text') and part.text:
                        text_preview = part.text[:120].replace('\n', ' ')
                        break
            
            event_logger = logging.getLogger("swarm.events")
            event_logger.info(
                f"EVENT #{event_count:04d} | author={author:<20s} | "
                f"final={is_final} | preview={text_preview or '(no text)'}"
            )

        log_banner(f"✅ SESSION COMPLETE — {event_count} events processed")

    finally:
        logger.info("🛑 Shutting down MCP Server...")
        mcp_proc.terminate()

if __name__ == "__main__":
    asyncio.run(main())
