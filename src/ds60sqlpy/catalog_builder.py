"""Build the checked-in curriculum catalog from the course artifact names."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from ds60sqlpy.catalog import TRACK_ORDER, find_repo_root

DAY_PATTERN = re.compile(r"^day(?P<day>\d{2})_(?P<slug>.+)$")
SEABORN_CACHE_DAYS = {17, 18, 19, 22, 24, 25, 26, 28, 45, 51, 56}
MODEL_DOWNLOAD_DAYS = {48, 49}
GEO_DOWNLOAD_DAYS = {27}
PYTHON_DEPENDENCY_OVERRIDES = {
    27: "geo",
    31: "data",
    32: "data",
    33: "data",
    34: "data",
    35: "data",
    36: "data",
    37: "data",
    38: "data",
    40: "data",
    42: "data",
    44: "production",
    45: "data",
    46: "deep-learning",
    47: "deep-learning",
    48: "deep-learning",
    49: "nlp",
    50: "ml",
    51: "data",
    52: "production",
    53: "production",
    54: "data",
    55: "production",
    56: "production",
    57: "data",
    58: "data",
}


def _title(slug: str) -> str:
    replacements = {
        "api": "API",
        "apis": "APIs",
        "bi": "BI",
        "cli": "CLI",
        "cnn": "CNN",
        "ctes": "CTEs",
        "cv": "CV",
        "db": "DB",
        "dml": "DML",
        "dwh": "DWH",
        "eda": "EDA",
        "etl": "ETL",
        "fastapi": "FastAPI",
        "hf": "Hugging Face",
        "json": "JSON",
        "kmeans": "K-means",
        "lightgbm": "LightGBM",
        "ml": "ML",
        "mlflow": "MLflow",
        "mlops": "MLOps",
        "nlp": "NLP",
        "numpy": "NumPy",
        "nn": "NN",
        "oop": "OOP",
        "pandas": "pandas",
        "pca": "PCA",
        "pdp": "PDP",
        "postgres": "PostgreSQL",
        "pytorch": "PyTorch",
        "repl": "REPL",
        "rls": "RLS",
        "scd": "SCD",
        "shap": "SHAP",
        "searchcv": "SearchCV",
        "sklearn": "scikit-learn",
        "sql": "SQL",
        "xml": "XML",
        "xgboost": "XGBoost",
        "viz": "Visualization",
    }
    words = []
    for index, word in enumerate(slug.split("_")):
        if index > 0 and word in {"and", "or", "to", "with"}:
            words.append(word)
        else:
            words.append(replacements.get(word, word.capitalize()))
    return " ".join(words)


def _phase(track: str, day: int) -> tuple[str, str, str, int]:
    if track == "bridge":
        level = "intermediate" if day <= 5 else "advanced"
        minutes = 105 if day <= 5 else 120
        return ("Python and PostgreSQL engineering", level, "bridge", minutes)

    if track == "python":
        if day <= 15:
            return ("Python foundations", "foundation", "core", 75)
        if day <= 30:
            return ("Data analysis and visualization", "intermediate", "data", 90)
        if day <= 45:
            return ("Statistics and machine learning", "intermediate", "ml", 105)
        return ("Production, advanced topics, and capstone", "advanced", "advanced", 120)

    if day <= 15:
        return ("SQL foundations and query building", "foundation", "postgres", 75)
    if day <= 30:
        return ("Windows, CTEs, and advanced querying", "intermediate", "postgres", 90)
    if day <= 45:
        return ("Performance, transactions, and operations", "advanced", "postgres", 105)
    return ("Applied analytics and capstones", "advanced", "postgres", 120)


def _python_lessons(root: Path) -> list[dict[str, Any]]:
    notebook_dir = root / "python" / "ds-60day" / "notebooks"
    guide_dir = root / "python" / "ds-60day" / "companion-guides"
    solution_dir = root / "python" / "ds-60day" / "solutions"
    lessons: list[dict[str, Any]] = []

    for notebook in sorted(notebook_dir.glob("day*.ipynb")):
        match = DAY_PATTERN.match(notebook.stem)
        if match is None:
            continue
        day = int(match.group("day"))
        slug = match.group("slug")
        phase, level, dependency_group, minutes = _phase("python", day)
        dependency_group = PYTHON_DEPENDENCY_OVERRIDES.get(day, dependency_group)
        guide = guide_dir / f"{notebook.stem}.md"
        solution_home = solution_dir / notebook.stem
        solution_paths = [
            path.relative_to(root).as_posix()
            for path in (
                solution_home / f"day{day:02d}_solutions.md",
                solution_home / f"day{day:02d}_solutions.ipynb",
            )
            if path.is_file()
        ]
        if day in MODEL_DOWNLOAD_DAYS:
            network = "optional-model-download"
        elif day in GEO_DOWNLOAD_DAYS:
            network = "optional-map-download"
        elif day in SEABORN_CACHE_DAYS:
            network = "first-run-seaborn-cache"
        else:
            network = "offline"

        lessons.append(
            {
                "id": f"python-{day:02d}",
                "track": "python",
                "day": day,
                "title": _title(slug),
                "level": level,
                "phase": phase,
                "estimated_minutes": minutes,
                "prerequisites": [] if day == 1 else [f"python-{day - 1:02d}"],
                "lesson_path": notebook.relative_to(root).as_posix(),
                "guide_path": guide.relative_to(root).as_posix(),
                "solution_paths": solution_paths,
                "dependency_group": dependency_group,
                "network": network,
            }
        )
    return lessons


def _sql_lessons(root: Path) -> list[dict[str, Any]]:
    lesson_dir = root / "sql" / "postgres-60day"
    guide_dir = lesson_dir / "companion-guides"
    solution_dir = lesson_dir / "solutions"
    lessons: list[dict[str, Any]] = []

    for script in sorted(lesson_dir.glob("day*.sql")):
        match = DAY_PATTERN.match(script.stem)
        if match is None:
            continue
        day = int(match.group("day"))
        slug = match.group("slug")
        phase, level, dependency_group, minutes = _phase("sql", day)
        solution_paths = [
            path.relative_to(root).as_posix()
            for path in (
                solution_dir / f"day{day:02d}_solutions.md",
                solution_dir / f"day{day:02d}_solutions.sql",
            )
            if path.is_file()
        ]
        lessons.append(
            {
                "id": f"sql-{day:02d}",
                "track": "sql",
                "day": day,
                "title": _title(slug),
                "level": level,
                "phase": phase,
                "estimated_minutes": minutes,
                "prerequisites": [] if day == 1 else [f"sql-{day - 1:02d}"],
                "lesson_path": script.relative_to(root).as_posix(),
                "guide_path": (guide_dir / f"{script.stem}.md").relative_to(root).as_posix(),
                "solution_paths": solution_paths,
                "dependency_group": dependency_group,
                "network": "offline",
                **({"stateful_group": "dwh-project"} if 52 <= day <= 54 else {}),
            }
        )
    return lessons


def _bridge_lessons(root: Path) -> list[dict[str, Any]]:
    lesson_dir = root / "bridge" / "lessons"
    guide_dir = root / "bridge" / "companion-guides"
    solution_dir = root / "bridge" / "solutions"
    lessons: list[dict[str, Any]] = []

    for script in sorted(lesson_dir.glob("day*.py")):
        match = DAY_PATTERN.match(script.stem)
        if match is None:
            continue
        day = int(match.group("day"))
        slug = match.group("slug")
        phase, level, dependency_group, minutes = _phase("bridge", day)
        solution_paths = [
            path.relative_to(root).as_posix()
            for path in (
                solution_dir / f"day{day:02d}_solutions.md",
                solution_dir / f"day{day:02d}_solution.py",
            )
            if path.is_file()
        ]
        prerequisites = ["python-15", "sql-15"] if day == 1 else [f"bridge-{day - 1:02d}"]
        lessons.append(
            {
                "id": f"bridge-{day:02d}",
                "track": "bridge",
                "day": day,
                "title": _title(slug),
                "level": level,
                "phase": phase,
                "estimated_minutes": minutes,
                "prerequisites": prerequisites,
                "lesson_path": script.relative_to(root).as_posix(),
                "guide_path": (guide_dir / f"{script.stem}.md").relative_to(root).as_posix(),
                "solution_paths": solution_paths,
                "dependency_group": dependency_group,
                "network": "offline",
            }
        )
    return lessons


def build_catalog(repo_root: Path | None = None) -> dict[str, Any]:
    """Return the complete catalog payload."""

    root = find_repo_root(repo_root)
    lessons = [*_python_lessons(root), *_sql_lessons(root), *_bridge_lessons(root)]
    return {
        "schema_version": 1,
        "generated_from": "course artifact filenames",
        "tracks": {
            "python": {
                "title": "Python and data science",
                "plan": "python/PYTHON_TRAINING.md",
            },
            "sql": {
                "title": "PostgreSQL",
                "plan": "sql/ADVANCED_SQL_60DAY_PLAN.md",
            },
            "bridge": {
                "title": "Python and PostgreSQL engineering",
                "plan": "bridge/README.md",
            },
        },
        "lessons": sorted(
            lessons,
            key=lambda item: (TRACK_ORDER[item["track"]], item["day"]),
        ),
    }


def write_catalog(repo_root: Path | None = None) -> Path:
    """Regenerate ``curriculum/catalog.json`` deterministically."""

    root = find_repo_root(repo_root)
    path = root / "curriculum" / "catalog.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = build_catalog(root)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path
