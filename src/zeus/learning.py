
"""Deterministic learning and relationship reinforcement for Zeus."""

from zeus.config import Config
from zeus.connectome import Connectome


class LearningEngine:
    """Manage relationship reinforcement and decay."""

    def __init__(self, config: Config) -> None:
        self.config = config

    def reinforce(
        self,
        connectome: Connectome,
        relationships: list[tuple[str, str]],
    ) -> None:
        """Reinforce relationships using simultaneous weight updates."""
        updates: dict[tuple[str, str], float] = {}

        for source, target in relationships:
            edge = connectome.get_edge(source, target)

            if edge is None:
                raise ValueError(
                    f"Relationship does not exist: {source} -> {target}"
                )

            current = updates.get(
                (source, target),
                edge.weight,
            )

            updated = current + (
                self.config.learning_rate
                * self.config.reinforcement_factor
                * (self.config.max_weight - current)
            )

            updates[(source, target)] = min(
                self.config.max_weight,
                max(0.0, updated),
            )

        for (source, target), weight in updates.items():
            connectome.update_edge_weight(source, target, weight)

    def decay(
        self,
        connectome: Connectome,
        relationships: list[tuple[str, str]] | None = None,
    ) -> None:
        """Decay selected relationships, or every relationship if omitted."""
        graph = connectome.to_graph()

        selected = (
            list(graph.edges)
            if relationships is None
            else relationships
        )

        updates: dict[tuple[str, str], float] = {}

        for source, target in selected:
            edge = connectome.get_edge(source, target)

            if edge is None:
                raise ValueError(
                    f"Relationship does not exist: {source} -> {target}"
                )

            updated = edge.weight * self.config.decay_factor
            updates[(source, target)] = max(0.0, updated)

        for (source, target), weight in updates.items():
            connectome.update_edge_weight(source, target, weight)

    def learn(
        self,
        connectome: Connectome,
        reinforced: list[tuple[str, str]],
        decayed: list[tuple[str, str]] | None = None,
    ) -> None:
        """Apply decay first, then reinforcement, in one learning cycle."""
        graph = connectome.to_graph()
        selected_decay = (
            list(graph.edges)
            if decayed is None
            else decayed
        )

        if len(set(reinforced)) != len(reinforced):
            raise ValueError("Duplicate reinforcement relationships are not allowed")

        if len(set(selected_decay)) != len(selected_decay):
            raise ValueError("Duplicate decay relationships are not allowed")

        initial_weights: dict[tuple[str, str], float] = {}

        for relationship in set(reinforced) | set(selected_decay):
            edge = connectome.get_edge(*relationship)

            if edge is None:
                raise ValueError(
                    f"Relationship does not exist: "
                    f"{relationship[0]} -> {relationship[1]}"
                )

            initial_weights[relationship] = edge.weight

        updates: dict[tuple[str, str], float] = {}

        for relationship, initial in initial_weights.items():
            weight = initial

            if relationship in selected_decay:
                weight *= self.config.decay_factor

            if relationship in reinforced:
                weight += (
                    self.config.learning_rate
                    * self.config.reinforcement_factor
                    * (self.config.max_weight - weight)
                )

            updates[relationship] = min(
                self.config.max_weight,
                max(0.0, weight),
            )

        for (source, target), weight in updates.items():
            connectome.update_edge_weight(source, target, weight)
