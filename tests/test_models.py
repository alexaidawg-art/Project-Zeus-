"""Tests for model-independent Node and Edge structures."""

import math

import pytest

from zeus.models import Edge, Node


def test_node_defaults() -> None:
    node = Node(id="1", node_type="concept", label="Artificial Intelligence")

    assert node.importance == 0.5
    assert node.confidence == 0.5
    assert node.attributes == {}


def test_node_normalized_label() -> None:
    node = Node(
        id="1",
        node_type="concept",
        label="  Artificial   Intelligence  ",
    )

    assert node.normalized_label == "artificial intelligence"


def test_node_attributes_are_independent() -> None:
    first = Node(id="1", node_type="concept", label="AI")
    second = Node(id="2", node_type="concept", label="Memory")

    first.attributes["source"] = "test"

    assert second.attributes == {}


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("id", ""),
        ("node_type", " "),
        ("label", ""),
    ],
)
def test_node_rejects_empty_text(field: str, value: str) -> None:
    values = {"id": "1", "node_type": "concept", "label": "AI"}
    values[field] = value

    with pytest.raises(ValueError):
        Node(**values)


@pytest.mark.parametrize("field", ["importance", "confidence"])
@pytest.mark.parametrize("value", [-0.1, 1.1, math.nan, math.inf, -math.inf])
def test_node_rejects_invalid_scores(field: str, value: float) -> None:
    values = {"id": "1", "node_type": "concept", "label": "AI"}
    values[field] = value

    with pytest.raises(ValueError):
        Node(**values)


@pytest.mark.parametrize("field", ["importance", "confidence"])
def test_node_rejects_boolean_scores(field: str) -> None:
    values = {"id": "1", "node_type": "concept", "label": "AI"}
    values[field] = True

    with pytest.raises(TypeError):
        Node(**values)


def test_node_rejects_non_dictionary_attributes() -> None:
    with pytest.raises(TypeError, match="attributes"):
        Node(
            id="1",
            node_type="concept",
            label="AI",
            attributes=[],  # type: ignore[arg-type]
        )


def test_edge_defaults() -> None:
    edge = Edge(source="1", target="2", edge_type="related_to")

    assert edge.weight == 0.5
    assert edge.attributes == {}


def test_edge_normalized_type() -> None:
    edge = Edge(
        source="1",
        target="2",
        edge_type="  related   to ",
    )

    assert edge.normalized_type == "RELATED TO"


def test_edge_attributes_are_independent() -> None:
    first = Edge(source="1", target="2", edge_type="related")
    second = Edge(source="2", target="3", edge_type="supports")

    first.attributes["source"] = "test"

    assert second.attributes == {}


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("source", ""),
        ("target", " "),
        ("edge_type", ""),
    ],
)
def test_edge_rejects_empty_text(field: str, value: str) -> None:
    values = {"source": "1", "target": "2", "edge_type": "related"}
    values[field] = value

    with pytest.raises(ValueError):
        Edge(**values)


@pytest.mark.parametrize("value", [-0.1, 1.1, math.nan, math.inf, -math.inf])
def test_edge_rejects_invalid_weight(value: float) -> None:
    with pytest.raises(ValueError):
        Edge(source="1", target="2", edge_type="related", weight=value)


def test_edge_rejects_boolean_weight() -> None:
    with pytest.raises(TypeError):
        Edge(
            source="1",
            target="2",
            edge_type="related",
            weight=True,
        )


def test_edge_rejects_non_dictionary_attributes() -> None:
    with pytest.raises(TypeError, match="attributes"):
        Edge(
            source="1",
            target="2",
            edge_type="related",
            attributes=[],  # type: ignore[arg-type]
        )