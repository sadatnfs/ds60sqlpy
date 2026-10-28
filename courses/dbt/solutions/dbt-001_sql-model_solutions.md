# dbt-001: SQL-model reference

The SQL reference returns one row with answer 42. Change the expression and inspect the emitted SQL and materialized table. The prepared project supplies the setup; use the full-project route to author and inspect configuration files.

```sql
-- A model is compiled and materialized by actual dbt and DuckDB.
select 6 * 7 as answer
```

This is actual dbt compilation and DuckDB materialization in the prepared fixture project. It does not execute the full project-editing exercises or deploy a cloud warehouse. Model tables have no row-order guarantee; use keys when comparing records.
