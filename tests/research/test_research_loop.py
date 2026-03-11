"""
BDD-style test for the ResearchAgent loop.
Adapted from the Dave Farley 4-layer approach for the standalone ADK swarm.
"""
import asyncio
import pytest
from dataclasses import dataclass
from swarm.drivers import ResearchResult, ResearchProtocolDriver


class MockMCPClient:
    """Layer 4: External System Stub."""
    def __init__(self):
        self.files = {}
        self.commands = []

    async def call_tool(self, name, args):
        if name == "execute_command":
            self.commands.append(args.get("command", ""))
            return "OK"
        if name == "read_research_file":
            return self.files.get(args["path"], "Error: not found")
        if name == "write_research_file":
            path = args["path"]
            content = args["content"]
            if args.get("append"):
                self.files[path] = self.files.get(path, "") + content
            else:
                self.files[path] = content
            return "OK"
        raise ValueError(f"Unknown tool: {name}")


class MockResearchDriver(ResearchProtocolDriver):
    """Layer 4: Mock driver that doesn't hit real filesystem or git."""
    def __init__(self):
        self.mcp = MockMCPClient()
        self.repo_path = "/tmp/test_research_env"
        self.setup_done = False
        self.results = []

    async def ensure_setup(self) -> bool:
        self.setup_done = True
        return True

    async def run_experiment(self, description: str) -> ResearchResult:
        return ResearchResult(
            val_bpb=1.42,
            peak_vram_gb=0.0,
            status="keep",
            description=description
        )

    async def log_result(self, result: ResearchResult) -> None:
        self.results.append(result)


# Layer 1 & 2: DSL
class ResearchDSL:
    def __init__(self, driver: MockResearchDriver):
        self.driver = driver

    async def given_fresh_environment(self):
        self.driver.setup_done = False
        self.driver.results = []

    async def when_setup_is_triggered(self):
        await self.driver.ensure_setup()

    async def when_experiment_runs(self, description="test"):
        result = await self.driver.run_experiment(description)
        await self.driver.log_result(result)

    def then_setup_is_complete(self):
        assert self.driver.setup_done is True

    def then_result_is_logged(self):
        assert len(self.driver.results) > 0

    def then_result_has_valid_bpb(self):
        assert self.driver.results[-1].val_bpb > 0

    def then_result_status_is(self, expected: str):
        assert self.driver.results[-1].status == expected


# Layer 1: Test Cases
@pytest.mark.asyncio
async def test_research_agent_setup_scenario():
    """BDD: Research Agent can initialize its environment."""
    driver = MockResearchDriver()
    dsl = ResearchDSL(driver)

    await dsl.given_fresh_environment()
    await dsl.when_setup_is_triggered()
    dsl.then_setup_is_complete()


@pytest.mark.asyncio
async def test_research_agent_experiment_scenario():
    """BDD: Research Agent can run an experiment and log results."""
    driver = MockResearchDriver()
    dsl = ResearchDSL(driver)

    await dsl.given_fresh_environment()
    await dsl.when_setup_is_triggered()
    await dsl.when_experiment_runs("baseline")
    dsl.then_result_is_logged()
    dsl.then_result_has_valid_bpb()
    dsl.then_result_status_is("keep")


@pytest.mark.asyncio
async def test_mcp_client_file_operations():
    """BDD: MCP client can read/write/append files."""
    mcp = MockMCPClient()

    # Write
    await mcp.call_tool("write_research_file", {"path": "test.txt", "content": "hello"})
    result = await mcp.call_tool("read_research_file", {"path": "test.txt"})
    assert result == "hello"

    # Append
    await mcp.call_tool("write_research_file", {"path": "test.txt", "content": " world", "append": True})
    result = await mcp.call_tool("read_research_file", {"path": "test.txt"})
    assert result == "hello world"

    # Missing file
    result = await mcp.call_tool("read_research_file", {"path": "missing.txt"})
    assert "Error" in result
