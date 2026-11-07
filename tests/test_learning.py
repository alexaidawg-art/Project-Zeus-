
"""Tests for deterministic Zeus learning and relationship updates."""

import pytest

from zeus.config import Config
from zeus.connectome import Connectome
from zeus.learning import LearningEngine
from zeus.models import Edge, Node


@pytest.fixture
def connectome() -> Connectome:
    graph = Connectome()
    graph.add_node(Node("a", "concept", "Artificial Intelligence"))
    graph.add_node(Node("b", "concept", "Learning"))
    graph.add_node(Node("c", "concept", "Memory"))
    graph.add_edge(Edge("a", "b", "related_to", weight=0.5))
    graph.add_edge(Edge("b", "c", "related_to", weight=0.8))
    return graph


@pytest.fixture
def engine() -> LearningEngine:
    return LearningEngine(Config())


def test_reinforce_increases_weight(
    connectome: Connectome,
    engine: LearningEngine,
) -> None:
    engine.reinforce(connectome, [("a", "b")])

    edge = connectome.get_edge("a", "b")
    assert edge is not None
    assert edge.weight == pytest.approx(0.53)


def test_reinforce_respects_max_weight(
    connectome: Connectome,
) -> None:
    graph = LearningEngine(Config(learning_rate=1.0))
    graph.reinforce(connectome, [("a", "b")])

    edge = connectome.get_edge("a", "b")
    assert edge is not None
    assert edge.weight == 1.0


def test_reinforce_preserves_edge_attributes(
    connectome: Connectome,
    engine: LearningEngine,
) -> None:
    connectome.update_edge_weight("a", "b", 0.5)
    engine.reinforce(connectome, [("a", "b")])

    edge = connectome.get_edge("a", "b")
    assert edge is not None
    assert edge.edge_type == "related_to"


def test_reinforce_rejects_missing_relationship(
    connectome: Connectome,
    engine: LearningEngine,
) -> None:
    with pytest.raises(ValueError, match="does not exist"):
        engine.reinforce(connectome, [("c", "a")])


def test_reinforce_empty_list_changes_nothing(
    connectome: Connectome,
    engine: LearningEngine,
) -> None:
    before = connectome.get_edge("a", "b")

    engine.reinforce(connectome, [])

    assert connectome.get_edge("a", "b") == before


def test_reinforce_batch_is_order_independent(
    connectome: Connectome,
) -> None:
    engine = LearningEngine(Config())
    engine.reinforce(connectome, [("a", "b"), ("b", "c")])

    first = connectome.get_edge("a", "b")
    second = connectome.get_edge("b", "c")

    assert first is not None
    assert second is not None
    assert first.weight == pytest.approx(0.53)
    assert second.weight == pytest.approx(0.812)


def test_decay_reduces_weight(
    connectome: Connectome,
    engine: LearningEngine,
) -> None:
    engine.decay(connectome, [("a", "b")])

    edge = connectome.get_edge("a", "b")
    assert edge is not None
    assert edge.weight == pytest.approx(0.3)


def test_decay_all_relationships_when_omitted(
    connectome: Connectome,
    engine: LearningEngine,
) -> None:
    engine.decay(connectome)

    first = connectome.get_edge("a", "b")
    second = connectome.get_edge("b", "c")

    assert first is not None
    assert second is not None
    assert first.weight == pytest.approx(0.3)
    assert second.weight == pytest.approx(0.48)


def test_decay_rejects_missing_relationship(
    connectome: Connectome,
    engine: LearningEngine,
) -> None:
    with pytest.raises(ValueError, match="does not exist"):
        engine.decay(connectome, [("c", "a")])


def test_decay_empty_list_changes_nothing(
    connectome: Connectome,
    engine: LearningEngine,
) -> None:
    before = connectome.get_edge("a", "b")

    engine.decay(connectome, [])

    assert connectome.get_edge("a", "b") == before


def test_learn_applies_decay_before_reinforcement(
    connectome: Connectome,
) -> None:
    engine = LearningEngine(Config())
    engine.learn(
        connectome,
        reinforced=[("a", "b")],
        decayed=[("a", "b")],
    )

    edge = connectome.get_edge("a", "b")
    assert edge is not None
    assert edge.weight == pytest.approx(0.342)


def test_learn_can_reinforce_without_decay(
    connectome: Connectome,
) -> None:
    engine = LearningEngine(Config())
    engine.learn(
        connectome,
        reinforced=[("a", "b")],
        decayed=[],
    )

    edge = connectome.get_edge("a", "b")
    assert edge is not None
    assert edge.weight == pytest.approx(0.53)


def test_learn_can_decay_without_reinforcement(
    connectome: Connectome,
) -> None:
    engine = LearningEngine(Config())
    engine.learn(
        connectome,
        reinforced=[],
        decayed=[("a", "b")],
    )

    edge = connectome.get_edge("a", "b")
    assert edge is not None
    assert edge.weight == pytest.approx(0.3)


def test_learn_decays_all_when_decay_list_omitted(
    connectome: Connectome,
) -> None:
    engine = LearningEngine(Config())
    engine.learn(connectome, reinforced=[])

    first = connectome.get_edge("a", "b")
    second = connectome.get_edge("b", "c")

    assert first is not None
    assert second is not None
    assert first.weight == pytest.approx(0.3)
    assert second.weight == pytest.approx(0.48)


def test_learn_rejects_duplicate_reinforcement(
    connectome: Connectome,
) -> None:
    engine = LearningEngine(Config())

    with pytest.raises(ValueError, match="Duplicate reinforcement"):
        engine.learn(
            connectome,
            reinforced=[("a", "b"), ("a", "b")],
            decayed=[],
        )


def test_learn_rejects_duplicate_decay(
    connectome: Connectome,
) -> None:
    engine = LearningEngine(Config())

    with pytest.raises(ValueError, match="Duplicate decay"):
        engine.learn(
            connectome,
            reinforced=[],
            decayed=[("a", "b"), ("a", "b")],
        )


def test_learn_rejects_missing_relationship(
    connectome: Connectome,
) -> None:
    engine = LearningEngine(Config())

    with pytest.raises(ValueError, match="does not exist"):
        engine.learn(
            connectome,
            reinforced=[("c", "a")],
            decayed=[],
        )


def test_learn_is_order_independent(
    connectome: Connectome,
) -> None:
    engine = LearningEngine(Config())

    engine.learn(
        connectome,
        reinforced=[("a", "b"), ("b", "c")],
        decayed=[("b", "c"), ("a", "b")],
    )

    first = connectome.get_edge("a", "b")
    second = connectome.get_edge("b", "c")

    assert first is not None
    assert second is not None
    assert first.weight == pytest.approx(0.342)
    assert second.weight == pytest.approx(0.486)
