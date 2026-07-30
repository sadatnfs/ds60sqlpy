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

PROFESSIONAL_LESSON_SPECS: tuple[dict[str, Any], ...] = (
    {
        "id": "sql-found-01",
        "track": "sql",
        "day": -1,
        "title": "Relational Design, DDL, and Integrity Constraints",
        "level": "foundation",
        "phase": "Relational foundations",
        "estimated_minutes": 150,
        "prerequisites": [],
        "lesson_path": "sql/professional/lessons/sql_found_01_relational_design.sql",
        "guide_path": "sql/professional/companion-guides/sql_found_01_relational_design.md",
        "solution_paths": [
            "sql/professional/solutions/sql_found_01_relational_design_solutions.md",
            "sql/professional/solutions/sql_found_01_relational_design_solutions.sql",
        ],
        "dependency_group": "postgres",
        "network": "offline",
    },
    {
        "id": "sql-found-02",
        "track": "sql",
        "day": 0,
        "title": "Versioned Schema Migrations and Safe Evolution",
        "level": "intermediate",
        "phase": "Relational foundations",
        "estimated_minutes": 180,
        "prerequisites": ["sql-found-01"],
        "lesson_path": "sql/professional/lessons/sql_found_02_versioned_migrations.sql",
        "guide_path": "sql/professional/companion-guides/sql_found_02_versioned_migrations.md",
        "solution_paths": [
            "sql/professional/solutions/sql_found_02_versioned_migrations_solutions.md",
            "sql/professional/solutions/sql_found_02_versioned_migrations_solutions.sql",
        ],
        "dependency_group": "postgres",
        "network": "offline",
    },
    {
        "id": "python-pro-01",
        "track": "python",
        "day": 61,
        "title": "Package Engineering and Local Release Workflow",
        "level": "intermediate",
        "phase": "Professional Python engineering",
        "estimated_minutes": 150,
        "prerequisites": ["python-15"],
        "lesson_path": "python/professional/lessons/py_pro_01_package_engineering.py",
        "guide_path": "python/professional/companion-guides/py_pro_01_package_engineering.md",
        "solution_paths": [
            "python/professional/solutions/py_pro_01_package_engineering_solutions.md",
            "python/professional/solutions/py_pro_01_package_engineering_solution.py",
        ],
        "dependency_group": "professional",
        "network": "offline",
    },
    {
        "id": "python-svc-01",
        "track": "python",
        "day": 62,
        "title": "Reliable HTTP Clients and External-Service Boundaries",
        "level": "intermediate",
        "phase": "Professional Python engineering",
        "estimated_minutes": 150,
        "prerequisites": ["python-15"],
        "lesson_path": "python/professional/lessons/py_svc_01_reliable_http_clients.py",
        "guide_path": "python/professional/companion-guides/py_svc_01_reliable_http_clients.md",
        "solution_paths": [
            "python/professional/solutions/py_svc_01_reliable_http_clients_solutions.md",
            "python/professional/solutions/py_svc_01_reliable_http_clients_solution.py",
        ],
        "dependency_group": "professional",
        "network": "offline",
    },
    {
        "id": "python-pro-02",
        "track": "python",
        "day": 63,
        "title": "Concurrency and Parallelism Decision Lab",
        "level": "advanced",
        "phase": "Professional Python engineering",
        "estimated_minutes": 180,
        "prerequisites": ["python-15"],
        "lesson_path": "python/professional/lessons/py_pro_02_concurrency_parallelism.py",
        "guide_path": "python/professional/companion-guides/py_pro_02_concurrency_parallelism.md",
        "solution_paths": [
            "python/professional/solutions/py_pro_02_concurrency_parallelism_solutions.md",
            "python/professional/solutions/py_pro_02_concurrency_parallelism_solution.py",
        ],
        "dependency_group": "professional",
        "network": "offline",
    },
    {
        "id": "python-data-01",
        "track": "python",
        "day": 64,
        "title": "Columnar Data, Arrow, and Embedded Analytical SQL",
        "level": "intermediate",
        "phase": "Professional data engineering",
        "estimated_minutes": 180,
        "prerequisites": ["python-23"],
        "lesson_path": "python/professional/lessons/py_data_01_arrow_duckdb.py",
        "guide_path": "python/professional/companion-guides/py_data_01_arrow_duckdb.md",
        "solution_paths": [
            "python/professional/solutions/py_data_01_arrow_duckdb_solutions.md",
            "python/professional/solutions/py_data_01_arrow_duckdb_solution.py",
        ],
        "dependency_group": "professional",
        "network": "offline",
    },
    {
        "id": "python-test-01",
        "track": "python",
        "day": 65,
        "title": "Test Architecture, Doubles, and Generative Testing",
        "level": "advanced",
        "phase": "Professional Python engineering",
        "estimated_minutes": 180,
        "prerequisites": ["python-10"],
        "lesson_path": "python/professional/lessons/py_test_01_architecture_generative.py",
        "guide_path": "python/professional/companion-guides/py_test_01_architecture_generative.md",
        "solution_paths": [
            "python/professional/solutions/py_test_01_architecture_generative_solutions.md",
            "python/professional/solutions/py_test_01_architecture_generative_solution.py",
        ],
        "dependency_group": "professional",
        "network": "offline",
    },
    {
        "id": "python-lang-01",
        "track": "python",
        "day": 66,
        "title": "Advanced Typing and the Python Data Model",
        "level": "advanced",
        "phase": "Professional Python engineering",
        "estimated_minutes": 180,
        "prerequisites": ["python-12"],
        "lesson_path": "python/professional/lessons/py_lang_01_typing_data_model.py",
        "guide_path": "python/professional/companion-guides/py_lang_01_typing_data_model.md",
        "solution_paths": [
            "python/professional/solutions/py_lang_01_typing_data_model_solutions.md",
            "python/professional/solutions/py_lang_01_typing_data_model_solution.py",
        ],
        "dependency_group": "quality",
        "network": "offline",
    },
    {
        "id": "python-stats-01",
        "track": "python",
        "day": 67,
        "title": "Resampling, Experiments, and Causal Boundaries",
        "level": "advanced",
        "phase": "Advanced statistics and experimentation",
        "estimated_minutes": 210,
        "prerequisites": ["python-32"],
        "lesson_path": "python/professional/lessons/py_stats_01_resampling_experiments.py",
        "guide_path": "python/professional/companion-guides/py_stats_01_resampling_experiments.md",
        "solution_paths": [
            "python/professional/solutions/py_stats_01_resampling_experiments_solutions.md",
            "python/professional/solutions/py_stats_01_resampling_experiments_solution.py",
        ],
        "dependency_group": "data",
        "network": "offline",
    },
    {
        "id": "python-ml-01",
        "track": "python",
        "day": 68,
        "title": "Reproducible Data and Model Delivery",
        "level": "advanced",
        "phase": "Production machine learning",
        "estimated_minutes": 210,
        "prerequisites": ["python-45"],
        "lesson_path": "python/professional/lessons/py_ml_01_reproducible_delivery.py",
        "guide_path": "python/professional/companion-guides/py_ml_01_reproducible_delivery.md",
        "solution_paths": [
            "python/professional/solutions/py_ml_01_reproducible_delivery_solutions.md",
            "python/professional/solutions/py_ml_01_reproducible_delivery_solution.py",
        ],
        "dependency_group": "production",
        "network": "offline",
    },
    {
        "id": "python-svc-02",
        "track": "python",
        "day": 69,
        "title": "Service Hardening and Observability",
        "level": "advanced",
        "phase": "Professional Python engineering",
        "estimated_minutes": 210,
        "prerequisites": ["python-55", "bridge-08", "python-svc-01", "python-ml-01"],
        "lesson_path": "python/professional/lessons/py_svc_02_hardening_observability.py",
        "guide_path": "python/professional/companion-guides/py_svc_02_hardening_observability.md",
        "solution_paths": [
            "python/professional/solutions/py_svc_02_hardening_observability_solutions.md",
            "python/professional/solutions/py_svc_02_hardening_observability_solution.py",
        ],
        "dependency_group": "production",
        "network": "offline",
    },
    {
        "id": "python-perf-01",
        "track": "python",
        "day": 70,
        "title": "Measurement-First Performance Engineering",
        "level": "advanced",
        "phase": "Python specialization",
        "estimated_minutes": 180,
        "prerequisites": ["python-23", "python-pro-02"],
        "lesson_path": "python/professional/lessons/py_perf_01_measurement_optimization.py",
        "guide_path": "python/professional/companion-guides/py_perf_01_measurement_optimization.md",
        "solution_paths": [
            "python/professional/solutions/py_perf_01_measurement_optimization_solutions.md",
            "python/professional/solutions/py_perf_01_measurement_optimization_solution.py",
        ],
        "dependency_group": "data",
        "network": "offline",
    },
    {
        "id": "sql-sec-01",
        "track": "sql",
        "day": 61,
        "title": "Schemas, Roles, Privileges, and Row-Level Security",
        "level": "advanced",
        "phase": "Database security and application safety",
        "estimated_minutes": 180,
        "prerequisites": ["sql-found-02", "sql-39"],
        "lesson_path": "sql/professional/lessons/sql_sec_01_roles_privileges_rls.sql",
        "guide_path": "sql/professional/companion-guides/sql_sec_01_roles_privileges_rls.md",
        "solution_paths": [
            "sql/professional/solutions/sql_sec_01_roles_privileges_rls_solutions.md",
            "sql/professional/solutions/sql_sec_01_roles_privileges_rls_solutions.sql",
        ],
        "dependency_group": "postgres",
        "network": "offline",
    },
    {
        "id": "sql-prog-01",
        "track": "sql",
        "day": 62,
        "title": "Functions, Procedures, and Triggers",
        "level": "advanced",
        "phase": "Database programming",
        "estimated_minutes": 180,
        "prerequisites": ["sql-found-02"],
        "lesson_path": "sql/professional/lessons/sql_prog_01_routines_triggers.sql",
        "guide_path": "sql/professional/companion-guides/sql_prog_01_routines_triggers.md",
        "solution_paths": [
            "sql/professional/solutions/sql_prog_01_routines_triggers_solutions.md",
            "sql/professional/solutions/sql_prog_01_routines_triggers_solutions.sql",
        ],
        "dependency_group": "postgres",
        "network": "offline",
    },
    {
        "id": "sql-types-01",
        "track": "sql",
        "day": 63,
        "title": "PostgreSQL-Native Types and Searchable Documents",
        "level": "advanced",
        "phase": "PostgreSQL data modelling",
        "estimated_minutes": 180,
        "prerequisites": ["sql-29"],
        "lesson_path": "sql/professional/lessons/sql_types_01_native_types_search.sql",
        "guide_path": "sql/professional/companion-guides/sql_types_01_native_types_search.md",
        "solution_paths": [
            "sql/professional/solutions/sql_types_01_native_types_search_solutions.md",
            "sql/professional/solutions/sql_types_01_native_types_search_solutions.sql",
        ],
        "dependency_group": "postgres",
        "network": "offline",
    },
    {
        "id": "sql-ops-01",
        "track": "sql",
        "day": 64,
        "title": "Index Types, Statistics, and Maintenance Lifecycle",
        "level": "advanced",
        "phase": "PostgreSQL operations",
        "estimated_minutes": 210,
        "prerequisites": ["sql-35", "sql-types-01"],
        "lesson_path": "sql/professional/lessons/sql_ops_01_indexes_statistics_maintenance.sql",
        "guide_path": (
            "sql/professional/companion-guides/sql_ops_01_indexes_statistics_maintenance.md"
        ),
        "solution_paths": [
            "sql/professional/solutions/sql_ops_01_indexes_statistics_maintenance_solutions.md",
            "sql/professional/solutions/sql_ops_01_indexes_statistics_maintenance_solutions.sql",
        ],
        "dependency_group": "postgres",
        "network": "offline",
    },
    {
        "id": "sql-test-01",
        "track": "sql",
        "day": 65,
        "title": "SQL Tests, Migration Checks, and Data Contracts",
        "level": "advanced",
        "phase": "Database quality engineering",
        "estimated_minutes": 180,
        "prerequisites": ["sql-found-02", "sql-42"],
        "lesson_path": "sql/professional/lessons/sql_test_01_contracts_migrations.sql",
        "guide_path": "sql/professional/companion-guides/sql_test_01_contracts_migrations.md",
        "solution_paths": [
            "sql/professional/solutions/sql_test_01_contracts_migrations_solutions.md",
            "sql/professional/solutions/sql_test_01_contracts_migrations_solutions.sql",
        ],
        "dependency_group": "postgres",
        "network": "offline",
    },
    {
        "id": "sql-analytics-01",
        "track": "sql",
        "day": 66,
        "title": "Reusable Analytical Query Patterns",
        "level": "advanced",
        "phase": "Advanced analytical SQL",
        "estimated_minutes": 240,
        "prerequisites": ["sql-30", "sql-test-01"],
        "lesson_path": "sql/professional/lessons/sql_analytics_01_query_patterns.sql",
        "guide_path": "sql/professional/companion-guides/sql_analytics_01_query_patterns.md",
        "solution_paths": [
            "sql/professional/solutions/sql_analytics_01_query_patterns_solutions.md",
            "sql/professional/solutions/sql_analytics_01_query_patterns_solutions.sql",
        ],
        "dependency_group": "postgres",
        "network": "offline",
    },
    {
        "id": "sql-ops-02",
        "track": "sql",
        "day": 67,
        "title": "Backup, Restore, and Recovery Rehearsals",
        "level": "advanced",
        "phase": "PostgreSQL operations",
        "estimated_minutes": 240,
        "prerequisites": ["sql-43", "sql-ops-01"],
        "lesson_path": "sql/professional/lessons/sql_ops_02_backup_restore_recovery.sql",
        "guide_path": "sql/professional/companion-guides/sql_ops_02_backup_restore_recovery.md",
        "solution_paths": [
            "sql/professional/solutions/sql_ops_02_backup_restore_recovery_solutions.md",
            "sql/professional/solutions/sql_ops_02_backup_restore_recovery_solutions.sql",
        ],
        "dependency_group": "postgres",
        "network": "optional-container-image",
    },
    {
        "id": "sql-ext-01",
        "track": "sql",
        "day": 68,
        "title": "PostgreSQL Extensions, Spatial Data, and Vectors",
        "level": "advanced",
        "phase": "PostgreSQL specialization",
        "estimated_minutes": 240,
        "prerequisites": ["sql-types-01", "sql-ops-01"],
        "lesson_path": "sql/professional/lessons/sql_ext_01_extensions_spatial_vector.sql",
        "guide_path": "sql/professional/companion-guides/sql_ext_01_extensions_spatial_vector.md",
        "solution_paths": [
            "sql/professional/solutions/sql_ext_01_extensions_spatial_vector_solutions.md",
            "sql/professional/solutions/sql_ext_01_extensions_spatial_vector_solutions.sql",
        ],
        "dependency_group": "postgres",
        "network": "optional-container-image",
    },
    {
        "id": "sql-repl-01",
        "track": "sql",
        "day": 69,
        "title": "Replication, Change Data Capture, and High Availability",
        "level": "advanced",
        "phase": "PostgreSQL specialization",
        "estimated_minutes": 240,
        "prerequisites": ["sql-ops-02", "sql-prog-01", "sql-test-01"],
        "lesson_path": "sql/professional/lessons/sql_repl_01_cdc_high_availability.sql",
        "guide_path": "sql/professional/companion-guides/sql_repl_01_cdc_high_availability.md",
        "solution_paths": [
            "sql/professional/solutions/sql_repl_01_cdc_high_availability_solutions.md",
            "sql/professional/solutions/sql_repl_01_cdc_high_availability_solutions.sql",
        ],
        "dependency_group": "postgres",
        "network": "optional-container-image",
    },
    {
        "id": "sql-temporal-01",
        "track": "sql",
        "day": 70,
        "title": "Temporal and Domain Modelling",
        "level": "advanced",
        "phase": "PostgreSQL specialization",
        "estimated_minutes": 210,
        "prerequisites": [
            "sql-found-01",
            "sql-types-01",
            "sql-prog-01",
            "sql-test-01",
            "sql-39",
        ],
        "lesson_path": "sql/professional/lessons/sql_temporal_01_domain_modelling.sql",
        "guide_path": "sql/professional/companion-guides/sql_temporal_01_domain_modelling.md",
        "solution_paths": [
            "sql/professional/solutions/sql_temporal_01_domain_modelling_solutions.md",
            "sql/professional/solutions/sql_temporal_01_domain_modelling_solutions.sql",
        ],
        "dependency_group": "postgres",
        "network": "offline",
    },
    {
        "id": "bridge-jupyter-01",
        "track": "bridge",
        "day": 9,
        "title": "PostgreSQL in Jupyter with SQL Magics",
        "level": "intermediate",
        "phase": "Interactive Python and PostgreSQL",
        "estimated_minutes": 150,
        "prerequisites": ["python-18", "sql-15", "bridge-03"],
        "lesson_path": ("bridge/professional/notebooks/bridge_jupyter_01_postgresql_magics.ipynb"),
        "guide_path": (
            "bridge/professional/companion-guides/bridge_jupyter_01_postgresql_magics.md"
        ),
        "solution_paths": [
            ("bridge/professional/solutions/bridge_jupyter_01_postgresql_magics_solutions.md"),
            ("bridge/professional/solutions/bridge_jupyter_01_postgresql_magics_solution.ipynb"),
        ],
        "dependency_group": "sql-notebooks",
        "network": "offline",
    },
    {
        "id": "bridge-ops-01",
        "track": "bridge",
        "day": 10,
        "title": "Migration Delivery and Application Observability",
        "level": "advanced",
        "phase": "Professional application and database operations",
        "estimated_minutes": 240,
        "prerequisites": ["bridge-08", "sql-found-02"],
        "lesson_path": "bridge/professional/lessons/bridge_ops_01_migration_observability.py",
        "guide_path": (
            "bridge/professional/companion-guides/bridge_ops_01_migration_observability.md"
        ),
        "solution_paths": [
            ("bridge/professional/solutions/bridge_ops_01_migration_observability_solutions.md"),
            ("bridge/professional/solutions/bridge_ops_01_migration_observability_solution.py"),
        ],
        "dependency_group": "bridge",
        "network": "offline",
    },
    {
        "id": "bridge-ai-01",
        "track": "bridge",
        "day": 11,
        "title": "AI Application Engineering with Deterministic Test Doubles",
        "level": "advanced",
        "phase": "Application specialization",
        "estimated_minutes": 240,
        "prerequisites": ["bridge-08", "python-test-01"],
        "lesson_path": "bridge/professional/lessons/bridge_ai_01_application_engineering.py",
        "guide_path": (
            "bridge/professional/companion-guides/bridge_ai_01_application_engineering.md"
        ),
        "solution_paths": [
            ("bridge/professional/solutions/bridge_ai_01_application_engineering_solutions.md"),
            ("bridge/professional/solutions/bridge_ai_01_application_engineering_solution.py"),
        ],
        "dependency_group": "bridge",
        "network": "offline",
    },
    {
        "id": "bridge-analytics-01",
        "track": "bridge",
        "day": 12,
        "title": "Analytics Engineering, Lineage, and Data Contracts",
        "level": "advanced",
        "phase": "Data engineering specialization",
        "estimated_minutes": 240,
        "prerequisites": ["bridge-05", "python-data-01", "sql-analytics-01"],
        "lesson_path": "bridge/professional/lessons/bridge_analytics_01_local_project.py",
        "guide_path": ("bridge/professional/companion-guides/bridge_analytics_01_local_project.md"),
        "solution_paths": [
            ("bridge/professional/solutions/bridge_analytics_01_local_project_solutions.md"),
            ("bridge/professional/solutions/bridge_analytics_01_local_project_solution.py"),
        ],
        "dependency_group": "professional",
        "network": "offline",
    },
)


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
                "prerequisites": ["sql-found-02"] if day == 1 else [f"sql-{day - 1:02d}"],
                "lesson_path": script.relative_to(root).as_posix(),
                "guide_path": (guide_dir / f"{script.stem}.md").relative_to(root).as_posix(),
                "solution_paths": solution_paths,
                "dependency_group": dependency_group,
                "network": "offline",
                **({"stateful_group": "dwh-project"} if 52 <= day <= 54 else {}),
            }
        )
    return lessons


def _professional_lessons() -> list[dict[str, Any]]:
    """Return explicitly authored professional and specialization modules."""

    return [dict(spec) for spec in PROFESSIONAL_LESSON_SPECS]


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
    lessons = [
        *_python_lessons(root),
        *_sql_lessons(root),
        *_bridge_lessons(root),
        *_professional_lessons(),
    ]
    return {
        "schema_version": 1,
        "generated_from": "course artifact filenames and professional lesson specifications",
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
