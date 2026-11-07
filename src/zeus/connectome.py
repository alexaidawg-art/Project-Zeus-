"""Graph management for the Zeus Connectome Core."""

import networkx as nx

from zeus.event_log import EventLog
from zeus.models import Edge, Node


class Connectome:
    """Manage typed nodes and relationships in a directed knowledge graph."""

    def __init__(self, event_log: EventLog | None = None) -> None:
        self._graph: nx.DiGraph = nx.DiGraph()
        self._normalized_labels: dict[str, str] = {}
        self.event_log = event_log if event_log is not None else EventLog()

    def add_node(self, node: Node) -> None:
        """Add a node while enforcing unique IDs and normalized labels."""
        if node.id in self._graph:
            raise ValueError(f"Node ID already exists: {node.id}")

        normalized_label = node.normalized_label
        if normalized_label in self._normalized_labels:
            raise ValueError(
                f"Normalized label already exists: {normalized_label}"
            )

        self._graph.add_node(
            node.id,
            node_type=node.node_type,
            label=node.label,
            attributes=dict(node.attributes),
            importance=node.importance,
            confidence=node.confidence,
        )
        self._normalized_labels[normalized_label] = node.id

        self.event_log.record(
            "node_created",
            {
                "node_id": node.id,
                "node_type": node.node_type,
                "label": node.label,
            },
        )

    def get_node(self, node_id: str) -> Node | None:
        """Retrieve a node by its ID."""
        if node_id not in self._graph:
            return None

        data = self._graph.nodes[node_id]
        return Node(
            id=node_id,
            node_type=data["node_type"],
            label=data["label"],
            attributes=dict(data["attributes"]),
            importance=data["importance"],
            confidence=data["confidence"],
        )

    def add_edge(self, edge: Edge) -> None:
        """Add a directed relationship between two existing nodes."""
        if edge.source not in self._graph:
            raise ValueError(f"Source node does not exist: {edge.source}")

        if edge.target not in self._graph:
            raise ValueError(f"Target node does not exist: {edge.target}")

        if self._graph.has_edge(edge.source, edge.target):
            raise ValueError(
                f"Relationship already exists: {edge.source} -> {edge.target}"
            )

        self._graph.add_edge(
            edge.source,
            edge.target,
            edge_type=edge.edge_type,
            weight=edge.weight,
            attributes=dict(edge.attributes),
        )

        self.event_log.record(
            "edge_created",
            {
                "source": edge.source,
                "target": edge.target,
                "edge_type": edge.edge_type,
                "weight": edge.weight,
            },
        )

    def get_edge(self, source: str, target: str) -> Edge | None:
        """Retrieve a directed relationship between two nodes."""
        if not self._graph.has_edge(source, target):
            return None

        data = self._graph.edges[source, target]
        return Edge(
            source=source,
            target=target,
            edge_type=data["edge_type"],
            weight=data["weight"],
            attributes=dict(data["attributes"]),
        )

    def update_edge_weight(
        self,
        source: str,
        target: str,
        weight: float,
    ) -> None:
        """Update the weight of an existing directed relationship."""
        edge = self.get_edge(source, target)

        if edge is None:
            raise ValueError(
                f"Relationship does not exist: {source} -> {target}"
            )

        updated = Edge(
            source=edge.source,
            target=edge.target,
            edge_type=edge.edge_type,
            weight=weight,
            attributes=edge.attributes,
        )

        self._graph.edges[source, target]["weight"] = updated.weight

        self.event_log.record(
            "edge_weight_updated",
            {
                "source": source,
                "target": target,
                "old_weight": edge.weight,
                "new_weight": updated.weight,
            },
        )

    def has_node(self, node_id: str) -> bool:
        """Check whether a node exists."""
        return node_id in self._graph

    def node_count(self) -> int:
        """Return the number of nodes."""
        return self._graph.number_of_nodes()

    def edge_count(self) -> int:
        """Return the number of directed relationships."""
        return self._graph.number_of_edges()

    def to_graph(self) -> nx.DiGraph:
        """Return a copy of the underlying graph."""
        return self._graph.copy()