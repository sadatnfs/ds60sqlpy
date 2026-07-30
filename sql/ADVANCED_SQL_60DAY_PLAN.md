# PostgreSQL 16+ learning plan — 60-day track

This plan describes the repository's actual PostgreSQL curriculum. “60 days” is
an ordered sequence, not a deadline: repeat a lesson, split a project across
several sessions, or pause whenever the concepts need more practice.

The exact machine-readable artifact map is
[`curriculum/catalog.json`](../curriculum/catalog.json). Before starting, read
the [PostgreSQL track README](postgres-60day/README.md). Narrative pre-reads are
indexed in the [companion-guide README](postgres-60day/companion-guides/README.md),
and worked answers are described in the
[solution README](postgres-60day/solutions/README.md).

## How to use the track

For each lesson:

1. Prepare and verify the disposable course database as documented in the
   PostgreSQL track README.
2. Read the matching companion guide.
3. Run the learner `.sql` file with `psql -X -v ON_ERROR_STOP=1`.
4. Solve the exercises in a scratch transaction and explain the result's grain,
   assumptions, and edge cases.
5. Compare your work with the Markdown explanation and executable solution.
6. Record progress only after you can explain why the query is correct.

PostgreSQL 16 or newer is required. The canonical container currently uses
PostgreSQL 17, while the curriculum is validated on PostgreSQL 16+.

## Safety and execution contracts

- `postgres-60day/00_setup.sql` drops and recreates the course-owned `training`
  schema. Run it only in the disposable training database, then run
  `00_verify.sql`.
- Normal learner lessons wrap demonstrations in `BEGIN` and `ROLLBACK`.
  Preserve that boundary while learning.
- Days 38 and 39 include genuinely concurrent exercises. Reproducing isolation
  anomalies, blocking, and deadlocks requires two or three `psql` sessions;
  one sequential file cannot demonstrate them faithfully.
- Days 52–54 are the declared stateful sequence. Day 52 drops, rebuilds, and
  commits the course-owned `dwh` schema. Run Day 52 before Days 53 and 54.
  Days 53 and 54 demonstrate changes inside rollback-safe transactions.
- Day 43 introduces backup and recovery concepts. Server-side `COPY`, WAL
  archiving, base backups, and point-in-time recovery depend on deployment and
  privileges; the learner file keeps unsafe filesystem operations commented.
- Day 44 can use `pg_stat_statements` when an administrator has installed and
  configured it. The core lesson remains usable without that extension.
- Query plans and timings depend on PostgreSQL version, statistics, cache
  state, hardware, concurrency, and data volume. The small deterministic seed
  can rationally produce sequential scans even when an index is well designed.
  There is no portable fixed speedup or runtime guarantee.

## Phase 1 — Relational querying and report foundations (Days 1–15)

### Core queries, joins, and sets

- [Day 1 — `SELECT`, `WHERE`, ordering, and limits](postgres-60day/day01_select_where_orderby.sql):
  filter customers and products, create derived columns, and return
  deterministic top-N results.
- [Day 2 — aggregates, `GROUP BY`, and `HAVING`](postgres-60day/day02_aggregates_groupby_having.sql):
  payment totals, customer tenure, and category gross-margin summaries.
- [Day 3 — inner joins](postgres-60day/day03_inner_joins.sql):
  traverse customers, orders, lines, products, payments, departments, and the
  employee hierarchy while watching join fanout.
- [Day 4 — outer joins and NULL-aware reconciliation](postgres-60day/day04_outer_joins.sql):
  find unpaid orders, unsold products, and customers without recent orders.
- [Day 5 — cross joins and self-joins](postgres-60day/day05_cross_self_joins.sql):
  create category-country combinations and three-level employee hierarchies.
- [Day 6 — `UNION`, `UNION ALL`, `INTERSECT`, and `EXCEPT`](postgres-60day/day06_set_operations.sql):
  compare customer, product, promotion, and order sets with compatible result
  shapes.
- [Day 7 — week-one report project](postgres-60day/day07_week1_project.sql):
  extend recent country-category revenue with payment method and customer
  cohort dimensions while preventing payment fanout.

### Subqueries, safe DML, and PostgreSQL functions

- [Day 8 — scalar and inline subqueries](postgres-60day/day08_scalar_inline_subqueries.sql):
  calculate country maximum orders and each customer's first order date.
- [Day 9 — correlated subqueries and existence tests](postgres-60day/day09_correlated_subqueries.sql):
  use `EXISTS` for high-value customers and `NOT EXISTS` for unsold products.
