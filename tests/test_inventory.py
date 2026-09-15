from pathlib import Path

import pytest

from artemis_ml.inventory import build_inventory, write_inventory


def test_build_inventory_uses_relative_paths_and_stable_order(tmp_path: Path) -> None:
    (tmp_path / "README.md").write_text("documentation", encoding="utf-8")
    (tmp_path / ".gitkeep").touch()
    (tmp_path / "nested").mkdir()
    (tmp_path / "nested" / "B.TIF").write_bytes(b"raster")
    (tmp_path / "a.csv").write_text("x,y\n1,2\n", encoding="utf-8")

    records = build_inventory(tmp_path)

    assert [record.relative_path for record in records] == ["a.csv", "nested/B.TIF"]
    assert records[0].suffix == ".csv"
    assert records[1].suffix == ".tif"
    assert len(records[0].sha256) == 64


def test_build_inventory_requires_a_directory(tmp_path: Path) -> None:
    missing = tmp_path / "missing"

    with pytest.raises(NotADirectoryError):
        build_inventory(missing)


def test_write_inventory_creates_json_manifest(tmp_path: Path) -> None:
    data_root = tmp_path / "data"
    data_root.mkdir()
    (data_root / "sample.txt").write_text("sample", encoding="utf-8")
    output_path = tmp_path / "processed" / "inventory.json"

    write_inventory(data_root, output_path)

    assert '"relative_path": "sample.txt"' in output_path.read_text(
        encoding="utf-8"
    )