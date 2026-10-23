#!/usr/bin/env python3
"""Initialize Docker-owned classroom volumes without exposing or rotating secrets."""

from __future__ import annotations

import os
import re
import secrets
import stat
import sys
import uuid
from pathlib import Path


class InitializationRefusal(ValueError):
    """Existing storage is retained for explicit review instead of overwritten."""


def identifier(value: str) -> int:
    if not re.fullmatch(r"[1-9][0-9]{0,9}", value):
        raise InitializationRefusal("Use a nonzero numeric classroom UID/GID.")
    result = int(value)
    if result > 2**31 - 1 or result in (65533, 65534):
        raise InitializationRefusal("The classroom identity cannot be a worker child identity.")
    return result


def _directory(path: Path) -> None:
    if not path.is_absolute():
        raise InitializationRefusal("Classroom volume targets must be absolute.")
    for component in (path, *path.parents):
        try:
            information = component.lstat()
        except FileNotFoundError:
            continue
        if stat.S_ISLNK(information.st_mode) or getattr(information, "st_reparse_tag", 0) in {
            0xA0000003,
            0xA000000C,
        }:
            raise InitializationRefusal(
                "Classroom volume targets cannot follow links or junctions."
            )
        if not stat.S_ISDIR(information.st_mode):
            raise InitializationRefusal("Classroom volume targets must be directories.")
    path.mkdir(mode=0o700, parents=True, exist_ok=True)


def _token(path: Path, uid: int, gid: int) -> bytes:
    information = path.lstat()
    if (
        not stat.S_ISREG(information.st_mode)
        or information.st_nlink != 1
        or stat.S_IMODE(information.st_mode) != 0o400
        or (information.st_uid, information.st_gid) != (uid, gid)
        or not 32 <= information.st_size <= 512
    ):
        raise InitializationRefusal(
            "Existing classroom token has invalid ownership or permissions; it was preserved."
        )
    value = path.read_bytes()
    if not 32 <= len(value) <= 512 or any(byte < 33 or byte > 126 for byte in value):
        raise InitializationRefusal("Existing classroom token is malformed; it was preserved.")
    return value


def initialize(runtime: Path, learning: Path, uid: int = 1000, gid: int = 1000) -> bool:
    """Create one stable token and initialize only empty Docker volume roots.

    Existing learner files and directories are never traversed or recursively
    chowned. Return whether this invocation published the token, never its value.
    """
    if type(uid) is not int or type(gid) is not int:
        raise InitializationRefusal("Use integer classroom identities.")
    uid, gid = identifier(str(uid)), identifier(str(gid))
    if any(part.casefold() == ".learning" for part in (*runtime.parts, *runtime.resolve().parts)):
        raise InitializationRefusal("Credentials must remain outside portable learner storage.")
    if runtime.resolve().is_relative_to(learning.resolve()) or learning.resolve().is_relative_to(
        runtime.resolve()
    ):
        raise InitializationRefusal("Credential and learner volumes must be separate.")
    _directory(runtime)
    _directory(learning)
    # flock is image-local standard library support. The shared volume lock
    # serializes concurrent Compose invocations as well as same-process callers.
    import fcntl

    lock_flags = os.O_CREAT | os.O_RDWR | getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(runtime / ".init.lock", lock_flags, 0o600)
    try:
        information = os.fstat(descriptor)
        if (
            not stat.S_ISREG(information.st_mode)
            or stat.S_IMODE(information.st_mode) != 0o600
            or information.st_uid != os.geteuid()
            or information.st_nlink != 1
        ):
            raise InitializationRefusal(
                "The private initializer lock is invalid; it was preserved."
            )
        fcntl.flock(descriptor, fcntl.LOCK_EX)
        try:
            return _initialize_locked(runtime, learning, uid, gid)
        finally:
            fcntl.flock(descriptor, fcntl.LOCK_UN)
    finally:
        os.close(descriptor)


def _initialize_locked(runtime: Path, learning: Path, uid: int, gid: int) -> bool:
    token = runtime / "token"
    contents = {item.name for item in runtime.iterdir()}
    if contents - {"token", ".init.lock"}:
        raise InitializationRefusal("Unexpected private runtime files were preserved for review.")
    created = False
    if "token" in contents:
        information = runtime.stat()
        if stat.S_IMODE(information.st_mode) != 0o700 or (
            information.st_uid,
            information.st_gid,
        ) != (uid, gid):
            raise InitializationRefusal(
                "Existing private runtime directory is not owned and private as expected."
            )
        _token(token, uid, gid)
    else:
        os.chown(runtime, uid, gid)
        runtime.chmod(0o700)
        temporary = runtime / (".token-" + uuid.uuid4().hex)
        flags = os.O_CREAT | os.O_EXCL | os.O_WRONLY | getattr(os, "O_NOFOLLOW", 0)
        descriptor = os.open(temporary, flags, 0o400)
        try:
            with os.fdopen(descriptor, "wb") as output:
                output.write(secrets.token_hex(32).encode("ascii"))
                output.flush()
                os.fchown(output.fileno(), uid, gid)
                os.fsync(output.fileno())
            try:
                # Publish without replacing a token created by another initializer.
                os.link(temporary, token, follow_symlinks=False)
                created = True
            except FileExistsError:
                _token(token, uid, gid)
        finally:
            temporary.unlink(missing_ok=True)
    information = learning.stat()
    if (information.st_uid, information.st_gid) != (uid, gid):
        if any(learning.iterdir()):
            raise InitializationRefusal(
                "Populated learner storage has a different owner; no files were changed."
            )
        os.chown(learning, uid, gid)
        learning.chmod(0o700)
    return created


def main() -> int:
    try:
        if sys.platform != "linux" or os.environ.get("DS60_CONTAINER") != "1" or os.geteuid() != 0:
            raise InitializationRefusal(
                "Run initialization only through the Docker classroom init service."
            )
        uid = identifier(os.environ.get("DS60_UID", "1000"))
        gid = identifier(os.environ.get("DS60_GID", "1000"))
        initialize(Path("/runtime"), Path("/learning"), uid, gid)
        return 0
    except (OSError, ValueError) as error:
        print(f"Classroom volume initialization refused: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
