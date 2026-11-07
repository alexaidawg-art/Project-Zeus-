
"""Tests for bounded deterministic spreading activation."""

import math

import pytest

from zeus.activation import ActivationEngine
from zeus.config import Config
from zeus.connectome import Connectome
from zeus.models import Edge, Node


@pytest.fixture
def connectome() -> Connectome:
    graph = Connectome()
    for node_id in ("a", "b", "c", "d", "e"):
        graph.add_node(Node(node_id, "concept", f"Concept {node_id}"))
    return graph


@pytest.fixture
def engine() -> ActivationEngine:
    return ActivationEngine(Config())


def test_empty_seeds_return_empty_result(
    engine: ActivationEngine,
    connectome: Connectome,
) -> None:
    assert engine.activate(connectome, {}) == {}


def test_seed_activation_is_preserved(
    engine: ActivationEngine,
    connectome: Connectome,
) -> None:
    result = engine.activate(connectome, {"a": 0.9})

    assert result == {"a": 0.9}


def test_activation_propagates_to_connected_node(
    engine: ActivationEngine,
    connectome: Connectome,
) -> None:
    connectome.add_edge(Edge("a", "b", "related", weight=0.8))

    result = engine.activate(connectome, {"a": 1.0})

    assert result["a"] == 1.0
    assert result["b"] == pytest.approx(0.64)


def test_activation_weakens_over_multiple_rounds(
    engine: ActivationEngine,
    connectome: Connectome,
) -> None:
    connectome.add_edge(Edge("a", "b", "related", weight=1.0))
    connectome.add_edge(Edge("b", "c", "related", weight=1.0))

    result = engine.activate(connectome, {"a": 1.0})

    assert result["b"] == pytest.approx(0.8)
    assert result["c"] == pytest.approx(0.64)


def test_activation_respects_horizon(
    connectome: Connectome,
) -> None:
    engine = ActivationEngine(Config(horizon=1))
    connectome.add_edge(Edge("a", "b", "related", weight=1.0))
    connectome.add_edge(Edge("b", "c", "related", weight=1.0))

    result = engine.activate(connectome, {"a": 1.0})

    assert "b" in result
    assert "c" not in result


def test_activation_respects_threshold(
    connectome: Connectome,
) -> None:
    engine = ActivationEngine(Config(threshold=0.2))
    connectome.add_edge(Edge("a", "b", "related", weight=0.2))

    result = engine.activate(connectome, {"a": 1.0})

    assert "b" not in result


def test_seed_below_threshold_is_ignored(
    connectome: Connectome,
) -> None:
    engine = ActivationEngine(Config(threshold=0.2))

    assert engine.activate(connectome, {"a": 0.1}) == {}


def test_top_k_limits_seed_frontier(
    connectome: Connectome,
) -> None:
    engine = ActivationEngine(Config(k=2, horizon=1))

    result = engine.activate(
        connectome,
        {"a": 0.9, "b": 0.8, "c": 0.7},
    )

    assert set(result) == {"a", "b"}


def test_top_k_limits_propagated_candidates(
    connectome: Connectome,
) -> None:
    engine = ActivationEngine(Config(k=2, horizon=1))
    connectome.add_edge(Edge("a", "b", "related", weight=1.0))
    connectome.add_edge(Edge("a", "c", "related", weight=0.8))
    connectome.add_edge(Edge("a", "d", "related", weight=0.6))

    result = engine.activate(connectome, {"a": 1.0})

    assert "b" in result
    assert "c" in result
    assert "d" not in result


def test_equal_scores_use_node_id_tiebreaking(
    connectome: Connectome,
) -> None:
    engine = ActivationEngine(Config(k=2))
    connectome.add_edge(Edge("a", "c", "related", weight=1.0))
    connectome.add_edge(Edge("a", "b", "related", weight=1.0))

    result = engine.activate(connectome, {"a": 1.0})

    assert "b" in result
    assert "c" not in result


def test_multiple_paths_use_strongest_contribution(
    connectome: Connectome,
) -> None:
    connectome.add_edge(Edge("a", "c", "related", weight=0.8))
    connectome.add_edge(Edge("b", "c", "related", weight=0.5))

    result = ActivationEngine(Config()).activate(
        connectome,
        {"a": 1.0, "b": 0.9},
    )

    assert result["c"] == pytest.approx(0.64)


def test_seed_activation_is_not_overwritten_by_weaker_path(
    connectome: Connectome,
) -> None:
    connectome.add_edge(Edge("a", "b", "related", weight=0.5))

    result = ActivationEngine(Config()).activate(
        connectome,
        {"a": 1.0, "b": 0.9},
    )

    assert result["b"] == 0.9


def test_propagation_follows_outgoing_edges_only(
    connectome: Connectome,
) -> None:
    connectome.add_edge(Edge("a", "b", "related", weight=1.0))

    result = ActivationEngine(Config()).activate(connectome, {"b": 1.0})

    assert "a" not in result


def test_cycles_do_not_increase_activation(
    connectome: Connectome,
) -> None:
    connectome.add_edge(Edge("a", "b", "related", weight=1.0))
    connectome.add_edge(Edge("b", "a", "related", weight=1.0))

    result = ActivationEngine(Config()).activate(connectome, {"a": 1.0})

    assert result["a"] == 1.0
    assert result["b"] == pytest.approx(0.8)


def test_results_are_sorted_by_score_then_id(
    connectome: Connectome,
) -> None:
    engine = ActivationEngine(Config(horizon=1))
    connectome.add_edge(Edge("a", "c", "related", weight=0.5))
    connectome.add_edge(Edge("a", "b", "related", weight=0.5))

    result = engine.activate(connectome, {"a": 1.0})

    assert list(result) == ["a", "b", "c"]


@pytest.mark.parametrize(
    "node_id",
    ["missing", "", " "],
)
def test_invalid_seed_node_ids_are_rejected(
    engine: ActivationEngine,
    connectome: Connectome,
    node_id: str,
) -> None:
    with pytest.raises(ValueError):
        engine.activate(connectome, {node_id: 1.0})


def test_non_string_seed_id_is_rejected(
    engine: ActivationEngine,
    connectome: Connectome,
) -> None:
    with pytest.raises(ValueError, match="non-empty strings"):
        engine.activate(connectome, {None: 1.0})  # type: ignore[dict-item]


@pytest.mark.parametrize("score", [True, False, "high"])
def test_non_numeric_seed_scores_are_rejected(
    engine: ActivationEngine,
    connectome: Connectome,
    score: object,
) -> None:
    with pytest.raises(TypeError, match="numeric"):
        engine.activate(
            connectome,
            {"a": score},  # type: ignore[dict-item]
        )


@pytest.mark.parametrize(
    "score",
    [-0.1, 1.1, math.nan, math.inf, -math.inf],
)
def test_invalid_seed_scores_are_rejected(
    engine: ActivationEngine,
    connectome: Connectome,
    score: float,
) -> None:
    with pytest.raises(ValueError, match="between 0 and 1"):
        engine.activate(connectome, {"a": score})


def test_top_k_helper_handles_empty_candidates(
    engine: ActivationEngine,
) -> None:
    assert engine._top_k({}) == {}


def test_top_k_helper_sorts_deterministically(
    engine: ActivationEngine,
) -> None:
    result = engine._top_k({"c": 0.5, "a": 0.9, "b": 0.9})

    assert list(result) == ["a", "b"]
