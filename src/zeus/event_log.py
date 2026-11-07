
"""Deterministic structured event logging for Zeus."""

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any


@dataclass(frozen=True)
class Event:
    """An immutable record of a Zeus system event."""

    sequence: int
    event_type: str
    timestamp: str
    payload: dict[str, Any] = field(default_factory=dict)


class EventLog:
    """Store ordered, immutable event records."""

    def __init__(self) -> None:
        self._events: list[Event] = []

    def record(
        self,
        event_type: str,
        payload: dict[str, Any] | None = None,
        timestamp: str | None = None,
    ) -> Event:
        """Record an event and return the created record."""
        if not isinstance(event_type, str) or not event_type.strip():
            raise ValueError("Event type must be a non-empty string")

        event_timestamp = timestamp or datetime.now(UTC).isoformat()

        if not isinstance(event_timestamp, str) or not event_timestamp.strip():
            raise ValueError("Timestamp must be a non-empty string")

        if payload is not None and not isinstance(payload, dict):
            raise TypeError("Event payload must be a dictionary")

        event = Event(
            sequence=len(self._events) + 1,
            event_type=event_type.strip(),
            timestamp=event_timestamp,
            payload=dict(payload or {}),
        )

        self._events.append(event)
        return event

    def get_events(self) -> tuple[Event, ...]:
        """Return all recorded events in sequence order."""
        return tuple(self._events)

    def get_events_by_type(self, event_type: str) -> tuple[Event, ...]:
        """Return events matching a specific event type."""
        return tuple(
            event
            for event in self._events
            if event.event_type == event_type
        )

    def event_count(self) -> int:
        """Return the number of recorded events."""
        return len(self._events)
