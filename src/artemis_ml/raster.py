"""Inspect and validate analysis-ready raster grids."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import rasterio
from affine import Affine
from rasterio.enums import Resampling
from rasterio.warp import reproject


@dataclass(frozen=True)
class RasterMetadata:
    """Grid and value metadata needed for aligned raster processing."""

    path: Path
    driver: str
    crs: str | None
    width: int
    height: int
    count: int
    dtype: str
    transform: Affine
    resolution: tuple[float, float]
    nodata: float | int | None


@dataclass(frozen=True)
class RasterScan:
    """Results from scanning candidate raster files."""

    readable: tuple[RasterMetadata, ...]
    unsupported: tuple[tuple[Path, str], ...]


def inspect_raster(path: Path) -> RasterMetadata:
    """Read metadata from one raster without loading its pixel values."""
    with rasterio.open(path) as dataset:
        return RasterMetadata(
            path=path,
            driver=dataset.driver,
            crs=dataset.crs.to_string() if dataset.crs else None,
            width=dataset.width,
            height=dataset.height,
            count=dataset.count,
            dtype=dataset.dtypes[0],
            transform=dataset.transform,
            resolution=dataset.res,
            nodata=dataset.nodata,
        )


def scan_rasters(paths: list[Path]) -> RasterScan:
    """Inspect candidates while retaining unsupported-file diagnostics."""
    readable = []
    unsupported = []
    for path in paths:
        try:
            readable.append(inspect_raster(path))
        except rasterio.errors.RasterioIOError as error:
            unsupported.append((path, str(error)))
    return RasterScan(tuple(readable), tuple(unsupported))


def write_raster_manifest(data_root: Path, output_path: Path) -> None:
    """Write metadata for candidate GeoTIFFs without reading pixel values."""
    import json

    candidates = sorted(
        path
        for path in data_root.rglob("*")
        if path.is_file() and path.suffix.lower() in {".tif", ".tiff"}
    )
    records = []
    for path in candidates:
        record = {"relative_path": path.relative_to(data_root).as_posix()}
        try:
            metadata = inspect_raster(path)
        except rasterio.errors.RasterioIOError as error:
            record.update({"readable": False, "error_type": type(error).__name__})
        else:
            record.update(
                {
                    "readable": True,
                    "driver": metadata.driver,
                    "crs": metadata.crs,
                    "width": metadata.width,
                    "height": metadata.height,
                    "count": metadata.count,
                    "dtype": metadata.dtype,
                    "resolution": metadata.resolution,
                    "nodata": metadata.nodata,
                }
            )
        records.append(record)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(records, indent=2) + "\n", encoding="utf-8")


def align_raster(
    source_path: Path,
    reference_path: Path,
    output_path: Path,
    *,
    resampling: Resampling,
    dst_nodata: float | int | None = None,
) -> RasterMetadata:
    """Warp a raster onto a reference grid and return output metadata.

    The caller must choose ``Resampling.nearest`` for categorical data such as
    labels and masks. Continuous predictors should use a documented
    continuous resampler such as ``bilinear`` or ``cubic``.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with rasterio.open(source_path) as source, rasterio.open(
        reference_path
    ) as reference:
        if source.crs is None or reference.crs is None:
            raise ValueError("Both source and reference rasters require a CRS")

        output_nodata = (
            source.nodata if dst_nodata is None else dst_nodata
        )
        profile = source.profile.copy()
        profile.update(
            driver="GTiff",
            height=reference.height,
            width=reference.width,
            transform=reference.transform,
            crs=reference.crs,
            nodata=output_nodata,
        )
        with rasterio.open(output_path, "w", **profile) as destination:
            for band_index in range(1, source.count + 1):
                reproject(
                    source=rasterio.band(source, band_index),
                    destination=rasterio.band(destination, band_index),
                    src_transform=source.transform,
                    src_crs=source.crs,
                    src_nodata=source.nodata,
                    dst_transform=reference.transform,
                    dst_crs=reference.crs,
                    dst_nodata=output_nodata,
                    resampling=resampling,
                )
    return inspect_raster(output_path)


def validate_common_grid(paths: list[Path]) -> RasterMetadata:
    """Require all rasters to share CRS, dimensions, and affine transform.

    The first raster is returned as the reference metadata. Value dtypes and
    NoData values may differ because continuous predictors and labels have
    different valid representations; their handling is validated separately.
    """
    if not paths:
        raise ValueError("At least one raster path is required")

    reference = inspect_raster(paths[0])
    for path in paths[1:]:
        candidate = inspect_raster(path)
        differences = []
        if candidate.crs != reference.crs:
            differences.append("CRS")
        if (candidate.width, candidate.height) != (
            reference.width,
            reference.height,
        ):
            differences.append("dimensions")
        if candidate.transform != reference.transform:
            differences.append("transform")
        if differences:
            changed = ", ".join(differences)
            raise ValueError(
                f"Raster grid mismatch: {path} differs in {changed} "
                f"from {reference.path}"
            )
    return reference