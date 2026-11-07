
import math

import pytest

from zeus.config import Config


def test_default_configuration():
    config = Config()

    assert config.k == 7
    assert config.activation_decay == 0.8
    assert config.threshold == 0.15
    assert config.horizon == 3
    assert config.learning_rate == 0.1
    assert config.max_weight == 1.0
    assert config.decay_period_days == 7
    assert config.consolidation_interval == 5


def test_custom_configuration():
    config = Config(k=10, horizon=5, learning_rate=0.25)

    assert config.k == 10
    assert config.horizon == 5
    assert config.learning_rate == 0.25


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("k", 0),
        ("horizon", 0),
        ("decay_period_days", 0),
        ("consolidation_interval", 0),
    ],
)
def test_positive_integer_validation(field, value):
    with pytest.raises(ValueError):
        Config(**{field: value})


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("activation_decay", -0.1),
        ("threshold", 1.1),
        ("learning_rate", -1),
        ("reinforcement_factor", 2),
        ("initial_weight", -0.1),
        ("max_weight", 1.1),
        ("decay_factor", -0.1),
        ("prune_threshold", 2),
        ("consolidation_weight", 1.5),
        ("activation_decay", math.nan),
        ("threshold", math.inf),
    ],
)
def test_bounded_value_validation(field, value):
    with pytest.raises(ValueError):
        Config(**{field: value})


def test_consolidation_strength_must_be_positive():
    with pytest.raises(ValueError):
        Config(consolidation_strength=0)


def test_consolidation_strength_must_be_finite():
    with pytest.raises(ValueError):
        Config(consolidation_strength=math.inf)


def test_initial_weight_cannot_exceed_maximum():
    with pytest.raises(ValueError):
        Config(initial_weight=0.9, max_weight=0.5)


def test_configuration_is_immutable():
    config = Config()

    with pytest.raises(AttributeError):
        config.k = 10
