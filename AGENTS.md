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
## Agent workflow

- Before editing, identify the concrete behavior, its controlling code path,
  and one focused check that could disconfirm the working hypothesis.
- Work in a tight propose-verify loop: make the smallest focused change, run
  the cheapest relevant test or check immediately, then use its feedback to
  repair or refine the same slice before expanding scope.
- Do not report a change as complete without executable validation when the
  environment provides one. State what was run and any checks that could not
  be performed.
- Treat passing tests and lint as evidence, not proof of scientific validity.
  Confirm model outputs, maps, figures, and other human-facing results against
  the intended research question and domain expectations.
- When a decision depends on visual, scientific, or editorial taste rather
  than an objective metric, surface the candidate result for human review and
  do not silently substitute the agent's preference.
- Preserve an explicit record of assumptions, random seeds, inputs, metrics,
  and unresolved uncertainty for model comparisons and generated artifacts.