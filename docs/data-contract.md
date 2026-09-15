# Data and ML contract

This project keeps the lab-provided files under `data/raw/` as private source
material. Processing creates reproducible, analysis-ready derivatives without
overwriting the source data.

## Recommended formats

| Layer | Format | Purpose |
| --- | --- | --- |
| Raw inputs | Native source format | Preserve provenance and enable reprocessing. |
| Aligned raster predictors | GeoTIFF, preferably tiled and compressed | One consistently aligned raster per predictor, or a documented multiband stack. |
| Raster labels or masks | GeoTIFF with an integer class type | Pixel-level labels with an explicit NoData value and class legend. |
| Vector labels and footprints | GeoParquet | Compact, typed, CRS-aware vector data for inspection and rasterization. |
| Classical-model samples | Parquet | Typed feature rows, label, coordinates, source window, split, and provenance identifiers. |
| CNN training samples | Chunked Zarr or an equivalent indexed array store | Fixed-size image patches, label patches, masks, and metadata without loading a full raster into memory. |

CSV is reserved for small interchange files. It is not the canonical training
format because it loses types, spatial metadata, and efficient column access.

## Required raster invariants

Every analysis-ready predictor and label must record and validate:

- CRS and coordinate units
- raster width, height, transform, extent, and pixel resolution
- band name, physical units, scaling, and NoData value
- resampling method used during alignment
- source identifier and processing configuration

Predictors must share the same grid. Continuous predictors use an explicitly
chosen continuous resampler; categorical labels and masks use nearest-neighbor
resampling only. NoData must remain distinguishable from a valid zero.

## Processing stages

1. Inventory raw sources and record checksums and metadata locally.
2. Select the study area and target grid from a documented reference layer.
3. Reproject, clip, align, and validate predictors into `data/interim/`.
4. Rasterize or otherwise normalize reference labels into the same grid.
5. Build a Parquet sample table for Random Forest and XGBoost.
6. Build spatially indexed, fixed-size patches for CNN experiments.
7. Split by spatial region or site before sampling patches or pixels; never let
   neighboring pixels from one site leak across train and validation sets.

## Model progression

The first reproducible baseline is a scikit-learn Random Forest, followed by
XGBoost using the same feature table, split definition, and evaluation metrics.
CNN work should begin only after the aligned raster and label contract passes
validation. The initial CNN should use a small, documented patch classifier or
semantic segmentation model, with the same held-out spatial regions as the
classical baselines.

All experiments must record the input manifest, feature names, class mapping,
split regions, random seed, library versions, metrics, and unresolved
uncertainty. Model quality does not replace human review of maps and scientific
interpretation.