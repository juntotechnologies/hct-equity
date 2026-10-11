# config

`project.json` is the single source for project values. It holds column names, paths, horizons, the synthetic-data note and the citation.

- Add a value here before you write it as a literal in code or docs.
- Read the file only through `hct_equity.config.load_config`. That function validates it with Pydantic models.
- When you add a key, add the matching field to the model in `src/hct_equity/config.py`.
