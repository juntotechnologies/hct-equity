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


class Project(BaseModel):
    model_config = ConfigDict(frozen=True)
    competition: str
    synthetic_note: str
    citation: str
    columns: Columns
    paths: Paths
    horizons_months: list[int]
    mlflow: MlflowSettings


def load_config(path: Path = CONFIG_PATH) -> Project:
    return Project.model_validate_json(path.read_text())
