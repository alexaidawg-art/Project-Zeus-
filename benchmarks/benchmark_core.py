
"""Reproducible benchmarks for the Zeus Connectome Core."""

from __future__ import annotations

import argparse
import json
import platform
import random
import statistics
import sys
import time
from pathlib import Path

import networkx as nx

from zeus.activation import ActivationEngine
from zeus.config import Config
from zeus.connectome import Connectome
from zeus.learning import LearningEngine
from zeus.models import Edge, Node


# Fixed benchmark parameters.
RANDOM_SEED = 1729
NODE_COUNT = 300
EDGE_COUNT = 1200
ACTIVATION_CALLS = 25
LEARNING_BATCH_SIZE = 8
WARMUP_ROUNDS = 2
MEASUREMENT_ROUNDS = 7


def build_connectome() -> tuple[Connectome, list[tuple[str, str]]]:
    """Build the same deterministic graph for every benchmark fixture."""
    rng = random.Random(RANDOM_SEED)
    connectome = Connectome()

    for index in range(NODE_COUNT):
        node_id = f"node-{index:03d}"
        connectome.add_node(
            Node(
                id=node_id,
                node_type="concept",
                label=f"Concept {index:03d}",
            )
        )

    pairs: list[tuple[str, str]] = []
    existing: set[tuple[str, str]] = set()

    # A directed ring ensures every node has an outgoing relationship.
    for index in range(NODE_COUNT):
        pair = (f"node-{index:03d}", f"node-{(index + 1) % NODE_COUNT:03d}")
        pairs.append(pair)
        existing.add(pair)

    # Add deterministic relationships until the target edge count is reached.
    while len(pairs) < EDGE_COUNT:
        source_index = rng.randrange(NODE_COUNT)
        target_index = rng.randrange(NODE_COUNT)

        if source_index == target_index:
            continue

        pair = (
            f"node-{source_index:03d}",
            f"node-{target_index:03d}",
        )

        if pair in existing:
            continue

        existing.add(pair)
        pairs.append(pair)

    for source, target in pairs:
        connectome.add_edge(
            Edge(
                source=source,
                target=target,
                edge_type="association",
                weight=rng.uniform(0.2, 1.0),
            )
        )

    return connectome, pairs


def summarize(samples: list[float]) -> dict[str, float]:
    """Return timing statistics in milliseconds."""
    milliseconds = [sample * 1000 for sample in samples]

    return {
        "average_ms": statistics.mean(milliseconds),
        "median_ms": statistics.median(milliseconds),
        "minimum_ms": min(milliseconds),
        "maximum_ms": max(milliseconds),
    }


def benchmark_activation(config: Config) -> dict[str, object]:
    """Measure repeated activation calls against one fixed graph."""
    connectome, _ = build_connectome()
    engine = ActivationEngine(config)

    seeds = {
        f"node-{index:03d}": 0.95 - (index * 0.02)
        for index in range(10)
    }

    def run_batch() -> None:
        for _ in range(ACTIVATION_CALLS):
            engine.activate(connectome, seeds)

    for _ in range(WARMUP_ROUNDS):
        run_batch()

    samples: list[float] = []

    for _ in range(MEASUREMENT_ROUNDS):
        start = time.perf_counter()
        run_batch()
        elapsed = time.perf_counter() - start
        samples.append(elapsed / ACTIVATION_CALLS)

    return {
        "operation": "ActivationEngine.activate",
        "calls_per_measurement": ACTIVATION_CALLS,
        "warmup_rounds": WARMUP_ROUNDS,
        "measurement_rounds": MEASUREMENT_ROUNDS,
        "timing": summarize(samples),
    }


def benchmark_learning(config: Config) -> dict[str, object]:
    """Measure learning with fresh, identical graphs per measurement."""
    engine = LearningEngine(config)

    def run_batch() -> None:
        fixtures: list[
            tuple[Connectome, list[tuple[str, str]], list[tuple[str, str]]]
        ] = []

        # Fixture construction happens outside the timed section.
        for _ in range(LEARNING_BATCH_SIZE):
            connectome, pairs = build_connectome()
            reinforced = pairs[:80]
            decayed = pairs[:100]
            fixtures.append((connectome, reinforced, decayed))

        start = time.perf_counter()

        for connectome, reinforced, decayed in fixtures:
            engine.learn(connectome, reinforced, decayed)

        return time.perf_counter() - start

    for _ in range(WARMUP_ROUNDS):
        run_batch()

    samples: list[float] = []

    for _ in range(MEASUREMENT_ROUNDS):
        elapsed = run_batch()
        samples.append(elapsed / LEARNING_BATCH_SIZE)

    return {
        "operation": "LearningEngine.learn",
        "graphs_per_measurement": LEARNING_BATCH_SIZE,
        "reinforced_relationships_per_graph": 80,
        "decayed_relationships_per_graph": 100,
        "warmup_rounds": WARMUP_ROUNDS,
        "measurement_rounds": MEASUREMENT_ROUNDS,
        "timing": summarize(samples),
    }


def run_benchmarks() -> dict[str, object]:
    """Run all core benchmarks and return structured results."""
    config = Config(
        k=25,
        horizon=5,
        threshold=0.05,
    )

    return {
        "project": "Project Zeus",
        "benchmark_version": "1.0",
        "random_seed": RANDOM_SEED,
        "graph": {
            "nodes": NODE_COUNT,
            "directed_edges": EDGE_COUNT,
        },
        "environment": {
            "python": sys.version,
            "platform": platform.platform(),
            "networkx": nx.__version__,
        },
        "configuration": {
            "k": config.k,
            "horizon": config.horizon,
            "threshold": config.threshold,
            "activation_decay": config.activation_decay,
            "learning_rate": config.learning_rate,
            "reinforcement_factor": config.reinforcement_factor,
            "decay_factor": config.decay_factor,
        },
        "benchmarks": [
            benchmark_activation(config),
            benchmark_learning(config),
        ],
    }


def main() -> None:
    """Run benchmarks and optionally write JSON results to a file."""
    parser = argparse.ArgumentParser(
        description="Run reproducible Project Zeus core benchmarks."
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Optional path for saving the JSON results.",
    )
    args = parser.parse_args()

    results = run_benchmarks()
    output = json.dumps(results, indent=2, sort_keys=True)

    print(output)

    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(output + "\n", encoding="utf-8")
        print(f"\nResults saved to: {args.output}")


if __name__ == "__main__":
    main()
