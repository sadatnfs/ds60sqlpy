#!/usr/bin/env python3
"""Import every advanced optional dependency without downloading lesson assets."""

from __future__ import annotations

import argparse

from ds60sqlpy.advanced_imports import (
    ADVANCED_IMPORT_TARGETS,
    probe_import,
    validate_target_manifest,
)


def parse_args() -> argparse.Namespace:
    """Parse command-line options."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--timeout",
        type=int,
        default=120,
        help="Maximum seconds allowed for each isolated import (default: 120).",
    )
    return parser.parse_args()


def main() -> int:
    """Run all probes and return a process status."""

    args = parse_args()
    manifest_errors = validate_target_manifest()
    if manifest_errors:
        for error in manifest_errors:
            print(f"FAIL manifest: {error}")
        return 1

    failures = 0
    for target in ADVANCED_IMPORT_TARGETS:
        result = probe_import(target, timeout_seconds=args.timeout)
        if result.passed:
            print(f"PASS {target.group}: {target.distribution} ({target.module}) {result.output}")
            continue
        failures += 1
        print(
            f"FAIL {target.group}: {target.distribution} "
            f"({target.module}); {result.output or 'no diagnostic output'}"
        )

    print(f"Advanced imports checked: {len(ADVANCED_IMPORT_TARGETS)}; failed: {failures}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
