"""Toy cohort that shows why a prognostic model cannot choose a treatment.

Each simulated patient has two potential outcomes: event risk under MAC and
under RIC. Real data shows only one. Here we keep both, so the truth is known.
"""

import dcurves
import numpy as np
import pandas as pd
from scipy.special import expit
from sklearn.linear_model import LogisticRegression

from hct_equity.config import SimulationSettings

# "severe" is visible to the simulated clinician but is not recorded in the data.
OBSERVED_FEATURES = ["frail", "ric", "frail_x_ric"]
ALL_FEATURES = ["frail", "severe", "ric", "frail_x_ric"]
UNREGULARISED = 1e6
MODEL_LABEL = "prognostic_model"


def treatment_logit(frail: np.ndarray, severe: np.ndarray, s: SimulationSettings) -> np.ndarray:
    return s.ric_logit_base + s.ric_logit_frail * frail + s.ric_logit_severe * severe


def event_logit(frail: np.ndarray, severe: np.ndarray, ric: int, s: SimulationSettings) -> np.ndarray:
    effect = np.where(frail == 1, s.ric_effect_frail, s.ric_effect_fit)
    return s.event_logit_base + s.event_logit_frail * frail + s.event_logit_severe * severe + ric * effect


def simulate_cohort(s: SimulationSettings) -> pd.DataFrame:
    rng = np.random.default_rng(s.seed)
    frail = rng.binomial(1, s.p_frail, s.n)
    severe = rng.binomial(1, s.p_severe, s.n)
    ric = rng.binomial(1, expit(treatment_logit(frail, severe, s)))
    risk_mac = expit(event_logit(frail, severe, 0, s))
    risk_ric = expit(event_logit(frail, severe, 1, s))
    risk_observed = np.where(ric == 1, risk_ric, risk_mac)
    frame = pd.DataFrame({"frail": frail, "severe": severe, "ric": ric})
    frame = frame.assign(risk_mac=risk_mac, risk_ric=risk_ric, risk_observed=risk_observed)
    return frame.assign(frail_x_ric=frail * ric, event=rng.binomial(1, risk_observed))


def with_treatment(frame: pd.DataFrame, ric: int) -> pd.DataFrame:
    return frame.assign(ric=ric, frail_x_ric=frame["frail"] * ric)


def fit_prognostic(frame: pd.DataFrame, features: list[str]) -> LogisticRegression:
    return LogisticRegression(C=UNREGULARISED).fit(frame[features], frame["event"])


def predict_risk(model: LogisticRegression, frame: pd.DataFrame, features: list[str]) -> np.ndarray:
    return model.predict_proba(frame[features])[:, 1]


def counterfactual_risks(
    model: LogisticRegression, frame: pd.DataFrame, features: list[str]
) -> tuple[np.ndarray, np.ndarray]:
    mac = predict_risk(model, with_treatment(frame, 0), features)
    ric = predict_risk(model, with_treatment(frame, 1), features)
    return mac, ric


def effect_by_frailty(frame: pd.DataFrame, model: LogisticRegression, features: list[str]) -> pd.DataFrame:
    """RIC minus MAC event risk: truth, the naive comparison, and the model."""
    mac, ric = counterfactual_risks(model, frame, features)
    table = frame.assign(true_effect=frame["risk_ric"] - frame["risk_mac"], model_effect=ric - mac)
    naive = frame.groupby(["frail", "ric"])["event"].mean().unstack()
    result = table.groupby("frail")[["true_effect", "model_effect"]].mean()
    return result.assign(naive_effect=naive[1] - naive[0])


def policy_risk(frame: pd.DataFrame, choose_ric: np.ndarray) -> float:
    return float(np.where(choose_ric, frame["risk_ric"], frame["risk_mac"]).mean())


def policy_choices(frame: pd.DataFrame, model: LogisticRegression, features: list[str]) -> dict[str, np.ndarray]:
    mac, ric = counterfactual_risks(model, frame, features)
    return {
        "Current practice": frame["ric"].to_numpy() == 1,
        "Everyone MAC": np.zeros(len(frame), dtype=bool),
        "Everyone RIC": np.ones(len(frame), dtype=bool),
        "Choose with prognostic model": ric < mac,
        "Choose with true risks": (frame["risk_ric"] < frame["risk_mac"]).to_numpy(),
    }


def compare_policies(frame: pd.DataFrame, model: LogisticRegression, features: list[str]) -> pd.DataFrame:
    choices = policy_choices(frame, model, features)
    rows = {name: {"event_risk": policy_risk(frame, c), "pct_ric": 100 * c.mean()} for name, c in choices.items()}
    return pd.DataFrame.from_dict(rows, orient="index")


def surveillance_dca(
    frame: pd.DataFrame, model: LogisticRegression, features: list[str], thresholds: list[float]
) -> pd.DataFrame:
    """DCA for an act-or-not decision, here extra surveillance. Risk is all it needs."""
    scored = frame.assign(**{MODEL_LABEL: predict_risk(model, frame, features)})
    return dcurves.dca(data=scored, outcome="event", modelnames=[MODEL_LABEL], thresholds=thresholds)


def arm_case_mix(frame: pd.DataFrame, column: str, arms: list[str], case_mix: list[str], event: str) -> pd.DataFrame:
    """Who received each treatment arm, and how often they had an event."""
    chosen = frame[frame[column].isin(arms)]
    grouped = chosen.groupby(column)
    table = grouped[case_mix].mean().add_prefix("mean_")
    return table.assign(n=grouped.size(), event_pct=100 * grouped[event].mean()).loc[arms]
