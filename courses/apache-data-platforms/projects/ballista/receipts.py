"""Commit complete receipts without masking the real execution outcome."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import TextIO


def emit_report(report: dict[str, object], destination: Path, stream: TextIO | None = None) -> bool:
    output = sys.stdout if stream is None else stream
    encoded = json.dumps(report, indent=2) + "\n"
    if len(encoded.encode()) > 100_000:
        raise ValueError("Receipt exceeds byte budget")
    temporary = destination.with_suffix(".pending")
    warning = None
    created = False
    try:
        with temporary.open("x") as handle:
            created = True
            handle.write(encoded)
            handle.flush()
            os.fsync(handle.fileno())
        destination.hardlink_to(temporary)
    except OSError as error:
        warning = (
            "Execution outcome is shown, but its receipt was not committed: " + type(error).__name__
        )
    finally:
        if created:
            try:
                temporary.unlink(missing_ok=True)
            except OSError:
                warning = (
                    warning + "; " if warning else ""
                ) + "An owned pending receipt needs inspection"
    if warning is not None:
        shown = report | {"storage_warning": warning}
        output.write(json.dumps(shown, indent=2) + "\n")
        return False
    output.write(encoded)
    return True
