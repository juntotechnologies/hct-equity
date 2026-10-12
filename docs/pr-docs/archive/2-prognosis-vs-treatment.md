# PR 2: Notebook on Prognosis and Treatment Effect

Status: done

Branch: `feature/prognosis-vs-treatment-notebook`

## Goal

Teaching notebook: why a prognostic model cannot choose a treatment, and what DCA can evaluate. Toy cohort (truth known) + CIBMTR synthetic data.

## Context

- Base: PR 1.
- Later models use treatment columns (e.g. `conditioning_intensity`) as inputs. Risk change ≠ treatment effect.

## Left off

Done: notebook 01 + `teaching.py` + tests. Key result (toy): model says RIC helps fit patients; truth: RIC harms. Model policy 61.9% event risk vs current practice 58.7%.

Next:
- Shaun: read shorthand notebook 01, run it, review.
- Shaun: decide notebook scope (keep toy / real data only / limits paragraph only).
- Models PR: Cox + gradient-boosted survival, 5-fold CV, stratified C-index, tests for `eda.py`, nested-function check.
- Kaggle submission, calibration + DCA, summary: see PR 1 Left off.

## Implementation Checklist

### Tier 1 - Configuration and tests

- [x] Dev dependencies: pytest, notebook tools.
- [x] Config: DCA thresholds, toy settings, real-data treatment example.
- [x] Config paths resolve against repo root (notebooks run from any directory).
- [x] Tests: config loading, threshold values, path resolution.

### Tier 2 - Teaching module

- [x] Toy cohort: two potential outcomes, one hidden confounder.
- [x] Effect by frailty: naive vs model vs truth.
- [x] Treatment policies vs true risks.
- [x] Surveillance DCA (dcurves) + treatment case-mix table.
- [x] Tests for each function.

### Tier 3 - Notebook

- [x] `notebooks/01_prognosis_vs_treatment_effect.ipynb`, no outputs.
- [x] Notebook + module listed in directory `AGENTS.md` files.
- [x] Abbreviation key at top of notebook.
- [x] Plain-language rewrite of notebook text: hospital example, answer key, every term defined at first use.
- [x] Shorthand ASD-STE100 rewrite of notebook text: fragments, tables, one key for all terms.

## Smoke Tests

**Notebook shows the trap · as analyst**

1. Open `notebooks/01_prognosis_vs_treatment_effect.ipynb`.
2. Run all cells.

Pass if:
- No cell errors.
- Fit patients: model effect sign ≠ true effect sign.
- Model policy event risk > current practice.
- DCA plot: model line above treat all at high thresholds.

**Notebook reads clearly · as non-specialist**

1. Read the notebook text from top to bottom.

Pass if:
- Each term or abbreviation has a definition before or at first use.
- The source of `true_effect`, `model_effect` and `naive_effect` is clear.

| Automated check | Command |
|-----------------|---------|
| Lint + format | `uv run ruff check src tests && uv run ruff format --check src tests` |
| Unit tests | `uv run pytest` |
