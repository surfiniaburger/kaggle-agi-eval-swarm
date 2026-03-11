import logging
import asyncio
from typing import Optional, List, Dict, Any
from .research_driver import ResearchResult

logger = logging.getLogger(__name__)

class SkillWriterProtocolDriver:
    """
    Layer 3: Protocol Driver for Skill Updates.
    Translates 'Analyze and Update' into file operations.
    """
    def __init__(self, mcp_client):
        self.mcp = mcp_client
        self.repo_path = "/Users/surfiniaburger/Desktop/mental-research-swarm/research_env"

    async def get_latest_results(self) -> str:
        """Reads results.tsv."""
        return await self.mcp.call_tool("read_research_file", {"path": "results.tsv"})

    async def get_latest_log(self) -> str:
        """Reads run.log."""
        try:
            return await self.mcp.call_tool("read_research_file", {"path": "run.log"})
        except:
            return ""

    async def update_skill(self, new_instructions: str) -> bool:
        """
        Updates program.md with new instructions or insights.
        """
        current_skill = await self.mcp.call_tool("read_research_file", {"path": "program.md"})
        
        # Improved replacement: target the section more precisely
        section_header = "## Research Insights"
        if section_header in current_skill:
            base_skill = current_skill.split(section_header)[0].strip()
        else:
            base_skill = current_skill.strip()

        updated_skill = base_skill + "\n\n" + section_header + "\n\n" + new_instructions
        
        await self.mcp.call_tool("write_research_file", {
            "path": "program.md",
            "content": updated_skill.strip() + "\n"
        })
        return True
