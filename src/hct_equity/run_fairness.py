"""Notebook 02 results: per-group metrics table and two figures."""

from dataclasses import dataclass

import matplotlib.pyplot as plt
import pandas as pd

from hct_equity import fairness, fairness_plots, model
from hct_equity.config import Project, load_config
from hct_equity.data import feature_columns, load_train


@dataclass(frozen=True)
class FairnessResults:
    metrics: pd.DataFrame
    stratified_c_index: float
    deciles: pd.DataFrame
    dca: pd.DataFrame


def model_features(project: Project, frame: pd.DataFrame) -> list[str]:
    """Competition models used race group as a feature, so this one does too."""
    return [*feature_columns(project, frame), project.columns.group]


def score(project: Project, frame: pd.DataFrame) -> pd.DataFrame:
    risk = model.out_of_fold_risk(frame, model_features(project, frame), project.columns, project.fairness)
    return frame.assign(**{project.columns.risk: risk})


def build_results(project: Project, scored: pd.DataFrame) -> FairnessResults:
    cols, settings = project.columns, project.fairness
    metrics = fairness.group_metrics(scored, cols, settings.horizon_months)
    return FairnessResults(
        metrics=metrics,
        stratified_c_index=fairness.stratified_c_index(metrics),
        deciles=fairness.calibration_by_decile(scored, cols, settings.horizon_months, settings.risk_bins),
        dca=fairness.dca_by_group(scored, cols, settings.horizon_months, settings.dca_thresholds.values()),
    )


def build_figures(project: Project, results: FairnessResults) -> dict[str, plt.Figure]:
    cols, style, note = project.columns, project.fairness.plot, project.synthetic_note
    names = project.fairness.figure_names
    return {
        names.calibration: fairness_plots.plot_calibration(results.deciles, cols, style, note),
        names.dca: fairness_plots.plot_dca_by_group(results.dca, cols, style, note),
    }


def write_results(project: Project, results: FairnessResults, figures: dict[str, plt.Figure]) -> None:
    table = results.metrics.round(3).to_markdown()
    summary = f"Stratified C-index (mean - SD): {results.stratified_c_index:.4f}"
    report = project.paths.reports / project.fairness.report_name
    report.write_text(f"_{project.synthetic_note}_\n\n{table}\n\n{summary}\n")
    for name, fig in figures.items():
        fig.savefig(project.paths.figures / name, dpi=150)


def main() -> None:
    project = load_config()
    results = build_results(project, score(project, load_train(project)))
    write_results(project, results, build_figures(project, results))


if __name__ == "__main__":
    main()
