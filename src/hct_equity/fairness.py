"""Discrimination, calibration and net benefit at one horizon, per race group. See notebooks/02."""

from collections.abc import Iterable

import dcurves
import numpy as np
import pandas as pd
from lifelines import KaplanMeierFitter
from lifelines.utils import concordance_index
from scipy.special import logit
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import KFold

from hct_equity.config import Columns

MODEL_LABEL = "Cox model"
RISK_CLIP = 1e-6


def km_risk(time: np.ndarray, event: np.ndarray, horizon: float) -> float:
    """Observed risk by the horizon, with censoring handled by Kaplan-Meier."""
    fitter = KaplanMeierFitter().fit(time, event)
    return float(1 - fitter.survival_function_at_times(horizon).iloc[0])


def horizon_status(time: np.ndarray, event: np.ndarray, horizon: float) -> np.ndarray:
    """1 = event by the horizon, 0 = event-free at the horizon, NaN = censored before it."""
    time, event = np.asarray(time), np.asarray(event)
    status = np.where(time > horizon, 0.0, np.nan)
    return np.where((time <= horizon) & (event == 1), 1.0, status)


def risk_logit(risk: np.ndarray) -> np.ndarray:
    return logit(np.clip(np.asarray(risk, dtype=float), RISK_CLIP, 1 - RISK_CLIP))


def fit_recalibration(risk: np.ndarray, status: np.ndarray) -> LogisticRegression:
    """Logistic recalibration on rows with known status at the horizon."""
    known = ~np.isnan(status)
    features = risk_logit(risk)[known].reshape(-1, 1)
    return LogisticRegression(C=np.inf).fit(features, status[known])


def calibration_slope(risk: np.ndarray, status: np.ndarray) -> float:
    return float(fit_recalibration(risk, np.asarray(status)).coef_[0, 0])


def one_group_metrics(frame: pd.DataFrame, columns: Columns, horizon: float) -> dict[str, float]:
    time, event, risk = frame[columns.time], frame[columns.event], frame[columns.risk]
    status = horizon_status(time, event, horizon)
    return {
        "n": len(frame),
        "events_by_horizon": int(np.nansum(status)),
        "c_index": concordance_index(time, -risk, event),
        "observed_expected": km_risk(time, event, horizon) / risk.mean(),
        "calibration_slope": calibration_slope(risk, status),
    }


def group_metrics(frame: pd.DataFrame, columns: Columns, horizon: float) -> pd.DataFrame:
    rows = {name: one_group_metrics(part, columns, horizon) for name, part in frame.groupby(columns.group)}
    return pd.DataFrame.from_dict(rows, orient="index").rename_axis(columns.group)


def stratified_c_index(metrics: pd.DataFrame) -> float:
    """Competition metric: mean minus population standard deviation of the per-group C-index."""
    return float(metrics["c_index"].mean() - metrics["c_index"].std(ddof=0))


def one_bin_calibration(frame: pd.DataFrame, columns: Columns, horizon: float) -> pd.Series:
    observed = km_risk(frame[columns.time], frame[columns.event], horizon)
    return pd.Series({"n": len(frame), "predicted": frame[columns.risk].mean(), "observed": observed})


def one_group_deciles(frame: pd.DataFrame, columns: Columns, horizon: float, bins: int) -> pd.DataFrame:
    labels = pd.qcut(frame[columns.risk], bins, labels=False, duplicates="drop").rename("risk_bin")
    rows = {name: one_bin_calibration(part, columns, horizon) for name, part in frame.groupby(labels)}
    return pd.DataFrame.from_dict(rows, orient="index").rename_axis("risk_bin")


def calibration_by_decile(frame: pd.DataFrame, columns: Columns, horizon: float, bins: int) -> pd.DataFrame:
    """Mean predicted vs Kaplan-Meier observed risk, per risk bin, per group."""
    parts = {name: one_group_deciles(part, columns, horizon, bins) for name, part in frame.groupby(columns.group)}
    return pd.concat(parts, names=[columns.group]).reset_index()


def one_group_dca(frame: pd.DataFrame, columns: Columns, horizon: float, thresholds: Iterable[float]) -> pd.DataFrame:
    scored = frame[[columns.time, columns.event, columns.risk]].rename(columns={columns.risk: MODEL_LABEL})
    return dcurves.dca(
        data=scored,
        outcome=columns.event,
        modelnames=[MODEL_LABEL],
        thresholds=list(thresholds),
        time=horizon,
        time_to_outcome_col=columns.time,
    )


def dca_by_group(frame: pd.DataFrame, columns: Columns, horizon: float, thresholds: Iterable[float]) -> pd.DataFrame:
    """Time-to-event decision curve analysis, one curve set per group."""
    parts = {name: one_group_dca(part, columns, horizon, thresholds) for name, part in frame.groupby(columns.group)}
    return pd.concat(parts, names=[columns.group]).reset_index(level=0)


def net_benefit_at(dca: pd.DataFrame, columns: Columns, thresholds: list[float]) -> pd.DataFrame:
    """Model net benefit at chosen thresholds: one row per group, one column per threshold."""
    model = dca[(dca["model"] == MODEL_LABEL) & dca["threshold"].round(4).isin(thresholds)]
    return model.pivot(index=columns.group, columns="threshold", values="net_benefit")


def recalibrate_fold(train: pd.DataFrame, test: pd.DataFrame, columns: Columns, horizon: float) -> np.ndarray:
    status = horizon_status(train[columns.time], train[columns.event], horizon)
    model = fit_recalibration(train[columns.risk], status)
    return model.predict_proba(risk_logit(test[columns.risk]).reshape(-1, 1))[:, 1]


def recalibrate_group(frame: pd.DataFrame, columns: Columns, horizon: float, folds: int, seed: int) -> pd.Series:
    """Cross-fitted: each row is recalibrated by a model that did not see it."""
    risk = pd.Series(np.nan, index=frame.index)
    for train_rows, test_rows in KFold(folds, shuffle=True, random_state=seed).split(frame):
        test = frame.iloc[test_rows]
        risk[test.index] = recalibrate_fold(frame.iloc[train_rows], test, columns, horizon)
    return risk


def recalibrated_risk(frame: pd.DataFrame, columns: Columns, horizon: float, folds: int, seed: int) -> pd.Series:
    """Exploratory: per-group logistic recalibration of the predicted risk."""
    parts = [recalibrate_group(part, columns, horizon, folds, seed) for _, part in frame.groupby(columns.group)]
    return pd.concat(parts).reindex(frame.index).rename(columns.risk)
