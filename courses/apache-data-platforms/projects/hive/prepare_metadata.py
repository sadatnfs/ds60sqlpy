"""Compile and verify one source/image-bound Hive metadata probe during preparation."""

from __future__ import annotations

import argparse
import hashlib
import os
import re
import subprocess
from pathlib import Path

KEYS = ("schema_version", "hive_image_id", "java_image_id", "source_sha256", "class_sha256")

SDK_JARS = (
    "hive-lib/hive-common-4.2.1.jar",
    "hive-lib/hive-standalone-metastore-client-4.2.1.jar",
    "hive-lib/hive-standalone-metastore-common-4.2.1.jar",
    "hive-lib/hive-classification-4.2.1.jar",
    "hive-lib/hive-storage-api-4.2.1.jar",
    "hive-lib/hive-serde-4.2.1.jar",
    "hive-lib/libthrift-0.16.0.jar",
    "hadoop-common/hadoop-common-3.4.1.jar",
)


def checksum(path: Path, limit: int = 1_000_000) -> str:
    if path.is_symlink() or not path.is_file() or path.stat().st_size > limit:
        raise ValueError("Prepared metadata identity requires bounded regular files")
    return hashlib.sha256(path.read_bytes()).hexdigest()


def manifest_bytes(values: dict[str, str]) -> bytes:
    return "".join(f"{key}\t{values[key]}\n" for key in KEYS).encode("ascii")


def verify(root: Path, source: Path, hive_image: str, java_image: str) -> dict[str, str]:
    manifest = root / "identity.tsv"
    classes = root / "classes"
    if (
        root.is_symlink()
        or classes.is_symlink()
        or not classes.is_dir()
        or {path.name for path in classes.iterdir()} != {"MetadataProbe.class"}
        or manifest.is_symlink()
        or not manifest.is_file()
        or manifest.stat().st_size > 4096
    ):
        raise ValueError("Prepared metadata inventory differs; no replacement occurred")
    expected = {
        "schema_version": "1",
        "hive_image_id": hive_image,
        "java_image_id": java_image,
        "source_sha256": checksum(source),
        "class_sha256": checksum(classes / "MetadataProbe.class"),
    }
    if manifest.read_bytes() != manifest_bytes(expected):
        raise ValueError("Prepared metadata source/class/image identity changed")
    return expected


def prepare(
    root: Path, source: Path, hive_image: str, java_image: str, action: str
) -> dict[str, str]:
    if any(
        re.fullmatch(r"sha256:[0-9a-f]{64}", image) is None for image in (hive_image, java_image)
    ):
        raise ValueError("Preparation requires exact inspected native image identities")
    if root.is_symlink() or not root.is_dir():
        raise ValueError("Use a regular owned preparation directory")
    if action == "compile":
        checksum(source)
        classes = root / "classes"
        if classes.exists() or classes.is_symlink() or (root / "identity.tsv").exists():
            raise ValueError("Refuse to replace an existing metadata compilation")
        classes.mkdir()
        jars = [root / name for name in SDK_JARS]
        if any(
            path.is_symlink() or not path.is_file() or path.stat().st_size > 150_000_000
            for path in jars
        ):
            raise ValueError("The actual release metadata SDK inventory differs")
        subprocess.run(
            [
                "javac",
                "--release",
                "21",
                "-proc:none",
                "-cp",
                ":".join(str(path) for path in jars),
                "-d",
                str(classes),
                str(source),
            ],
            check=True,
            timeout=90,
        )
        expected = {
            "schema_version": "1",
            "hive_image_id": hive_image,
            "java_image_id": java_image,
            "source_sha256": checksum(source),
            "class_sha256": checksum(classes / "MetadataProbe.class"),
        }
        with (root / "identity.tsv").open("xb") as handle:
            handle.write(manifest_bytes(expected))
    return verify(root, source, hive_image, java_image)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=["compile", "verify"])
    args = parser.parse_args()
    expected = prepare(
        Path("/prepared"),
        Path("/project/MetadataProbe.java"),
        os.environ.get("DS60_HIVE_SOURCE_IMAGE_ID", ""),
        os.environ.get("DS60_HIVE_JAVA_IMAGE_ID", ""),
        args.action,
    )
    print(
        "Prepared metadata source, class and native image identities verified: "
        + expected["source_sha256"]
    )


if __name__ == "__main__":
    main()
