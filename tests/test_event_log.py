
"""Tests for Zeus structured event logging."""

from dataclasses import FrozenInstanceError
from datetime import datetime

import pytest

from zeus.event_log import EventLog


def test_record_creates_event() -> None:
    log = EventLog()

    event = log.record(
        "node_created",
        {"node_id": "alpha"},
        "2026-11-07T12:00:00+00:00",
    )

    assert event.sequence == 1
    assert event.event_type == "node_created"
    assert event.timestamp == "2026-11-07T12:00:00+00:00"
    assert event.payload == {"node_id": "alpha"}


def test_sequence_numbers_increase() -> None:
    log = EventLog()

    first = log.record("node_created")
    second = log.record("edge_created")
    third = log.record("learning_cycle")

    assert (first.sequence, second.sequence, third.sequence) == (1, 2, 3)


def test_record_uses_utc_timestamp_when_omitted() -> None:
    log = EventLog()

    event = log.record("system_started")
    parsed = datetime.fromisoformat(event.timestamp)

    assert parsed.tzinfo is not None
    assert parsed.utcoffset().total_seconds() == 0


def test_record_strips_event_type_whitespace() -> None:
    log = EventLog()

    event = log.record("  node_created  ")

    assert event.event_type == "node_created"


def test_record_uses_empty_payload_by_default() -> None:
    log = EventLog()

    event = log.record("system_started")

    assert event.payload == {}


def test_get_events_returns_sequence_order() -> None:
    log = EventLog()

    log.record("first")
    log.record("second")
    log.record("third")

    events = log.get_events()

    assert [event.event_type for event in events] == [
        "first",
        "second",
        "third",
    ]


def test_get_events_returns_tuple() -> None:
    log = EventLog()
    log.record("system_started")

    assert isinstance(log.get_events(), tuple)


def test_get_events_by_type_filters_events() -> None:
    log = EventLog()

    log.record("node_created", {"node_id": "a"})
    log.record("edge_created", {"source": "a", "target": "b"})
    log.record("node_created", {"node_id": "b"})

    events = log.get_events_by_type("node_created")

    assert len(events) == 2
    assert all(event.event_type == "node_created" for event in events)


def test_get_events_by_unknown_type_returns_empty_tuple() -> None:
    log = EventLog()
    log.record("node_created")

    assert log.get_events_by_type("unknown") == ()


def test_event_count_tracks_records() -> None:
    log = EventLog()

    assert log.event_count() == 0

    log.record("first")
    log.record("second")

    assert log.event_count() == 2


def test_event_record_is_frozen() -> None:
    log = EventLog()
    event = log.record("node_created")

    with pytest.raises(FrozenInstanceError):
        event.sequence = 99  # type: ignore[misc]


@pytest.mark.parametrize("event_type", ["", "   "])
def test_record_rejects_empty_event_type(event_type: str) -> None:
    log = EventLog()

    with pytest.raises(ValueError, match="non-empty"):
        log.record(event_type)


def test_record_rejects_non_string_event_type() -> None:
    log = EventLog()

    with pytest.raises(ValueError, match="non-empty"):
        log.record(123)  # type: ignore[arg-type]


def test_record_rejects_non_dictionary_payload() -> None:
    log = EventLog()

    with pytest.raises(TypeError, match="dictionary"):
        log.record("node_created", ["alpha"])  # type: ignore[arg-type]


def test_record_rejects_whitespace_timestamp() -> None:
    log = EventLog()

    with pytest.raises(ValueError, match="Timestamp"):
        log.record("node_created", timestamp="   ")


def test_record_rejects_non_string_timestamp() -> None:
    log = EventLog()

    with pytest.raises(ValueError, match="Timestamp"):
        log.record("node_created", timestamp=123)  # type: ignore[arg-type]
