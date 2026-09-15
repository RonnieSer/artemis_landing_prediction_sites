"""Build a local, reproducible inventory of private data inputs."""

from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import asdict, dataclass
from pathlib import Path


_CONTROL_FILES = {"README.md", ".gitkeep"}


@dataclass(frozen=True)
class FileRecord:
    """Metadata for one data file, using a repository-relative path."""

    relative_path: str
    size_bytes: int
    sha256: str
    suffix: str


def _sha256(path: Path, chunk_size: int = 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(chunk_size), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build_inventory(data_root: Path) -> list[FileRecord]:
    """Return sorted metadata for private files below ``data_root``.

    Control files used to document the data directory are excluded. All paths
    in the result are relative to ``data_root`` so the manifest is portable.
    """
    if not data_root.is_dir():
        raise NotADirectoryError(f"Data root does not exist: {data_root}")

    records = []
    for path in sorted(data_root.rglob("*")):
        if not path.is_file() or path.name in _CONTROL_FILES:
            continue
        records.append(
            FileRecord(
                relative_path=path.relative_to(data_root).as_posix(),
                size_bytes=path.stat().st_size,
                sha256=_sha256(path),
                suffix=path.suffix.lower(),
            )
        )
    return records


def write_inventory(data_root: Path, output_path: Path) -> None:
    """Write a JSON inventory, creating only the requested local output path."""
    records = [asdict(record) for record in build_inventory(data_root)]
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(records, indent=2) + "\n",
        encoding="utf-8",
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-root", type=Path, default=Path("data"))
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/processed/source_inventory.json"),
    )
    args = parser.parse_args()
    write_inventory(args.data_root, args.output)
    print(f"Wrote inventory to {args.output}")


if __name__ == "__main__":
    main()