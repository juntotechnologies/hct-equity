# PR 1: Bootstrap the Repository

Status: done

Branch: `chore/bootstrap-repo`

## Goal

Set up project: uv env, config, EDA, AGENTS.md files, PR templates.

## Context

- Repo had README only.
- Rules check: pass. Public code + aggregate results OK. Data redistribution: forbidden.

## Left off

Done: setup + EDA. Horizon: 12 mo main, 24 mo second check. MLflow: removed.

Next:
- PR 2: notebook, prognosis vs treatment effect. Open, base = this branch.
- Models: Cox + gradient-boosted survival, 5-fold CV, stratified C-index.
- Kaggle submission: notebook, private. Ask Shaun before submit.
- Calibration + DCA by race group, 12 + 24 mo.
- Summary (1 page) + README (3 commands).

## Implementation Checklist

### Tier 1 - Project files

- [x] uv project, Python 3.11, analysis packages, Pydantic, ruff.
- [x] `config/project.json`: single source for project values.
- [x] Git ignores `data/`, `.env`, Python caches.
- [x] Root `AGENTS.md` + one `AGENTS.md` per directory.
- [x] PR template + PR doc templates.
- [x] Rule: commit early and often.
- [x] Rule: pithy PR docs and descriptions, ASD-STE100 shorthand. Script: `scripts/pr-body.sh`.

### Tier 2 - EDA

- [x] Typed config loading + data access.
- [x] Remove MLflow. Results: files under `reports/`.
- [x] EDA summaries: counts, missing values, event rate, event time, known status per horizon.
- [x] Aggregate tables → `reports/eda/`. Kaplan-Meier figure → `figures/`.
- [ ] Tests for `eda.py`. Moved to models PR.
- [ ] Check that fails on nested function (no ruff rule). Moved to models PR.

## Smoke Tests

**EDA figure has synthetic label · as analyst**

1. Open `figures/eda_km_by_group.png`.

Pass if:
- Title says data is synthetic.
- Six curves, one per race group.

| Automated check | Command |
|-----------------|---------|
| Lint + format | `uv run ruff check src && uv run ruff format --check src` |
