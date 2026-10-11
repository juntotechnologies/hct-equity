# PR: Notebook on Prognosis and Treatment Effect

Status: in-scope work complete

Branch: `feature/prognosis-vs-treatment-notebook`

## Goal

This PR adds a teaching notebook. The notebook shows why a prognostic model cannot choose a treatment, and which decisions DCA can evaluate. It uses a toy cohort where the true treatment effect is known. Then it shows the same pattern in the CIBMTR synthetic data.

## Context

PR 1 adds the project setup and EDA. The models in later PRs use treatment columns, for example `conditioning_intensity`, as inputs. Readers can confuse a change in predicted risk with a treatment effect. This notebook explains the difference before the model results.

## Implementation Checklist

### Tier 1 - Configuration and tests

- [x] Add pytest and notebook tools as development dependencies.
- [x] Add DCA thresholds, toy settings and the real-data treatment example to `config/project.json`.
- [x] Resolve configured paths against the repository root, so notebooks run from any directory.
- [x] Add tests for configuration loading, threshold values and path resolution.

### Tier 2 - Teaching module

- [x] Add the toy cohort with two potential outcomes and one hidden confounder.
- [x] Add the naive, model and true effect comparison by frailty.
- [x] Add treatment policy comparison against the true risks.
- [x] Add the surveillance DCA with dcurves and the treatment case-mix table.
- [x] Add tests for each function.

### Tier 3 - Notebook

- [x] Add `notebooks/01_prognosis_vs_treatment_effect.ipynb` without outputs.
- [x] List the notebook and module in the directory `AGENTS.md` files.

## Smoke Tests

**Notebook explains the trap · as analyst**

1. Open `notebooks/01_prognosis_vs_treatment_effect.ipynb`.
2. Run all cells.

Pass if:
- All cells run without an error.
- For fit patients, the model effect has the opposite sign to the true effect.
- The prognostic model policy has a higher event risk than current practice.
- The DCA plot shows the model line above treat all at high thresholds.

| Automated check | Command |
|-----------------|---------|
| Lint and format | `uv run ruff check src tests && uv run ruff format --check src tests` |
| Unit tests | `uv run pytest` |
