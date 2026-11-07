
"""Validated configuration for the Zeus Connectome Core."""

from dataclasses import dataclass
import math


@dataclass(frozen=True)
class Config:
    # Activation
    k: int = 7
    activation_decay: float = 0.8
    threshold: float = 0.15
    horizon: int = 3

    # Learning
    learning_rate: float = 0.1
    reinforcement_factor: float = 0.6
    initial_weight: float = 0.3
    max_weight: float = 1.0

    # Memory maintenance
    decay_factor: float = 0.6
    decay_period_days: int = 7
    prune_threshold: float = 0.02

    # Consolidation
    consolidation_interval: int = 5
    consolidation_weight: float = 0.6
    consolidation_strength: float = 4.0

    def __post_init__(self):
        if self.k < 1:
            raise ValueError("k must be at least 1")

        if self.horizon < 1:
            raise ValueError("horizon must be at least 1")

        if self.decay_period_days < 1:
            raise ValueError("decay_period_days must be positive")

        if self.consolidation_interval < 1:
            raise ValueError("consolidation_interval must be positive")

        bounded = {
            "activation_decay": self.activation_decay,
            "threshold": self.threshold,
            "learning_rate": self.learning_rate,
            "reinforcement_factor": self.reinforcement_factor,
            "initial_weight": self.initial_weight,
            "max_weight": self.max_weight,
            "decay_factor": self.decay_factor,
            "prune_threshold": self.prune_threshold,
            "consolidation_weight": self.consolidation_weight,
        }

        for name, value in bounded.items():
            if not math.isfinite(value) or not 0 <= value <= 1:
                raise ValueError(f"{name} must be finite and between 0 and 1")

        if not math.isfinite(self.consolidation_strength):
            raise ValueError("consolidation_strength must be finite")

        if self.consolidation_strength <= 0:
            raise ValueError("consolidation_strength must be positive")

        if self.initial_weight > self.max_weight:
            raise ValueError("initial_weight cannot exceed max_weight")
