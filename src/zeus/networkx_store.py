
"""Versioned JSON persistence for the Zeus Connectome graph."""

import json
import math
import os
import tempfile
from pathlib import Path
from typing import Any

import networkx as nx

from zeus.graph_store import GraphStore


FORMAT_VERSION = 1


class NetworkXStore(GraphStore):
    """Persist directed NetworkX graphs using atomic, versioned JSON files."""

    def save(self, graph: nx.DiGraph, path: Path) -> None:
        """Save a graph atomically to the given path."""
        if not isinstance(graph, nx.DiGraph) or graph.is_multigraph():
            raise TypeError("graph must be a NetworkX DiGraph")

        payload = {
            "format_version": FORMAT_VERSION,
            "graph": graph.graph,
            "nodes": [
                {"id": node, "attributes": attributes}
                for node, attributes in graph.nodes(data=True)
            ],
            "edges": [
                {
                    "source": source,
                    "target": target,
                    "attributes": attributes,
                }
                for source, target, attributes in graph.edges(data=True)
            ],
        }

        # Validate JSON compatibility before touching the destination file.
        serialized = json.dumps(
            payload,
            sort_keys=True,
            allow_nan=False,
            separators=(",", ":"),
        )

        temporary_path: str | None = None

        try:
            with tempfile.NamedTemporaryFile(
                mode="w",
                encoding="utf-8",
                dir=path.parent,
                prefix=f".{path.name}.",
                suffix=".tmp",
                delete=False,
            ) as temporary_file:
                temporary_path = temporary_file.name
                temporary_file.write(serialized)
                temporary_file.flush()
                os.fsync(temporary_file.fileno())

            os.replace(temporary_path, path)
            temporary_path = None
        finally:
            if temporary_path is not None:
                try:
                    os.unlink(temporary_path)
                except FileNotFoundError:
                    pass

    def load(self, path: Path) -> nx.DiGraph:
        """Load and validate a versioned graph JSON file."""
        with path.open("r", encoding="utf-8") as file:
            payload: Any = json.load(file)

        if not isinstance(payload, dict):
            raise TypeError("graph data must be a JSON object")

        if payload.get("format_version") != FORMAT_VERSION:
            raise ValueError("unsupported graph format version")

        graph_attributes = payload.get("graph")
        nodes = payload.get("nodes")
        edges = payload.get("edges")

        if not isinstance(graph_attributes, dict):
            raise TypeError("graph attributes must be an object")
        if not isinstance(nodes, list) or not isinstance(edges, list):
            raise TypeError("nodes and edges must be lists")

        graph = nx.DiGraph()
        graph.graph.update(graph_attributes)

        for item in nodes:
            if not isinstance(item, dict):
                raise TypeError("each node must be an object")

            node_id = item.get("id")
            attributes = item.get("attributes")

            self._validate_node_id(node_id)

            if not isinstance(attributes, dict):
                raise TypeError("node attributes must be an object")
            if node_id in graph:
                raise ValueError("duplicate node identifier")

            graph.add_node(node_id, **attributes)

        for item in edges:
            if not isinstance(item, dict):
                raise TypeError("each edge must be an object")

            source = item.get("source")
            target = item.get("target")
            attributes = item.get("attributes")

            self._validate_node_id(source)
            self._validate_node_id(target)

            if source not in graph or target not in graph:
                raise ValueError("edge references an unknown node")
            if not isinstance(attributes, dict):
                raise TypeError("edge attributes must be an object")
            if graph.has_edge(source, target):
                raise ValueError("duplicate directed edge")

            graph.add_edge(source, target, **attributes)

        return graph

    def exists(self, path: Path) -> bool:
        """Return whether a persisted graph file exists."""
        return path.is_file()

    @staticmethod
    def _validate_node_id(node_id: Any) -> None:
        """Restrict node IDs to JSON-safe scalar values."""
        if not isinstance(node_id, (str, int, float, bool)):
            raise TypeError("node identifiers must be strings, numbers, or booleans")

        if isinstance(node_id, float) and not math.isfinite(node_id):
            raise ValueError("node identifiers cannot be non-finite numbers")
