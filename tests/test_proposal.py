
"""Tests for safe Connectome proposal validation."""

import pytest

from zeus.config import Config
from zeus.connectome import Connectome
from zeus.models import Edge, Node
from zeus.proposal import ProposalValidator


@pytest.fixture
def validator() -> ProposalValidator:
    return ProposalValidator(Config())


@pytest.fixture
def connectome() -> Connectome:
    graph = Connectome()
    graph.add_node(Node("a", "concept", "Alpha"))
    graph.add_node(Node("b", "concept", "Beta"))
    return graph


def snapshot(connectome: Connectome) -> tuple[dict, int]:
    """Capture graph data and event count before validation."""
    graph = connectome.to_graph()
    return (
        {
            "nodes": sorted(
                (node, dict(data))
                for node, data in graph.nodes(data=True)
            ),
            "edges": sorted(
                (source, target, dict(data))
                for source, target, data in graph.edges(data=True)
            ),
        },
        connectome.event_log.event_count(),
    )


def test_valid_create_node(validator, connectome):
    proposal = {
        "operation": "create_node",
        "id": "c",
        "node_type": "concept",
        "label": "Gamma",
    }

    assert validator.validate(connectome, proposal) is True
    assert not connectome.has_node("c")


def test_valid_create_edge(validator, connectome):
    proposal = {
        "operation": "create_edge",
        "source": "a",
        "target": "b",
        "edge_type": "related_to",
        "weight": 0.7,
    }

    assert validator.validate(connectome, proposal) is True
    assert connectome.get_edge("a", "b") is None


def test_valid_update_edge_weight(validator, connectome):
    connectome.add_edge(Edge("a", "b", "related_to", 0.5))

    proposal = {
        "operation": "update_edge_weight",
        "source": "a",
        "target": "b",
        "weight": 0.8,
    }

    assert validator.validate(connectome, proposal) is True
    assert connectome.get_edge("a", "b").weight == 0.5


def test_non_dictionary_proposal_raises_type_error(validator, connectome):
    with pytest.raises(TypeError, match="dictionary"):
        validator.validate(connectome, "invalid")


@pytest.mark.parametrize("operation", [None, 123, [], {}])
def test_non_string_operation_raises_type_error(
    validator, connectome, operation
):
    with pytest.raises(TypeError, match="operation must be a string"):
        validator.validate(connectome, {"operation": operation})


def test_missing_operation_raises_value_error(validator, connectome):
    with pytest.raises(ValueError, match="operation must be a string"):
        validator.validate(connectome, {})


def test_unsupported_operation_raises_value_error(validator, connectome):
    with pytest.raises(ValueError, match="Unsupported"):
        validator.validate(connectome, {"operation": "delete_node"})


@pytest.mark.parametrize(
    "proposal",
    [
        {"operation": "create_node"},
        {"operation": "create_node", "id": "c"},
        {
            "operation": "create_node",
            "id": "c",
            "node_type": "concept",
        },
    ],
)
def test_create_node_missing_fields(validator, connectome, proposal):
    with pytest.raises(ValueError, match="Missing required"):
        validator.validate(connectome, proposal)


@pytest.mark.parametrize(
    "proposal",
    [
        {"operation": "create_edge"},
        {
            "operation": "create_edge",
            "source": "a",
        },
        {
            "operation": "create_edge",
            "source": "a",
            "target": "b",
        },
    ],
)
def test_create_edge_missing_fields(validator, connectome, proposal):
    with pytest.raises(ValueError, match="Missing required"):
        validator.validate(connectome, proposal)


@pytest.mark.parametrize(
    "proposal",
    [
        {"operation": "update_edge_weight"},
        {
            "operation": "update_edge_weight",
            "source": "a",
        },
        {
            "operation": "update_edge_weight",
            "source": "a",
            "target": "b",
        },
    ],
)
def test_update_weight_missing_fields(validator, connectome, proposal):
    with pytest.raises(ValueError, match="Missing required"):
        validator.validate(connectome, proposal)


def test_duplicate_node_id_is_rejected(validator, connectome):
    proposal = {
        "operation": "create_node",
        "id": "a",
        "node_type": "concept",
        "label": "Another label",
    }

    with pytest.raises(ValueError, match="already exists"):
        validator.validate(connectome, proposal)


