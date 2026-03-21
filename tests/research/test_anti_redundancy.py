import pytest
from swarm.agents import AntiRedundancyFilter
from swarm.drivers import ResearchResult

def create_result(score: float) -> ResearchResult:
    return ResearchResult(val_score=score, peak_vram_gb=1.0, status="keep", description="")

def test_anti_redundancy_not_enough_history():
    filter = AntiRedundancyFilter(threshold=0.005, window=3)
    history = [create_result(0.5), create_result(0.501)]
    assert filter.check(history) is False

def test_anti_redundancy_stagnant():
    filter = AntiRedundancyFilter(threshold=0.005, window=3)
    history = [
        create_result(0.500),
        create_result(0.502),
        create_result(0.504)
    ]
    # Max delta is 0.504 - 0.500 = 0.004 < 0.005 -> Stagnant
    assert filter.check(history) is True

def test_anti_redundancy_improving():
    filter = AntiRedundancyFilter(threshold=0.005, window=3)
    history = [
        create_result(0.500),
        create_result(0.510),
        create_result(0.520)
    ]
    # Max delta is 0.520 - 0.500 = 0.020 >= 0.005 -> Not Stagnant
    assert filter.check(history) is False
