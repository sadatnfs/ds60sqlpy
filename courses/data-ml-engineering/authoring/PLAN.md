# Data and ML Engineering book plan

The aggregate admits this book only when all 72 complete chapter artifacts exist.
Chapters 001 through 032 and 041 through 056 are owned by the data/ML curriculum
agent. Root owns 033 through 040 in authoring/ml-lifecycle/. Chapters 057 through
072 and the inference-service project are owned by the serving agent. Existing
ML engineering and dbt courses remain separate focused workshops with stable IDs.

## Reader and teaching contract

Start with no engineering background. Introduce concrete vocabulary, syntax,
inputs, outputs and failure boundaries before tool names. Each chapter has
original theory, two complete explained cases, changed-condition diagnosis,
credible uses, answered interview/practice discussion and primary references.
There are no forced exams or hidden answers. Mathematics uses explicit TeX.
A complete authoritative program is inserted at <!-- worked-program -->.

## Initial runtime boundaries

Use prepared python-core, data-engineering, spark-local-python and llm-torch-cpu
profiles. No new package dependency is assumed by this plan. Ordinary pads use
owned temporary directories, bounded deterministic fixtures and no networking,
package downloads, cloud credentials or listening daemons. A mechanism model is
labelled as such and never described as an actual Kafka, Flink, Airflow,
Cassandra, Pinot, object-store or table-format deployment. Actual prepared
library/SQL/ASGI operations and real local HTTP project checks are distinct.

The data-product project provides a bounded owned Docker ingestion/publication
workflow with real loopback HTTP, durable local state, identity-aware retries,
contracts and controlled failure/recovery checks. The existing local ML service
is a cross-linked focused workshop. Any additional service topology or new
runtime package will be coordinated with root before implementation. The reserved
projects/inference-service tree is exclusively owned by the serving agent.
Apache/open-data tool execution belongs to its maintained owned workshops; links
will be added when those paths are finalized. Their service success will not be
inferred from this book's bounded semantic models.

## Deterministic fragment contract

Each owned fragment supplies chapters.json with records containing id, title,
level, minutes, prerequisites, runtime_profile, language, concepts, outcome,
guide_source, source_path and related_paths. Source paths are repository-relative.
related_paths contains optional label/path objects for existing local material.
Each chapter Markdown has a full H1, Worked case 1/2 sections and exactly one
worked-program marker. The complete program supplies example_one(), example_two()
and main() or an explicitly agreed equivalent. The aggregate generator copies
published guides, inserts exact source fences, relocates local links, and emits
track.json/lessons.json only when the full 001 through 072 set validates. Tutorial
admissions expose the complete source directly with empty solution_paths.

## Chapters 001 through 056

