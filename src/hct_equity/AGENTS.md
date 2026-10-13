# src/hct_equity

This is the Python package. Install it with `uv sync`. Run modules with `uv run python -m hct_equity.<module>`.

| Module | Job |
|--------|-----|
| `config.py` | Loads and validates `config/project.json` into typed models. |
| `data.py` | Owns the data file layout. Other modules read data only through it. |
| `eda.py` | Pure EDA summaries and the Kaplan-Meier figure. |
| `run_eda.py` | Runs the EDA. Writes tables and the figure. |
| `teaching.py` | Toy cohort with known treatment effects, for notebook 01. |
| `model.py` | Cox model with out-of-fold risk at one horizon, for notebook 02. |
| `fairness.py` | Pure per-group C-index, calibration, DCA and recalibration, for notebook 02. |
| `fairness_plots.py` | Calibration and DCA figures, for notebook 02. |
| `run_fairness.py` | Runs notebook 02's analysis. Writes the metrics table and figures. |
| `readable.py` | Shows notebook tables with plain labels and formatted numbers, from `config/labels.json`. |

- Keep pure logic in modules like `eda.py`. Keep file side effects in `run_*.py` modules.
- Pass the `Project` object or its parts as arguments. Do not read the config file inside a function.
- Every output must carry `synthetic_note`.
- Ruff enforces the limits in `pyproject.toml`. Run the lint command in the root `AGENTS.md` before each commit.
