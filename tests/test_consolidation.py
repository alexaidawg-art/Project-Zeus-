
"""Tests for deterministic Zeus relationship consolidation."""

import pytest

from zeus.config import Config
from zeus.connectome import Connectome
from zeus.consolidation import ConsolidationEngine
from zeus.models import Edge, Node


@pytest.fixture
def connectome() -> Connectome:
    graph = Connectome()
    graph.add_node(Node("a", "concept", "Artificial Intelligence"))
    graph.add_node(Node("b", "concept", "Learning"))
    graph.add_node(Node("c", "concept", "Memory"))
    graph.add_edge(Edge("a", "b", "related_to", weight=0.8))
    graph.add_edge(Edge("b", "c", "related_to", weight=0.4))
    return graph


@pytest.fixture
def engine() -> ConsolidationEngine:
    return ConsolidationEngine(Config())


def test_consolidate_strengthens_qualifying_relationship(
    connectome: Connectome,
    engine: ConsolidationEngine,
) -> None:
    count = engine.consolidate(connectome)

    edge = connectome.get_edge("a", "b")
    assert edge is not None
    assert edge.weight == pytest.approx(0.96)
    assert count == 1


def test_consolidate_leaves_weak_relationship_unchanged(
    connectome: Connectome,
    engine: ConsolidationEngine,
) -> None:
    engine.consolidate(connectome)

    edge = connectome.get_edge("b", "c")
    assert edge is not None
    assert edge.weight == pytest.approx(0.4)


def test_consolidate_includes_threshold_boundary(
    connectome: Connectome,
) -> None:
    connectome.update_edge_weight("b", "c", 0.6)
    engine = ConsolidationEngine(Config())

    count = engine.consolidate(connectome)

    edge = connectome.get_edge("b", "c")
    assert edge is not None
    assert edge.weight > 0.6
    assert count == 2


def test_consolidate_respects_maximum_weight(
    connectome: Connectome,
) -> None:
    connectome.update_edge_weight("a", "b", 0.99)
    engine = ConsolidationEngine(Config())

    engine.consolidate(connectome)

    edge = connectome.get_edge("a", "b")
    assert edge is not None
    assert edge.weight <= 1.0


def test_consolidate_preserves_edge_type(
    connectome: Connectome,
    engine: ConsolidationEngine,
) -> None:
    engine.consolidate(connectome)

    edge = connectome.get_edge("a", "b")
    assert edge is not None
    assert edge.edge_type == "related_to"


def test_consolidate_empty_graph() -> None:
    graph = Connectome()
    engine = ConsolidationEngine(Config())

    assert engine.consolidate(graph) == 0


def test_consolidate_graph_without_qualifying_edges(
    connectome: Connectome,
) -> None:
    connectome.update_edge_weight("a", "b", 0.2)
    connectome.update_edge_weight("b", "c", 0.3)
    engine = ConsolidationEngine(Config())

    count = engine.consolidate(connectome)

    assert count == 0
    assert connectome.get_edge("a", "b").weight == 0.2
    assert connectome.get_edge("b", "c").weight == 0.3


def test_consolidate_is_deterministic(
    connectome: Connectome,
) -> None:
    first = ConsolidationEngine(Config())
    second = ConsolidationEngine(Config())

    first_result = first.consolidate(connectome)
    first_weights = {
        edge: connectome.get_edge(*edge).weight
        for edge in [("a", "b"), ("b", "c")]
    }

    second_result = second.consolidate(connectome)

    assert first_result == 1
    assert second_result == 1
    assert first_weights[("a", "b")] == pytest.approx(0.96)


def test_consolidate_uses_configured_strength(
    connectome: Connectome,
) -> None:
    engine = ConsolidationEngine(
        Config(consolidation_strength=1.0)
    )

    engine.consolidate(connectome)

    edge = connectome.get_edge("a", "b")
    assert edge is not None
    assert edge.weight == pytest.approx(0.9)
