
"""Tests for Connectome event logging integration."""

import pytest

from zeus.connectome import Connectome
from zeus.event_log import EventLog
from zeus.models import Edge, Node


@pytest.fixture
def connectome() -> Connectome:
    graph = Connectome()
    graph.add_node(Node("a", "concept", "Artificial Intelligence"))
    graph.add_node(Node("b", "concept", "Learning"))
    return graph


def test_node_creation_records_event(connectome: Connectome) -> None:
    events = connectome.event_log.get_events()

    assert len(events) == 2
    assert events[0].event_type == "node_created"
    assert events[0].payload["node_id"] == "a"
    assert events[1].payload["node_id"] == "b"


def test_edge_creation_records_event(connectome: Connectome) -> None:
    connectome.add_edge(Edge("a", "b", "related_to", weight=0.5))

    events = connectome.event_log.get_events()
    event = events[-1]

    assert event.event_type == "edge_created"
    assert event.sequence == 3
    assert event.payload == {
        "source": "a",
        "target": "b",
        "edge_type": "related_to",
        "weight": 0.5,
    }


def test_weight_update_records_old_and_new_weights(
    connectome: Connectome,
) -> None:
    connectome.add_edge(Edge("a", "b", "related_to", weight=0.5))

    connectome.update_edge_weight("a", "b", 0.8)

    event = connectome.event_log.get_events()[-1]

    assert event.event_type == "edge_weight_updated"
    assert event.payload["old_weight"] == 0.5
    assert event.payload["new_weight"] == 0.8


def test_failed_node_creation_records_no_event(
    connectome: Connectome,
) -> None:
    before = connectome.event_log.event_count()

    with pytest.raises(ValueError, match="already exists"):
        connectome.add_node(Node("a", "concept", "Another Concept"))

    assert connectome.event_log.event_count() == before


def test_duplicate_normalized_label_records_no_event(
    connectome: Connectome,
) -> None:
    before = connectome.event_log.event_count()

    with pytest.raises(ValueError, match="Normalized label"):
        connectome.add_node(Node("c", "concept", " artificial intelligence "))

    assert connectome.event_log.event_count() == before


def test_failed_edge_creation_records_no_event(
    connectome: Connectome,
) -> None:
    before = connectome.event_log.event_count()

    with pytest.raises(ValueError, match="Source node"):
        connectome.add_edge(Edge("missing", "b", "related_to"))

    assert connectome.event_log.event_count() == before


def test_duplicate_edge_records_no_event(
    connectome: Connectome,
) -> None:
    edge = Edge("a", "b", "related_to")
    connectome.add_edge(edge)
    before = connectome.event_log.event_count()

    with pytest.raises(ValueError, match="already exists"):
        connectome.add_edge(edge)

    assert connectome.event_log.event_count() == before


def test_failed_weight_update_records_no_event(
    connectome: Connectome,
) -> None:
    before = connectome.event_log.event_count()

    with pytest.raises(ValueError, match="does not exist"):
        connectome.update_edge_weight("a", "b", 0.8)

    assert connectome.event_log.event_count() == before


def test_connectome_accepts_shared_event_log() -> None:
    event_log = EventLog()
    first = Connectome(event_log)
    second = Connectome(event_log)

    first.add_node(Node("a", "concept", "First"))
    second.add_node(Node("b", "concept", "Second"))

    events = event_log.get_events()

    assert len(events) == 2
    assert events[0].payload["node_id"] == "a"
    assert events[1].payload["node_id"] == "b"
    assert first.event_log is event_log
    assert second.event_log is event_log


def test_default_connectome_has_its_own_event_log() -> None:
    first = Connectome()
    second = Connectome()

    first.add_node(Node("a", "concept", "First"))

    assert first.event_log.event_count() == 1
    assert second.event_log.event_count() == 0
