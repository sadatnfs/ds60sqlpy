"""Isolated import probes for the optional advanced lesson dependencies."""

from __future__ import annotations

import subprocess
import sys
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ImportTarget:
    """One installed distribution and its public import module."""

    group: str
    distribution: str
    module: str


@dataclass(frozen=True, slots=True)
class ImportResult:
    """Result of importing one optional dependency in a fresh process."""

    target: ImportTarget
    returncode: int
    output: str

    @property
    def passed(self) -> bool:
        """Return whether the import process exited successfully."""

        return self.returncode == 0


ADVANCED_IMPORT_TARGETS: tuple[ImportTarget, ...] = (
    ImportTarget("bridge", "psycopg", "psycopg"),
    ImportTarget("bridge", "psycopg-pool", "psycopg_pool"),
    ImportTarget("ml", "imbalanced-learn", "imblearn"),
    ImportTarget("ml", "lightgbm", "lightgbm"),
    ImportTarget("ml", "lime", "lime"),
    ImportTarget("ml", "pmdarima", "pmdarima"),
    ImportTarget("ml", "shap", "shap"),
    ImportTarget("ml", "xgboost", "xgboost"),
    ImportTarget("production", "dask", "dask"),
    ImportTarget("production", "fastapi", "fastapi"),
    ImportTarget("production", "mlflow", "mlflow"),
    ImportTarget("production", "prefect", "prefect"),
    ImportTarget("production", "pydantic", "pydantic"),
    ImportTarget("production", "uvicorn", "uvicorn"),
    ImportTarget("deep-learning", "torch", "torch"),
    ImportTarget("deep-learning", "torchvision", "torchvision"),
    ImportTarget("nlp", "accelerate", "accelerate"),
    ImportTarget("nlp", "datasets", "datasets"),
    ImportTarget("nlp", "evaluate", "evaluate"),
    ImportTarget("nlp", "spacy", "spacy"),
    ImportTarget("nlp", "transformers", "transformers"),
    ImportTarget("geo", "contextily", "contextily"),
    ImportTarget("geo", "geodatasets", "geodatasets"),
    ImportTarget("geo", "geopandas", "geopandas"),
    ImportTarget("geo", "networkx", "networkx"),
)


def build_probe_code(target: ImportTarget) -> str:
    """Build the tiny program used by an isolated import probe."""

    return (
        "from importlib import import_module\n"
        "from importlib.metadata import version\n"
        f"import_module({target.module!r})\n"
        f"print(version({target.distribution!r}))\n"
    )


def probe_import(target: ImportTarget, *, timeout_seconds: int = 120) -> ImportResult:
    """Import one target in a child process without fetching external assets."""

    try:
        completed = subprocess.run(
            [sys.executable, "-c", build_probe_code(target)],
            check=False,
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
        )
    except subprocess.TimeoutExpired as exc:
        output = f"timed out after {timeout_seconds}s"
        if exc.stderr:
            stderr = (
                exc.stderr.decode(errors="replace") if isinstance(exc.stderr, bytes) else exc.stderr
            )
            output = f"{output}: {stderr}"
        return ImportResult(target=target, returncode=124, output=output)

    output = completed.stdout.strip() if completed.returncode == 0 else completed.stderr.strip()
    return ImportResult(
        target=target,
        returncode=completed.returncode,
        output=output,
    )


def validate_target_manifest(
    targets: tuple[ImportTarget, ...] = ADVANCED_IMPORT_TARGETS,
) -> list[str]:
    """Return duplicate or malformed target-manifest errors."""

    errors: list[str] = []
    distributions: set[str] = set()
    modules: set[str] = set()
    for target in targets:
        if not target.group or not target.distribution or not target.module:
            errors.append(f"blank import target field: {target!r}")
        if target.distribution in distributions:
            errors.append(f"duplicate distribution: {target.distribution}")
        if target.module in modules:
            errors.append(f"duplicate module: {target.module}")
        distributions.add(target.distribution)
        modules.add(target.module)
    return errors
