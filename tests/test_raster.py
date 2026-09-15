from pathlib import Path

import numpy as np
import pytest
import rasterio
from rasterio.enums import Resampling
from rasterio.transform import from_origin

from artemis_ml.raster import (
    align_raster,
    inspect_raster,
    scan_rasters,
    validate_common_grid,
    write_raster_manifest,
)


def _write_raster(path: Path, *, x_origin: float = 0.0) -> None:
    with rasterio.open(
        path,
        "w",
        driver="GTiff",
        width=5,
        height=4,
        count=1,
        dtype="float32",
        crs="EPSG:4326",
        transform=from_origin(x_origin, 4, 1, 1),
        nodata=-9999,
    ) as dataset:
        dataset.write(np.ones((1, 4, 5), dtype="float32"))


def test_inspect_raster_returns_grid_metadata(tmp_path: Path) -> None:
    raster_path = tmp_path / "predictor.tif"
    _write_raster(raster_path)

    metadata = inspect_raster(raster_path)

    assert metadata.driver == "GTiff"
    assert metadata.crs == "EPSG:4326"
    assert (metadata.width, metadata.height) == (5, 4)
    assert metadata.resolution == (1.0, 1.0)
    assert metadata.nodata == -9999.0


def test_validate_common_grid_accepts_aligned_rasters(tmp_path: Path) -> None:
    first = tmp_path / "first.tif"
    second = tmp_path / "second.tif"
    _write_raster(first)
    _write_raster(second)

    reference = validate_common_grid([first, second])

    assert reference.path == first


def test_validate_common_grid_rejects_shifted_raster(tmp_path: Path) -> None:
    reference = tmp_path / "reference.tif"
    shifted = tmp_path / "shifted.tif"
    _write_raster(reference)
    _write_raster(shifted, x_origin=0.5)

    with pytest.raises(ValueError, match="transform"):
        validate_common_grid([reference, shifted])


def test_scan_rasters_keeps_unsupported_candidates(tmp_path: Path) -> None:
    readable = tmp_path / "readable.tif"
    unsupported = tmp_path / "unsupported.tif"
    _write_raster(readable)
    unsupported.write_bytes(b"not a raster")

    scan = scan_rasters([readable, unsupported])

    assert [metadata.path for metadata in scan.readable] == [readable]
    assert scan.unsupported[0][0] == unsupported


def test_align_raster_uses_reference_grid(tmp_path: Path) -> None:
    source = tmp_path / "source.tif"
    reference = tmp_path / "reference.tif"
    output = tmp_path / "interim" / "aligned.tif"
    _write_raster(source, x_origin=0.5)
    _write_raster(reference)

    metadata = align_raster(
        source,
        reference,
        output,
        resampling=Resampling.nearest,
    )

    reference_metadata = inspect_raster(reference)
    assert metadata.crs == reference_metadata.crs
    assert metadata.transform == reference_metadata.transform
    assert (metadata.width, metadata.height) == (
        reference_metadata.width,
        reference_metadata.height,
    )


def test_write_raster_manifest_records_unreadable_candidates(tmp_path: Path) -> None:
    data_root = tmp_path / "data"
    data_root.mkdir()
    readable = data_root / "readable.tif"
    unsupported = data_root / "unsupported.tif"
    _write_raster(readable)
    unsupported.write_bytes(b"not a raster")
    output = tmp_path / "processed" / "raster_manifest.json"

    write_raster_manifest(data_root, output)

    manifest = output.read_text(encoding="utf-8")
    assert '"readable": true' in manifest
    assert '"readable": false' in manifest
    assert "RasterioIOError" in manifest