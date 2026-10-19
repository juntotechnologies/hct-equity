import numpy as np
import pandas as pd
import pytest

from hct_equity import fairness
from hct_equity.config import Columns

COLUMNS = Columns(id="ID", event="efs", time="efs_time", group="race_group", risk="predicted_risk")


def scored_frame(seed: int = 0, n: int = 400) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    risk = rng.uniform(0.1, 0.9, n)
    event_by_12 = rng.uniform(size=n) < risk
    time = np.where(event_by_12, rng.uniform(0.5, 11.5, n), rng.uniform(12.5, 60, n))
    return pd.DataFrame(
        {
            "efs_time": time,
            "efs": np.where(event_by_12, 1, rng.integers(0, 2, n)),
            "race_group": np.where(np.arange(n) % 2 == 0, "A", "B"),
            "predicted_risk": risk,
        }
    )


def test_km_risk_without_censoring_is_the_event_fraction():
    time = np.array([1.0, 2.0, 13.0, 14.0])
    event = np.array([1, 1, 0, 1])
    assert fairness.km_risk(time, event, 12) == pytest.approx(0.5)


def test_horizon_status_marks_early_censoring_unknown():
    status = fairness.horizon_status(np.array([3.0, 3.0, 20.0]), np.array([1, 0, 1]), 12)
    assert status[0] == 1
    assert np.isnan(status[1])
    assert status[2] == 0


def test_calibration_slope_is_one_for_true_risks():
    frame = scored_frame(n=20000)
    status = fairness.horizon_status(frame["efs_time"], frame["efs"], 12)
    assert fairness.calibration_slope(frame["predicted_risk"], status) == pytest.approx(1.0, abs=0.1)


def test_group_metrics_has_one_row_per_group():
    table = fairness.group_metrics(scored_frame(), COLUMNS, 12)
    assert list(table.index) == ["A", "B"]
    assert set(table.columns) == {"n", "events_by_horizon", "c_index", "observed_expected", "calibration_slope"}
    assert table["n"].sum() == 400


def test_true_risks_are_well_calibrated():
    table = fairness.group_metrics(scored_frame(n=20000), COLUMNS, 12)
    assert table["observed_expected"].to_numpy() == pytest.approx([1.0, 1.0], abs=0.05)


def test_stratified_c_index_is_mean_minus_population_std():
    metrics = pd.DataFrame({"c_index": [0.6, 0.7]})
    assert fairness.stratified_c_index(metrics) == pytest.approx(0.65 - 0.05)


def test_calibration_by_decile_returns_bins_per_group():
    table = fairness.calibration_by_decile(scored_frame(), COLUMNS, 12, 5)
    assert table.groupby(COLUMNS.group).size().to_dict() == {"A": 5, "B": 5}
    assert table[["predicted", "observed"]].ge(0).all().all()


def test_dca_by_group_labels_each_group():
    result = fairness.dca_by_group(scored_frame(), COLUMNS, 12, [0.2, 0.4])
    assert set(result[COLUMNS.group]) == {"A", "B"}
    assert set(result["model"]) == {fairness.MODEL_LABEL, "all", "none"}


def test_recalibration_returns_one_risk_per_row_in_range():
    frame = scored_frame()
    recalibrated = fairness.recalibrated_risk(frame, COLUMNS, 12, folds=3, seed=0)
    assert recalibrated.index.equals(frame.index)
    assert recalibrated.between(0, 1).all()


def test_net_benefit_at_pivots_groups_by_threshold():
    result = fairness.dca_by_group(scored_frame(), COLUMNS, 12, [0.2, 0.4])
    table = fairness.net_benefit_at(result, COLUMNS, [0.2, 0.4])
    assert table.shape == (2, 2)


def test_net_benefit_gain_subtracts_the_best_default():
    dca = pd.DataFrame(
        {
            "race_group": ["A"] * 6,
            "model": [fairness.MODEL_LABEL, "all", "none"] * 2,
            "threshold": [0.2, 0.2, 0.2, 0.6, 0.6, 0.6],
            "net_benefit": [0.5, 0.4, 0.0, 0.1, -0.2, 0.0],
        }
    )
    gain = fairness.net_benefit_gain(dca, COLUMNS, [0.2, 0.6])
    assert gain.loc["A", 0.2] == pytest.approx(0.1)
    assert gain.loc["A", 0.6] == pytest.approx(0.1)
