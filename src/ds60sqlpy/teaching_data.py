"""Read fixed reviewed course fixtures, including original offline teaching tables.

This adapter locates course assets rather than deriving them from a copied pad's
filename. It imports only the standard library until a DataFrame is requested.
No API accepts a caller-controlled file path or downloads a dataset.
"""

from __future__ import annotations

import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import pandas as pd  # type: ignore[import-untyped]

_FIXTURES = {
    "professional-sales": "python/professional/fixtures/data/sales.csv",
    "experiment-outcomes": "python/professional/fixtures/data/experiment_outcomes.csv",
    "beginner-orders": "python/professional/fixtures/data/beginner_orders.csv",
    "tiny-package-project": "python/professional/fixtures/tiny_package/pyproject.toml",
    "restaurant-bills": "python/fixtures/restaurant-bills.csv",
    "passenger-outcomes": "python/fixtures/passenger-outcomes.csv",
    "bird-measurements": "python/fixtures/bird-measurements.csv",
}
_COLUMNS = {
    "bird-measurements": (
        "species",
        "island",
        "bill_length_mm",
        "bill_depth_mm",
        "flipper_length_mm",
        "body_mass_g",
        "sex",
    ),
    "restaurant-bills": ("total_bill", "tip", "sex", "smoker", "day", "time", "size"),
    "passenger-outcomes": (
        "survived",
        "pclass",
        "sex",
        "age",
        "sibsp",
        "parch",
        "fare",
        "embarked",
        "class",
        "who",
        "adult_male",
        "deck",
        "embark_town",
        "alive",
        "alone",
    ),
}
MAX_FIXTURE_BYTES = 256_000


def _course_root() -> Path:
    configured = os.environ.get("DS60_REPO_ROOT")
    if configured:
        candidates = [Path(configured)]
    else:
        current = Path.cwd()
        candidates = [current, *current.parents]
        # The thin Core worker sanitizes environment flags; its inherited
        # public course source has this fixed path and the same root contract.
        candidates.append(Path("/opt/course"))
    for candidate in candidates:
        if candidate.is_symlink():
            continue
        root = candidate.resolve()
        if (
            (root / "pyproject.toml").is_file()
            and (root / "python/ds-60day").is_dir()
            and (root / "sql/postgres-60day").is_dir()
        ):
            return root
    raise FileNotFoundError(
        "Prepared course assets are unavailable. Use the classroom image, run from "
        "the repository, or set DS60_REPO_ROOT to a reviewed course checkout."
    )


def _course_file(relative: str) -> Path:
    root = _course_root()
    parts = PurePosixPath(relative)
    if parts.is_absolute() or ".." in parts.parts:
        raise ValueError("Course fixtures require fixed repository-relative paths")
    cursor = root
    for part in parts.parts:
        if part not in {entry.name for entry in cursor.iterdir()}:
            raise FileNotFoundError("A required reviewed teaching fixture is unavailable")
        cursor = cursor / part
        if cursor.is_symlink():
            raise ValueError("Teaching fixtures cannot traverse symbolic links")
    if not cursor.is_file() or not cursor.resolve().is_relative_to(root):
        raise ValueError("Teaching fixture must be a regular file within the course")
    return cursor


def teaching_fixture(name: str) -> Path:
    """Resolve one named authored fixture without following a learner pad location."""
    if not isinstance(name, str) or name not in _FIXTURES:
        raise ValueError("Choose a registered teaching fixture name")
    return _course_file(_FIXTURES[name])


def load_teaching_frame(name: str) -> pd.DataFrame:
    """Return a fresh typed synthetic table from checked-in, digest-checked CSV.

    These original fixtures are not Seaborn samples or historical observations.
    Their values support bounded programming examples, not population inference.
    """
    if not isinstance(name, str) or name not in _COLUMNS:
        raise ValueError("Choose restaurant-bills, passenger-outcomes or bird-measurements")
    import pandas as pd

    manifest_path = _course_file("python/fixtures/manifest.json")
    if manifest_path.stat().st_size > 4096:
        raise ValueError("Teaching fixture manifest exceeds its limit")
    manifest = json.loads(manifest_path.read_text("utf-8"))
    if (
        not isinstance(manifest, dict)
        or set(manifest) != {"schema_version", "datasets"}
        or type(manifest["schema_version"]) is not int
        or manifest["schema_version"] != 1
        or not isinstance(manifest["datasets"], dict)
    ):
        raise ValueError("Invalid teaching fixture manifest")
    entry = manifest["datasets"].get(name)
    if (
        not isinstance(entry, dict)
        or set(entry) != {"kind", "rows", "sha256"}
        or entry["kind"] != "synthetic"
        or type(entry["rows"]) is not int
        or not 1 <= entry["rows"] <= 1000
        or not isinstance(entry["sha256"], str)
    ):
        raise ValueError("Invalid synthetic teaching dataset metadata")
    path = teaching_fixture(name)
    with path.open("rb") as stream:
        content = stream.read(MAX_FIXTURE_BYTES + 1)
    if len(content) > MAX_FIXTURE_BYTES or hashlib.sha256(content).hexdigest() != entry["sha256"]:
        raise ValueError("Teaching dataset differs from its reviewed content identity")
    frame = pd.read_csv(io.BytesIO(content))
    if tuple(frame.columns) != _COLUMNS[name] or len(frame) != entry["rows"]:
        raise ValueError("Teaching dataset schema or population differs from its contract")
    if name == "restaurant-bills":
        domains = {
            "day": ["Thur", "Fri", "Sat", "Sun"],
            "time": ["Lunch", "Dinner"],
            "sex": ["Male", "Female"],
            "smoker": ["Yes", "No"],
        }
    elif name == "passenger-outcomes":
        domains = {"class": ["First", "Second", "Third"], "deck": list("ABCDEFG")}
    else:
        domains = {
            "species": ["Adelie", "Chinstrap", "Gentoo"],
            "island": ["Biscoe", "Dream", "Torgersen"],
        }
    for column, categories in domains.items():
        if not frame[column].dropna().isin(categories).all():
            raise ValueError("Teaching dataset contains an undeclared category")
        frame[column] = pd.Categorical(frame[column], categories=categories, ordered=True)
    frame.attrs.update(dataset_id=name, dataset_kind="synthetic", source_sha256=entry["sha256"])
    return frame
