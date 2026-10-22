"""Restore the host loader environment when a frozen app launches external tools.

This module changes loader state only. Callers still own validation and
sanitization of connection variables and other application configuration.
"""

from __future__ import annotations

import contextlib
import os
import sys
from collections.abc import Iterator, Mapping
from pathlib import Path


def external_program_environment(
    base: Mapping[str, str] | None = None,
) -> dict[str, str]:
    """Restore a frozen app's external-program library environment in a copy."""

    environment = dict(os.environ if base is None else base)
    if getattr(sys, "frozen", False):
        for name in ("LD_LIBRARY_PATH", "LIBPATH", "DYLD_LIBRARY_PATH"):
            original = environment.get(f"{name}_ORIG")
            if original is None:
                environment.pop(name, None)
            else:
                environment[name] = original
        for name in tuple(environment):
            if name.startswith("_PYI_") or name == "_MEIPASS2":
                environment.pop(name, None)
        bundle = str(getattr(sys, "_MEIPASS", ""))
        if bundle:
            environment["PATH"] = os.pathsep.join(
                part
                for part in environment.get("PATH", "").split(os.pathsep)
                if part and not Path(part).is_relative_to(bundle)
            )
    return environment


@contextlib.contextmanager
def external_dll_directory() -> Iterator[None]:
    """Undo Windows' frozen-process DLL search path only while spawning a child."""

    if not (os.name == "nt" and getattr(sys, "frozen", False)):
        yield
        return
    import ctypes

    windows_library = getattr(ctypes, "WinDLL")  # noqa: B009
    kernel = windows_library("kernel32", use_last_error=True)
    kernel.GetDllDirectoryW.argtypes = [ctypes.c_ulong, ctypes.c_wchar_p]
    kernel.GetDllDirectoryW.restype = ctypes.c_ulong
    kernel.SetDllDirectoryW.argtypes = [ctypes.c_wchar_p]
    length = kernel.GetDllDirectoryW(0, None)
    previous = ctypes.create_unicode_buffer(length + 1)
    kernel.GetDllDirectoryW(len(previous), previous)
    if not kernel.SetDllDirectoryW(None):
        raise OSError("Could not prepare the external backend DLL search path.")
    try:
        yield
    finally:
        kernel.SetDllDirectoryW(previous.value or None)
