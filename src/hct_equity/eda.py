"""Pure EDA summaries. Each summary maps one frame to one row of numbers."""

from collections.abc import Callable
from functools import partial

import matplotlib.pyplot as plt
import pandas as pd
from lifelines import KaplanMeierFitter

from hct_equity.config import Columns

ALL_LABEL = "All"

Summary = Callable[[pd.DataFrame], dict[str, float]]


def by_group(frame: pd.DataFrame, group: str, summary: Summary) -> pd.DataFrame:
    rows = {ALL_LABEL: summary(frame)}
    rows |= {name: summary(part) for name, part in frame.groupby(group)}
    return pd.DataFrame.from_dict(rows, orient="index")


def cohort_summary(frame: pd.DataFrame, cols: Columns, features: list[str]) -> dict[str, float]:
    time = frame[cols.time]
    return {
        "n": len(frame),
        "missing_cell_pct": 100 * frame[features].isna().to_numpy().mean(),
        "efs_event_pct": 100 * frame[cols.event].mean(),
        "time_p25": time.quantile(0.25),
        "time_median": time.median(),
        "time_p75": time.quantile(0.75),
        "time_max": time.max(),
    }


def known_status(frame: pd.DataFrame, cols: Columns, horizon: float) -> dict[str, float]:
    event = frame[cols.event] == 1
    early = frame[cols.time] <= horizon
    censored_early = 100 * (~event & early).mean()
    return {
        "event_by_h_pct": 100 * (event & early).mean(),
        "event_free_past_h_pct": 100 * (~early).mean(),
        "censored_before_h_pct": censored_early,
        "known_pct": 100 - censored_early,
    }


def km_risk(frame: pd.DataFrame, cols: Columns, horizons: list[int]) -> dict[str, float]:
    fitter = KaplanMeierFitter().fit(frame[cols.time], frame[cols.event])
    survival = fitter.survival_function_at_times(horizons)
    return {f"km_risk_{h}m_pct": 100 * (1 - s) for h, s in zip(horizons, survival, strict=True)}


def top_missing(frame: pd.DataFrame, features: list[str], k: int) -> pd.Series:
    return (100 * frame[features].isna().mean()).sort_values(ascending=False).head(k)


def known_status_table(frame: pd.DataFrame, cols: Columns, horizons: list[int]) -> pd.DataFrame:
    tables = {h: by_group(frame, cols.group, partial(known_status, cols=cols, horizon=h)) for h in horizons}
    return pd.concat(tables, names=["horizon_m", "group"])


def plot_km_by_group(frame: pd.DataFrame, cols: Columns, horizons: list[int], note: str) -> plt.Figure:
    fig, ax = plt.subplots(figsize=(8, 5))
    for name, part in frame.groupby(cols.group):
        fitter = KaplanMeierFitter(label=name).fit(part[cols.time], part[cols.event])
        fitter.plot_survival_function(ax=ax, ci_show=False)
    for h in horizons:
        ax.axvline(h, color="grey", linestyle="--", linewidth=1)
    ax.set(xlabel="Months since HCT", ylabel="Event-free survival", xlim=(0, 60))
    ax.set_title(f"Event-free survival by race group\n{note}", fontsize=10)
    ax.legend(fontsize=8)
    fig.tight_layout()
    return fig
