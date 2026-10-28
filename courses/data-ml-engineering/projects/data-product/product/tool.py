"""Fixed operator commands for the owned data-product state."""

from __future__ import annotations

import argparse
import os
import secrets
from pathlib import Path
from typing import Any

from .contracts import (
    HEX,
    ConflictError,
    ContractError,
    StateError,
    canonical,
    owner_identity,
    read_regular,
)
from .journal import Journal
from .publication import Publisher, image_identity, read_product
from .raw_store import RawStore


def paths() -> tuple[Path, Path, Path, Path]:
    return (
        Path(os.environ.get("DS60_PRODUCT_RAW_DIR", "/state/raw")),
        Path(os.environ.get("DS60_PRODUCT_PUBLISHED_DIR", "/state/published")),
        Path(os.environ.get("DS60_PRODUCT_CONTROL_DIR", "/state/control")),
        Path(os.environ.get("DS60_PRODUCT_PRIVATE_DIR", "/state/private")),
    )


def initialize(owner: str) -> dict[str, Any]:
    raw, published, control, private = paths()
    import duckdb
    import polars as pl
    import pyarrow as pa

    if (
        duckdb.sql("select 42").fetchall()[0][0] != 42
        or pl.DataFrame({"n": [20, 22]})["n"].sum() != 42
        or pa.array([20, 22]).to_pylist() != [20, 22]
    ):
        raise StateError("The selected image failed its fixed data-library probe")
    for directory in (raw, published, control, private):
        if directory.is_symlink():
            raise StateError("Workshop directories cannot be symbolic links")
        directory.mkdir(mode=0o700, exist_ok=True)
    owner_file = private / "owner"
    if owner_file.exists() or owner_file.is_symlink():
        if read_regular(owner_file, 100).decode().strip() != owner:
            raise StateError("Private state belongs to another workshop")
    else:
        with owner_file.open("x", encoding="ascii") as stream:
            stream.write(owner + "\n")
        owner_file.chmod(0o600)
    token_file = private / "token"
    if token_file.exists() or token_file.is_symlink():
        token = read_regular(token_file, 100).decode().strip()
        if HEX.fullmatch(token) is None:
            raise StateError("Saved private token is malformed")
    else:
        descriptor = os.open(token_file, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(descriptor, "w", encoding="ascii") as stream:
            stream.write(secrets.token_hex(32) + "\n")
            stream.flush()
            os.fsync(stream.fileno())
    RawStore(raw, owner, writable=True)
    Journal(control, owner)
    return {"initialized": True, "existing_state_retained": True, "token_printed": False}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="action", required=True)
    for name in ("initialize", "query", "recover", "history"):
        sub.add_parser(name)
    publish = sub.add_parser("publish")
    publish.add_argument("batch_id")
    publish.add_argument("--failpoint", choices=("before-pointer", "after-pointer"))
    rollback = sub.add_parser("rollback")
    rollback.add_argument("version_id")
    rollback.add_argument("--reason", required=True)
    args = parser.parse_args()
    try:
        owner = owner_identity(os.environ["DS60_PRODUCT_OWNER"])
        raw, published, control, _ = paths()
        if args.action == "initialize":
            result = initialize(owner)
        elif args.action == "query":
            result = read_product(published, owner)
        else:
            publisher = Publisher(
                raw, published, control, owner, image_identity(os.environ["DS60_PRODUCT_IMAGE_ID"])
            )
            if args.action == "publish":
                result = publisher.publish(args.batch_id, failpoint=args.failpoint)
            elif args.action == "recover":
                result = publisher.recover()
            elif args.action == "history":
                result = {"operations": publisher.journal.records()}
            else:
                result = publisher.rollback(args.version_id, args.reason)
        print(canonical(result).decode())
        return 2 if result.get("status") == "rejected" else 0
    except (ContractError, ConflictError) as error:
        print(canonical({"error": type(error).__name__, "message": str(error)}).decode())
        return 2
    except (StateError, FileNotFoundError, KeyError, OSError) as error:
        print(
            canonical(
                {"error": type(error).__name__, "message": str(error), "automatic_replay": False}
            ).decode()
        )
        return 3


if __name__ == "__main__":
    raise SystemExit(main())
