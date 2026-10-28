# dbt authoring

Maintain prose and practice in units.json, executable Python project programs in
../references/, SQL model variants in ../variants/ and the complete owned retail
project in ../projects/retail/. The latter is ordinary maintained dbt SQL/YAML
source, not generated runtime output. Never commit its target, logs, dbt_packages
or database files.

Run `python courses/dbt/authoring/build.py`, then the same command with --check.
The shared owned publisher is courses/ml-engineering/authoring/publish.py.
Format Python references before generation. Root's SQLfmt adapter handles SQL
and Jinja; PostgreSQL formatting must not rewrite these templates.

All ordinary project examples use installed dbt Core and dbt-duckdb against
owned temporary DuckDB files. Calls in one process are sequential. Local package
preparation is explicit and has no remote dependency. Run actual compile/build,
tests, snapshots and artifact checks; never present simulated status as dbt output.

The SQL-model variant uses the separate fixed fixture from the runtime contract.
Full configuration and project-file activities remain in the Python/CLI route.
Do not conflate model access with database permissions, state selection with
execution, a successful process with scientific correctness, or a local fixture
with a deployed cloud service. Preserve assertions and known failure cases.
