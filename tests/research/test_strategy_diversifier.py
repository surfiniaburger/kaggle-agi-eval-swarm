"""
Canon TDD Test Suite: StrategyDiversifier

Test List (from implementation_plan.md):
1. [x] test_diversifier_allows_first_category — First proposal always passes
2. [x] test_diversifier_allows_different_categories — Alternating categories pass
3. [x] test_diversifier_rejects_same_category_streak — 3+ same categories rejected
4. [x] test_diversifier_classifies_learning_changes — Learning keywords correctly categorized
5. [x] test_diversifier_classifies_metacognition_changes — Metacognition keywords correctly categorized
"""
import pytest
from swarm.agents import StrategyDiversifier


def test_diversifier_allows_first_category():
    """GIVEN a fresh diversifier, WHEN the first strategy is submitted,
    THEN it should always be allowed regardless of category."""
    diversifier = StrategyDiversifier(max_streak=2)
    
    result = diversifier.check("Design a task testing memory and recall for few_shot learning")
    
    assert result.allowed is True
    assert result.category == "learning"


def test_diversifier_allows_different_categories():
    """GIVEN two learning strategies, WHEN a metacognition strategy is submitted,
    THEN it should be allowed because the category changed."""
    diversifier = StrategyDiversifier(max_streak=2)
    
    diversifier.check("Design a task testing memory and recall for few_shot learning")
    diversifier.check("A task focusing on adaptation and knowledge_acquisition")
    result = diversifier.check("Evaluate model metacognition and confidence in self_correction")
    
    assert result.allowed is True
    assert result.category == "metacognition"


def test_diversifier_rejects_same_category_streak():
    """GIVEN two consecutive learning strategies,
    WHEN a third learning strategy is submitted,
    THEN it should be REJECTED to force exploration."""
    diversifier = StrategyDiversifier(max_streak=2)
    
    diversifier.check("Design a task testing memory and recall for few_shot learning")
    diversifier.check("A task focusing on adaptation and knowledge_acquisition")
    result = diversifier.check("Another task testing in_context memory")
    
    assert result.allowed is False
    assert result.category == "learning"
    assert "Explore a different axis" in result.reason


def test_diversifier_classifies_learning_changes():
    """GIVEN various learning-related texts,
    WHEN classified, THEN they should all map to 'learning'."""
    diversifier = StrategyDiversifier()
    
    assert diversifier.classify("testing memory and recall") == "learning"
    assert diversifier.classify("focusing on adaptation") == "learning"
    assert diversifier.classify("few_shot in_context examples") == "learning"


def test_diversifier_classifies_metacognition_changes():
    """GIVEN various metacognition-related texts,
    WHEN classified, THEN they should all map to 'metacognition'."""
    diversifier = StrategyDiversifier()
    
    assert diversifier.classify("measure confidence and doubt") == "metacognition"
    assert diversifier.classify("force hallucination and self_correction") == "metacognition"
    assert diversifier.classify("knowing when to express uncertainty") == "metacognition"
