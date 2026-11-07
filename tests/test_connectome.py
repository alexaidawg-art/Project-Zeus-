
"""Tests for the Zeus Connectome graph manager."""

import networkx as nx
import pytest

from zeus.connectome import Connectome
from zeus.models import Edge, Node


@pytest.fixture
def connectome() -> Connectome:
    return Connectome()


@pytest.fixture
def populated_connectome(connectome: Connectome) -> Connectome:
    connectome.add_node(Node("a", "concept", "Artificial Intelligence"))
    connectome.add_node(Node("b", "concept", "Learning"))
    return connectome


def test_empty_connectome_counts(connectome: Connectome) -> None:
    assert connectome.node_count() == 0
    assert connectome.edge_count() == 0


def test_add_and_retrieve_node(connectome: Connectome) -> None:
    node = Node("a", "concept", "Artificial Intelligence", importance=0.8)
    connectome.add_node(node)

    result = connectome.get_node("a")

    assert result == node
    assert connectome.node_count() == 1


def test_get_missing_node_returns_none(connectome: Connectome) -> None:
    assert connectome.get_node("missing") is None


def test_has_node(connectome: Connectome) -> None:
    connectome.add_node(Node("a", "concept", "AI"))

    assert connectome.has_node("a")
    assert not connectome.has_node("missing")


def test_reject_duplicate_node_id(populated_connectome: Connectome) -> None:
    with pytest.raises(ValueError, match="Node ID already exists"):
        populated_connectome.add_node(Node("a", "concept", "Robotics"))


def test_reject_duplicate_normalized_label(
    populated_connectome: Connectome,
) -> None:
    with pytest.raises(ValueError, match="Normalized label already exists"):
        populated_connectome.add_node(
            Node("c", "concept", "  ARTIFICIAL   INTELLIGENCE ")
        )


def test_node_attributes_are_copied_on_add(connectome: Connectome) -> None:
    attributes = {"source": "test"}
    node = Node("a", "concept", "AI", attributes=attributes)

    connectome.add_node(node)
    attributes["source"] = "changed"

    result = connectome.get_node("a")
    assert result is not None
    assert result.attributes["source"] == "test"


def test_node_attributes_are_copied_on_retrieval(
    connectome: Connectome,
) -> None:
    connectome.add_node(Node("a", "concept", "AI", attributes={"source": "test"}))

    result = connectome.get_node("a")
    assert result is not None
    result.attributes["source"] = "changed"

    stored = connectome.get_node("a")
    assert stored is not None
    assert stored.attributes["source"] == "test"


def test_add_and_retrieve_edge(populated_connectome: Connectome) -> None:
    edge = Edge("a", "b", "related_to", weight=0.8)
    populated_connectome.add_edge(edge)

    assert populated_connectome.get_edge("a", "b") == edge
    assert populated_connectome.edge_count() == 1


def test_get_missing_edge_returns_none(
    populated_connectome: Connectome,
) -> None:
    assert populated_connectome.get_edge("a", "b") is None


def test_reject_missing_source_node(
    populated_connectome: Connectome,
) -> None:
    with pytest.raises(ValueError, match="Source node does not exist"):
        populated_connectome.add_edge(Edge("missing", "b", "related_to"))


def test_reject_missing_target_node(
    populated_connectome: Connectome,
) -> None:
    with pytest.raises(ValueError, match="Target node does not exist"):
        populated_connectome.add_edge(Edge("a", "missing", "related_to"))


def test_reject_duplicate_edge(
    populated_connectome: Connectome,
) -> None:
    edge = Edge("a", "b", "related_to")
    populated_connectome.add_edge(edge)

    with pytest.raises(ValueError, match="Relationship already exists"):
        populated_connectome.add_edge(edge)


def test_reverse_edges_are_distinct(
    populated_connectome: Connectome,
) -> None:
    populated_connectome.add_edge(Edge("a", "b", "supports"))
    populated_connectome.add_edge(Edge("b", "a", "supported_by"))

    assert populated_connectome.edge_count() == 2


def test_edge_attributes_are_copied(populated_connectome: Connectome) -> None:
    attributes = {"context": "test"}
    edge = Edge("a", "b", "related_to", attributes=attributes)

    populated_connectome.add_edge(edge)
    attributes["context"] = "changed"

    result = populated_connectome.get_edge("a", "b")
    assert result is not None
    assert result.attributes["context"] == "test"


def test_to_graph_returns_copy(populated_connectome: Connectome) -> None:
    graph = populated_connectome.to_graph()

    assert isinstance(graph, nx.DiGraph)
    assert graph.number_of_nodes() == 2

    graph.add_node("external")

    assert populated_connectome.node_count() == 2
    assert not populated_connectome.has_node("external")


def test_graph_copy_preserves_relationships(
    populated_connectome: Connectome,
) -> None:
    populated_connectome.add_edge(Edge("a", "b", "related_to", weight=0.7))

    graph = populated_connectome.to_graph()

    assert graph.has_edge("a", "b")
    assert graph.edges["a", "b"]["weight"] == 0.7
