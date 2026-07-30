# DS60 assessment rubrics

Use these rubrics only when placement, review, or readiness is requested.
Score demonstrated behavior; lesson counts are supporting evidence, not proof.

## Rating scale

| Rating | Evidence |
|---|---|
| Not yet | Cannot complete the task with conceptual hints; vocabulary or prerequisite is missing. |
| Developing | Completes a close example with pseudocode or partial implementation. |
| Independent | Completes a new bounded task, explains the result, and diagnoses ordinary mistakes. |
| Transfer | Adapts the concept to a new context, tests edge cases, and explains tradeoffs. |

## Python foundations

Check whether the learner can:

- choose appropriate built-in types and explain mutability;
- write small functions with clear inputs, outputs, and exceptions;
- use iteration, comprehensions, generators, files, and context managers;
- structure a module and virtual environment;
- add useful type hints and tests;
- debug from a traceback instead of guessing.

Readiness for the data track requires mostly Independent evidence through
functions, data structures, files, modules, and testing.

## Data and machine learning

Check whether the learner can:

- inspect shape, types, missingness, and leakage risks before modeling;
- perform joins and grouped calculations at the intended grain;
- build preprocessing inside a scikit-learn pipeline;
- choose a metric and validation scheme that matches the question;
- distinguish training, validation, and test evidence;
- communicate limitations, uncertainty, and reproducibility requirements.

Readiness for advanced production lessons requires Independent pipeline,
evaluation, and testing evidence—not merely a model that runs.

## PostgreSQL

Check whether the learner can:

- state the row grain and keys before writing a join;
- reason about `NULL`, three-valued logic, grouping, and query order;
- write deterministic filters, joins, aggregates, CTEs, and window functions;
- use transactions and parameterized queries safely;
- interpret the important nodes and row estimates in `EXPLAIN ANALYZE`;
- propose an index from a real predicate and verify rather than assume impact;
- identify when a script changes persistent database state.

Advanced readiness requires Independent evidence on windows, CTEs,
transactions, and plan reading.

Professional database readiness also checks whether the learner can:

- model grain, cardinality, and invariants with keys and constraints;
- evolve a schema through reviewed, versioned migrations;
- demonstrate least privilege and row-level-security behavior as distinct roles;
- select and maintain PostgreSQL index types from measured evidence;
- rehearse restore verification instead of treating a backup file as proof; and
- test data contracts, temporal assumptions, and analytical pattern grain.

## Python and PostgreSQL engineering

Check whether the learner can:

- separate configuration, domain policy, and database-driver boundaries;
- bind values safely and compose identifiers without string interpolation;
- state who owns commit, rollback, connection, and cursor lifetimes;
- distinguish retryable transient failures from permanent failures and explain
  why idempotency matters;
- test policy with fakes while naming the behavior that only PostgreSQL can
  prove;
- validate and account for every input row in bounded ETL;
- bound async work and preserve cancellation cleanup; and
- attach useful operational context without logging secrets or personal data.

Bridge completion requires Independent evidence on safe queries, transactions,
tests, and failure handling. A fake-backed pass alone is not Transfer evidence
for live database behavior.

## Professional Python and data engineering

Check whether the learner can:

- build and inspect an installed wheel from a clean src-layout project;
- choose async I/O, threads, or processes from workload evidence and platform constraints;
- preserve schema and null semantics across CSV, Arrow, Parquet, pandas, and DuckDB;
- design retry, pagination, idempotency, timeout, and redaction policy around an HTTP boundary;
- use Protocols, generics, fixtures, fakes, and generative tests without confusing static and runtime guarantees;
- state the experimental assumptions behind uncertainty and causal claims; and
- attach data, environment, model, service, and migration evidence to a release.

Transfer evidence requires a new local case, deterministic tests, and an
explanation of tradeoffs—not merely running the reference implementation.

## Interactive PostgreSQL notebooks

Check whether the learner can:

- explain line versus cell magics and select the correct kernel;
- connect through `DS60_DATABASE_URL` without exposing credentials;
- use `:value` binding and explain why `{{...}}` is SQL generation;
- bound result retrieval and reason about JupySQL autocommit;
- move a result into pandas without changing its grain; and
- name what a notebook proves versus what application-level Psycopg tests prove.

## Review format

Return:

1. the demonstrated strengths;
2. the highest-leverage gap, with exact evidence;
3. one remediation exercise;
4. the recommended lesson ID;
5. the conditions for reassessment.

Do not assign a numeric grade unless the learner requests one.
