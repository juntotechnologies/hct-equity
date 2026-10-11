from hct_equity.config import Thresholds, load_config


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
