# Project progress log

## 2026-09-14

### Direction established

- The project targets semi-automated lunar geologic mapping for Artemis
  exploration sites using LROC, LOLA, and Mini-RF-derived predictors.
- The workflow will preserve geospatial rasters as authoritative inputs,
  derive Parquet tables for Random Forest and XGBoost, and derive indexed
  raster patches for future CNN experiments.
- Spatial splits are required to prevent neighboring pixels from leaking
  between training and validation data.
- Scientific interpretation, map quality, and visual or editorial choices
  require human review even when automated checks pass.

### Repository guidance

- Expanded `AGENTS.md` with a mandatory propose-verify workflow, focused
  validation, scientific review, reproducibility records, and uncertainty
  tracking.
- Added `docs/data-contract.md` describing canonical formats, raster
  invariants, processing stages, and the planned classical-model/CNN path.
- Updated `README.md` to reference GeoParquet, CNN patches, and the data
  contract.

### Environment and packaging

- Created `.venv` with Python 3.11.9.
- Installed the pinned dependencies from `requirements.txt`.
- Added `pyproject.toml` for the `src` package layout, pytest configuration,
  and editable installation.
- The virtual environment and generated data artifacts remain Git-ignored.

### Implemented code

- `src/artemis_ml/inventory.py` builds a local source inventory with relative
  paths, file sizes, suffixes, and SHA-256 checksums.
- `src/artemis_ml/raster.py` provides raster metadata inspection, readable and
  unsupported-file scanning, common-grid validation, reference-grid alignment,
  and metadata-only raster manifest generation.
- `src/artemis_ml/layers.py` validates explicit reference, predictor, and label
  selections, including data-root path safety and nearest-neighbor labels.
- `configs/layers.example.json` provides the configuration template that still
  needs real layer paths and predictor names.

### Verification

- The latest full test suite passes: `12 passed`.
- Ruff reports no lint findings.
- Synthetic tests cover inventory creation, raster metadata, shifted-grid
  rejection, unsupported raster handling, alignment, manifest generation, and
  layer configuration validation.
- Local data inspection found many raster candidates, mixed source drivers,
  and two files that Rasterio cannot read. No raw data was modified or
  committed.

### Next session

1. Review the local raster metadata manifest without exposing private data.
2. Fill `configs/layers.example.json` with the confirmed reference, predictor,
   and label paths.
3. Generate and validate aligned products under `data/interim/`.
4. Build a labeled Parquet feature table with spatial train/validation splits.
5. Establish Random Forest and XGBoost baselines before adding CNN patches and
   a CNN model library.