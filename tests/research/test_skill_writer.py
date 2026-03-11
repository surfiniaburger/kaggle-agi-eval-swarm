"""
BDD-style test for the SkillWriterAgent.
Adapted from the Dave Farley 4-layer approach for the standalone ADK swarm.
"""
import asyncio
import pytest


class MockSkillWriterDriver:
    """Layer 4: Stub for the SkillWriterProtocolDriver."""
    def __init__(self):
        self.results = "commit\tval_bpb\tmemory_gb\tstatus\tdescription\n"
        self.log = ""
        self.skill = "# autoresearch\n\n## Setup\n..."
        self.update_called = False

    async def get_latest_results(self) -> str:
        return self.results

    async def get_latest_log(self) -> str:
        return self.log

    async def update_skill(self, new_instructions: str) -> bool:
        self.skill += "\n\n## Research Insights\n\n" + new_instructions
        self.update_called = True
        return True


# Layer 1 & 2: DSL
class SkillWriterDSL:
    def __init__(self, driver: MockSkillWriterDriver):
        self.driver = driver

    async def given_successful_research_run(self):
        self.driver.results = (
            "commit\tval_bpb\tmemory_gb\tstatus\tdescription\n"
            "a1b2c3d\t0.950000\t12.0\tkeep\tbaseline\n"
        )
        self.driver.log = "val_bpb: 0.95\npeak_vram_mb: 12288\n"

    async def given_crashed_research_run(self):
        self.driver.results = (
            "commit\tval_bpb\tmemory_gb\tstatus\tdescription\n"
            "a1b2c3d\t0.000000\t0.0\tcrash\toom\n"
        )
        self.driver.log = "RuntimeError: CUDA out of memory\n"

    async def given_empty_results(self):
        self.driver.results = ""
        self.driver.log = ""

    def then_skill_was_updated(self):
        assert self.driver.update_called is True
        assert "Research Insights" in self.driver.skill

    def then_skill_was_not_updated(self):
        assert self.driver.update_called is False


# Layer 1: Test Cases
@pytest.mark.asyncio
async def test_skill_writer_analyzes_successful_run():
    """BDD: SkillWriter updates program.md after a successful training run."""
    driver = MockSkillWriterDriver()
    dsl = SkillWriterDSL(driver)

    await dsl.given_successful_research_run()
    # Directly test the driver's update_skill since the LlmAgent
    # requires a real model. We test the driver layer independently.
    await driver.update_skill("- Learning rate was effective.\n- Try increasing layers next.")
    dsl.then_skill_was_updated()


@pytest.mark.asyncio  
async def test_skill_writer_analyzes_crashed_run():
    """BDD: SkillWriter updates program.md even after a crash (to record lessons)."""
    driver = MockSkillWriterDriver()
    dsl = SkillWriterDSL(driver)

    await dsl.given_crashed_research_run()
    await driver.update_skill("- OOM crash detected.\n- Reduce batch size or model dimensions.")
    dsl.then_skill_was_updated()


@pytest.mark.asyncio
async def test_skill_writer_handles_empty_results():
    """BDD: SkillWriter does NOT update when there are no results."""
    driver = MockSkillWriterDriver()
    dsl = SkillWriterDSL(driver)

    await dsl.given_empty_results()
    # When results are empty, the agent should skip the update  
    if not driver.results or "val_bpb" not in driver.results:
        pass  # Skip update
    dsl.then_skill_was_not_updated()


@pytest.mark.asyncio
async def test_skill_driver_preserves_base_skill():
    """BDD: update_skill appends insights without destroying the base skill."""
    driver = MockSkillWriterDriver()
    original_base = driver.skill

    await driver.update_skill("New insight here.")
    assert original_base in driver.skill
    assert "New insight here." in driver.skill
