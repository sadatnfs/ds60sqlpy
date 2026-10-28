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
evaluation, and testing evidence. Running a model alone is insufficient.

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
explanation of tradeoffs. Running the reference implementation alone is insufficient.

## Interactive PostgreSQL notebooks

Check whether the learner can:

- explain line versus cell magics and select the correct kernel;
- connect through `DS60_DATABASE_URL` without exposing credentials;
- use `:value` binding and explain why `{{...}}` is SQL generation;
- bound result retrieval and reason about JupySQL autocommit;
- move a result into pandas without changing its grain; and
- name what a notebook proves versus what application-level Psycopg tests prove.

## Compiled languages and JavaScript/TypeScript

Check whether the learner can:

- explain source, compilation or type checking, execution and diagnostics as
  distinct steps;
- satisfy the classroom entrypoint and filename contract without guessing;
- choose representations and abstractions, test boundaries and explain failures;
- reason about pointers, representation, allocation and lifetime in C/C++,
  ownership and borrowing in Rust, or reference/resource behavior in Java/C#;
- explain Go cancellation, goroutine ownership and module boundaries without
  assuming a classroom pad can fetch arbitrary dependencies;
- distinguish Swift portable language behavior from Apple UI lifecycle,
  simulator and signing work;
- preserve Arrow schema and null semantics and distinguish NaN from missingness;
- distinguish TypeScript's static checking from runtime validation; and
- separate browser APIs from Node behavior, including asynchronous cancellation
  and cleanup.

Independent evidence includes a new bounded program, a diagnosed defect and an
explanation of why its tests cover the important behavior. Successful reference
compilation alone does not establish readiness for larger projects.

For D3, assess data joins and stable keys, scale domains, accessibility,
interaction cleanup and resize behavior with a new small dataset. A rendered
chart or a saved browser observation alone does not establish correct encoding,
accessibility or independent verification.

## Web and GPU routes

For HTML/CSS, inspect semantic structure, accessible names, keyboard order,
responsive layout and the actual painted result. For PHP, distinguish validation,
contextual escaping, prepared values and server-side ownership. Ask the learner
to explain why a request/session model differs from the separately prepared real
HTTP fixture. A successful preview or printout is not an accessibility or security
qualification. Keep browser observations distinct from trusted worker checks.

For CUDA, ask the learner to explain the execution/memory model, index bounds,
ownership, synchronization and numerical tolerance before optimizing. CPU models,
compilation, device correctness and profiling are separate evidence. Optional
hardware being unavailable is not a failed learner answer. Compare PyTorch and
TensorFlow device placement, gradient state, precision and synchronization using
actual framework contracts. For GPU Spark, require supported executed operator
and plan evidence, configuration/version compatibility and a fair CPU comparison;
a plugin flag or arbitrary Python UDF does not establish acceleration.

## Scala, Spark and systems

Check Scala language foundations before distributed Spark work. Ask the learner
to explain schema, row grain, lazy evaluation, partitioning, shuffles, ordering,
null semantics and bounded collection. A local job does not prove cluster scale.

For Docker, distinguish image layers, container processes and persistent
volumes. Review build context, runtime identity, port publishing versus container
networking, health checks, Compose service discovery and a verified restore into
an independent disposable volume. Building an image is not proof of persistence
or recovery. Never test cleanup against unrelated resources or learner volumes.

For Kubernetes, review desired versus observed state, resource identity,
readiness, failure diagnosis and cleanup in an explicitly owned disposable
target. Ask the learner to trace a request through Pod addresses, Service and
EndpointSlice selection, DNS, ingress or Gateway and load-balancer behavior.
Separate address allocation, reachability, source egress and destination ingress
policy, and application listening behavior. A manifest does not prove that a
CNI, controller, public load balancer or IPv6 path actually exists. Do not use
production access or a completed apply command as evidence of understanding.
Availability of a local tool is separate from runtime proof.

## Statistics, ML and language-model tutorials

For practice routes, assess whether the learner can define notation and units,
state assumptions, prevent leakage, select meaningful evaluation, inspect error
cases and explain limitations. Distinguish a toy mechanism, a trained model and
a useful system. For RAG or fine-tuning, require evidence about retrieval or
adaptation and held-out task quality rather than only fluent output.

For TensorFlow and PyTorch, ask for tensor shapes, gradient behavior, train/eval
mode, checkpoint contents, data leakage prevention and a small reproducible
comparison. One trained example does not qualify GPU behavior or distributed
training. For NLP, relate tokenization and representation to the selected task,
baseline, split and error analysis instead of rewarding fluent text alone.

Statistics/ML, Applied Science, Bayesian Computing, Data and ML Engineering
and the Apache/open-data route are tutorials without exams or problem sets.
If a learner asks for a discussion of readiness, use their explanations and volunteered
examples. Do not impose a hidden test or withhold its worked answers. Reading
markers remain personal progress rather than certification.

## Review format

Return:

1. the demonstrated strengths;
2. the highest-leverage gap, with exact evidence;
3. one remediation exercise;
4. the recommended lesson ID;
5. the conditions for reassessment.

Do not assign a numeric grade unless the learner requests one.

## Scientific and data-system review examples

Use these only for a requested discussion or practice review, never as a hidden
gate on tutorial answers.

- Bayesian computation: explain the generative model and prior/predictive checks;
  compare an exact oracle, sampler diagnostics and decision uncertainty. Zero
  divergences in a tiny run is insufficient evidence of convergence.
- Applied science: identify the estimand, data availability, censoring or
  inclusion mechanism, assumptions and a counterexample before selecting a method.
- Polars/dbt: state grain, key cardinality, null and time policies; distinguish
  an optimized plan or successful build from correct metrics and publication.
- ML systems: trace feature availability through training and serving, validate
  artifacts, and explain a reversible release decision and actual rollback.
- Julia: explain dispatch, shapes, aliasing, numerical error and thread ownership;
  support performance claims with equivalent completed work and measurements.
- LLM evaluation: distinguish sampled populations, correlated uncertainty,
  contamination, judge bias, preference optimization and held-out utility.

Recommend actual stable lesson IDs from the current catalog and preserve source,
notes and result history. Do not manufacture a score from lesson completion.
