"""Step 1 EDA: write aggregate tables and one figure."""

from functools import partial
from pathlib import Path

import pandas as pd

from hct_equity import eda
from hct_equity.config import Project, load_config
from hct_equity.data import feature_columns, load_train

TOP_MISSING = 10


def build_tables(project: Project, frame: pd.DataFrame) -> dict[str, pd.DataFrame]:
    cols, horizons = project.columns, project.horizons_months
    features = feature_columns(project, frame)
    summary = partial(eda.cohort_summary, cols=cols, features=features)
    return {
        "cohort": eda.by_group(frame, cols.group, summary),
        "km_risk": eda.by_group(frame, cols.group, partial(eda.km_risk, cols=cols, horizons=horizons)),
        "known_status": eda.known_status_table(frame, cols, horizons),
        "top_missing": eda.top_missing(frame, features, TOP_MISSING).to_frame("missing_pct"),
    }


def write_tables(tables: dict[str, pd.DataFrame], out_dir: Path, note: str) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    for name, table in tables.items():
        path = out_dir / f"{name}.md"
        path.write_text(f"_{note}_\n\n{table.round(2).to_markdown()}\n")


def main() -> None:
    project = load_config()
    frame = load_train(project)
    write_tables(build_tables(project, frame), project.paths.reports / "eda", project.synthetic_note)
    fig = eda.plot_km_by_group(frame, project.columns, project.horizons_months, project.synthetic_note)
    fig.savefig(project.paths.figures / "eda_km_by_group.png", dpi=150)


if __name__ == "__main__":
    main()
