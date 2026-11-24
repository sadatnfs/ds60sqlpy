"""Remove pip's vendored pkg_resources and keep pip's own metadata accurate.

pip vendors ``pkg_resources`` (published as setuptools) only for its legacy
metadata backend. On Python 3.11 to 3.13 pip uses ``importlib.metadata`` by
default, and the image sets ``_PIP_USE_IMPORTLIB_METADATA=1`` so pip can never
fall back. This step deletes the unused package, then rewrites the vendored
CycloneDX SBOM, ``vendor.txt`` and the wheel RECORD so every inventory matches
the files that remain. It fails if any trace of the vendored setuptools stays.

Usage: python prune_pip_vendor.py [SITE_PACKAGES ...]
Without arguments it prunes the running interpreter's purelib directory.
"""

from __future__ import annotations

import base64
import csv
import hashlib
import io
import json
import shutil
import sys
import sysconfig
from pathlib import Path

REMOVED = "setuptools"
PACKAGE = "pkg_resources"


class PruneError(RuntimeError):
    pass


def _digest(data: bytes) -> str:
    raw = base64.urlsafe_b64encode(hashlib.sha256(data).digest()).rstrip(b"=")
    return "sha256=" + raw.decode("ascii")


def _component_refs(bom: dict) -> set[str]:
    refs = set()
    for component in bom.get("components", []):
        if str(component.get("name", "")).lower() == REMOVED:
            refs.add(str(component.get("bom-ref") or component.get("purl") or ""))
    return refs


def prune_bom(text: str) -> str:
    bom = json.loads(text)
    refs = _component_refs(bom)
    bom["components"] = [
        c for c in bom.get("components", []) if str(c.get("name", "")).lower() != REMOVED
    ]
    dependencies = []
    for entry in bom.get("dependencies", []):
        if entry.get("ref") in refs:
            continue
        if "dependsOn" in entry:
            entry["dependsOn"] = [ref for ref in entry["dependsOn"] if ref not in refs]
        dependencies.append(entry)
    if "dependencies" in bom:
        bom["dependencies"] = dependencies
    return json.dumps(bom, indent=2, sort_keys=True) + "\n"


def prune_vendor_txt(text: str) -> str:
    kept = [
        line
        for line in text.splitlines(keepends=True)
        if line.split("==", 1)[0].strip().lower() != REMOVED
    ]
    return "".join(kept)


def _record_path(site: Path) -> Path:
    records = sorted(site.glob("pip-*.dist-info/RECORD"))
    if len(records) != 1:
        raise PruneError(f"Expected one pip RECORD in {site}, found {len(records)}")
    return records[0]


def prune_metadata(text: str) -> str:
    license_file = f"License-File: src/pip/_vendor/{PACKAGE}/"
    return "".join(
        line for line in text.splitlines(keepends=True) if not line.startswith(license_file)
    )


def _removed(path: str) -> bool:
    if path.startswith(f"pip/_vendor/{PACKAGE}/"):
        return True
    parts = path.split("/", 1)
    return (
        len(parts) == 2
        and parts[0].startswith("pip-")
        and parts[0].endswith(".dist-info")
        and parts[1].startswith(f"licenses/src/pip/_vendor/{PACKAGE}/")
    )


def _rewrite_record(site: Path, changed: dict[str, bytes]) -> None:
    record = _record_path(site)
    rows = []
    for row in csv.reader(io.StringIO(record.read_text("utf-8"))):
        if not row:
            continue
        path = row[0]
        if _removed(path):
            continue
        if path in changed:
            row = [path, _digest(changed[path]), str(len(changed[path]))]
        rows.append(row)
    out = io.StringIO()
    csv.writer(out, lineterminator="\n").writerows(rows)
    record.write_text(out.getvalue(), "utf-8")


def prune(site: Path) -> bool:
    """Prune one site-packages directory. Return False when it has no pip."""
    vendor = site / "pip/_vendor"
    if not vendor.is_dir():
        return False
    info = _record_path(site).parent
    for directory in (vendor / PACKAGE, info / f"licenses/src/pip/_vendor/{PACKAGE}"):
        if directory.exists():
            shutil.rmtree(directory)
    changed: dict[str, bytes] = {}
    for path, rewrite in (
        (vendor / "bom.cdx.json", prune_bom),
        (vendor / "vendor.txt", prune_vendor_txt),
        (info / "METADATA", prune_metadata),
    ):
        if path.is_file():
            data = rewrite(path.read_text("utf-8")).encode("utf-8")
            path.write_bytes(data)
            changed[path.relative_to(site).as_posix()] = data
    _rewrite_record(site, changed)
    verify(site)
    return True


def verify(site: Path) -> None:
    vendor = site / "pip/_vendor"
    if (vendor / PACKAGE).exists():
        raise PruneError(f"{vendor / PACKAGE} still exists")
    bom = vendor / "bom.cdx.json"
    if bom.is_file():
        data = json.loads(bom.read_text("utf-8"))
        if _component_refs(data) or REMOVED in json.dumps(data.get("dependencies", [])):
            raise PruneError(f"{bom} still lists {REMOVED}")
    txt = vendor / "vendor.txt"
    if txt.is_file() and prune_vendor_txt(txt.read_text("utf-8")) != txt.read_text("utf-8"):
        raise PruneError(f"{txt} still lists {REMOVED}")
    record = _record_path(site)
    if any(_removed(row[0]) for row in csv.reader(io.StringIO(record.read_text("utf-8"))) if row):
        raise PruneError(f"pip RECORD in {site} still lists {PACKAGE}")
    if (record.parent / f"licenses/src/pip/_vendor/{PACKAGE}").exists():
        raise PruneError(f"pip license copy of {PACKAGE} in {site} still exists")
    metadata = record.parent / "METADATA"
    if metadata.is_file() and prune_metadata(metadata.read_text("utf-8")) != metadata.read_text(
        "utf-8"
    ):
        raise PruneError(f"pip METADATA in {site} still lists the {PACKAGE} license")


def main(argv: list[str]) -> int:
    sites = [Path(arg) for arg in argv] or [Path(sysconfig.get_paths()["purelib"])]
    try:
        pruned = [site for site in sites if prune(site)]
    except (OSError, ValueError, PruneError) as error:
        print(f"prune_pip_vendor: {error}", file=sys.stderr)
        return 1
    if not pruned:
        print("prune_pip_vendor: no pip installation found", file=sys.stderr)
        return 1
    for site in pruned:
        print(f"prune_pip_vendor: removed vendored {PACKAGE} from {site}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
