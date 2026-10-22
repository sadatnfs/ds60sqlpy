"""Serialize local learner-state mutations across threads and processes.

Reads need no lock file because writers replace complete JSON files atomically.
A mutation holds a persistent sibling lock file while reading, changing, and
replacing state. Never unlink that lock file: another process may hold its inode.
"""

from __future__ import annotations

import json
import os
import sys
import tempfile
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from threading import Lock, RLock
from typing import Any, BinaryIO

if sys.platform == "win32":
    import msvcrt
else:
    import fcntl

_GUARD = Lock()
_THREAD_LOCKS: dict[Path, RLock] = {}


def _thread_lock(path: Path) -> RLock:
    identity = path.resolve()
    with _GUARD:
        return _THREAD_LOCKS.setdefault(identity, RLock())


def _acquire(stream: BinaryIO) -> None:
    if sys.platform == "win32":
        stream.seek(0, os.SEEK_END)
        if stream.tell() == 0:
            stream.write(b"\0")
            stream.flush()
        stream.seek(0)
        msvcrt.locking(stream.fileno(), msvcrt.LK_LOCK, 1)
    else:
        fcntl.flock(stream.fileno(), fcntl.LOCK_EX)


def _release(stream: BinaryIO) -> None:
    if sys.platform == "win32":
        stream.seek(0)
        msvcrt.locking(stream.fileno(), msvcrt.LK_UNLCK, 1)
    else:
        fcntl.flock(stream.fileno(), fcntl.LOCK_UN)


@contextmanager
def locked_update(path: Path) -> Iterator[None]:
    """Hold a mutation lock through the complete read-modify-replace sequence.

    This context creates the parent and sibling lock only for an explicit
    mutation. Readers must not call it. Locks are advisory and intended for
    local course workspaces; all course writers must participate.
    """
    with _thread_lock(path):
        path.parent.mkdir(parents=True, exist_ok=True)
        lock_path = path.with_name(path.name + ".lock")
        with lock_path.open("a+b") as lock:
            _acquire(lock)
            try:
                yield
            finally:
                _release(lock)


def atomic_json_write(path: Path, payload: dict[str, Any]) -> None:
    """Replace a JSON file with one unique complete temporary file.

    The caller must already hold locked_update when preserving existing state.
    A serialization or replace failure leaves the previous state intact and
    removes only this write's temporary file.
    """
    temporary: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            newline="\n",
            dir=path.parent,
            prefix=f".{path.name}.",
            suffix=".tmp",
            delete=False,
        ) as output:
            temporary = Path(output.name)
            json.dump(payload, output, indent=2, ensure_ascii=False)
            output.write("\n")
            output.flush()
            os.fsync(output.fileno())
        temporary.replace(path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
