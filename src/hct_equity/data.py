"""Owns the competition file layout. Other modules read data only through here."""

import pandas as pd

from hct_equity.config import Project


def load_train(project: Project) -> pd.DataFrame:
    return pd.read_csv(project.paths.train)


def feature_columns(project: Project, frame: pd.DataFrame) -> list[str]:
    reserved = set(project.columns.model_dump().values())
    return [name for name in frame.columns if name not in reserved]
