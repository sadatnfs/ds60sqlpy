"""Apply the SHA-256 pinned Spark jar overrides during the Spark worker image build.

The upstream Spark 4.0.1 distribution bundles Hive, Spark Connect, Kubernetes, and
ZooKeeper client jars that the classroom never loads, plus standalone dependency jars
with published security fixes. This script deletes the unused jars and swaps each
standalone jar for the pinned fixed release listed in ``jar-overrides.json``. It fails
closed: a missing expected jar, an unexpected leftover, or a checksum mismatch stops
the build instead of producing a partially patched Spark.
"""

from __future__ import annotations

import hashlib
import json
import shutil
import sys
from pathlib import Path

from fetch_pinned import MAX_BYTES, open_download


def load_manifest(path: Path) -> dict:
    manifest = json.loads(path.read_text(encoding="utf-8"))
    if manifest.get("schema") != 1:
        raise SystemExit(f"Unsupported jar override manifest schema in {path}")
    return manifest


def apply(spark_home: Path, manifest: dict) -> list[str]:
    jars = spark_home / "jars"
    release = (spark_home / "RELEASE").read_text(encoding="utf-8")
    if f"Spark {manifest['spark_version']} " not in release:
        raise SystemExit(
            f"Jar overrides target Spark {manifest['spark_version']}; RELEASE says: {release!r}"
        )
    actions: list[str] = []
    for relative in manifest["remove_paths"]:
        target = spark_home / relative
        if not target.is_dir():
            raise SystemExit(f"Expected Spark directory is missing: {target}")
        shutil.rmtree(target)
        actions.append(f"removed {relative}/")
    for name in manifest["remove_jars"]:
        (jars / name).unlink()
        actions.append(f"removed {name}")
    for item in manifest["replace_jars"]:
        (jars / item["remove"]).unlink()
        with open_download(item["url"], 120) as response:
            data = response.read(MAX_BYTES + 1)
        if len(data) > MAX_BYTES or hashlib.sha256(data).hexdigest() != item["sha256"]:
            raise SystemExit(f"Pinned jar size or SHA-256 mismatch: {item['url']}")
        destination = jars / item["jar"]
        with destination.open("xb") as output:
            output.write(data)
        destination.chmod(0o644)
        actions.append(f"replaced {item['remove']} with {item['jar']}")
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
