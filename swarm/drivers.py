import os
import json
import logging
from typing import Optional, Dict, Any, List
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class ResearchResult:
    val_score: float
    peak_vram_gb: float
    status: str
    description: str

class ResearchProtocolDriver:
    """
    Layer 3: Protocol Driver.
    Translates research concepts into MCP tool calls.
    """
    def __init__(self, mcp_client):
        self.mcp = mcp_client
        self.repo_path = "/Users/surfiniaburger/Desktop/kaggle-agi-eval-swarm/research_env"

    async def log_result(self, result: ResearchResult) -> None:
        state_path = "benchmark_state.json"
        res = await self.mcp.call_tool("read_research_file", {"path": state_path})
        
        history = []
        if "Error" not in res and res.strip() != "":
            try:
                history = json.loads(res)
            except:
                history = []
                
        history.append({
            "val_score": result.val_score,
            "peak_vram_gb": result.peak_vram_gb,
            "status": result.status,
            "description": result.description
        })
        
        await self.mcp.call_tool("write_research_file", {
            "path": state_path,
            "content": json.dumps(history, indent=2)
        })

    async def ensure_setup(self) -> bool:
        from datetime import datetime
        # Use a more unique tag: MonthDay-HourMinute
        tag = datetime.now().strftime("%b%d-%H%M").lower()
        branch_name = f"autoresearch/{tag}"
        
        try:
            await self.mcp.call_tool("execute_command", {
                "command": f"git checkout -b {branch_name}",
                "cwd": self.repo_path
            })
        except:
            await self.mcp.call_tool("execute_command", {
                "command": f"git checkout {branch_name}",
                "cwd": self.repo_path
            })

        state_path = "benchmark_state.json"
        res = await self.mcp.call_tool("read_research_file", {"path": state_path})
        if "Error" in res:
            await self.mcp.call_tool("write_research_file", {
                "path": state_path,
                "content": "[]"
            })
        return True

    async def get_history(self) -> List[ResearchResult]:
        """Reads benchmark_state.json and returns a list of ResearchResult objects."""
        res = await self.mcp.call_tool("read_research_file", {"path": "benchmark_state.json"})
        history = []
        if "Error" in res or not res.strip():
            return history
            
        try:
            data = json.loads(res)
            for item in data:
                history.append(ResearchResult(
                    val_score=float(item.get("val_score", 0.0)),
                    peak_vram_gb=float(item.get("peak_vram_gb", 0.0)),
                    status=item.get("status", "unknown"),
                    description=item.get("description", "")
                ))
        except Exception as e:
            logger.warning(f"Error parsing history JSON: {e}")
        return history

    async def run_experiment(self, description: str) -> ResearchResult:
        await self.mcp.call_tool("execute_command", {
            "command": f'git add benchmark.py && git commit -m "autocommit: {description}"',
            "cwd": self.repo_path
        })

        await self.mcp.call_tool("execute_command", {
            "command": "uv run -q benchmark.py > run.log 2>&1",
            "cwd": self.repo_path,
            "timeout": 1200
        })

        return await self._parse_metrics("run.log")

    async def _parse_metrics(self, log_filename: str) -> ResearchResult:
        val_score = 0.0
        log_content = await self.mcp.call_tool("read_research_file", {"path": log_filename})
        for line in log_content.splitlines():
            if "DISCRIMINATORY_GAP:" in line:
                try:
                    val_score = float(line.split("DISCRIMINATORY_GAP:")[1].strip())
                except:
                    pass
                
        # If the metric line was found, it's not a crash, even if the score is 0.0
        is_metric_present = any("DISCRIMINATORY_GAP:" in line for line in log_content.splitlines())
        
        return ResearchResult(
            val_score=val_score,
            peak_vram_gb=0.0,
            status="keep" if is_metric_present else "crash",
            description="Benchmark run"
        )

    async def read_crash_log(self, max_lines: int = 30) -> str:
        """Read the last N lines of run.log for crash diagnosis feedback.
        
        Returns the tail of the log so the Brain/Hands can learn from failures
        instead of blindly repeating the same broken patterns.
        """
        try:
            content = await self.mcp.call_tool("read_research_file", {"path": "run.log"})
            if not content or not content.strip():
                return ""
            lines = content.strip().split("\n")
            tail = lines[-max_lines:]
            return "\n".join(tail)
        except Exception:
            return ""

class SkillWriterProtocolDriver:
    """
    Layer 3: Protocol Driver for Skill Updates.
    """
    def __init__(self, mcp_client):
        self.mcp = mcp_client
        self.repo_path = "/Users/surfiniaburger/Desktop/kaggle-agi-eval-swarm/research_env"

    async def get_latest_results(self) -> str:
        return await self.mcp.call_tool("read_research_file", {"path": "benchmark_state.json"})

    async def get_latest_log(self) -> str:
        try:
            return await self.mcp.call_tool("read_research_file", {"path": "run.log"})
        except:
            return ""

    async def update_skill(self, new_instructions: str) -> bool:
        current_skill = await self.mcp.call_tool("read_research_file", {"path": "program.md"})
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
