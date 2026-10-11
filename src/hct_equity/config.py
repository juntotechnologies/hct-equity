"""Typed project configuration, loaded once from config/project.json."""

from pathlib import Path

from pydantic import BaseModel, ConfigDict

CONFIG_PATH = Path(__file__).resolve().parents[2] / "config" / "project.json"


class Columns(BaseModel):
    model_config = ConfigDict(frozen=True)
    id: str
    event: str
    time: str
    group: str


class Paths(BaseModel):
    model_config = ConfigDict(frozen=True)
    train: Path
    figures: Path
    reports: Path


class MlflowSettings(BaseModel):
    model_config = ConfigDict(frozen=True)
    default_tracking_uri: str
    experiment: str
    tags: dict[str, str]


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


class Project(BaseModel):
    model_config = ConfigDict(frozen=True)
    competition: str
    synthetic_note: str
    citation: str
    columns: Columns
    paths: Paths
    horizons_months: list[int]
    mlflow: MlflowSettings
    dca_thresholds: Thresholds
    teaching_simulation: SimulationSettings
    treatment_example: TreatmentExample


def load_config(path: Path = CONFIG_PATH) -> Project:
    return Project.model_validate_json(path.read_text())