- [Day 10 — DML with subqueries](postgres-60day/day10_dml_with_subqueries.sql):
  practice temporary-table creation, `UPDATE`, `DELETE`, `RETURNING`, and
  rollback verification without persisting changes.
- [Day 11 — `CASE` expressions](postgres-60day/day11_case_expressions.sql):
  create revenue tiers, time-of-day buckets, and conditional aggregates.
- [Day 12 — string functions](postgres-60day/day12_string_functions.sql):
  normalize country values and build labels using PostgreSQL text functions
  and `to_char` for numeric presentation.
- [Day 13 — date, time, intervals, and time zones](postgres-60day/day13_date_time_functions.sql):
  calculate quarters and days since last order. Because the repository defines
  no fiscal start month, the maintained answer states its UTC calendar-quarter
  assumption.
- [Day 14 — numeric precision and casting](postgres-60day/day14_numeric_and_casting.sql):
  use exact `numeric`, `ROUND`, `CEIL`, `FLOOR`, safe division, casts, and JSONB
  text extraction.
- [Day 15 — segmented revenue project](postgres-60day/day15_phase1_project.sql):
  extend monthly segment-country revenue with at least two documented
  dimensions and reconcile the result against line-item totals.

## Phase 2 — Windows, CTEs, and semi-structured data (Days 16–30)

### Window functions

- [Day 16 — window fundamentals](postgres-60day/day16_window_functions_fundamentals.sql):
  compute customer lifetime totals and product share of category revenue
  without collapsing detail rows.
- [Day 17 — `ROW_NUMBER`, `RANK`, and `DENSE_RANK`](postgres-60day/day17_rank_functions.sql):
  compare tie behavior and return top customers within country.
- [Day 18 — `LAG` and `LEAD`](postgres-60day/day18_lag_lead.sql):
  compare dense product-month sales and find the next strictly higher
  department salary.
- [Day 19 — running and moving aggregates](postgres-60day/day19_running_aggregates.sql):
  build a dense daily calendar for literal 30-day revenue windows and
  cumulative product quantities.
- [Day 20 — `FIRST_VALUE` and `LAST_VALUE`](postgres-60day/day20_first_last_value.sql):
  compare product revenue with its first observed month and study frame
  boundaries. The employee exercise explicitly simulates history because the
  schema has no salary-history table.
- [Day 21 — `NTILE` and `PERCENT_RANK`](postgres-60day/day21_distribution_functions.sql):
  assign product sales deciles and rank orders within customer.
- [Day 22 — multi-level windows](postgres-60day/day22_advanced_windows.sql):
  rank category revenue within country and overall, then compare department and
  company salary ranks.

### CTE pipelines, reshaping, JSONB, XML, and text search

- [Day 23 — common table expressions](postgres-60day/day23_ctes_intro.sql):
  name monthly-revenue and Electronics-revenue stages and understand
  PostgreSQL's CTE inlining behavior.
- [Day 24 — recursive CTEs](postgres-60day/day24_recursive_ctes.sql):
  enumerate every manager's direct and indirect reports with cycle-safe paths,
  then generate and sum integers 1 through 100.
- [Day 25 — multiple CTEs and hierarchies](postgres-60day/day25_multiple_ctes_hierarchies.sql):
  combine employee-manager levels with department metrics and build a
  filter → enrich → aggregate → present pipeline.
- [Day 26 — CTEs with windows](postgres-60day/day26_ctes_with_windows.sql):
  calculate month-over-month growth and top product-order contributions.
- [Day 27 — pivot and unpivot patterns](postgres-60day/day27_pivot_unpivot.sql):
  reshape data with conditional aggregation and lateral `VALUES`; optionally
  study `tablefunc.crosstab`. The seeded `budgets` table is already long-form,
  so the unpivot exercise demonstrates a deliberate wide-to-long round trip.
- [Day 28 — JSONB and XML](postgres-60day/day28_json_xml.sql):
  extract event metadata, group path segments, parse `xml_docs.payload` with
  `xpath`, and reconcile XML order status with relational data.
- [Day 29 — pattern matching and full-text search](postgres-60day/day29_pattern_matching.sql):
  use `LIKE`/`ILIKE`, PostgreSQL POSIX regular expressions, `to_tsvector`, and
  `to_tsquery`.
- [Day 30 — cohort retention and CLV project](postgres-60day/day30_phase2_project.sql):
  extend cohort-month revenue with cohort size, retention rate, and a documented
  moving-average CLV heuristic.

## Phase 3 — Plans, physical design, concurrency, and operations (Days 31–45)

### Plans, indexes, and query structure

