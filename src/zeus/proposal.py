
"""Validation of proposed Connectome changes."""

from typing import Any

from zeus.config import Config
from zeus.connectome import Connectome
from zeus.models import Edge, Node


class ProposalValidator:
    """Validate proposed graph changes without mutating the Connectome."""

    ALLOWED_OPERATIONS = {
        "create_node",
        "create_edge",
        "update_edge_weight",
    }

    def __init__(self, config: Config) -> None:
        self.config = config

    def validate(
        self,
        connectome: Connectome,
        proposal: dict[str, Any],
    ) -> bool:
        """Return True when a proposal is valid; otherwise raise ValueError."""
        if not isinstance(proposal, dict):
            raise TypeError("Proposal must be a dictionary")

        operation = proposal.get("operation")

        if not isinstance(operation, str):
            raise ValueError("Proposal operation must be a string")

        if operation not in self.ALLOWED_OPERATIONS:
            raise ValueError(f"Unsupported proposal operation: {operation}")

        if operation == "create_node":
            self._validate_node(connectome, proposal)
        elif operation == "create_edge":
            self._validate_edge(connectome, proposal)
        elif operation == "update_edge_weight":
            self._validate_weight_update(connectome, proposal)

        return True

    def _validate_node(
        self,
        connectome: Connectome,
        proposal: dict[str, Any],
    ) -> None:
        required = {"id", "node_type", "label"}
        self._check_required(proposal, required)

        node = Node(
            id=proposal["id"],
            node_type=proposal["node_type"],
            label=proposal["label"],
            attributes=proposal.get("attributes", {}),
            importance=proposal.get("importance", 0.5),
            confidence=proposal.get("confidence", 0.5),
        )

        if connectome.has_node(node.id):
            raise ValueError(f"Node ID already exists: {node.id}")

        for existing_id in connectome.to_graph().nodes:
            existing = connectome.get_node(existing_id)
            if existing is not None and (
                existing.normalized_label == node.normalized_label
            ):
                raise ValueError(
                    f"Normalized label already exists: {node.normalized_label}"
                )

    def _validate_edge(
        self,
        connectome: Connectome,
        proposal: dict[str, Any],
    ) -> None:
        required = {"source", "target", "edge_type"}
        self._check_required(proposal, required)

        edge = Edge(
            source=proposal["source"],
            target=proposal["target"],
            edge_type=proposal["edge_type"],
            weight=proposal.get("weight", self.config.initial_weight),
            attributes=proposal.get("attributes", {}),
        )

        if not connectome.has_node(edge.source):
            raise ValueError(f"Source node does not exist: {edge.source}")

        if not connectome.has_node(edge.target):
            raise ValueError(f"Target node does not exist: {edge.target}")

        if connectome.to_graph().has_edge(edge.source, edge.target):
            raise ValueError(
                f"Relationship already exists: {edge.source} -> {edge.target}"
            )

    def _validate_weight_update(
        self,
        connectome: Connectome,
        proposal: dict[str, Any],
    ) -> None:
        required = {"source", "target", "weight"}
        self._check_required(proposal, required)

        source = proposal["source"]
        target = proposal["target"]

        edge = connectome.get_edge(source, target)

        if edge is None:
            raise ValueError(
                f"Relationship does not exist: {source} -> {target}"
            )

        updated = Edge(
            source=edge.source,
            target=edge.target,
            edge_type=edge.edge_type,
            weight=proposal["weight"],
            attributes=edge.attributes,
        )

        if updated.weight > self.config.max_weight:
            raise ValueError("Proposed weight exceeds configured maximum")

    @staticmethod
    def _check_required(
        proposal: dict[str, Any],
        required: set[str],
    ) -> None:
        missing = required - proposal.keys()

        if missing:
            raise ValueError(
                f"Missing required proposal fields: {', '.join(sorted(missing))}"
            )
