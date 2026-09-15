"""Validate explicit reference, predictor, and label layer selections."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

_RESAMPLING_METHODS = {"nearest", "bilinear", "cubic", "average", "mode"}


@dataclass(frozen=True)
class LayerSelection:
    """One selected raster and its intended resampling method."""

    path: Path
    resampling: str
    name: str | None = None


@dataclass(frozen=True)
class LayerConfig:
    """Explicit raster roles used by the alignment pipeline."""

    reference: Path
    predictors: tuple[LayerSelection, ...]
    label: LayerSelection


def _resolve_data_path(data_root: Path, relative_path: str) -> Path:
    candidate = (data_root / relative_path).resolve()
    root = data_root.resolve()
    if candidate != root and root not in candidate.parents:
        raise ValueError(f"Layer path escapes data root: {relative_path}")
    if not candidate.is_file():
        raise FileNotFoundError(candidate)
    return candidate


def _parse_selection(data_root: Path, raw: dict, *, require_name: bool) -> LayerSelection:
    path_value = raw.get("path")
    if not isinstance(path_value, str):
        raise ValueError("Each layer requires a string path")
    resampling = raw.get("resampling", "nearest")
    if resampling not in _RESAMPLING_METHODS:
        raise ValueError(f"Unsupported resampling method: {resampling}")
    name = raw.get("name")
    if require_name and not isinstance(name, str):
        raise ValueError("Each predictor requires a name")
    return LayerSelection(
        path=_resolve_data_path(data_root, path_value),
        resampling=resampling,
        name=name,
    )


def load_layer_config(config_path: Path, data_root: Path) -> LayerConfig:
    """Load and validate a JSON layer configuration."""
    raw = json.loads(config_path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError("Layer configuration must be a JSON object")

    reference_value = raw.get("reference")
    if not isinstance(reference_value, str):
        raise ValueError("Layer configuration requires a reference path")
    predictors_value = raw.get("predictors")
    if not isinstance(predictors_value, list) or not predictors_value:
        raise ValueError("Layer configuration requires predictors")
    label_value = raw.get("label")
    if not isinstance(label_value, dict):
        raise ValueError("Layer configuration requires a label")

    predictors = tuple(
        _parse_selection(data_root, predictor, require_name=True)
        for predictor in predictors_value
    )
    label = _parse_selection(data_root, label_value, require_name=False)
    if label.resampling != "nearest":
        raise ValueError("Labels must use nearest resampling")
    return LayerConfig(
        reference=_resolve_data_path(data_root, reference_value),
        predictors=predictors,
        label=label,
    )