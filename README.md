# Artemis Landing Prediction Sites

Research code for comparing Random Forest and XGBoost workflows for
semi-automated lunar geologic mapping at Artemis exploration sites.

## Data policy

The research data is intentionally **not** part of this repository. Put it in
`data/` on the computer where the analysis runs. Git ignores the contents of
that directory and common raster, vector, table, and model-artifact formats.
Only `data/README.md` and `data/.gitkeep` are tracked.

This repository is therefore safe to pull on a lab computer and combine with
local data supplied by the Artemis Science Team. Before committing, run:

```bash
git status --short
git check-ignore -v data/raw/example.tif
```

The second command should report that the file is ignored.

## Environment setup

The project targets Python 3.11.9, recorded in `.python-version`.

With `pyenv`:

```bash
pyenv install 3.11.9       # only if it is not installed already
pyenv local 3.11.9
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m ipykernel install --user --name artemis-landing --display-name "Python (artemis-landing)"
```

Without `pyenv`, install Python 3.11.9 using the lab's approved package
manager, then run the virtual-environment commands from the repository root.

Verify the environment:

```bash
python --version
python -c "import geopandas, rasterio, sklearn, xgboost; print('Environment OK')"
```

## Working conventions

- Keep notebooks, scripts, and configuration in Git; keep research data local.
- Use paths relative to the repository root rather than personal absolute paths.
- Record preprocessing assumptions, CRS, raster resolution, and model settings
  in code or a tracked experiment note.
- Use the fixed random seed from the proposal where reproducibility matters.
- Never commit API keys, credentials, unpublished maps, or generated model
  artifacts.

## Suggested workflow

1. Put the lab-provided files under `data/raw/`.
2. Preprocess and align rasters into `data/interim/`.
3. Build GeoParquet feature tables and labels under `data/processed/`.
4. Train and validate Random Forest and XGBoost models from the same spatial
  splits.
5. Build indexed raster patches for CNN experiments after raster validation.
6. Save figures and maps locally under `outputs/`.
7. Commit only code, documentation, configuration, and reproducible metadata.

See [`docs/data-contract.md`](docs/data-contract.md) for the format and
alignment requirements.

## GitHub repository

Use the repository name `artemis_landing_prediction_sites` on GitHub so it
matches this local project. The commands below create the first local commit
and connect an already-created GitHub repository:

```bash
git init
git add .
git commit -m "Initialize Artemis landing site ML project"
git branch -M main
git remote add origin https://github.com/<your-account>/artemis_landing_prediction_sites.git
git push -u origin main
```

Create the GitHub repository as private if any project metadata is sensitive.
Do not upload the contents of `data/`.