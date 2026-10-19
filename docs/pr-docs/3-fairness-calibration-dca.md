# PR 3: Calibration and DCA by Race Group

Status: underway

Branch: `feature/fairness-calibration-dca`

## Goal

Answer one question: the competition scored ranking (stratified C-index); does good ranking give equally good decisions in each race group? Notebook 02 shows C-index, calibration and net benefit by race group at 12 months, for 1 Cox model with out-of-fold predictions. Synthetic data; the result is a proposal to test on real CIBMTR data.

## Context

- PR 1: config, data loader, EDA. PR 2: notebook 01 (prognosis vs treatment effect).
- No model existed before this PR.
- Data: 28,800 rows, 6 race groups (~4,800 each). 52% have an event before 12 months; 0.8% are censored before 12 months.

## Left off

Status (2026-10-13): build done; tables readable; waiting for Shaun's review at the "first DCA" checkpoint.
Done: config, model, metrics, plots, run script, notebook 02. 28 tests, lint and a full notebook run pass.
Result: calibration near-equal (O/E 0.97–1.04); net benefit gain at p_t 0.6 differs 0.07–0.17 by group.
Next:
- Shaun: run notebook 02 and review (smoke test).
- Shaun: approve a public Kaggle notebook. It must be self-contained; it cannot import `hct_equity`.
- Follow-up: `eda.km_risk` and `fairness.km_risk` overlap; merge into one.

## Implementation Checklist

### Tier 1 - Configuration

- [x] Config: `fairness` section (horizon, folds, seed, penalizer, risk bins). Horizon must be one of `horizons_months`.
- [x] Tests: config loads; a horizon outside `horizons_months` fails validation.

### Tier 2 - Metrics by group (`fairness.py`, pure)

- [x] Per group: n, events by 12 months, C-index, observed/expected (O/E) ratio, calibration slope.
- [x] Stratified C-index: mean minus standard deviation across groups (competition metric).
- [x] Calibration by risk decile: mean predicted vs Kaplan-Meier (KM) observed risk.
- [x] Time-to-event DCA per group with `dcurves`.
- [x] Net benefit gain: model minus the better of treat all / treat none. Raw net benefit tracks event rate.
- [x] Tests for each function, on small frames with known answers.

### Tier 3 - Model (`model.py`)

- [x] Cox model (lifelines, ridge penalty). In-fold imputation and one-hot encoding. No tuning.
- [x] 5-fold out-of-fold 12-month risk, stratified by race group and event.
- [x] Tests: every row gets 1 prediction; risk in [0, 1]; no fold sees its own test rows.

### Tier 4 - Plots, run script, notebook

- [x] Plots: 1 calibration figure, 1 DCA figure (1 panel per group). Each carries `synthetic_note`.
- [x] `run_fairness.py`: writes the metrics table to `reports/` and figures to `figures/`.
- [x] Notebook 02, 6 sections: question, data and model, C-index, calibration, DCA, result.
- [x] Exploratory: per-group recalibration; does it restore net benefit?
- [x] Notebook 02 tables use plain labels and formatted numbers (`readable.py`, merged from `main`).

## Smoke Tests

- [ ] **Notebook 02 reads as one argument** · as Shaun
  1. Open notebook 02.
  2. Run all cells.
  3. Read top to bottom.

  **Pass if:**
  - Synthetic-data note is in the first cell and on each figure.
  - Metrics table has 6 groups with n, events, C-index, O/E, slope.
  - Calibration figure: 1 line per group and a diagonal.
  - DCA figure: 6 panels with model, treat all, treat none.
  - Result cell states what differs, by how much, and why it matters.

| Automated check | Tests |
|-----------------|-------|
| Config horizon validation | `tests/test_config.py` |
| Metric values on known inputs | `tests/test_fairness.py` |
| Out-of-fold predictions | `tests/test_model.py` |
| Figure titles carry the synthetic note | `tests/test_fairness_plots.py` |

## Product Decisions

- 1 model, not top public solutions: no model existed, and top solutions need their notebooks run. Notebook says "1 model".
- Race group is a model feature, as in competition models.
- Compare groups by net benefit gain, not raw net benefit: overall event rates differ (47–63%).
- 12-month horizon only. 24 months is future work.
- Censoring: O/E and decile calibration use KM observed risk. Calibration slope drops the 0.8% censored before 12 months.
- Notebook 01 stays as is. This notebook replaces its causal scope for the CIBMTR pitch.

## Scope

- Calibration and net benefit by race group, 1 model, 12 months.

## Non-Goals

- EDA beyond 1 cohort table, feature engineering, tuning, multiple models.
- SHAP, other fairness metrics, causal inference, 24-month horizon.
- Public Kaggle notebook: needs Shaun's approval; separate step.

## Related Docs

- [PR 2: Notebook on prognosis and treatment effect](./archive/2-prognosis-vs-treatment.md)
