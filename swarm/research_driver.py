import os
import json
import logging
import asyncio
from typing import Optional, Dict, Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class ResearchResult:
    val_bpb: float
    peak_vram_gb: float
    status: str
    description: str

class ResearchProtocolDriver:
    """
    Layer 3: Protocol Driver.
    Translates domain concepts into technical actions (MCP tool calls).
    """
    def __init__(self, mcp_client):
        self.mcp = mcp_client
        self.repo_path = "/Users/surfiniaburger/Desktop/mental-research-swarm/research_env"

    async def log_result(self, result: ResearchResult) -> None:
        """
        Appends the experiment result to results.tsv.
        """
        line = f"baseline\t{result.val_bpb}\t{result.peak_vram_gb}\t{result.status}\t{result.description}\n"
        await self.mcp.call_tool("write_research_file", {
            "path": "results.tsv",
            "content": line,
            "append": True
        })

    async def ensure_setup(self) -> bool:
        """
        Implements Step 1-6 of program.md: Agree on tag, branch, results.tsv.
        """
        # 1. Agree on run tag (e.g. mar10)
        from datetime import datetime
        tag = datetime.now().strftime("%b%d").lower()
        branch_name = f"autoresearch/{tag}"
        
        # 2. Check if branch exists and create if not
        try:
            await self.mcp.call_tool("execute_command", {
                "command": f"git checkout -b {branch_name}",
                "cwd": self.repo_path
            })
        except Exception as e:
            logger.info(f"Branch {branch_name} might already exist or git error: {e}")
            await self.mcp.call_tool("execute_command", {
                "command": f"git checkout {branch_name}",
                "cwd": self.repo_path
            })

        # 3. Read README to confirm repo context (Domain requirement)
        await self.mcp.call_tool("read_research_file", {
            "path": "README.md"
        })

        # 4. Check results.tsv
        results_path = "results.tsv"
        res = await self.mcp.call_tool("read_research_file", {"path": results_path})
        if "Error" in res:
            logger.info("results.tsv missing, creating with header...")
            # Create if missing
            header = "commit\tval_bpb\tmemory_gb\tstatus\tdescription\n"
            await self.mcp.call_tool("write_research_file", {
                "path": results_path,
                "content": header
            })
            
        return True

    async def run_experiment(self, description: str) -> ResearchResult:
        """
        Runs the 5-minute training loop and parses metrics.
        """
        # git commit first
        await self.mcp.call_tool("execute_command", {
            "command": 'git add train.py && git commit -m "autocommit: ' + description + '"',
            "cwd": self.repo_path
        })

        # Run training
        await self.mcp.call_tool("execute_command", {
            "command": "uv run train.py > run.log 2>&1",
            "cwd": self.repo_path,
            "timeout": 600 # 10 mins soft limit from program.md
        })

        # Parse metrics from logs
        # This will be refined as we see the log output
        return await self._parse_metrics("run.log")

    async def _parse_metrics(self, log_filename: str) -> ResearchResult:
        """
        Parses val_bpb and peak_vram_mb from run.log.
        """
        log_content = await self.mcp.call_tool("read_research_file", {"path": log_filename})
        
        val_bpb = 0.0
        peak_vram_gb = 0.0
        
        for line in log_content.splitlines():
            if line.startswith("val_bpb:"):
                val_bpb = float(line.split(":")[1].strip())
            if line.startswith("peak_vram_mb:"):
                vram_mb = float(line.split(":")[1].strip())
                peak_vram_gb = vram_mb / 1024.0
                
        return ResearchResult(
            val_bpb=val_bpb,
            peak_vram_gb=round(peak_vram_gb, 1),
            status="keep" if val_bpb > 0 else "crash",
            description="Experiment run"
        )
