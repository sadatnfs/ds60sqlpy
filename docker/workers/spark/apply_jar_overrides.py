"""Apply the SHA-256 pinned Spark jar overrides during the Spark worker image build.

The upstream Spark distribution bundles Hive, Spark Connect, Kubernetes, and ZooKeeper
client jars that the classroom never loads, plus dependency jars with published security
fixes. This script deletes the unused jars, swaps each standalone jar for the pinned
fixed release listed in ``jar-overrides.json``, and re-shades libraries that Spark and
Hadoop bundle inside their own jars (``reshade_jars``) with pinned fixed releases
relocated into the same package prefix (see ``jar_reshade.py``). It fails closed: a
missing expected jar or namespace, an unexpected leftover, or a checksum mismatch stops
the build instead of producing a partially patched Spark.
"""

from __future__ import annotations

import hashlib
import json
import shutil
import sys
from pathlib import Path
from typing import Any

from fetch_pinned import MAX_BYTES, open_download
from jar_reshade import Relocation, Relocator, ReshadeError, Source, reshade

SHA256_HEX = frozenset("0123456789abcdef")


def _strings(value: object, where: str) -> list[str]:
    if not isinstance(value, list) or not all(isinstance(item, str) and item for item in value):
        raise SystemExit(f"{where} must be a list of non-empty strings")
    return value


def _download_item(item: object, where: str) -> None:
    if not isinstance(item, dict):
        raise SystemExit(f"{where} must be an object")
    for key in ("url", "sha256", "jar"):
        if not isinstance(item.get(key), str) or not item[key]:
            raise SystemExit(f"{where}.{key} must be a non-empty string")
    if not item["url"].startswith("https://"):
        raise SystemExit(f"{where}.url must use HTTPS")
    if len(item["sha256"]) != 64 or not set(item["sha256"]) <= SHA256_HEX:
        raise SystemExit(f"{where}.sha256 must be 64 lowercase hex digits")


def validate_manifest(manifest: object) -> dict[str, Any]:
    """Check the manifest shape so a typo fails before any jar is touched."""
    if not isinstance(manifest, dict) or manifest.get("schema") != 1:
        raise SystemExit("Unsupported jar override manifest schema")
    if not isinstance(manifest.get("spark_version"), str):
        raise SystemExit("spark_version must be a string")
    _strings(manifest.get("remove_paths", []), "remove_paths")
    _strings(manifest.get("remove_jars", []), "remove_jars")
    for index, item in enumerate(manifest.get("replace_jars", [])):
        _download_item(item, f"replace_jars[{index}]")
        if not isinstance(item.get("remove"), str):
            raise SystemExit(f"replace_jars[{index}].remove must be a string")
    for index, target in enumerate(manifest.get("reshade_jars", [])):
        where = f"reshade_jars[{index}]"
        if not isinstance(target, dict) or not isinstance(target.get("jar"), str):
            raise SystemExit(f"{where}.jar must be a string")
        relocations = target.get("relocations")
        if not isinstance(relocations, list) or not relocations:
            raise SystemExit(f"{where}.relocations must be a non-empty list")
        for rule in relocations:
            if not isinstance(rule, dict) or set(rule) != {"from", "to"}:
                raise SystemExit(f"{where}.relocations entries need exactly from and to")
            _strings([rule["from"], rule["to"]], f"{where}.relocations")
        _strings(target.get("excludes", []), f"{where}.excludes")
        items = target.get("items")
        if not isinstance(items, list) or not items:
            raise SystemExit(f"{where}.items must be a non-empty list")
        for number, item in enumerate(items):
            label = f"{where}.items[{number}]"
            if not isinstance(item, dict):
                raise SystemExit(f"{label} must be an object")
            if not _strings(item.get("namespaces"), f"{label}.namespaces"):
                raise SystemExit(f"{label}.namespaces must not be empty")
            _strings(item.get("metadata", []), f"{label}.metadata")
            for position, source in enumerate(item.get("sources", [])):
                _download_item(source, f"{label}.sources[{position}]")
                if not isinstance(source.get("relocate", True), bool):
                    raise SystemExit(f"{label}.sources[{position}].relocate must be a boolean")
    return manifest


def load_manifest(path: Path) -> dict[str, Any]:
    return validate_manifest(json.loads(path.read_text(encoding="utf-8")))


def download(item: dict[str, Any]) -> bytes:
    """Return one pinned download, failing closed on size or SHA-256 mismatch."""
    with open_download(item["url"], 120) as response:
        data: bytes = response.read(MAX_BYTES + 1)
    if len(data) > MAX_BYTES or hashlib.sha256(data).hexdigest() != item["sha256"]:
        raise SystemExit(f"Pinned jar size or SHA-256 mismatch: {item['url']}")
    return data


def reshade_jar(path: Path, target: dict[str, Any]) -> list[str]:
    """Apply every reshade item of one manifest entry to the jar at ``path``."""
    relocator = Relocator(
        [Relocation(rule["from"], rule["to"]) for rule in target["relocations"]],
        target.get("excludes", []),
    )
    plain = Relocator([])
    data = path.read_bytes()
    actions: list[str] = []
    for item in target["items"]:
        sources = [
            Source(download(source), relocator if source.get("relocate", True) else plain)
            for source in item.get("sources", [])
        ]
        try:
            data, report = reshade(data, item["namespaces"], item.get("metadata", []), sources)
        except ReshadeError as error:
            raise SystemExit(f"Reshade of {path.name} failed: {error}") from error
        actions.append(f"reshaded {path.name}: {'; '.join(report)}")
    path.write_bytes(data)
    path.chmod(0o644)
    return actions


def apply(spark_home: Path, manifest: dict[str, Any]) -> list[str]:
    jars = spark_home / "jars"
    release = (spark_home / "RELEASE").read_text(encoding="utf-8")
    if f"Spark {manifest['spark_version']} " not in release:
        raise SystemExit(
            f"Jar overrides target Spark {manifest['spark_version']}; RELEASE says: {release!r}"
        )
    actions: list[str] = []
    for relative in manifest.get("remove_paths", []):
        target = spark_home / relative
        if not target.is_dir():
            raise SystemExit(f"Expected Spark directory is missing: {target}")
        shutil.rmtree(target)
        actions.append(f"removed {relative}/")
    for name in manifest.get("remove_jars", []):
        (jars / name).unlink()
        actions.append(f"removed {name}")
    for item in manifest.get("replace_jars", []):
        (jars / item["remove"]).unlink()
        data = download(item)
        destination = jars / item["jar"]
        with destination.open("xb") as output:
            output.write(data)
        destination.chmod(0o644)
        actions.append(f"replaced {item['remove']} with {item['jar']}")
    for target in manifest.get("reshade_jars", []):
        path = jars / target["jar"]
        if not path.is_file():
            raise SystemExit(f"Expected Spark jar to reshade is missing: {path}")
        actions += reshade_jar(path, target)
    return actions


def main(arguments: list[str]) -> int:
    if len(arguments) != 2:
        print("Usage: apply_jar_overrides.py SPARK_HOME MANIFEST", file=sys.stderr)
        return 2
    for line in apply(Path(arguments[0]), load_manifest(Path(arguments[1]))):
        print(line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
