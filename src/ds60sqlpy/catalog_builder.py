"""Build the checked-in curriculum catalog from the course artifact names."""

from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path
from typing import Any

from ds60sqlpy.catalog import catalog_order_key, find_repo_root
from ds60sqlpy.curriculum_framework import infer_runner, load_extensions
from ds60sqlpy.study_plan import LEARNING_PATHS

DAY_PATTERN = re.compile(r"^day(?P<day>\d{2})_(?P<slug>.+)$")
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
    58: "quality",
}

PROFESSIONAL_LESSON_SPECS: tuple[dict[str, Any], ...] = (
    {
        "id": "sql-found-01",
        "track": "sql",
        "day": -1,
        "title": "Relational Design, DDL, and Integrity Constraints",
        "level": "intermediate",
        "phase": "Relational engineering",
        "estimated_minutes": 150,
        "prerequisites": ["sql-15"],
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
        "phase": "Relational engineering",
        "estimated_minutes": 180,
        "prerequisites": ["sql-found-01", "sql-39"],
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


# New learning gaps have stable IDs; historical days keep their identity.
PROFESSIONAL_LESSON_SPECS += (
    {
        "id": "python-foundations-01",
        "title": "Read a Program, Trace Its State, and Predict Its Output",
        "level": "foundation",
        "prerequisites": ["python-01"],
        "estimated_minutes": 120,
        "track": "python",
        "day": -10,
        "phase": "Python foundations and confidence",
        "dependency_group": "core",
        "network": "offline",
        "lesson_path": "python/professional/lessons/py_foundations_01_read_trace_state.py",
        "guide_path": "python/professional/companion-guides/py_foundations_01_read_trace_state.md",
        "solution_paths": [
            "python/professional/solutions/py_foundations_01_read_trace_state_solutions.md",
            "python/professional/solutions/py_foundations_01_read_trace_state_solution.py",
        ],
    },
    {
        "id": "python-foundations-02",
        "title": "Debug from Evidence Instead of Guessing",
        "level": "foundation",
        "prerequisites": ["python-03"],
        "estimated_minutes": 150,
        "track": "python",
        "day": -9,
        "phase": "Python foundations and confidence",
        "dependency_group": "core",
        "network": "offline",
        "lesson_path": "python/professional/lessons/py_foundations_02_debug_evidence.py",
        "guide_path": "python/professional/companion-guides/py_foundations_02_debug_evidence.md",
        "solution_paths": [
            "python/professional/solutions/py_foundations_02_debug_evidence_solutions.md",
            "python/professional/solutions/py_foundations_02_debug_evidence_solution.py",
        ],
    },
    {
        "id": "python-foundations-03",
        "title": "Turn Messy Text into Trustworthy Records",
        "level": "foundation",
        "prerequisites": ["python-08"],
        "estimated_minutes": 180,
        "track": "python",
        "day": -8,
        "phase": "Python foundations and confidence",
        "dependency_group": "core",
        "network": "offline",
        "lesson_path": "python/professional/lessons/py_foundations_03_clean_records.py",
        "guide_path": "python/professional/companion-guides/py_foundations_03_clean_records.md",
        "solution_paths": [
            "python/professional/solutions/py_foundations_03_clean_records_solutions.md",
            "python/professional/solutions/py_foundations_03_clean_records_solution.py",
        ],
    },
    {
        "id": "python-foundations-04",
        "title": "Build Your First Auditable Data Investigation",
        "level": "foundation",
        "prerequisites": ["python-foundations-03", "python-10"],
        "estimated_minutes": 210,
        "track": "python",
        "day": -7,
        "phase": "Python foundations and confidence",
        "dependency_group": "core",
        "network": "offline",
        "lesson_path": "python/professional/lessons/py_foundations_04_first_investigation.py",
        "guide_path": (
            "python/professional/companion-guides/py_foundations_04_first_investigation.md"
        ),
        "solution_paths": [
            "python/professional/solutions/py_foundations_04_first_investigation_solutions.md",
            "python/professional/solutions/py_foundations_04_first_investigation_solution.py",
        ],
    },
    {
        "id": "python-data-02",
        "title": "Exact Values, Unicode Identity, and Calendar Boundaries",
        "level": "advanced",
        "prerequisites": ["python-21", "python-29"],
        "estimated_minutes": 240,
        "track": "python",
        "day": 71,
        "phase": "Professional data engineering",
        "dependency_group": "core",
        "network": "offline",
        "lesson_path": "python/professional/lessons/py_data_02_exact_values_time_text.py",
        "guide_path": "python/professional/companion-guides/py_data_02_exact_values_time_text.md",
        "solution_paths": [
            "python/professional/solutions/py_data_02_exact_values_time_text_solutions.md",
            "python/professional/solutions/py_data_02_exact_values_time_text_solution.py",
        ],
    },
    {
        "id": "python-ml-02",
        "title": "Leakage-Resistant Evaluation Across Groups and Time",
        "level": "advanced",
        "prerequisites": ["python-35", "python-data-02"],
        "estimated_minutes": 270,
        "track": "python",
        "day": 72,
        "phase": "Professional model evaluation",
        "dependency_group": "core",
        "network": "offline",
        "lesson_path": "python/professional/lessons/py_ml_02_group_time_evaluation.py",
        "guide_path": "python/professional/companion-guides/py_ml_02_group_time_evaluation.md",
        "solution_paths": [
            "python/professional/solutions/py_ml_02_group_time_evaluation_solutions.md",
            "python/professional/solutions/py_ml_02_group_time_evaluation_solution.py",
        ],
    },
    {
        "id": "python-pro-03",
        "title": "Restartable File Pipelines and Honest Durability Guarantees",
        "level": "advanced",
        "prerequisites": ["python-23", "python-10"],
        "estimated_minutes": 270,
        "track": "python",
        "day": 73,
        "phase": "Professional Python engineering",
        "dependency_group": "core",
        "network": "offline",
        "lesson_path": "python/professional/lessons/py_pro_03_restartable_file_pipeline.py",
        "guide_path": "python/professional/companion-guides/py_pro_03_restartable_file_pipeline.md",
        "solution_paths": [
            "python/professional/solutions/py_pro_03_restartable_file_pipeline_solutions.md",
            "python/professional/solutions/py_pro_03_restartable_file_pipeline_solution.py",
        ],
    },
    {
        "id": "sql-start-01",
        "track": "sql",
        "day": -4,
        "title": "Reading Tables and Result Grain",
        "level": "foundation",
        "phase": "Beginner practice",
        "estimated_minutes": 90,
        "prerequisites": [],
        "lesson_path": "sql/professional/lessons/sql_start_01_tables_and_grain.sql",
        "guide_path": "sql/professional/companion-guides/sql_start_01_tables_and_grain.md",
        "solution_paths": [
            "sql/professional/solutions/sql_start_01_tables_and_grain_solutions.md",
            "sql/professional/solutions/sql_start_01_tables_and_grain_solutions.sql",
        ],
        "dependency_group": "postgres",
        "network": "offline",
    },
    {
        "id": "sql-start-02",
        "track": "sql",
        "day": -3,
        "title": "Values NULL and Deterministic Order",
        "level": "foundation",
        "phase": "Beginner practice",
        "estimated_minutes": 90,
        "prerequisites": ["sql-start-01"],
        "lesson_path": "sql/professional/lessons/sql_start_02_values_null_order.sql",
        "guide_path": "sql/professional/companion-guides/sql_start_02_values_null_order.md",
        "solution_paths": [
            "sql/professional/solutions/sql_start_02_values_null_order_solutions.md",
            "sql/professional/solutions/sql_start_02_values_null_order_solutions.sql",
        ],
        "dependency_group": "postgres",
        "network": "offline",
    },
    {
        "id": "sql-start-03",
        "track": "sql",
        "day": -2,
        "title": "Query Construction and Debugging",
        "level": "foundation",
        "phase": "Beginner practice",
        "estimated_minutes": 90,
        "prerequisites": ["sql-start-02"],
        "lesson_path": "sql/professional/lessons/sql_start_03_query_debugging.sql",
        "guide_path": "sql/professional/companion-guides/sql_start_03_query_debugging.md",
        "solution_paths": [
            "sql/professional/solutions/sql_start_03_query_debugging_solutions.md",
            "sql/professional/solutions/sql_start_03_query_debugging_solutions.sql",
        ],
        "dependency_group": "postgres",
        "network": "offline",
    },
    {
        "id": "sql-quality-01",
        "track": "sql",
        "day": 71,
        "title": "Bag Reconciliation and Join Fanout",
        "level": "advanced",
        "phase": "Advanced correctness labs",
        "estimated_minutes": 180,
        "prerequisites": ["sql-06", "sql-23", "sql-test-01"],
        "lesson_path": "sql/professional/lessons/sql_quality_01_bags_and_fanout.sql",
        "guide_path": "sql/professional/companion-guides/sql_quality_01_bags_and_fanout.md",
        "solution_paths": [
            "sql/professional/solutions/sql_quality_01_bags_and_fanout_solutions.md",
            "sql/professional/solutions/sql_quality_01_bags_and_fanout_solutions.sql",
        ],
        "dependency_group": "postgres",
        "network": "offline",
    },
    {
        "id": "sql-scale-01",
        "track": "sql",
        "day": 72,
        "title": "Cursor Pagination and Bounded Batches",
        "level": "advanced",
        "phase": "Advanced correctness labs",
        "estimated_minutes": 180,
        "prerequisites": ["sql-35", "sql-38", "sql-test-01"],
        "lesson_path": "sql/professional/lessons/sql_scale_01_cursors_and_batches.sql",
        "guide_path": "sql/professional/companion-guides/sql_scale_01_cursors_and_batches.md",
        "solution_paths": [
            "sql/professional/solutions/sql_scale_01_cursors_and_batches_solutions.md",
            "sql/professional/solutions/sql_scale_01_cursors_and_batches_solutions.sql",
        ],
        "dependency_group": "postgres",
        "network": "offline",
    },
    {
        "id": "sql-concurrency-01",
        "track": "sql",
        "day": 73,
        "title": "Isolation Traces and Optimistic Concurrency",
        "level": "advanced",
        "phase": "Advanced correctness labs",
        "estimated_minutes": 180,
        "prerequisites": ["sql-39", "sql-test-01"],
        "lesson_path": "sql/professional/lessons/sql_concurrency_01_isolation_and_versions.sql",
        "guide_path": (
            "sql/professional/companion-guides/sql_concurrency_01_isolation_and_versions.md"
        ),
        "solution_paths": [
            "sql/professional/solutions/sql_concurrency_01_isolation_and_versions_solutions.md",
            "sql/professional/solutions/sql_concurrency_01_isolation_and_versions_solutions.sql",
        ],
        "dependency_group": "postgres",
        "network": "offline",
    },
)


PROFESSIONAL_LESSON_SPECS += (
    {
        "id": "bridge-capstone-01",
        "track": "bridge",
        "day": 13,
        "title": "Evidence-Driven Data Product and Incident Review",
        "level": "advanced",
        "phase": "Integrated evidence capstone",
        "estimated_minutes": 240,
        "prerequisites": ["bridge-08", "sql-quality-01", "python-pro-03"],
        "lesson_path": "bridge/professional/lessons/bridge_capstone_01_evidence_review.py",
        "guide_path": "bridge/professional/companion-guides/bridge_capstone_01_evidence_review.md",
        "solution_paths": [
            "bridge/professional/solutions/bridge_capstone_01_evidence_review_solutions.md",
            "bridge/professional/solutions/bridge_capstone_01_evidence_review_solution.py",
        ],
        "dependency_group": "core",
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
                "prerequisites": (
                    []
                    if day == 1
                    else [
                        {
                            2: "python-foundations-01",
                            4: "python-foundations-02",
                            9: "python-foundations-03",
                            11: "python-foundations-04",
                            # Days 46-49 are optional deep-learning and NLP lessons
                            # outside the Core image; Day 50 builds on Day 45.
                            50: "python-45",
                        }.get(day, f"python-{day - 1:02d}")
                    ]
                ),
                "lesson_path": notebook.relative_to(root).as_posix(),
                "guide_path": guide.relative_to(root).as_posix(),
                "solution_paths": solution_paths,
                "dependency_group": dependency_group,
                "network": network,
            }
        )
    return lessons


def _sql_title(slug: str) -> str:
    """Use readable SQL terminology while retaining the historical file and ID."""
    titles = {
        "select_where_orderby": "SELECT, WHERE, ORDER BY and LIMIT",
        "aggregates_groupby_having": "Aggregates, GROUP BY and HAVING",
        "rank_functions": "ROW_NUMBER, RANK and DENSE_RANK",
        "lag_lead": "LAG and LEAD",
        "first_last_value": "FIRST_VALUE and LAST_VALUE",
        "ctes_intro": "Common Table Expressions",
        "multiple_ctes_hierarchies": "Multiple CTEs and Hierarchies",
        "ctes_with_windows": "CTEs with Window Functions",
        "explain_analyze": "EXPLAIN and EXPLAIN ANALYZE",
    }
    title = titles.get(slug, _title(slug))
    return re.sub(r"\b(Week|Project|Part)([0-9]+)\b", r"\1 \2", title)


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
                "title": _sql_title(slug),
                "level": level,
                "phase": phase,
                "estimated_minutes": minutes,
                "prerequisites": (
                    ["sql-start-03"]
                    if day == 1
                    else ["sql-found-01"]
                    if day == 16
                    else ["sql-found-02"]
                    if day == 40
                    else [f"sql-{day - 1:02d}"]
                ),
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


# Readable titles by stable lesson ID; files, IDs and saved work keep their historical names.
LESSON_TITLES: dict[str, str] = {
    "python-01": "Python Setup and the REPL",
    "python-02": "Variables and Core Types",
    "python-03": "Control Flow, Truthiness, and Exceptions",
    "python-04": "Loops, Comprehensions, and Generators",
    "python-05": "Functions, Docstrings, and Type Hints",
    "python-06": "Lists, Tuples, Sets, and Dictionaries",
    "python-07": "Strings, Regular Expressions, and pathlib",
    "python-08": "Files, JSON, CSV, and Context Managers",
    "python-09": "Modules, Packages, and Imports",
    "python-10": "Testing with pytest",
    "python-foundations-04": "Build Your First Data Investigation",
    "python-11": "Debugging, Logging, and Profiling",
    "python-12": "Classes and Dataclasses",
    "python-13": "Functional Tools: itertools and functools",
    "python-14": "Code Quality with Ruff, mypy, and pytest",
    "python-15": "Project: A Testable Command-Line Data Tool",
    "python-16": "NumPy Arrays, Vectorization, and Broadcasting",
    "python-17": "pandas Series, DataFrames, and Indexing",
    "python-18": "Loading and Cleaning Data with pandas",
    "python-19": "Grouping, Pivoting, and Melting in pandas",
    "python-20": "Merging and Joining DataFrames",
    "python-21": "Time Series with pandas",
    "python-22": "Advanced pandas: Vectorization, query, and Categoricals",
    "python-23": "Streaming Data Pipelines with Generators",
    "python-24": "Exploratory Data Analysis Best Practices",
    "python-25": "Visualization with Matplotlib and seaborn",
    "python-26": "Interactive Visualization with Plotly and Altair",
    "python-27": "Geospatial and Domain-Specific Visualization",
    "python-28": "Feature Engineering with scikit-learn",
    "python-29": "Data Validation with Schemas",
    "python-30": "Project: Reproducible EDA and Preprocessing",
    "python-32": "Statistical Inference: Intervals and Tests",
    "python-33": "Linear Algebra and Matrices",
    "python-34": "scikit-learn Estimators and Pipelines",
    "python-35": "Model Evaluation and Cross-Validation",
    "python-36": "PCA and Feature Selection",
    "python-37": "Regularized Linear Models",
    "python-38": "Decision Trees and Random Forests",
    "python-39": "Gradient Boosting with XGBoost and LightGBM",
    "python-40": "Hyperparameter Tuning with Grid and Randomized Search",
    "python-41": "Handling Class Imbalance",
    "python-42": "K-Means Clustering and Anomaly Detection",
    "python-43": "Model Interpretation with SHAP and Partial Dependence",
    "python-44": "Serving a Model with FastAPI",
    "python-45": "Project: End-to-End Modeling",
    "python-47": "PyTorch Tensors, Modules, and Training Loops",
    "python-48": "Transfer Learning with CNNs",
    "python-49": "NLP Basics with Hugging Face and spaCy",
    "python-50": "Time-Series Forecasting and Evaluation",
    "python-51": "Target Encoding and Leakage-Safe Features",
    "python-52": "Scaling with Dask and Chunked pandas",
    "python-53": "Experiment Tracking with MLflow",
    "python-54": "Model Monitoring and Governance",
    "python-55": "Containerizing a FastAPI Model Service",
    "python-56": "Workflow Orchestration with Prefect",
    "python-57": "Security, Privacy, and Ethics",
    "python-58": "Code Review, Refactoring, and Tests",
    "python-59": "Capstone Kickoff and Planning",
    "python-60": "Capstone Completion and Presentation",
    "python-pro-01": "Package Engineering and a Local Release Workflow",
    "python-svc-01": "Reliable HTTP Clients for External Services",
    "python-pro-02": "Choosing Concurrency or Parallelism",
    "python-data-01": "Columnar Data with Arrow, Parquet, and DuckDB",
    "python-stats-01": "Resampling, Experiments, and Causal Limits",
    "python-data-02": "Exact Decimals, Unicode Text, and Calendar Boundaries",
    "python-ml-02": "Leakage-Safe Evaluation Across Groups and Time",
    "python-pro-03": "Restartable File Pipelines and Durability Guarantees",
    "sql-start-02": "Values, NULL, and Deterministic Order",
    "sql-01": "SELECT, WHERE, ORDER BY, and LIMIT",
    "sql-02": "Aggregates, GROUP BY, and HAVING",
    "sql-03": "Inner Joins and Predicate Placement",
    "sql-04": "Outer Joins and Unmatched Rows",
    "sql-05": "Cross Joins and Self-Joins",
    "sql-06": "Set Operations: UNION, INTERSECT, and EXCEPT",
    "sql-07": "Week 1 Project: From Questions to Queries",
    "sql-08": "Scalar and Inline Subqueries",
    "sql-09": "Correlated Subqueries and EXISTS",
    "sql-10": "Changing Data with Subqueries: INSERT, UPDATE, DELETE, and Upsert",
    "sql-11": "CASE Expressions and Conditional Logic",
    "sql-12": "String Functions and Text Processing",
    "sql-13": "Date and Time Functions and Time Zones",
    "sql-14": "Numeric Types, Casting, and Precision",
    "sql-15": "Phase 1 Project: Multi-Dimensional Revenue Report",
    "sql-16": "Window Function Fundamentals: OVER, PARTITION BY, and Frames",
    "sql-17": "Ranking with ROW_NUMBER, RANK, and DENSE_RANK",
    "sql-18": "LAG and LEAD: Comparing Neighboring Rows",
    "sql-19": "Running Totals and Moving Windows",
    "sql-20": "FIRST_VALUE, LAST_VALUE, and Window Frames",
    "sql-21": "Distribution Functions: NTILE, PERCENT_RANK, and CUME_DIST",
    "sql-22": "Advanced Windows: Named Windows, Multiple Partitions, and Exclusions",
    "sql-23": "Common Table Expressions (CTEs)",
    "sql-24": "Recursive CTEs for Hierarchies and Graphs",
    "sql-27": "Pivoting and Unpivoting",
    "sql-28": "JSONB and XML in PostgreSQL",
    "sql-29": "Pattern Matching: LIKE, Regular Expressions, and Full-Text Search",
    "sql-30": "Phase 2 Project: Cohort Retention and Customer Lifetime Value",
    "sql-31": "Reading Plans with EXPLAIN and EXPLAIN ANALYZE",
    "sql-32": "B-Tree Index Fundamentals",
    "sql-33": "Composite, Covering, and Partial Indexes",
    "sql-34": "Query Optimization Techniques",
    "sql-35": "Avoiding Common Performance Pitfalls",
    "sql-36": "Materialized Views and Caching",
    "sql-37": "Partitioning and Sharding",
    "sql-38": "Transactions and Isolation Levels",
    "sql-39": "Locks, Blocking, and Deadlocks",
    "sql-40": "Advanced Analytic Functions",
    "sql-41": "Complex Aggregations: FILTER, String Aggregation, and CUBE",
    "sql-42": "Data Quality and Validation",
    "sql-43": "Logical Export, Staging, and Restore Checks",
    "sql-44": "Monitoring and Diagnostics",
    "sql-45": "Phase 3 Project: Query Optimization",
    "sql-46": "E-Commerce Project, Part 1: Lifetime Value and Cohorts",
    "sql-47": "E-Commerce Project, Part 2: Cohort Retention",
    "sql-48": "E-Commerce Project, Part 3: Product Affinity and Attribution",
    "sql-49": "Finance Project, Part 1: Revenue Forecasting",
    "sql-50": "Finance Project, Part 2: Budget Variance",
    "sql-51": "Finance Project, Part 3: Cash Flow",
    "sql-52": "Data Warehouse Project, Part 1: Star Schema",
    "sql-53": "Data Warehouse Project, Part 2: Slowly Changing Dimensions",
    "sql-54": "Data Warehouse Project, Part 3: Aggregate Tables",
    "sql-55": "BI Project, Part 1: Drill-Downs and Subtotals",
    "sql-56": "BI Project, Part 2: Percentiles and CUBE",
    "sql-57": "BI Project, Part 3: Trends and Anomalies",
    "sql-58": "Final Capstone, Part 1: Ingestion and Data Quality",
    "sql-59": "Final Capstone, Part 2: Stakeholder Analytics",
    "sql-60": "Final Capstone, Part 3: End-to-End Sign-Off",
    "sql-types-01": "Native PostgreSQL Types and Full-Text Search",
    "sql-temporal-01": "Temporal Data and Domain Modelling",
    "bridge-01": "Configuration, Logging, and Typed CLI Boundaries",
    "bridge-02": "Protocols, Context Managers, and Decorators",
    "bridge-03": "Safe Parameterized Queries with Psycopg",
    "bridge-04": "Transactions, Idempotency, and Retries",
    "bridge-05": "Database Tests, Fixtures, and Test Doubles",
    "bridge-06": "Bulk ETL and Data Validation",
    "bridge-07": "Async I/O and Bounded Concurrency",
    "bridge-08": "Production Capstone: Observability, Security, and Recovery",
}


# One-sentence learner outcomes shown under a lesson title; the phase remains the fallback.
LESSON_OUTCOMES: dict[str, str] = {
    "python-01": (
        "Run a short program in the classroom, read its output, and fix a first NameError."
    ),
    "python-02": "Convert text to numbers and Booleans on purpose, then format the result.",
    "python-03": "Order branches correctly and catch only the errors you can handle.",
    "python-04": (
        "Repeat work with loops, build lists with comprehensions, and consume generators lazily."
    ),
    "python-05": (
        "Write functions with clear parameters, return values, docstrings, and type hints."
    ),
    "python-06": "Choose a list, tuple, set, or dictionary for what the data must guarantee.",
    "python-07": "Clean text, match patterns with regular expressions, and build portable paths.",
    "python-08": "Read and write text, JSON, and CSV files safely with context managers.",
    "python-09": "Split code into modules and packages and run a package with python -m.",
    "python-10": (
        "Write pytest tests for normal, boundary, and invalid inputs and read the failures."
    ),
    "python-11": "Find bugs from tracebacks and logs, and measure before optimizing.",
    "python-12": "Model related data and behavior with classes and dataclasses.",
    "python-13": "Compose iterators with itertools and functools instead of hand-written loops.",
    "python-14": "Format, lint, and type-check code with Ruff and mypy.",
    "python-15": "Build and test a small command-line tool that summarizes a CSV file.",
    "python-16": "Create NumPy arrays and replace loops with vectorized, broadcast operations.",
    "python-17": "Select pandas rows and columns by label, position, and Boolean mask.",
    "python-18": "Load a dataset, profile it, and clean it without changing the raw data.",
    "python-19": "Summarize groups and reshape tables with groupby, pivot_table, and melt.",
    "python-20": "Join tables on keys and check row counts and unmatched records.",
    "python-21": "Resample, roll, and lag time-stamped data with an explicit time zone.",
    "python-22": "Replace row-wise apply with vectorized code, query, and categoricals.",
    "python-23": "Build lazy, batched data pipelines from generator functions.",
    "python-24": "Profile a dataset and record questions, caveats, and quality checks.",
    "python-25": "Make labeled Matplotlib and seaborn charts and export them reproducibly.",
    "python-26": "Make interactive Plotly and Altair charts and export offline HTML.",
    "python-27": "Map geographic data with the right coordinate reference system.",
    "python-28": "Encode, scale, and bin features in scikit-learn without leaking test data.",
    "python-29": "Turn data expectations into pandera schemas that fail with clear messages.",
    "python-30": "Deliver a reproducible EDA and preprocessing project with a decision log.",
    "python-31": "Simulate probabilities and apply Bayes' rule to base-rate problems.",
    "python-32": "Compute confidence intervals and hypothesis tests and interpret them correctly.",
    "python-33": "Use matrix shapes, rank, and least squares to fit a linear model.",
    "python-34": "Fit scikit-learn estimators inside leakage-safe pipelines.",
    "python-35": "Choose metrics and cross-validation designs that give honest estimates.",
    "python-36": "Reduce dimensions with PCA and select features, fitting both inside CV.",
    "python-37": "Tune ridge and lasso penalties and interpret coefficient shrinkage.",
    "python-38": "Train decision trees and random forests and measure held-out importance.",
    "python-39": "Train gradient-boosted models with early stopping and a fair comparison.",
    "python-40": "Tune hyperparameters with grid and randomized search and nested CV.",
    "python-41": "Evaluate rare-class models and choose a decision threshold deliberately.",
    "python-42": "Cluster with k-means and rank anomalies, checking stability.",
    "python-43": (
        "Explain a model with SHAP, partial dependence, and permutation importance, without "
        "causal claims."
    ),
    "python-44": "Serve a trained pipeline behind a validated FastAPI endpoint.",
    "python-45": "Deliver an end-to-end modeling project with a baseline and a saved pipeline.",
    "python-46": "Explain tensors, gradients, and the optimizer loop behind neural networks.",
    "python-47": "Write a correct PyTorch training and evaluation loop.",
    "python-48": "Adapt a pretrained CNN with frozen layers and an offline fallback.",
    "python-49": "Tokenize text and compare a local baseline with a cached pretrained model.",
    "python-50": "Forecast with time-safe splits and compare against naive baselines.",
    "python-51": "Build out-of-fold target encodings that do not leak labels.",
    "python-52": "Process larger-than-memory data with Dask partitions and chunked pandas.",
    "python-53": "Track runs, parameters, metrics, and artifacts with MLflow.",
    "python-54": "Monitor drift and delayed labels and decide when to retrain.",
    "python-55": "Containerize a FastAPI model service with a small image and a health check.",
    "python-56": "Orchestrate retryable, idempotent tasks with Prefect.",
    "python-57": "Minimize and protect personal data and check fairness evidence.",
    "python-58": "Refactor safely behind tests and review code changes.",
    "python-59": "Scope a capstone: decision, data contract, baseline, and stop rules.",
    "python-60": "Finish, reproduce, and present a capstone with clearly scoped claims.",
}


def _clean_outcome(lines: list[str]) -> str:
    raw = " ".join(" ".join(lines).split())
    text = re.sub(
        r"`([^`]*)`|\*\*([^*]+)\*\*|\[([^\]]+)\]\([^)]*\)",
        lambda m: next(group for group in m.groups() if group is not None),
        raw,
    ).strip()
    # List items are often sentence fragments ("distinguish x and y;").
    text = text.rstrip(";,: ")
    if text[:1].islower() and not raw.startswith("`"):
        text = text[0].upper() + text[1:]
    return text if not text or text.endswith((".", "?", "!")) else text + "."


def _derived_outcome(root: Path, item: dict[str, Any]) -> str | None:
    """The lesson's own goal: its source ``Focus:`` line, else its first objective."""

    source = root / item["lesson_path"]
    if source.suffix in {".sql", ".py"} and source.is_file():
        lines = source.read_text(encoding="utf-8").splitlines()
        for index, line in enumerate(lines):
            focus = re.match(r"\s*(?:--|#)\s*Focus:\s*(\S.*)$", line)
            if focus:
                parts = [focus.group(1)]
                for follow in lines[index + 1 :]:
                    more = re.match(r"\s*(?:--|#)[ \t]{2,}(\S.*)$", follow)
                    if more is None:
                        break
                    parts.append(more.group(1))
                if outcome := _clean_outcome(parts):
                    return outcome
    guide = root / item["guide_path"]
    if guide.suffix == ".md" and guide.is_file():
        lines = guide.read_text(encoding="utf-8").splitlines()
        for index, line in enumerate(lines):
            if line.strip() != "## Learning objectives":
                continue
            rest = lines[index + 1 :]
            # Skip blank lines and an introduction such as "By the end, you can:".
            while rest and (not rest[0].strip() or rest[0].rstrip().endswith(":")):
                rest.pop(0)
            bullet = re.match(r"(?:[-*]|\d+\.)[ \t]+(\S.*)$", rest[0]) if rest else None
            if bullet is None:
                return None
            parts = [bullet.group(1)]
            for follow in rest[1:]:
                if not re.match(r"[ \t]+\S", follow):
                    break
                parts.append(follow.strip())
            return _clean_outcome(parts) or None
    return None


def build_catalog(repo_root: Path | None = None) -> dict[str, Any]:
    """Return the complete catalog payload."""

    root = find_repo_root(repo_root)
    extensions = load_extensions(root)
    lessons = [
        *_python_lessons(root),
        *_sql_lessons(root),
        *_bridge_lessons(root),
        *_professional_lessons(),
        *extensions.lessons,
    ]
    identifiers = [item["id"] for item in lessons]
    if len(identifiers) != len(set(identifiers)):
        raise ValueError("Extensions must not replace existing lesson IDs.")
    stale = (set(LESSON_TITLES) | set(LESSON_OUTCOMES)) - set(identifiers)
    if stale:
        raise ValueError(f"Title or outcome overrides name unknown lessons: {sorted(stale)}")
    derived = {
        item["id"]: outcome
        for item in lessons
        if item["id"] not in LESSON_OUTCOMES
        and "outcome" not in item
        and (outcome := _derived_outcome(root, item))
    }
    # Text shared by several lessons is template prose, not a lesson's own goal.
    shared = {text for text, count in Counter(derived.values()).items() if count > 2}
    for item in lessons:
        item["title"] = LESSON_TITLES.get(item["id"], item["title"])
        if item["id"] in LESSON_OUTCOMES:
            item["outcome"] = LESSON_OUTCOMES[item["id"]]
        elif derived.get(item["id"]) not in (None, *shared):
            item["outcome"] = derived[item["id"]]
    track_days = [(item["track"], item["day"]) for item in lessons]
    if len(track_days) != len(set(track_days)):
        raise ValueError("Catalog contains duplicate track/day pairs.")
    for item in lessons:
        item.setdefault("runner", infer_runner(item["lesson_path"], item["track"]))
        missing = set(item["prerequisites"]) - set(identifiers)
        if missing:
            raise ValueError(f"{item['id']} has unknown prerequisites: {sorted(missing)}")
    artifact_owners: dict[str, str] = {}
    for item in lessons:
        for path in (item["lesson_path"], item["guide_path"], *item["solution_paths"]):
            identity = (root / path).resolve().as_posix().casefold()
            if identity in artifact_owners:
                raise ValueError(
                    f"Catalog artifact appears more than once: {path} "
                    f"({artifact_owners[identity]}, {item['id']})"
                )
            artifact_owners[identity] = item["id"]
    remaining = {item["id"]: set(item["prerequisites"]) for item in lessons}
    while ready := {key for key, prerequisites in remaining.items() if not prerequisites}:
        for key in ready:
            del remaining[key]
        for prerequisites in remaining.values():
            prerequisites.difference_update(ready)
    if remaining:
        raise ValueError(f"Catalog has a prerequisite cycle: {sorted(remaining)}")
    for path_id, path in extensions.learning_paths.items():
        if path_id in identifiers:
            raise ValueError(f"Learning path IDs must not collide with lesson IDs: {path_id}")
        if path_id in LEARNING_PATHS:
            raise ValueError(f"Extensions must not replace an existing learning path: {path_id}")
        if set(path["targets"]) - set(identifiers):
            raise ValueError(f"Learning path {path_id} has unknown target lessons.")
    track_order = {track: index for index, track in enumerate(extensions.tracks)}
    return {
        "schema_version": 1,
        "generated_from": (
            "course artifact filenames, professional specifications and registered extensions"
        ),
        "tracks": extensions.tracks,
        "learning_paths": extensions.learning_paths,
        "lessons": sorted(
            lessons,
            key=lambda item: catalog_order_key(
                item["track"],
                item["day"],
                item["id"],
                track_order,
            ),
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
