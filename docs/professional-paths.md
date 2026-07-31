# Professional and specialization paths

The historical Days 1–60 remain stable. Named modules add the relational
foundations and professional practice that do not fit honestly into one more
linear countdown. The generated catalog is the source of truth for exact
prerequisites and artifact paths:

```powershell
# Windows PowerShell
.\.venv\Scripts\python.exe scripts\course.py catalog
```

```bash
# macOS/Linux
.venv/bin/python scripts/course.py catalog
```

Choose a lane from demonstrated prerequisites. You do not need every
specialization to call the shared curriculum complete.

## Add relational engineering after SQL fundamentals

A new SQL learner begins with
[SQL Day 1 — SELECT, WHERE, and ORDER BY](../sql/postgres-60day/companion-guides/day01_select_where_orderby.md).
The named relational-engineering modules then deepen responsibilities at the
point where their prerequisites make sense:

1. Complete SQL Days 1–15.
2. Take [`sql-found-01` — relational design, DDL, and constraints](../sql/professional/companion-guides/sql_found_01_relational_design.md).
3. Complete the transaction and locking sequence through SQL Day 39.
4. Take [`sql-found-02` — versioned migrations and safe evolution](../sql/professional/companion-guides/sql_found_02_versioned_migrations.md).

Both named scripts use isolated disposable schemas; SQL Days 1–60 continue to
query the seeded `training` schema.

## Professional Python engineering lane

| Stable ID | Practice |
| --- | --- |
| [`python-pro-01`](../python/professional/companion-guides/py_pro_01_package_engineering.md) | Build, inspect, install, and invoke a local package artifact |
| [`python-svc-01`](../python/professional/companion-guides/py_svc_01_reliable_http_clients.md) | Design a timeout, pagination, retry, idempotency, and redaction boundary |
| [`python-pro-02`](../python/professional/companion-guides/py_pro_02_concurrency_parallelism.md) | Choose async I/O, threads, or processes and bound failure and backpressure |
| [`python-test-01`](../python/professional/companion-guides/py_test_01_architecture_generative.md) | Build fixture, fake, contract, and property-based test architecture |
| [`python-lang-01`](../python/professional/companion-guides/py_lang_01_typing_data_model.md) | Apply generics, Protocols, typed mappings, descriptors, MRO, and runtime protocols |
| [`python-svc-02`](../python/professional/companion-guides/py_svc_02_hardening_observability.md) | Harden and observe a local service, then work a small incident |

## Professional data and model lane

| Stable ID | Practice |
| --- | --- |
| [`python-data-01`](../python/professional/companion-guides/py_data_01_arrow_duckdb.md) | Preserve schema through Arrow and Parquet, then query locally with DuckDB |
| [`python-stats-01`](../python/professional/companion-guides/py_stats_01_resampling_experiments.md) | Use resampling, effect sizes, power, and experimental boundaries |
| [`python-ml-01`](../python/professional/companion-guides/py_ml_01_reproducible_delivery.md) | Attach data, environment, schema, promotion, and rollback evidence to a model |
| [`python-perf-01`](../python/professional/companion-guides/py_perf_01_measurement_optimization.md) | Profile memory and time before choosing vectorization, processes, or native code |

## Professional PostgreSQL lane

| Stable ID | Practice |
| --- | --- |
| [`sql-sec-01`](../sql/professional/companion-guides/sql_sec_01_roles_privileges_rls.md) | Prove schema, privilege, and row-level-security behavior as distinct roles |
| [`sql-prog-01`](../sql/professional/companion-guides/sql_prog_01_routines_triggers.md) | Choose among constraints, routines, triggers, and application code |
| [`sql-types-01`](../sql/professional/companion-guides/sql_types_01_native_types_search.md) | Model arrays, ranges, domains, JSONB/jsonpath, and full-text search |
| [`sql-ops-01`](../sql/professional/companion-guides/sql_ops_01_indexes_statistics_maintenance.md) | Select index types and reason about statistics, vacuum, bloat, and cost |
| [`sql-test-01`](../sql/professional/companion-guides/sql_test_01_contracts_migrations.md) | Test migrations, invariants, reconciliations, fixtures, and producer contracts |
| [`sql-analytics-01`](../sql/professional/companion-guides/sql_analytics_01_query_patterns.md) | Practise islands, sessions, funnels, as-of joins, attribution, and retention |
| [`sql-ops-02`](../sql/professional/companion-guides/sql_ops_02_backup_restore_recovery.md) | Verify logical restore, then plan bounded optional PITR rehearsals |

## Cross-track lane

| Stable ID | Practice |
| --- | --- |
| [`bridge-jupyter-01`](../bridge/professional/companion-guides/bridge_jupyter_01_postgresql_magics.md) | Query the disposable PostgreSQL database with `%sql` and `%%sql` safely |
| [`bridge-ops-01`](../bridge/professional/companion-guides/bridge_ops_01_migration_observability.md) | Deliver a migration with transaction, retry, log, metric, and recovery evidence |
| [`bridge-ai-01`](../bridge/professional/companion-guides/bridge_ai_01_application_engineering.md) | Build retrieval and structured-output boundaries with deterministic model doubles |
| [`bridge-analytics-01`](../bridge/professional/companion-guides/bridge_analytics_01_local_project.md) | Build a local model DAG with lineage, semantic definitions, tests, and contracts |

For the notebook connection bootstrap, use
[PostgreSQL in Jupyter](setup/jupyter-postgresql.md).

## Opt-in PostgreSQL specializations

These modules are useful only when their domain matches the learner's goal.
Their default paths remain safe on a normal laptop; server-wide, extension, or
multi-node behavior is capability-gated.

| Stable ID | Practice |
| --- | --- |
| [`sql-ext-01`](../sql/professional/companion-guides/sql_ext_01_extensions_spatial_vector.md) | Compare extension boundaries for text, crypto, spatial, vector, and foreign data |
| [`sql-repl-01`](../sql/professional/companion-guides/sql_repl_01_cdc_high_availability.md) | Model outbox/consumer idempotency, then study optional replication and failover |
| [`sql-temporal-01`](../sql/professional/companion-guides/sql_temporal_01_domain_modelling.md) | Model valid/system time, range exclusions, ledgers, audits, and retention |

## Evidence before completion

A module is complete when the learner can:

1. reproduce the main behavior from a clean local state;
2. pass the module's self-check or tests;
3. explain one failure mode and one tradeoff without the solution open; and
4. distinguish local/fake evidence from any optional live or platform-specific
   evidence.

Use the exact stable ID when recording optional progress:

```powershell
# Windows PowerShell
.\.venv\Scripts\python.exe scripts\course.py progress complete python-pro-01 `
    --notes "Built and inspected a wheel from a clean target."
```

```bash
# macOS/Linux
.venv/bin/python scripts/course.py progress complete python-pro-01 \
  --notes "Built and inspected a wheel from a clean target."
```
