"""
Research MCP Server — Layer 4 (External System Stub)
Provides shell and filesystem primitives for the Research Agent.
"""
import os
import subprocess
import logging
from fastmcp import FastMCP

logger = logging.getLogger(__name__)
mcp = FastMCP("Research Assistant 🧪")

# Scoped path for safety
SAFE_REPO_PATH = "/Users/surfiniaburger/Desktop/mental-research-swarm/research_env"

import asyncio

@mcp.tool()
async def execute_command(command: str, cwd: str = SAFE_REPO_PATH, timeout: int = 300) -> str:
    """
    Executes a shell command within the scoped research repository asynchronously.
    """
    logger.info(f"🐚 Executing: {command} in {cwd}")
    if not cwd.startswith(SAFE_REPO_PATH):
        return f"Error: CWD {cwd} is outside of safe research path {SAFE_REPO_PATH}"
    
    try:
        process = await asyncio.create_subprocess_shell(
            command,
            cwd=cwd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        try:
            stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=timeout)
            return (stdout.decode() + stderr.decode()).strip()
        except asyncio.TimeoutError:
            process.kill()
            return "Error: Command timed out."
            
    except Exception as e:
        return f"Error executing command: {str(e)}"

@mcp.tool()
async def read_research_file(path: str) -> str:
    """Reads a file from the research repository."""
    full_path = os.path.join(SAFE_REPO_PATH, path) if not os.path.isabs(path) else path
    if not full_path.startswith(SAFE_REPO_PATH):
        return "Error: Path outside of safe research scope."
    
    try:
        with open(full_path, "r") as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {str(e)}"

@mcp.tool()
async def write_research_file(path: str, content: str, append: bool = False) -> str:
    """Writes or appends to a file in the research repository."""
    full_path = os.path.join(SAFE_REPO_PATH, path) if not os.path.isabs(path) else path
    if not full_path.startswith(SAFE_REPO_PATH):
        return "Error: Path outside of safe research scope."
    
    mode = "a" if append else "w"
    try:
        with open(full_path, mode) as f:
            f.write(content)
        return f"Successfully {'appended to' if append else 'wrote to'} {path}"
    except Exception as e:
        return f"Error writing file: {str(e)}"

if __name__ == "__main__":
    mcp.run()
