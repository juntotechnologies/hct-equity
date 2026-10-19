import numpy as np
import pandas as pd
import pytest

from hct_equity import model
from hct_equity.config import Columns, load_config

COLUMNS = Columns(id="ID", event="efs", time="efs_time", group="race_group", risk="predicted_risk")


@pytest.fixture(scope="module")
def frame() -> pd.DataFrame:
    rng = np.random.default_rng(1)
    n = 300
    age = rng.normal(50, 10, n)
    age[::17] = np.nan
    return pd.DataFrame(
        {
            "ID": np.arange(n),
            "efs_time": rng.exponential(20 * np.exp(-(np.nan_to_num(age, nan=50) - 50) / 20)),
            "efs": rng.integers(0, 2, n),
            "race_group": np.where(np.arange(n) % 3 == 0, "A", "B"),
            "age": age,
            "donor": rng.choice(["x", "y", None], n),
        }
    )


@pytest.fixture(scope="module")
def settings():
    return load_config().fairness.model_copy(update={"folds": 3})


def test_split_features_separates_text_from_numbers(frame):
    categorical, numeric = model.split_features(frame, ["age", "donor", "race_group"])
    assert categorical == ["donor", "race_group"]
    assert numeric == ["age"]


def test_fold_assignments_cover_every_row_once(frame, settings):
    folds = model.fold_assignments(frame, COLUMNS, settings.folds, settings.seed)
    assert len(folds) == len(frame)
    assert set(folds) == {0, 1, 2}


def test_out_of_fold_risk_has_one_valid_risk_per_row(frame, settings):
    risk = model.out_of_fold_risk(frame, ["age", "donor", "race_group"], COLUMNS, settings)
    assert risk.index.equals(frame.index)
    assert risk.name == COLUMNS.risk
    assert risk.between(0, 1).all()


class RecordingFit:
    """Records the training rows of each fold, then fits as usual."""

    def __init__(self, fit):
        self.fit = fit
        self.train_indexes: list[set] = []

    def __call__(self, design, time, event, penalizer):
        self.train_indexes.append(set(design.index))
        return self.fit(design, time, event, penalizer)


def test_fold_model_never_sees_its_test_rows(frame, settings, monkeypatch):
    recorder = RecordingFit(model.fit_cox)
    monkeypatch.setattr(model, "fit_cox", recorder)
    folds = model.fold_assignments(frame, COLUMNS, settings.folds, settings.seed)
    model.out_of_fold_risk(frame, ["age", "donor"], COLUMNS, settings)
    for fold, train_index in enumerate(recorder.train_indexes):
        assert train_index.isdisjoint(set(frame.index[folds == fold]))
