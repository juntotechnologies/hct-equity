# src/hct_equity

This is the Python package. Install it with `uv sync`. Run modules with `uv run python -m hct_equity.<module>`.

| Module | Job |
|--------|-----|
| `config.py` | Loads and validates `config/project.json` into typed models. |
| `data.py` | Owns the data file layout. Other modules read data only through it. |
| `eda.py` | Pure EDA summaries and the Kaplan-Meier figure. |
| `run_eda.py` | Runs the EDA. Writes tables and the figure. |
| `teaching.py` | Toy cohort with known treatment effects, for notebook 01. |

- Keep pure logic in modules like `eda.py`. Keep file side effects in `run_*.py` modules.
- Pass the `Project` object or its parts as arguments. Do not read the config file inside a function.
- Every output must carry `synthetic_note`.
- Ruff enforces the limits in `pyproject.toml`. Run the lint command in the root `AGENTS.md` before each commit.
