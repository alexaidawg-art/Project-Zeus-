
"""Bounded deterministic spreading activation for the Zeus Connectome."""

import math

from zeus.config import Config
from zeus.connectome import Connectome


class ActivationEngine:
    """Propagate activation through a Connectome using bounded top-k selection."""

    def __init__(self, config: Config) -> None:
        self.config = config

    def activate(
        self,
        connectome: Connectome,
        seeds: dict[str, float],
    ) -> dict[str, float]:
        """Return activation scores after bounded graph propagation."""
        graph = connectome.to_graph()

        if not seeds:
            return {}

        for node_id, score in seeds.items():
            if not isinstance(node_id, str) or not node_id.strip():
                raise ValueError("Seed node IDs must be non-empty strings")
            if node_id not in graph:
                raise ValueError(f"Seed node does not exist: {node_id}")
            if isinstance(score, bool) or not isinstance(score, (int, float)):
                raise TypeError("Seed activation scores must be numeric")
            if not math.isfinite(score) or not 0 <= score <= 1:
                raise ValueError("Seed activation scores must be between 0 and 1")

        active = {
            node_id: float(score)
            for node_id, score in seeds.items()
            if score >= self.config.threshold
        }

        frontier = self._top_k(active)

        active = dict(frontier)

        for _ in range(self.config.horizon):
            candidates: dict[str, float] = {}

            for source, activation in frontier.items():
                for target, edge_data in graph[source].items():
                    contribution = (
                        activation
                        * edge_data["weight"]
                        * self.config.activation_decay
                    )

                    if contribution < self.config.threshold:
                        continue

                    if contribution > active.get(target, 0.0):
                        candidates[target] = max(
                            candidates.get(target, 0.0),
                            contribution,
                        )

            frontier = self._top_k(candidates)

            if not frontier:
                break

            active.update(frontier)

        return dict(
            sorted(
                active.items(),
                key=lambda item: (-item[1], item[0]),
            )
        )

    def _top_k(self, candidates: dict[str, float]) -> dict[str, float]:
        """Keep the strongest k candidates with deterministic tie-breaking."""
        selected = sorted(
            candidates.items(),
            key=lambda item: (-item[1], item[0]),
        )[: self.config.k]

        return dict(selected)
