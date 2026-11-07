
"""Tests for Connectome relationship updates."""

import pytest

from zeus.connectome import Connectome
from zeus.models import Edge, Node


@pytest.fixture
def connectome() -> Connectome:
    graph = Connectome()
    graph.add_node(Node("a", "concept", "Artificial Intelligence"))
    graph.add_node(Node("b", "concept", "Learning"))
    graph.add_edge(
        Edge("a", "b", "related_to", weight=0.5, attributes={"source": "test"})
    )
    return graph


def test_update_edge_weight(connectome: Connectome) -> None:
    connectome.update_edge_weight("a", "b", 0.8)

    edge = connectome.get_edge("a", "b")

    assert edge is not None
    assert edge.weight == 0.8


def test_update_preserves_edge_type(connectome: Connectome) -> None:
    connectome.update_edge_weight("a", "b", 0.8)

    edge = connectome.get_edge("a", "b")

    assert edge is not None
    assert edge.edge_type == "related_to"


def test_update_preserves_attributes(connectome: Connectome) -> None:
    connectome.update_edge_weight("a", "b", 0.8)

    edge = connectome.get_edge("a", "b")

    assert edge is not None
    assert edge.attributes == {"source": "test"}


def test_update_rejects_missing_relationship(
    connectome: Connectome,
) -> None:
    with pytest.raises(ValueError, match="Relationship does not exist"):
        connectome.update_edge_weight("b", "a", 0.8)


@pytest.mark.parametrize("weight", [-0.1, 1.1, float("nan"), float("inf")])
def test_update_rejects_invalid_weight(
    connectome: Connectome,
    weight: float,
) -> None:
    with pytest.raises(ValueError):
        connectome.update_edge_weight("a", "b", weight)
