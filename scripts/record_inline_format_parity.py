"""Collect or verify static Python-fence formatting parity without changing history."""

from __future__ import annotations

import argparse
import json
import sys
import tempfile
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.source_format_parity import (  # noqa: E402
    INLINE_KIND,
    INLINE_RECEIPT,
    MAX_INLINE_GUIDE,
    MAX_INLINE_RECEIPT,
    MAX_INLINE_RECORDS,
    _inline_path,
    create_inline_record,
    load_inline_records,
    verify_inline_record,
)


def regular_source(root: Path, name: str) -> bytes:
    _inline_path(name)
    path = root / name
    for parent in [path, *path.parents]:
        if parent.is_symlink():
            raise ValueError("Inline parity source path must not contain a symlink")
        if parent == root:
            break
    if not path.is_file() or not 0 < path.stat().st_size <= MAX_INLINE_GUIDE:
        raise ValueError("Inline parity source is missing or exceeds its bound: " + name)
    with path.open("rb") as stream:
        raw = stream.read(MAX_INLINE_GUIDE + 1)
    if not 0 < len(raw) <= MAX_INLINE_GUIDE:
        raise ValueError("Inline parity source exceeds its byte bound: " + name)
    return raw


def collect(root: Path, before_root: Path, paths: list[str]) -> dict[str, Any]:
    if not paths or len(paths) != len(set(paths)) or len(paths) > MAX_INLINE_RECORDS:
        raise ValueError("Supply bounded unique paths for inline parity")
    records = load_inline_records(root)
    selected = set(paths)
    for name, record in records.items():
        if name not in selected:
            verify_inline_record(record, regular_source(root, name))
    for name in paths:
        before = regular_source(before_root, name)
        after = regular_source(root, name)
        original = verify_inline_record(records[name], before) if name in records else before
        if before == after:
            continue
        records[name] = create_inline_record(name, original, after)
    if len(records) > MAX_INLINE_RECORDS:
        raise ValueError("Inline parity record count exceeds its bound")
    return {
        "schema_version": 1,
        "evidence_kind": INLINE_KIND,
        "records": [records[name] for name in sorted(records)],
    }


def verify(root: Path) -> int:
    target = root / INLINE_RECEIPT
    if not target.is_file():
        raise ValueError("Missing inline formatting parity receipt")
    records = load_inline_records(root)
    for name, record in records.items():
        verify_inline_record(record, regular_source(root, name))
    return len(records)


def publish(root: Path, output: Path, payload: dict[str, Any]) -> None:
    output = output.absolute()
    for path in [output, *output.parents]:
        if path.is_symlink():
            raise ValueError("Inline parity output must not contain a symlink")
    if output.exists() and output != (root / INLINE_RECEIPT).absolute():
        raise ValueError("Use a fresh explicit output path")
    raw = (json.dumps(payload, indent=2, ensure_ascii=True) + "\n").encode()
    if len(raw) > MAX_INLINE_RECEIPT:
        raise ValueError("Inline parity output exceeds its byte bound")
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(
            dir=output.parent, prefix=output.name + ".", delete=False
        ) as stream:
            temporary = Path(stream.name)
            stream.write(raw)
        temporary.chmod(0o644)
        temporary.replace(output)
    finally:
        if temporary is not None and temporary.exists():
            temporary.unlink()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=ROOT)
    parser.add_argument("--before", type=Path, help="Validated pre-format snapshot root")
    parser.add_argument(
        "--path", action="append", default=[], help="Explicit changed Markdown path"
    )
    parser.add_argument(
        "--output", type=Path, help="Default: current repository's additive inline receipt"
    )
    parser.add_argument(
        "--verify", action="store_true", help="Read-only verification of all current bindings"
    )
    args = parser.parse_args()
    root = args.repo.absolute()
    if args.verify:
        if args.before is not None or args.path or args.output is not None:
            parser.error("--verify cannot collect or write a receipt")
        count = verify(root)
    else:
        if args.before is None:
            parser.error(
                "Collection requires a validated --before snapshot and explicit --path values"
            )
        payload = collect(root, args.before.absolute(), args.path)
        publish(root, args.output or root / INLINE_RECEIPT, payload)
        count = len(payload["records"])
    print(f"Verified static Python-fence formatting parity: {count} guides; no execution claim")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
