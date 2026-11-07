
"""Deterministic relationship consolidation for Zeus."""

from zeus.config import Config
from zeus.connectome import Connectome


class ConsolidationEngine:
    """Strengthen qualifying relationships in the Zeus Connectome."""

    def __init__(self, config: Config) -> None:
        self.config = config

    def consolidate(self, connectome: Connectome) -> int:
        """Strengthen qualifying relationships and return the update count."""
        graph = connectome.to_graph()
        updates: dict[tuple[str, str], float] = {}

        for source, target, data in graph.edges(data=True):
            weight = data["weight"]

            if weight < self.config.consolidation_weight:
                continue

            remaining = self.config.max_weight - weight
            strength = (
                self.config.consolidation_strength
                / (self.config.consolidation_strength + 1)
            )

            updated = weight + (remaining * strength)

            updates[(source, target)] = min(
                self.config.max_weight,
                max(0.0, updated),
            )

        for (source, target), weight in updates.items():
            connectome.update_edge_weight(source, target, weight)

        return len(updates)
