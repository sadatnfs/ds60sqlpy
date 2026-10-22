"""Container-only identity setup and host-backed learning-data checks."""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path

from ds60sqlpy.sql_notebook import SqlNotebookError, validate_course_database_target
from ds60sqlpy.sql_runner import default_course_database_url

WORKSPACE = Path("/workspace")
GOSU = "/usr/sbin/gosu"


@dataclass(frozen=True, slots=True)
class ContainerSettings:
    uid: int
    gid: int
    port: int
    rootless: bool


def _identifier(environment: Mapping[str, str], name: str, default: int) -> int:
    text = environment.get(name, str(default))
    if not text.isdecimal() or not 0 <= int(text) <= 2**31 - 1:
        raise ValueError(f"{name} must be a nonnegative numeric user/group identifier.")
    return int(text)


def container_settings(
    environment: Mapping[str, str], *, uid_map: str | None = None
) -> ContainerSettings:
    """Validate numeric identity and require actual namespace mapping for UID0."""

    if environment.get("DS60_CONTAINER") != "1":
        raise ValueError("This helper runs only in the DS60 container image.")
    uid = _identifier(environment, "DS60_UID", 1000)
    gid = _identifier(environment, "DS60_GID", 1000)
    port = _identifier(environment, "DS60_LAB_PORT", 8765)
    if not 1 <= port <= 65535:
        raise ValueError("DS60_LAB_PORT must be between 1 and 65535.")
    rootless = environment.get("DS60_ROOTLESS") == "1"
    if uid == 0:
        if uid_map is None:
            try:
                uid_map = Path("/proc/self/uid_map").read_text(encoding="utf-8")
            except OSError as exc:
                raise ValueError("Cannot verify the requested rootless user mapping.") from exc
        try:
            inside, outside, length = map(int, uid_map.splitlines()[0].split())
        except (ValueError, IndexError) as exc:
            raise ValueError("Cannot verify the requested rootless user mapping.") from exc
        if not rootless or inside != 0 or outside == 0 or length < 1:
            raise ValueError("UID 0 requires a verified rootless engine and DS60_ROOTLESS=1.")
    if environment.get("DS60_COURSE_USER", "admin") not in {"admin", "ds60"}:
        raise ValueError("DS60_COURSE_USER must be admin or the explicit legacy ds60 login.")
    return ContainerSettings(uid, gid, port, rootless)


def prepare_workspace_root(workspace: Path, settings: ContainerSettings) -> None:
    """Change only the ephemeral workspace root, never the mounted learner tree."""

    if workspace.is_symlink():
        raise ValueError("The container workspace root must not be a symbolic link.")
    get_uid = getattr(os, "geteuid", None)
    chown = getattr(os, "chown", None)
    if get_uid is None or chown is None:
        raise ValueError("The image requires Linux-container user/group support.")
    if get_uid() != 0:
        raise ValueError("Keep the image's default entrypoint so it can prepare /workspace.")
    workspace.mkdir(parents=True, exist_ok=True)
    status = workspace.stat()
    if (status.st_uid, status.st_gid) != (settings.uid, settings.gid):
        chown(workspace, settings.uid, settings.gid)


def learning_environment(
    workspace: Path, environment: Mapping[str, str], settings: ContainerSettings
) -> dict[str, str]:
    """Check the host bind as the application user, preserving existing content."""

    result = dict(environment)
    target = result.get("DS60_LAB_DATABASE_URL") or default_course_database_url(result)
    try:
        result["DS60_DATABASE_URL"] = validate_course_database_target(target)
    except SqlNotebookError as exc:
        raise ValueError(str(exc)) from exc
    learning = workspace / ".learning"
    if not learning.is_dir():
        raise ValueError(
            "Mount a host learning directory at /workspace/.learning. "
            "Use the host launcher to create it before starting Compose."
        )
    try:
        with tempfile.NamedTemporaryFile(prefix=".write-check-", dir=learning):
            pass
        home = learning / "home"
        if home.is_symlink() or not home.resolve().is_relative_to(learning.resolve()):
            raise ValueError("The learning home must remain inside the mounted learning directory.")
        home.mkdir(mode=0o700, exist_ok=True)
    except OSError as exc:
        raise ValueError(
            "The host learning directory is not writable by the application identity. "
            "Start with the host launcher or set DS60_UID/DS60_GID to your host user. "
            "Existing progress was not changed or recursively chowned."
        ) from exc
    result.update({"HOME": str(home), "XDG_CACHE_HOME": str(home / ".cache")})
    # Host DS60_DATABASE_URL values are deliberately not a Compose input. Only
    # this separately named advanced override can replace the internal target.
    result["DS60_LAB_PORT"] = str(settings.port)
    return result


def entrypoint() -> int:
    """Prepare a single ephemeral directory, then replace root with gosu."""

    try:
        settings = container_settings(os.environ)
        prepare_workspace_root(WORKSPACE, settings)
        command = sys.argv[1:] or [sys.executable, "/opt/course/docker/start_lab.py"]
        os.execv(GOSU, [GOSU, f"{settings.uid}:{settings.gid}", *command])
    except (OSError, ValueError) as exc:
        print(f"Could not prepare DS60 container: {exc}", file=sys.stderr)
        return 2


def warm_matplotlib(workspace: Path) -> bool:
    """Warm trusted Agg/font initialization after dropping the container user."""

    from ds60sqlpy.execution import matplotlib_cache_environment

    environment = {**os.environ, **matplotlib_cache_environment(workspace)}
    code = (
        "import importlib.util\n"
        "if importlib.util.find_spec('matplotlib') is not None:\n"
        " import matplotlib; matplotlib.use('Agg')\n"
        " from matplotlib import font_manager\n"
        " import matplotlib.pyplot as plt\n"
        " figure = plt.figure(); figure.canvas.draw(); plt.close(figure)\n"
    )
    try:
        result = subprocess.run(
            [sys.executable, "-I", "-c", code],
            env=environment,
            stdin=subprocess.DEVNULL,
            capture_output=True,
            timeout=30,
            check=False,
        )
        if result.returncode == 0:
            return True
    except (OSError, subprocess.TimeoutExpired):
        pass
    print(
        "Warning: Matplotlib startup cache did not finish within the startup check. "
        "Python and SQL remain available; a first plot may reach the coding-pad time limit. "
        "See the plotting guidance in docs/offline-app.md.",
        file=sys.stderr,
    )
    return False


def start_lab() -> int:
    """Run the app after identity drop, storing durable work only in the bind."""

    try:
        settings = container_settings(os.environ)
        get_uid = getattr(os, "geteuid", None)
        if get_uid is None or get_uid() != settings.uid:
            raise ValueError("The app must run through the configured gosu identity drop.")
        os.environ.update(learning_environment(WORKSPACE, os.environ, settings))
        warm_matplotlib(WORKSPACE)
        from ds60sqlpy.desktop import main

        return main(
            [
                "--repo",
                "/opt/course",
                "--workspace",
                str(WORKSPACE),
                "--container",
                "--port",
                str(settings.port),
                "--no-browser",
            ]
        )
    except (OSError, ValueError) as exc:
        print(f"Could not start DS60 container: {exc}", file=sys.stderr)
        return 2
