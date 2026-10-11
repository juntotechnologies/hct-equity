import numpy as np
import pandas as pd
import pytest

from hct_equity import teaching
from hct_equity.config import load_config


@pytest.fixture(scope="module")
def cohort():
    settings = load_config().teaching_simulation.model_copy(update={"n": 4000})
    return teaching.simulate_cohort(settings)


def test_cohort_has_both_potential_outcomes(cohort):
    expected = {"frail", "severe", "ric", "risk_mac", "risk_ric", "risk_observed", "event"}
    assert expected <= set(cohort.columns)
    assert cohort["event"].isin([0, 1]).all()


def test_true_effect_has_opposite_sign_by_frailty(cohort):
    effect = cohort["risk_ric"] - cohort["risk_mac"]
    assert (effect[cohort["frail"] == 1] < 0).all()
    assert (effect[cohort["frail"] == 0] > 0).all()


def test_policy_risk_uses_the_chosen_potential_outcome():
    frame = pd.DataFrame({"risk_mac": [0.2, 0.6], "risk_ric": [0.4, 0.1]})
    assert teaching.policy_risk(frame, np.array([False, True])) == pytest.approx(0.15)
    assert teaching.policy_risk(frame, np.array([True, False])) == pytest.approx(0.5)


def test_best_policy_is_never_worse_than_any_other(cohort):
    model = teaching.fit_prognostic(cohort, teaching.OBSERVED_FEATURES)
    table = teaching.compare_policies(cohort, model, teaching.OBSERVED_FEATURES)
    assert table.loc["Choose with true risks", "event_risk"] == table["event_risk"].min()
