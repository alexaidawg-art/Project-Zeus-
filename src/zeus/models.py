
"""Model-independent knowledge structures for the Zeus Connectome Core."""

import math
from dataclasses import dataclass, field
from typing import Any


def _validate_text(value: str, field_name: str) -> None:
    """Ensure required text fields contain non-whitespace text."""
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} must be a non-empty string")


def _validate_unit_interval(value: float, field_name: str) -> None:
    """Ensure a numeric value is finite and between zero and one."""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"{field_name} must be a number")
    if not math.isfinite(value) or not 0 <= value <= 1:
        raise ValueError(f"{field_name} must be finite and between 0 and 1")


@dataclass
class Node:
    """A single concept, memory, entity, or other knowledge item."""

    id: str
    node_type: str
    label: str
    attributes: dict[str, Any] = field(default_factory=dict)
    importance: float = 0.5
    confidence: float = 0.5

    def __post_init__(self) -> None:
        _validate_text(self.id, "id")
        _validate_text(self.node_type, "node_type")
        _validate_text(self.label, "label")

        if not isinstance(self.attributes, dict):
            raise TypeError("attributes must be a dictionary")

        _validate_unit_interval(self.importance, "importance")
        _validate_unit_interval(self.confidence, "confidence")

    @property
    def normalized_label(self) -> str:
        """Return a normalized label for consistent comparisons."""
        return " ".join(self.label.split()).casefold()


@dataclass
class Edge:
    """A typed, weighted relationship between two knowledge nodes."""

    source: str
    target: str
    edge_type: str
    weight: float = 0.5
    attributes: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        _validate_text(self.source, "source")
        _validate_text(self.target, "target")
        _validate_text(self.edge_type, "edge_type")

        if not isinstance(self.attributes, dict):
            raise TypeError("attributes must be a dictionary")

        _validate_unit_interval(self.weight, "weight")

    @property
    def normalized_type(self) -> str:
        """Return a normalized relationship type."""
        return " ".join(self.edge_type.split()).upper()
