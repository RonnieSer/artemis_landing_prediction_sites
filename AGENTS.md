# Agent instructions

## Project scope

This repository supports semi-automated lunar geologic mapping using Random
Forest and XGBoost with LROC, LOLA, and Mini-RF-derived predictors.

## Data protection

- Treat all files under `data/` as private local inputs.
- Never weaken `.gitignore` to commit research data or generated artifacts.
- Do not print sensitive data paths, credentials, or unpublished map contents in
  logs or documentation.
- Use repository-relative paths so code runs after being pulled on a lab
  computer.

## Python

- Use Python 3.11.9 and install from `requirements.txt`.
- Prefer `pathlib.Path` and explicit function arguments over hard-coded paths.
- Keep random seeds explicit for model training and comparisons.
- Preserve CRS, raster alignment, NoData handling, and spatial resolution in
  preprocessing code.

## Changes and validation

- Keep changes focused and avoid committing notebooks with embedded private
  outputs.
- Run `python -m pytest` for tests and `ruff check .` for linting when code is
  present.
- Before pushing, inspect `git status --short` and verify that no data files are
  staged.