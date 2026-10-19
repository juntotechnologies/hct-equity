"""Cox model with out-of-fold predicted risk at one horizon. No tuning. See notebooks/02."""

import numpy as np
import pandas as pd
from lifelines import CoxPHFitter
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.model_selection import StratifiedKFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from hct_equity.config import Columns, FairnessSettings

MISSING_LABEL = "missing"
MIN_CATEGORY_COUNT = 20


def split_features(frame: pd.DataFrame, features: list[str]) -> tuple[list[str], list[str]]:
    numeric = frame[features].select_dtypes("number").columns.tolist()
    return [name for name in features if name not in numeric], numeric


def build_preprocessor(categorical: list[str], numeric: list[str]) -> ColumnTransformer:
    """Fit inside each fold, so imputation and encoding never see the test rows."""
    text = make_pipeline(
        SimpleImputer(strategy="constant", fill_value=MISSING_LABEL),
        OneHotEncoder(
            drop="first", sparse_output=False, min_frequency=MIN_CATEGORY_COUNT, handle_unknown="infrequent_if_exist"
        ),
    )
    numbers = make_pipeline(SimpleImputer(strategy="median", add_indicator=True), StandardScaler())
    transformer = ColumnTransformer([("text", text, categorical), ("numbers", numbers, numeric)])
    return transformer.set_output(transform="pandas")


def fit_cox(design: pd.DataFrame, time: pd.Series, event: pd.Series, penalizer: float) -> CoxPHFitter:
    data = design.assign(_time=time.to_numpy(), _event=event.to_numpy())
    return CoxPHFitter(penalizer=penalizer).fit(data, duration_col="_time", event_col="_event")


def horizon_risk(cox: CoxPHFitter, design: pd.DataFrame, horizon: float) -> np.ndarray:
    return 1 - cox.predict_survival_function(design, times=[horizon]).to_numpy()[0]


def fold_assignments(frame: pd.DataFrame, columns: Columns, folds: int, seed: int) -> np.ndarray:
    """Stratify by group and event, so every fold has the same mix."""
    strata = frame[columns.group].astype(str) + "_" + frame[columns.event].astype(str)
    assignment = np.empty(len(frame), dtype=int)
    for fold, (_, test_rows) in enumerate(StratifiedKFold(folds, shuffle=True, random_state=seed).split(frame, strata)):
        assignment[test_rows] = fold
    return assignment


def predict_fold(
    train: pd.DataFrame, test: pd.DataFrame, features: list[str], columns: Columns, settings: FairnessSettings
) -> np.ndarray:
    preprocessor = build_preprocessor(*split_features(train, features))
    design = preprocessor.fit_transform(train[features])
    cox = fit_cox(design, train[columns.time], train[columns.event], settings.penalizer)
    return horizon_risk(cox, preprocessor.transform(test[features]), settings.horizon_months)


def out_of_fold_risk(
    frame: pd.DataFrame, features: list[str], columns: Columns, settings: FairnessSettings
) -> pd.Series:
    """Each row's risk comes from a model fitted without that row."""
    folds = fold_assignments(frame, columns, settings.folds, settings.seed)
    risk = pd.Series(np.nan, index=frame.index, name=columns.risk)
    for fold in range(settings.folds):
        test = folds == fold
        risk[test] = predict_fold(frame[~test], frame[test], features, columns, settings)
    return risk
