"""Patch plotting display only when a learner imports the corresponding library."""

from __future__ import annotations

import importlib.abc
import importlib.machinery
import sys
from collections.abc import Callable
from types import ModuleType
from typing import Any


class _Loader(importlib.abc.Loader):
    def __init__(self, original: Any, patch: Callable[[ModuleType], None]) -> None:
        self.original = original
        self.patch = patch

    def create_module(self, spec: Any) -> Any:
        method = getattr(self.original, "create_module", None)
        return method(spec) if method else None

    def exec_module(self, module: ModuleType) -> None:
        self.original.exec_module(module)
        self.patch(module)

    def __getattr__(self, name: str) -> Any:
        return getattr(self.original, name)


class _Finder(importlib.abc.MetaPathFinder):
    def __init__(self, patches: dict[str, Callable[[ModuleType], None]]) -> None:
        self.patches = patches

    def find_spec(self, fullname: str, path: Any = None, target: Any = None) -> Any:
        if fullname not in self.patches:
            return None
        spec = importlib.machinery.PathFinder.find_spec(fullname, path, target)
        if spec is not None and spec.loader is not None:
            spec.loader = _Loader(spec.loader, self.patches[fullname])
        return spec


def install_display_hooks(
    plotly: Callable[[ModuleType], None], matplotlib: Callable[[ModuleType], None] | None = None
) -> None:
    """Install two exact-name hooks without importing optional plotting packages.

    The fixed callbacks run after the library's own initialization. Ordinary
    numerical or text programs incur no Matplotlib or Plotly import overhead.
    """
    patches = {"plotly.io": plotly}
    if matplotlib is not None:
        patches["matplotlib.pyplot"] = matplotlib
    for name, callback in patches.items():
        if name in sys.modules:
            callback(sys.modules[name])
    sys.meta_path.insert(0, _Finder(patches))
