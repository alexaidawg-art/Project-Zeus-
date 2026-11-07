
"""Tests for versioned NetworkX graph persistence."""

import json
from pathlib import Path

import networkx as nx
import pytest

from zeus.networkx_store import FORMAT_VERSION, NetworkXStore


@pytest.fixture
def store() -> NetworkXStore:
    return NetworkXStore()


@pytest.fixture
def sample_graph() -> nx.DiGraph:
    graph = nx.DiGraph()
    graph.graph["name"] = "test"
    graph.add_node("a", kind="concept")
    graph.add_node("b", kind="memory")
    graph.add_edge("a", "b", weight=0.75)
    return graph


def test_save_and_load_round_trip(
    store: NetworkXStore, sample_graph: nx.DiGraph, tmp_path: Path
) -> None:
    path = tmp_path / "graph.json"
    store.save(sample_graph, path)
    loaded = store.load(path)

    assert loaded.graph == sample_graph.graph
    assert list(loaded.nodes(data=True)) == list(sample_graph.nodes(data=True))
    assert list(loaded.edges(data=True)) == list(sample_graph.edges(data=True))


def test_save_writes_versioned_json(
    store: NetworkXStore, sample_graph: nx.DiGraph, tmp_path: Path
) -> None:
    path = tmp_path / "graph.json"
    store.save(sample_graph, path)

    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["format_version"] == FORMAT_VERSION


def test_exists(store: NetworkXStore, tmp_path: Path) -> None:
    path = tmp_path / "graph.json"
    assert not store.exists(path)
    path.write_text("{}", encoding="utf-8")
    assert store.exists(path)


def test_load_missing_file(store: NetworkXStore, tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        store.load(tmp_path / "missing.json")


def test_load_invalid_json(store: NetworkXStore, tmp_path: Path) -> None:
    path = tmp_path / "graph.json"
    path.write_text("{invalid", encoding="utf-8")

    with pytest.raises(json.JSONDecodeError):
        store.load(path)


@pytest.mark.parametrize("payload", [[], None, "invalid"])
def test_load_rejects_non_object_payload(
    store: NetworkXStore, tmp_path: Path, payload: object
) -> None:
    path = tmp_path / "graph.json"
    path.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(TypeError):
        store.load(path)


def test_load_rejects_unsupported_version(
    store: NetworkXStore, tmp_path: Path
) -> None:
    path = tmp_path / "graph.json"
    path.write_text(
        json.dumps({"format_version": 999, "graph": {}, "nodes": [], "edges": []}),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="unsupported"):
        store.load(path)


@pytest.mark.parametrize(
    "payload",
    [
        {"format_version": FORMAT_VERSION, "graph": [], "nodes": [], "edges": []},
        {"format_version": FORMAT_VERSION, "graph": {}, "nodes": {}, "edges": []},
        {"format_version": FORMAT_VERSION, "graph": {}, "nodes": [], "edges": {}},
    ],
)
def test_load_rejects_invalid_top_level_fields(
    store: NetworkXStore, tmp_path: Path, payload: dict[str, object]
) -> None:
    path = tmp_path / "graph.json"
    path.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(TypeError):
        store.load(path)


def test_load_rejects_invalid_node(
    store: NetworkXStore, tmp_path: Path
) -> None:
    path = tmp_path / "graph.json"
    payload = {
        "format_version": FORMAT_VERSION,
        "graph": {},
        "nodes": [None],
        "edges": [],
    }
    path.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(TypeError):
        store.load(path)


def test_load_rejects_invalid_node_attributes(
    store: NetworkXStore, tmp_path: Path
) -> None:
    path = tmp_path / "graph.json"
    payload = {
        "format_version": FORMAT_VERSION,
        "graph": {},
        "nodes": [{"id": "a", "attributes": []}],
        "edges": [],
    }
    path.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(TypeError):
        store.load(path)


def test_load_rejects_duplicate_node(
    store: NetworkXStore, tmp_path: Path
) -> None:
    path = tmp_path / "graph.json"
    node = {"id": "a", "attributes": {}}
    payload = {
        "format_version": FORMAT_VERSION,
        "graph": {},
        "nodes": [node, node],
        "edges": [],
    }
    path.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(ValueError, match="duplicate node"):
        store.load(path)


def test_load_rejects_unknown_edge_node(
    store: NetworkXStore, tmp_path: Path
) -> None:
    path = tmp_path / "graph.json"
    payload = {
        "format_version": FORMAT_VERSION,
        "graph": {},
        "nodes": [{"id": "a", "attributes": {}}],
        "edges": [
            {"source": "a", "target": "missing", "attributes": {}}
        ],
    }
    path.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(ValueError, match="unknown node"):
        store.load(path)


def test_load_rejects_invalid_edge(
    store: NetworkXStore, tmp_path: Path
) -> None:
    path = tmp_path / "graph.json"
    payload = {
        "format_version": FORMAT_VERSION,
        "graph": {},
        "nodes": [{"id": "a", "attributes": {}}],
        "edges": [None],
    }
    path.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(TypeError):
        store.load(path)


def test_load_rejects_invalid_edge_attributes(
    store: NetworkXStore, tmp_path: Path
) -> None:
    path = tmp_path / "graph.json"
    payload = {
        "format_version": FORMAT_VERSION,
        "graph": {},
        "nodes": [{"id": "a", "attributes": {}}],
        "edges": [
            {"source": "a", "target": "a", "attributes": []}
        ],
    }
    path.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(TypeError):
        store.load(path)


def test_load_rejects_duplicate_edge(
    store: NetworkXStore, tmp_path: Path
) -> None:
    path = tmp_path / "graph.json"
    edge = {"source": "a", "target": "a", "attributes": {}}
    payload = {
        "format_version": FORMAT_VERSION,
        "graph": {},
        "nodes": [{"id": "a", "attributes": {}}],
        "edges": [edge, edge],
    }
    path.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(ValueError, match="duplicate directed edge"):
        store.load(path)


@pytest.mark.parametrize("node_id", [[], {}, None])
def test_load_rejects_invalid_node_identifier(
    store: NetworkXStore, tmp_path: Path, node_id: object
) -> None:
    path = tmp_path / "graph.json"
    payload = {
        "format_version": FORMAT_VERSION,
        "graph": {},
        "nodes": [{"id": node_id, "attributes": {}}],
        "edges": [],
    }
    path.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(ValueError, match="node identifiers"):
        store.load(path)


def test_save_rejects_multigraph(
    store: NetworkXStore, tmp_path: Path
) -> None:
    with pytest.raises(TypeError):
        store.save(nx.MultiDiGraph(), tmp_path / "graph.json")


def test_save_rejects_non_finite_data(
    store: NetworkXStore, tmp_path: Path
) -> None:
    graph = nx.DiGraph()
    graph.add_node("a", weight=float("nan"))

    with pytest.raises(ValueError):
        store.save(graph, tmp_path / "graph.json")


def test_failed_save_preserves_existing_file(
    store: NetworkXStore, tmp_path: Path
) -> None:
    path = tmp_path / "graph.json"
    path.write_text("original", encoding="utf-8")

    graph = nx.DiGraph()
    graph.add_node("a", weight=float("nan"))

    with pytest.raises(ValueError):
        store.save(graph, path)

    assert path.read_text(encoding="utf-8") == "original"
