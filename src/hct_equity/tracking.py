"""MLflow setup: every run goes to the configured experiment with project tags."""

import os

import mlflow

from hct_equity.config import MlflowSettings


def start_run(settings: MlflowSettings, run_name: str) -> mlflow.ActiveRun:
    uri = os.environ.get("MLFLOW_TRACKING_URI", settings.default_tracking_uri)
    mlflow.set_tracking_uri(uri)
    mlflow.set_experiment(settings.experiment)
    return mlflow.start_run(run_name=run_name, tags=settings.tags)