| Chapter | Runtime | Complete case 1 | Changed-condition case 2 |
| --- | --- | --- | --- |
| dme-001: From a record to an engineering decision | python-core | Trace a small record-to-metric pipeline and define its observable contract | Reject a plausible but invalid record without silently changing the population |
| dme-002: Files, paths, processes and the Linux container boundary | python-core | Read and write owned UTF-8 files through explicit paths | Separate successful output from a child process that fails on stderr |
| dme-003: Values, units, missingness and clocks | python-core | Normalize aware timestamps and retain the meaning of missing values | Expose a unit or timezone mismatch that otherwise produces valid-looking numbers |
| dme-004: SQL, row grain, keys and relational reasoning | data-engineering | Execute real DuckDB joins and grouped metrics with an independent row oracle | Detect duplicate-dimension fanout and a changed COUNT denominator |
| dme-005: Python functions, collections and state boundaries | python-core | Build a pure transformation with explicit inputs and outputs | Diagnose a mutable-state or exhausted-iterator mistake |
| dme-006: Tests, invariants and evidence that can falsify a claim | python-core | Check hand-derived outputs, boundaries and changed inputs | Show why a plausible invariant alone can accept an incorrect transformation |
| dme-007: Structural schemas and semantic data contracts | data-engineering | Validate a strict typed input and a compatible additive schema change | Reject a units or identity change that a basic type check cannot detect |
| dme-008: Source, dependency and data identities for reproducible work | python-core | Build a reviewable source/data/configuration hash manifest | Invalidate a claimed result when an input or transformation identity changes |
| dme-009: File ingestion, manifests and resumable delivery | data-engineering | Ingest a declared CSV/JSON delivery with checksums and row reconciliation | Reject a truncated or repeated delivery without publishing duplicate data |
| dme-010: HTTP APIs, pagination, retries and idempotency | data-engineering | Exercise an actual local ASGI pagination contract without network access | Compare retry-safe request identity with a duplicated non-idempotent action |
| dme-011: Change-data capture events and ordered application | python-core | Apply synthetic insert/update/delete events to a real local SQLite table | Reject stale versions and replay safely; distinguish this from capturing a database WAL |
| dme-012: Facts, dimensions and slowly changing business meaning | data-engineering | Build and query a real dimensional product at a declared grain | Resolve a historical dimension interval instead of using the current value |
| dme-013: JSON, CSV, Parquet and Arrow interoperability | data-engineering | Round-trip typed columnar records and inspect actual Arrow/Parquet schemas | Show the information lost by an unqualified text-format round-trip |
| dme-014: Event time, availability time and late-known facts | python-core | Select only information known at a decision cutoff | Separate a late arrival from an invalid future observation and report coverage |
| dme-015: Atomic publication and consistent consumer views | python-core | Publish a checked local manifest through an atomic pointer replacement | Fail before publication on partial writes or corrupted artifact bytes |
| dme-016: Data quality, deduplication and explicit quarantine | data-engineering | Retain valid and rejected Polars records with concrete reason codes | Handle conflicting duplicate identities without arbitrary row loss |
| dme-017: Choosing and comparing local query engines | data-engineering | Compare actual SQLite, DuckDB and Polars results under one contract | Explain a null, type or ordering difference without treating syntax parity as semantic parity |
| dme-018: Columnar layout, partition pruning and bounded reads | data-engineering | Inspect real partitioned Parquet fragments selected by a predicate | Compare small-file or partition-layout changes while preserving the same answer |
| dme-019: Spark partitions, shuffles and skew | spark-local-python | Execute and inspect a real Spark aggregation and its physical shuffle boundary | Use a two-stage hot-key strategy and reconcile it with an independent result |
| dme-020: Orchestration, dependencies and safe retries | python-core | Execute a bounded local DAG with recorded completed artifact identities | Reconcile an uncertain outcome before retrying; label the scheduler as a mechanism model |
| dme-021: Transactions, idempotency and the outbox pattern | python-core | Commit a state change and an outbox event in one actual SQLite transaction | Replay delivery without applying the same identified effect twice |
| dme-022: Backfills, overlapping windows and correction policies | data-engineering | Rebuild a declared half-open historical interval and reconcile it | Repair a late correction without overwriting a newer accepted partition |
| dme-023: Stream windows, watermarks and state lifetime | python-core | Trace a bounded event-time window mechanism under out-of-order arrivals | Account for late side outputs and deliberate state expiry without claiming a Flink runtime |
| dme-024: Checkpoints, replay and state-schema evolution | python-core | Restore a versioned checkpoint and compare with a full replay oracle | Reject incompatible or corrupted state before resuming publication |
| dme-025: Object storage, object identity and conditional updates | python-core | Model versioned object publication and conditional pointer updates explicitly | Demonstrate a stale-writer conflict; link the actual object-store workshop separately |
| dme-026: Lake file organization, manifests and evolution | data-engineering | Query an actual versioned Parquet manifest with DuckDB | Evolve a field and verify old/new reader behavior against declared compatibility rules |
| dme-027: Table formats: snapshots, transactions and concurrency | data-engineering | Investigate snapshot and delete invariants using real local files and a clearly labelled table-format model | Compare conflicting writers and explain the additional guarantees required from Iceberg, Delta or Hudi |
| dme-028: Catalogs, discovery, ownership and access decisions | data-engineering | Query a real local metadata catalog and resolve a versioned dataset contract | Detect an unauthorized or stale publication; distinguish application policy from external IAM |
| dme-029: Cassandra: access paths, partition keys and consistency | python-core | Derive query-shaped partition keys and quantify a hot-partition case | Trace version/tombstone and consistency choices without pretending the pad runs Cassandra |
| dme-030: Pinot and low-latency analytical serving | data-engineering | Compute a query oracle and choose a compatible ingestion grain | Contrast append and upsert interpretation; reserve actual Pinot execution for its owned service workshop |
| dme-031: Lineage, provenance and reproducible investigations | python-core | Trace an actual artifact dependency graph using content identities | Find the earliest invalidated descendant after an input or transformation changes |
| dme-032: Governance, minimization, retention and review | data-engineering | Enforce a declared synthetic access/retention policy and preserve an audit record | Show how pseudonymization or aggregate output can still retain identifying information |
| dme-033: Frame an ML decision and establish a baseline | data-engineering | Train and evaluate a real baseline for an explicitly defined synthetic decision | Contrast aggregate accuracy with missed-positive cost and cohort coverage |
| dme-034: Point-in-time feature retrieval and the feature-store boundary | data-engineering | Use actual local Feast retrieval against a two-clock independent oracle | Preserve the request population when unknown, expired or late-known features are missing |
| dme-035: Feature quality and fitted transformations | data-engineering | Fit a real preprocessing pipeline on training rows only | Handle missing values and unseen categories without leaking evaluation information |
| dme-036: Train/serve consistency and safe model interfaces | data-engineering | Compare fitted-pipeline predictions with a reviewed JSON inference interface | Reject changed feature order, units or schema before scoring |
| dme-037: Reproducible training, snapshots and computation state | data-engineering | Repeat a seeded training run with declared data/configuration identities | Separate numerical tolerance from false claims of cross-platform byte identity |
| dme-038: Temporal evaluation, calibration and decision uncertainty | data-engineering | Evaluate a realistic future or grouped cohort with calibrated metrics | Contrast immature labels or repeated-entity leakage with the proper evaluation population |
| dme-039: Experiments, MLflow registry and acceptance decisions | data-engineering | Create and read back real local MLflow runs and model versions | Withhold activation when the declared evidence gate fails, even if registration succeeded |
| dme-040: Artifacts, integrity and the software supply chain | python-core | Validate a bounded model manifest and its exact content hashes | Reject tampered or incompatible artifacts; distinguish integrity from source trust |
| dme-041: Batch and online inference as different contracts | data-engineering | Compare real batch predictions with a local ASGI request contract | Reject stale or invalid requests while keeping model/version identity explicit |
| dme-042: HTTP serving, concurrency and cancellation boundaries | data-engineering | Exercise a bounded real ASGI contract and resource cleanup | Reconcile a request whose outcome is unknown instead of blindly replaying it |
| dme-043: Observability, SLOs and error budgets | python-core | Compute request-based service indicators with explicit eligible denominators | Detect a burst and contrast fast versus slow burn windows using declared observations |
| dme-044: Data drift, model quality and delayed labels | python-core | Measure a changed input distribution without inferring quality loss automatically | Evaluate matured outcome cohorts and expose missing-label coverage |
| dme-045: Security boundaries, secrets and shared systems | python-core | Enforce a synthetic resource-authorization contract and safe request validation | Reject unauthorized access or an unsafe path while stating the limits of a local workshop |
| dme-046: Capacity, latency and cost at the system boundary | python-core | Compute a bounded workload/capacity model and check its assumptions | Compare burst behavior or scan amplification with average-based estimates and illustrative cost units |
| dme-047: Incidents, retries, failure domains and degraded service | python-core | Trace a declared circuit-breaker/retry mechanism with bounded probes | Quantify retry amplification and preserve a controlled fallback after failure |
| dme-048: Delivery, compatibility and rollback | data-engineering | Perform a compatible local schema migration and accepted-version switch | Roll back a rejected candidate while retaining the prior consumer contract |
| dme-049: Capstone: a validated local data product | data-engineering | Connect ingestion, quarantine, real analytical transformation and an accepted publication manifest | Withhold publication after a deliberate contract violation and retain diagnostic evidence |
| dme-050: Capstone: late data, replay and backfill repair | python-core | Reconcile identified streaming-style updates with a full batch recomputation | Restore a checkpoint and apply a late correction without duplicate effects |
| dme-051: Capstone: features, training, registry and inference | data-engineering | Connect actual Feast, fitted training, MLflow evidence and local inference | Reject a changed feature/model contract before activation and publish a compact model card |
| dme-052: Backup, restore and recovery objectives | python-core | Create and restore an actual consistent SQLite backup with checked evidence | Measure the declared recovery gap and reject an incompatible or corrupted backup |
| dme-053: Migration between schemas, formats and consumers | data-engineering | Maintain simultaneous compatible readers during a real local migration | Reconcile a failed cutover and preserve the accepted consumer version |
| dme-054: Operational drill: detection, rollback and learning | data-engineering | Diagnose a bounded fault using actual recorded workflow/service evidence | Recover an accepted state and document which external guarantees remain untested |
| dme-055: System-design interviews grounded in constraints | python-core | Compare two defensible designs using explicit workload and correctness requirements | Identify the missing evidence that would change a design decision instead of reciting tool names |
| dme-056: An evidence-backed engineering portfolio | python-core | Assemble a reproducible local investigation with source, input, test and runtime evidence | Invalidate an unsupported claim and distinguish local success from production qualification |

## Verification progression

Author in coherent eight-chapter blocks. Verify each actual library and process
example in the prepared Linux image, with independent row/numerical/system
oracles and deliberate failure cases. Record source hashes and separate syntax,
unit tests, ordinary worker execution, owned service lifecycle and browser
rendering evidence. Do not run shared generators or publish incomplete admission.
The final book needs full source/TeX/link validation, exact reference execution,
source-bound output checks where declared, browser rendering and saved-state
qualification through the root integration workflow.