- [Day 31 — `EXPLAIN` and `EXPLAIN ANALYZE`](postgres-60day/day31_explain_analyze.sql):
  compare estimates with actual rows and observe predicate selectivity.
- [Day 32 — index fundamentals](postgres-60day/day32_index_fundamentals.sql):
  create rollback-safe B-tree demonstrations and compare plans with and without
  indexes.
- [Day 33 — composite, covering, and partial indexes](postgres-60day/day33_index_optimization_strategies.sql):
  study leftmost-prefix behavior, `INCLUDE`, and immutable partial-index
  predicates.
- [Day 34 — query optimization](postgres-60day/day34_query_optimization.sql):
  compare subqueries and joins, push selective work to the right stage, bound
  rows safely, and project only needed columns.
- [Day 35 — performance pitfalls](postgres-60day/day35_avoiding_pitfalls.sql):
  rewrite function-wrapped timestamp predicates and correlated aggregates while
  preserving result semantics.
- [Day 36 — materialized views](postgres-60day/day36_materialized_views.sql):
  create, query, refresh, and compare a reporting snapshot with its base query.
- [Day 37 — native range partitioning](postgres-60day/day37_partitioning_sharding.sql):
  build monthly event partitions, observe pruning, and test partition indexes.
  The runnable lesson is single-cluster PostgreSQL partitioning; cross-server
  sharding remains an architectural discussion, not a feature implemented by
  this script.

### Transactions, analytics, quality, and database operations

- [Day 38 — transactions and isolation](postgres-60day/day38_transactions_isolation.sql):
  study ACID, savepoints, `READ COMMITTED`, `REPEATABLE READ`, and
  `SERIALIZABLE`; use multiple sessions for non-repeatable reads, phantoms, and
  serialization failures.
- [Day 39 — locks and deadlocks](postgres-60day/day39_locks_deadlocks.sql):
  inspect `pg_locks`, reproduce blocking and deadlocks in separate sessions,
  apply consistent lock ordering, and use `FOR UPDATE SKIP LOCKED` for queue
  claiming.
- [Day 40 — advanced analytics](postgres-60day/day40_analytic_functions_advanced.sql):
  calculate rolling variance and standard deviation, z-scores, ordered-set
  percentiles, and ratio-to-total metrics.
- [Day 41 — complex aggregations](postgres-60day/day41_complex_aggregations.sql):
  combine aggregate `FILTER`, conditional metrics, and ordered `string_agg`.
- [Day 42 — data-quality validation](postgres-60day/day42_data_quality_validation.sql):
  profile NULLs, duplicates, invalid domains, and referential or constraint
  violations.
- [Day 43 — backup and recovery concepts](postgres-60day/day43_backup_recovery.sql):
  distinguish server-side `COPY` from client-side `\copy`, stage a subset, and
  discuss logical restore, WAL, and point-in-time recovery boundaries.
- [Day 44 — monitoring and diagnostics](postgres-60day/day44_monitoring_diagnostics.sql):
  inspect `pg_stat_activity`, use plans for diagnosis, and optionally query
  administrator-enabled `pg_stat_statements`.
- [Day 45 — optimization project](postgres-60day/day45_phase3_optimization_project.sql):
  compare a non-sargable baseline, a range-predicate rewrite, an index, and
  pre-aggregation. Report locally observed plans, rows, buffers, and timings;
  do not claim a universal percentage improvement.

## Phase 4 — Applied PostgreSQL projects (Days 46–60)

### Project 1: e-commerce analytics

- [Day 46 — LTV segmentation and cohort setup](postgres-60day/day46_project1_ecommerce_part1.sql):
  calculate customer lifetime value, threshold segments, and revenue by cohort
  offsets.
- [Day 47 — cohort retention](postgres-60day/day47_project1_ecommerce_part2.sql):
  turn active-customer counts into retention rates and prepare retention curves for
  the latest cohorts.
- [Day 48 — product affinity and campaign attribution](postgres-60day/day48_project1_ecommerce_part3.sql):
  build market-basket pairs, first/last touch summaries, assisted conversions,
  and fractional multi-touch attribution.

### Project 2: finance and operations

- [Day 49 — revenue forecasts](postgres-60day/day49_project2_finance_part1.sql):
  compare monthly revenue, year-over-year growth, seasonal-naive forecasts, and
  moving-average forecasts with explicit error metrics.
- [Day 50 — expense and budget variance](postgres-60day/day50_project2_finance_part2.sql):
  reconcile monthly actuals with budgets, calculate rolling variance, flag
  overspend, and reshape a variance report.
