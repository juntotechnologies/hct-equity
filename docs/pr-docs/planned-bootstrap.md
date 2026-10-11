# PR: Bootstrap the Repository

Status: in-scope work complete

Branch: `chore/bootstrap-repo`

## Goal

This PR sets up the project. It adds the uv project, the configuration file, the EDA module and the agent instructions. After this PR, an agent can read `AGENTS.md` and work without a scan of the full repository.

## Context

The repository had only a README. The competition rules check passed. The rules allow public code and aggregate results. They forbid redistribution of the data.

## Implementation Checklist

### Tier 1 - Project files

- [x] Add the uv project for Python 3.11 with the analysis packages, Pydantic and ruff.
- [x] Add `config/project.json` as the single source for project values.
- [x] Ignore `data/`, `.env`, `mlflow.db` and `mlruns/` in git.
- [x] Add the root `AGENTS.md` with project knowledge and one `AGENTS.md` for each directory.
- [x] Add the PR template and the PR doc templates.

### Tier 2 - EDA

- [x] Add typed config loading, data access and MLflow run setup.
- [x] Add EDA summaries: counts, missing values, event rate, event time, and known status at each horizon.
- [x] Write aggregate EDA tables to `reports/eda/` and the Kaplan-Meier figure to `figures/`.
- [ ] Add unit tests for `eda.py` and `config.py`. Moved to the models PR.
- [ ] Add a check that fails on a nested function. Ruff has no rule for this. Moved to the models PR.

## Smoke Tests

**EDA figure shows synthetic label · as analyst**

1. Open `figures/eda_km_by_group.png`.

Pass if:
- The title says the data is synthetic.
- There is one curve for each of the six race groups.

| Automated check | Command |
|-----------------|---------|
| Lint and format | `uv run ruff check src && uv run ruff format --check src` |
