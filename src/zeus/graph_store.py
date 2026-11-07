
"""Storage contract for the Zeus Connectome graph."""

from pathlib import Path
from typing import Protocol

import networkx as nx


class GraphStore(Protocol):
    """Contract for persistent directed graph storage."""

    def save(self, graph: nx.DiGraph, path: Path) -> None:
        """Persist a graph to the given path."""
        ...

    def load(self, path: Path) -> nx.DiGraph:
        """Load a graph from the given path."""
        ...

    def exists(self, path: Path) -> bool:
        """Return whether persisted graph data exists."""
        ...
