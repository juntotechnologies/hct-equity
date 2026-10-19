import json

import pytest
from pydantic import ValidationError

from hct_equity.config import CONFIG_PATH, Project, Thresholds, load_config


def test_config_loads_and_validates():
    project = load_config()
    assert project.horizons_months == [12, 24]


def test_threshold_values_include_both_ends():
    values = Thresholds(start=0.05, stop=0.5, step=0.01).values()
    assert values[0] == 0.05
    assert values[-1] == 0.5
    assert len(values) == 46


def test_paths_resolve_against_repository_root():
    project = load_config()
    assert project.paths.train.is_absolute()
    assert project.paths.train.parent.parent == project.paths.figures.parent


def test_fairness_settings_load():
    fairness = load_config().fairness
    assert fairness.horizon_months in load_config().horizons_months
    assert fairness.folds >= 2


def test_fairness_horizon_must_be_a_project_horizon():
    raw = json.loads(CONFIG_PATH.read_text())
    raw["fairness"]["horizon_months"] = 7
    with pytest.raises(ValidationError):
        Project.model_validate(raw)
