"""Apply one checked exit-status correction to a reviewed Spark 4.x wrapper.

The original Apache-licensed file and license header remain intact. This patch
does not change scheduling or TorchDistributor's public interface. Refuse a new
upstream source instead of guessing that this change is still appropriate.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from importlib import import_module
from pathlib import Path
from zipfile import ZipFile

MEMBER = "pyspark/ml/torch/torch_run_process_wrapper.py"
# Each reviewed upstream wrapper waits for torchrun and then falls off the end of
# its main block, so the process exits zero even when a rank failed. Spark 4.3.0
# only changed the line decoding to an explicit UTF-8 codec.
REVIEWED_WRAPPERS = {
    "d04cf01e605ee98d60f8b113ea4bf74316caa16031db671201cafd4d22dc6b61": "4.0.1",
    "d9a4219524fef849f22a7ff4accc9fbcee353e8fd8768943a8b0365217da44c4": "4.3.0",
}
ADDITION = b"""
    # DS60: propagate torchrun failure even if a training result was serialized.
    # Upstream Spark 4.0.1 and 4.3.0 otherwise exit zero after task.wait().
    sys.exit(task.returncode if task.returncode >= 0 else 128 - task.returncode)
"""


def upstream(version: str) -> str:
    return (
        f"https://github.com/apache/spark/blob/v{version}/"
        "python/pyspark/ml/torch/torch_run_process_wrapper.py"
    )


def reviewed(digest: str) -> dict[str, str] | None:
    version = REVIEWED_WRAPPERS.get(digest)
    if version is None:
        return None
    return {"spark_version": version, "original_sha256": digest, "upstream": upstream(version)}


def patch_archive(path: Path) -> dict[str, str]:
    with ZipFile(path) as source:
        original = source.read(MEMBER)
        review = reviewed(hashlib.sha256(original).hexdigest())
        if original.endswith(ADDITION):
            review = reviewed(hashlib.sha256(original[: -len(ADDITION)]).hexdigest())
            if review is None:
                raise ValueError("the existing wrapper patch does not match the reviewed source")
            patched = original
        else:
            if review is None:
                raise ValueError(
                    "unreviewed Spark wrapper; inspect source before applying this patch"
                )
            patched = original + ADDITION
        members = [(item, source.read(item.filename)) for item in source.infolist()]
    temporary = path.with_suffix(".ds60-patch.tmp")
    try:
        with ZipFile(temporary, "w") as target:
            for item, data in members:
                target.writestr(item, patched if item.filename == MEMBER else data)
        temporary.replace(path)
    finally:
        temporary.unlink(missing_ok=True)
    return {
        "patch": "propagate-torchrun-exit-status",
        **review,
        "patched_sha256": hashlib.sha256(patched).hexdigest(),
    }


def wrapper_status(path: Path, *, archive: bool = True) -> dict[str, str]:
    if archive:
        with ZipFile(path) as source:
            data = source.read(MEMBER)
    else:
        data = path.read_bytes()
    if data.endswith(ADDITION):
        review = reviewed(hashlib.sha256(data[: -len(ADDITION)]).hexdigest())
        if review is not None:
            return {
                "status": "prepared",
                **review,
                "patched_sha256": hashlib.sha256(data).hexdigest(),
            }
    review = reviewed(hashlib.sha256(data).hexdigest())
    if review is not None:
        return {"status": "needs-explicit-preparation", **review}
    raise ValueError("unreviewed Spark wrapper: refuse to guess or silently patch")


def patch_file(path: Path) -> dict[str, str]:
    status = wrapper_status(path, archive=False)
    if status["status"] == "prepared":
        return status
    original = path.read_bytes()
    temporary = path.with_suffix(path.suffix + ".ds60-patch.tmp")
    try:
        temporary.write_bytes(original + ADDITION)
        temporary.chmod(path.stat().st_mode)
        temporary.replace(path)
    finally:
        temporary.unlink(missing_ok=True)
    return wrapper_status(path, archive=False)


def require_prepared_wrapper() -> dict[str, str]:
    archive = Path(os.environ.get("SPARK_HOME", "/opt/spark")) / "python/lib/pyspark.zip"
    if archive.is_file():
        status = wrapper_status(archive)
    else:
        torch_run_process_wrapper = import_module("pyspark.ml.torch.torch_run_process_wrapper")

        source_file = torch_run_process_wrapper.__file__
        if source_file is None:
            raise RuntimeError("Prepared Spark wrapper has no inspectable source file")
        status = wrapper_status(Path(source_file), archive=False)
    if status["status"] != "prepared":
        raise RuntimeError(
            "Prepare the reviewed Spark exit-status correction explicitly before training"
        )
    return status


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    location = parser.add_mutually_exclusive_group(required=True)
    location.add_argument("--archive", type=Path)
    location.add_argument("--file", type=Path)
    parser.add_argument(
        "--apply", action="store_true", help="explicit build-time mutation; default is read-only"
    )
    args = parser.parse_args()
    path = args.archive or args.file
    if args.apply:
        receipt = patch_archive(path) if args.archive else patch_file(path)
    else:
        receipt = wrapper_status(path, archive=bool(args.archive))
    print(json.dumps(receipt, sort_keys=True))
    return 0 if args.apply or receipt["status"] == "prepared" else 1


if __name__ == "__main__":
    raise SystemExit(main())