def test_duplicate_normalized_label_is_rejected(validator, connectome):
    proposal = {
        "operation": "create_node",
        "id": "c",
        "node_type": "concept",
        "label": "  ALPHA  ",
    }

    with pytest.raises(ValueError, match="Normalized label"):
        validator.validate(connectome, proposal)


def test_missing_source_node_is_rejected(validator, connectome):
    proposal = {
        "operation": "create_edge",
        "source": "missing",
        "target": "b",
        "edge_type": "related_to",
    }

    with pytest.raises(ValueError, match="Source node"):
        validator.validate(connectome, proposal)


def test_missing_target_node_is_rejected(validator, connectome):
    proposal = {
        "operation": "create_edge",
        "source": "a",
        "target": "missing",
        "edge_type": "related_to",
    }

    with pytest.raises(ValueError, match="Target node"):
        validator.validate(connectome, proposal)


def test_duplicate_edge_is_rejected(validator, connectome):
    connectome.add_edge(Edge("a", "b", "related_to"))

    proposal = {
        "operation": "create_edge",
        "source": "a",
        "target": "b",
        "edge_type": "another_type",
    }

    with pytest.raises(ValueError, match="already exists"):
        validator.validate(connectome, proposal)


@pytest.mark.parametrize("weight", [-0.1, 1.1, float("nan"), float("inf")])
def test_create_edge_invalid_weight_is_rejected(
    validator, connectome, weight
):
    proposal = {
        "operation": "create_edge",
        "source": "a",
        "target": "b",
        "edge_type": "related_to",
        "weight": weight,
    }

    with pytest.raises(ValueError):
        validator.validate(connectome, proposal)


def test_create_edge_respects_configured_maximum(connectome):
    validator = ProposalValidator(Config(max_weight=0.5))

    proposal = {
        "operation": "create_edge",
        "source": "a",
        "target": "b",
        "edge_type": "related_to",
        "weight": 0.8,
    }

    with pytest.raises(ValueError, match="configured maximum"):
        validator.validate(connectome, proposal)


def test_update_missing_edge_is_rejected(validator, connectome):
    proposal = {
        "operation": "update_edge_weight",
        "source": "a",
        "target": "b",
        "weight": 0.8,
    }

    with pytest.raises(ValueError, match="does not exist"):
        validator.validate(connectome, proposal)


def test_update_weight_above_configured_maximum(connectome):
    connectome.add_edge(Edge("a", "b", "related_to", 0.4))
    validator = ProposalValidator(Config(max_weight=0.5))

    proposal = {
        "operation": "update_edge_weight",
        "source": "a",
        "target": "b",
        "weight": 0.8,
    }

    with pytest.raises(ValueError, match="configured maximum"):
        validator.validate(connectome, proposal)


@pytest.mark.parametrize("weight", [-0.1, 1.1, float("nan")])
def test_update_invalid_weight_is_rejected(
    validator, connectome, weight
):
    connectome.add_edge(Edge("a", "b", "related_to", 0.5))

    proposal = {
        "operation": "update_edge_weight",
        "source": "a",
        "target": "b",
        "weight": weight,
    }

    with pytest.raises(ValueError):
        validator.validate(connectome, proposal)


@pytest.mark.parametrize(
    "proposal",
    [
        {
            "operation": "create_node",
            "id": "c",
            "node_type": "concept",
            "label": "Gamma",
        },
        {
            "operation": "create_edge",
            "source": "a",
            "target": "b",
            "edge_type": "related_to",
        },
    ],
)
def test_successful_validation_never_mutates_connectome(
    validator, connectome, proposal
):
    before = snapshot(connectome)

    validator.validate(connectome, proposal)

    assert snapshot(connectome) == before


def test_update_validation_never_mutates_connectome(
    validator, connectome
):
    connectome.add_edge(Edge("a", "b", "related_to", 0.5))
    before = snapshot(connectome)

    validator.validate(
        connectome,
        {
            "operation": "update_edge_weight",
            "source": "a",
            "target": "b",
            "weight": 0.8,
        },
    )

    assert snapshot(connectome) == before


def test_failed_validation_never_mutates_connectome(
    validator, connectome
):
    before = snapshot(connectome)

    proposal = {
        "operation": "create_node",
        "id": "a",
        "node_type": "concept",
        "label": "Duplicate",
    }

    with pytest.raises(ValueError):
        validator.validate(connectome, proposal)

    assert snapshot(connectome) == before
