# hct-equity

**Exploratory; not peer-reviewed.**

Synthetic data (Kaggle CIBMTR competition; generated from de-identified patients)

Models for the Kaggle competition "CIBMTR - Equity in post-HCT Survival Predictions". HCT means hematopoietic cell transplantation. The project compares models by race group with calibration and decision curve analysis (DCA).

## Contents

| Path | Contents |
|------|----------|
| `notebooks/` | Notebook 01: prognosis versus treatment effect. Notebook 02: calibration and DCA by race group. |
| `figures/` | Generated figures. |
| `reports/` | Generated aggregate tables. |
| `src/hct_equity/` | Python package. |

## Run

This repository has code only. It does not contain competition data. Download the data from Kaggle under the competition rules. `AGENTS.md` lists the commands.

## Data source

Tushar Deshpande, Deniz Akdemir, Walter Reade, Ashley Chow, Maggie Demkin, and Yung-Tsi Bolon. CIBMTR - Equity in post-HCT Survival Predictions. https://kaggle.com/competitions/equity-post-HCT-survival-predictions. Kaggle.

## License

Code: MIT. See `LICENSE`. The license does not cover the competition data.
