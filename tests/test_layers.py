import json
from pathlib import Path

import pytest

from artemis_ml.layers import load_layer_config


def _write_config(tmp_path: Path, **overrides: object) -> tuple[Path, Path]:
    data_root = tmp_path / "data"
    data_root.mkdir()
    for name in ("reference.tif", "predictor.tif", "label.tif"):
        (data_root / name).write_bytes(b"placeholder")
    config = {
        "reference": "reference.tif",
        "predictors": [
            {"name": "elevation", "path": "predictor.tif", "resampling": "bilinear"}
        ],
        "label": {"path": "label.tif", "resampling": "nearest"},
        **overrides,
    }
    config_path = tmp_path / "layers.json"
    config_path.write_text(json.dumps(config), encoding="utf-8")
    return config_path, data_root


def test_load_layer_config_validates_roles_and_paths(tmp_path: Path) -> None:
    config_path, data_root = _write_config(tmp_path)

    config = load_layer_config(config_path, data_root)

    assert config.reference == (data_root / "reference.tif").resolve()
    assert config.predictors[0].name == "elevation"
    assert config.label.resampling == "nearest"


def test_load_layer_config_rejects_non_nearest_labels(tmp_path: Path) -> None:
    config_path, data_root = _write_config(
        tmp_path,
        label={"path": "label.tif", "resampling": "bilinear"},
    )

    with pytest.raises(ValueError, match="Labels must use nearest"):
        load_layer_config(config_path, data_root)


def test_load_layer_config_rejects_path_escape(tmp_path: Path) -> None:
    config_path, data_root = _write_config(
        tmp_path,
        reference="../outside.tif",
    )

    with pytest.raises(ValueError, match="escapes data root"):
        load_layer_config(config_path, data_root)