#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: build_package.py <lab_dir>")
        return 2

    lab_dir = Path(sys.argv[1]).resolve()
    manifest_path = lab_dir / "pipeline" / "manifests" / "content-manifest.json"
    if not manifest_path.exists():
        print("Manifest is missing.")
        return 1

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    file_list = manifest.get("packageIncludes", [])
    if not isinstance(file_list, list) or not file_list:
        print("packageIncludes must be a non-empty list of relative file paths.")
        return 1
    inputs = []
    seen = set()
    for relative in file_list:
        if not isinstance(relative, str) or Path(relative).is_absolute():
            print("Package inputs must be relative file paths.")
            return 1
        src = (lab_dir / relative).resolve()
        if not src.is_relative_to(lab_dir) or not src.is_file() or src in seen:
            print(f"Missing, duplicate, or out-of-lab package input: {relative}")
            return 1
        seen.add(src)
        inputs.append((src, src.relative_to(lab_dir).as_posix()))

    dist_dir = lab_dir / "dist"
    dist_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    package_name = f"lab06-content-package-{timestamp}.zip"
    package_path = dist_dir / package_name

    package_entries = []
    with ZipFile(package_path, "w", compression=ZIP_DEFLATED) as archive:
        for src, relative in inputs:
            archive.write(src, arcname=relative)
            package_entries.append(
                {
                    "path": relative,
                    "sha256": sha256_file(src),
                    "size": src.stat().st_size,
                }
            )

    checksum = sha256_file(package_path)
    sha_path = dist_dir / f"{package_name}.sha256"
    sha_path.write_text(f"{checksum}  {package_name}\n", encoding="utf-8")

    manifest_out = dist_dir / f"{package_name}.manifest.json"
    manifest_out.write_text(
        json.dumps(
            {
                "createdUtc": timestamp,
                "package": package_name,
                "packageSha256": checksum,
                "entries": package_entries,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    latest = dist_dir / "latest-package.txt"
    latest.write_text(package_name + "\n", encoding="utf-8")

    print(f"Created {package_path}")
    print(f"Created {sha_path}")
    print(f"Created {manifest_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
