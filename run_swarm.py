import asyncio
import subprocess
import os
import logging
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from swarm.agents import ResearchAgent, SkillWriterAgent
from swarm.drivers import ResearchProtocolDriver, SkillWriterProtocolDriver
from swarm.coordinator import SwarmCoordinator

logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

REPO_PATH = "/Users/surfiniaburger/Desktop/mental-research-swarm/research_env"
APP_NAME = "mental_research_swarm"
USER_ID = "surfiniaburger"
SESSION_ID = "swarm_001"

async def main():
    logger.info("🚀 Launching ADK Research Swarm")

    # 1. Start MCP Server in the background
    logger.info("🧪 Starting Research MCP Server...")
    mcp_proc = subprocess.Popen(
        ["uv", "run", "python3", "swarm/mcp_server.py"],
        cwd="/Users/surfiniaburger/Desktop/mental-research-swarm",
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    await asyncio.sleep(2)

    try:
        # 2. Local MCP Client Mock (as per ADK sample integration)
        from swarm import mcp_server
        class LocalMCPClient:
            async def call_tool(self, name, args):
                if name == "execute_command": return await mcp_server.execute_command(**args)
                if name == "read_research_file": return await mcp_server.read_research_file(**args)
                if name == "write_research_file": return await mcp_server.write_research_file(**args)
                raise ValueError(f"Unknown tool: {name}")

        mcp_client = LocalMCPClient()

        # 3. Component Setup
        r_driver = ResearchProtocolDriver(mcp_client)
        sw_driver = SkillWriterProtocolDriver(mcp_client)
        
        research_agent = ResearchAgent(
            name="TheHands", 
            model=os.environ.get("USER_LLM_MODEL", "ollama/qwen2.5-coder:1.5b"),
            driver=r_driver
        )
        skill_writer = SkillWriterAgent(
            name="TheBrain",
            model=os.environ.get("SKILL_WRITER_MODEL", "ollama/qwen2.5-coder:3b"),
            driver=sw_driver
        )
        
        coordinator = SwarmCoordinator(
            name="SwarmCoordinator",
            research_agent=research_agent,
            skill_writer=skill_writer
        )

        # 4. ADK Runner & Session
        session_service = InMemorySessionService()
        await session_service.create_session(
            app_name=APP_NAME, 
            user_id=USER_ID, 
            session_id=SESSION_ID,
            state={"topic": "Optimize 11M parameter TinyLlama BPB"}
        )
        
        runner = Runner(
            agent=coordinator,
            app_name=APP_NAME,
            session_service=session_service
        )

        # 5. Execute Swarm
        content = types.Content(role='user', parts=[types.Part(text="Start autonomous research.")])
        logger.info("🤖 Swarm session active. Monitoring loop...")
        
        async for event in runner.run_async(user_id=USER_ID, session_id=SESSION_ID, new_message=content):
            # Log significant events or final response
            pass

        logger.info("✅ Multi-Agent session concluded.")

    finally:
        logger.info("🛑 Shutting down MCP Server...")
        mcp_proc.terminate()

if __name__ == "__main__":
    asyncio.run(main())