- [Day 51 — cash-flow projection](postgres-60day/day51_project2_finance_part3.sql):
  combine cash inflow, expense outflow, operating margin, rolling periods, and
  seasonal net-cash projections.

### Project 3: dimensional warehouse

- [Day 52 — star schema and initial load](postgres-60day/day52_project3_dwh_part1.sql):
  reset and commit `dwh`, load date/customer/product dimensions and the sales
  fact, then extend the model with country and payment structures.
- [Day 53 — slowly changing dimensions](postgres-60day/day53_project3_dwh_part2_scd.sql):
  practice Type 2 customer and product change capture, date-valid fact lookup,
  and audit columns against the Day 52 warehouse.
- [Day 54 — warehouse aggregates and checks](postgres-60day/day54_project3_dwh_part3_aggregations.sql):
  build monthly sales aggregates, validate them against facts, and design
  product-month refresh logic.

Run these three files in order. Day 52 intentionally persists only the
course-owned warehouse schema; Days 53 and 54 roll their demonstrations back.

### Project 4: multidimensional BI

- [Day 55 — drill-down and subtotal design](postgres-60day/day55_project4_bi_part1.sql):
  use `ROLLUP`, `CUBE`, grouping indicators, and top-N detail across reporting
  dimensions.
- [Day 56 — percentiles and multidimensional rankings](postgres-60day/day56_project4_bi_part2.sql):
  calculate country-month percentiles, product ranks, and multi-dimension
  subtotals while measuring row-count growth.
- [Day 57 — trends, anomalies, and forecast accuracy](postgres-60day/day57_project4_bi_part3.sql):
  compare rolling standard-deviation and median-absolute-deviation anomaly
  scores, seasonal baselines, and forecast error.

### Final integrated capstone

- [Day 58 — staging, cleaning, and validation](postgres-60day/day58_final_capstone_part1.sql):
  normalize messy customer input, parse dates, validate JSONB and email/country
  domains, upsert valid rows, and extend the staging contract where requested.
- [Day 59 — business logic and stakeholder queries](postgres-60day/day59_final_capstone_part2.sql):
  assemble LTV, funnels, market baskets, finance variance, assisted marketing
  conversions, index experiments, and scale considerations.
- [Day 60 — integration and evidence-based sign-off](postgres-60day/day60_final_capstone_part3.sql):
  create rollback-safe quality and business views, run stakeholder queries,
  inspect plans, propose indexes, and document tradeoffs and exceptions.

The capstone has no hardware-independent runtime threshold. Define acceptance
criteria for the database and dataset you actually test, preserve before/after
plans, reconcile business totals, and explain any remaining quality exception.

## Relational foundations and professional extensions

The original Days 1–60 remain stable. New learners should first complete
`sql-found-01` (relational design and constraints) and `sql-found-02`
(versioned migrations). Ten named professional modules then extend the track:

- `sql-sec-01`: roles, privileges, safe search paths, and row-level security
- `sql-prog-01`: functions, procedures, triggers, and auditing boundaries
- `sql-types-01`: native PostgreSQL types and searchable documents
- `sql-ops-01`: index types, statistics, vacuum, and maintenance lifecycle
- `sql-test-01`: SQL tests, migration checks, and data contracts
- `sql-analytics-01`: reusable analytical-query patterns
- `sql-ops-02`: logical backup/restore and recovery rehearsal design
- `sql-ext-01`: extension, spatial, and vector capability boundaries
- `sql-repl-01`: replication, CDC, and high-availability reasoning
- `sql-temporal-01`: temporal, ledger, and retention modelling

The default labs stay inside the disposable `advanced_sql_training` database.
Administrator-only features use capability checks and explanatory exercises
instead of changing server configuration. See
[professional paths](../docs/professional-paths.md) for direct artifact links.

## What completion means

Completing the track means more than executing every file. You should be able
to:

- state the input and output grain of a query and prove joins do not multiply
  a metric accidentally;
- choose PostgreSQL joins, subqueries, CTEs, windows, JSONB/XML functions,
  ordered-set aggregates, and reshaping patterns for a stated requirement;
- interpret estimates versus actuals without treating one plan node as
  universally good or bad;
- design indexes and partitions from observed query shapes and data
  distribution;
- reproduce and explain transaction isolation and lock behavior with safe,
  bounded concurrent sessions;
- distinguish rollback-safe demonstrations from the declared stateful
  warehouse sequence; and
- hand off a project with executable SQL, reconciliations, assumptions,
  operational cautions, and evidence appropriate to the tested environment.
