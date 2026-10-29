"""Lifecycle ownership for child groups started with start_new_session=True."""

from __future__ import annotations

import contextlib
import os
import signal
import subprocess


def cleanup_process_group(process: subprocess.Popen, *, grace_seconds: float = 1) -> None:
    """Retire all descendants even when their direct parent has already exited."""
    try:
        os.killpg(process.pid, signal.SIGTERM)
    except ProcessLookupError:
        if process.poll() is None:
            process.wait()
    else:
        # Waiting on an exited direct child returns immediately. SIGKILL must
        # still reach orphaned descendants that ignored the preceding SIGTERM.
        with contextlib.suppress(subprocess.TimeoutExpired):
            process.wait(timeout=grace_seconds)
        with contextlib.suppress(ProcessLookupError):
            os.killpg(process.pid, signal.SIGKILL)
        process.wait()
