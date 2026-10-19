"""Typed project configuration, loaded once from config/project.json."""

from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, model_validator

CONFIG_PATH = Path(__file__).resolve().parents[2] / "config" / "project.json"
LABELS_PATH = CONFIG_PATH.with_name("labels.json")

FormatKind = Literal[
    "percent",
    "percent_one_decimal",
    "percent_value",
    "points",
    "count",
    "one_decimal",
    "two_decimals",
    "three_decimals",
    "signed_three_decimals",
]


class Columns(BaseModel):
    model_config = ConfigDict(frozen=True)
    id: str
    event: str
    time: str
    group: str
    risk: str


class Paths(BaseModel):
    model_config = ConfigDict(frozen=True)
    train: Path
    figures: Path
    reports: Path


class Thresholds(BaseModel):
    model_config = ConfigDict(frozen=True)
    start: float
    stop: float
    step: float

    def values(self) -> list[float]:
        count = round((self.stop - self.start) / self.step) + 1
        return [round(self.start + i * self.step, 4) for i in range(count)]


class SimulationSettings(BaseModel):
    """Toy cohort where the true treatment effect is known. See notebooks/01."""

    model_config = ConfigDict(frozen=True)
    n: int
    seed: int
    p_frail: float
    p_severe: float
    ric_logit_base: float
    ric_logit_frail: float
    ric_logit_severe: float
    event_logit_base: float
    event_logit_frail: float
    event_logit_severe: float
    ric_effect_frail: float
    ric_effect_fit: float


class TreatmentExample(BaseModel):
    model_config = ConfigDict(frozen=True)
    column: str
    arms: list[str]
    case_mix: list[str]


class FairnessFigures(BaseModel):
    model_config = ConfigDict(frozen=True)
    calibration: str
    dca: str


class FairnessPlot(BaseModel):
    """Validated categorical palette, one slot per group in sorted order."""

    model_config = ConfigDict(frozen=True)
    group_colors: list[str]
    group_markers: list[str]
    model_color: str
    reference_color: str
    treat_none_color: str


class FairnessSettings(BaseModel):
    """Calibration and DCA by race group. See notebooks/02."""

    model_config = ConfigDict(frozen=True)
    horizon_months: int
    folds: int
    seed: int
    penalizer: float
    risk_bins: int
    dca_thresholds: Thresholds
    table_thresholds: list[float]
    figure_names: FairnessFigures
    plot: FairnessPlot
    report_name: str


class Project(BaseModel):
    model_config = ConfigDict(frozen=True)
    competition: str
    synthetic_note: str
    citation: str
    columns: Columns
    paths: Paths
    horizons_months: list[int]
    dca_thresholds: Thresholds
    teaching_simulation: SimulationSettings
    treatment_example: TreatmentExample
    teaching_dca_thresholds: Thresholds
    fairness: FairnessSettings

    @model_validator(mode="after")
    def fairness_horizon_is_a_project_horizon(self) -> "Project":
        if self.fairness.horizon_months not in self.horizons_months:
            raise ValueError(f"fairness.horizon_months must be one of {self.horizons_months}")
        return self


def resolve_paths(paths: Paths, root: Path) -> Paths:
    return Paths(**{name: root / value for name, value in paths})


def load_config(path: Path = CONFIG_PATH) -> Project:
    """Paths resolve against the repository root, so notebooks can run from any directory."""
    project = Project.model_validate_json(path.read_text())
    return project.model_copy(update={"paths": resolve_paths(project.paths, path.parents[1])})


class Labels(BaseModel):
    """Display names and number formats for notebook tables."""

    model_config = ConfigDict(frozen=True)
    combined_index_name: str
    index_names: dict[str, str]
    values: dict[str, dict[str, str]]
    column_templates: dict[str, str]
    columns: dict[str, str]
    formats: dict[str, FormatKind]


def load_labels(path: Path = LABELS_PATH) -> Labels:
    return Labels.model_validate_json(path.read_text())
