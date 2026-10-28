# Data and ML Engineering

A complete tutorial from engineering foundations through data systems, dependable ML workflows and the LLM serving lifecycle.

The 72 tutorial chapters connect engineering foundations, data systems, ML
lifecycle decisions and LLM serving. Every chapter provides original theory,
two complete explained cases, failure diagnosis, answered interview discussion
and a maintained executable reference. There are no forced exams or hidden
answers. Start at dme-001 or follow a selected chapter's direct prerequisites.

## Open the book

Follow the [main Docker setup](../../README.md), then open the printed address
ending in `/classroom` and select **Data and ML Engineering**. A lightweight
`./classroom --starter` session can read the entire book and run Core chapters.
To select the complete set of ordinary runtimes used by this book from the
repository root:

```sh
BUILDKIT_PROGRESS=plain ./classroom \
  --profile data-engineering --profile spark-local-python --profile llm-torch-cpu
```

Core is included automatically. Explicit profile flags replace the saved profile
selection, so include any additional language profiles you want to retain in that
selection. Later `./classroom` reuses the saved selection; `./classroom stop`
retains learner state, and `./classroom resume` starts without building or pulling.
See the [launcher guide](../../docs/one-command-classroom.md) for the full contract.

The host needs a Linux-container Docker engine and the documented Bash launcher;
Windows uses WSL 2. Compilers, Python packages and Spark's JVM belong inside the
prepared images. Use images matching the native engine architecture. No GPU,
cloud account, downloaded model weights or host language installation is needed
for the ordinary worked programs.

## Follow the learning route

| Chapters | Focus |
| --- | --- |
| [001-008](guides/dme-001.md) | Records, types, SQL grain, functions, tests and reproducibility |
| [009-016](guides/dme-009.md) | Ingestion, APIs, change events, history, time and quality |
| [017-024](guides/dme-017.md) | Query engines, Parquet, Spark, orchestration and checkpoints |
| [025-032](guides/dme-025.md) | Storage, snapshots, catalogs, Cassandra, Pinot and governance |
| [033-040](guides/dme-033.md) | Features, training, evaluation, MLflow and artifact acceptance |
| [041-048](guides/dme-041.md) | Serving, SLOs, monitoring, security, capacity and delivery |
| [049-056](guides/dme-049.md) | Connected capstones, restore, migration and recovery |
| [057-072](guides/dme-057.md) | LLM requests, weights, kernels, scheduling and streaming |

Read the changed-condition cases before editing the reference. Compare actual
output with the chapter's independent oracle, and inspect rejected conditions as
well as successful ones. Saved drafts, notes and results belong to their lesson
and runtime. A read marker or successful reference execution records activity;
it does not certify mastery or production readiness.

## Use the complete projects separately

Ordinary pads create bounded temporary state and do not start long-lived servers.
For persistent service work, copy the maintained project source into a new
learner-owned folder and follow that project's instructions:

- [Data-product service](projects/data-product/README.md): real HTTP snapshot
  ingestion, SQLite, Polars/DuckDB, immutable Parquet, failure recovery and rollback.
- [Inference service](projects/inference-service/README.md): actual CPU model
  execution, bounded requests, SSE, cancellation and durable operation receipts.
- [Focused ML service](../ml-engineering/projects/local-system/README.md): retained
  feature/model state, explicit activation, prediction and monitoring.
- [Apache and open-data workshops](../apache-data-platforms/README.md): separately
  prepared actual services for the mechanisms discussed in this book.

A Python mechanism model is identified as a model. It is never presented as an
executed Kafka, Flink, Cassandra, Pinot, cloud object store or table-format
service. Native program execution, application tests, actual HTTP service checks
and architecture/hardware qualification remain separate evidence.

## Chapter directory

| Chapter | Stage | Prepared runtime |
| --- | --- | --- |
| [dme-001: From a record to an engineering decision](guides/dme-001.md) | beginner | `python-core` |
| [dme-002: Files, paths, processes and the Linux container boundary](guides/dme-002.md) | beginner | `python-core` |
| [dme-003: Values, units, missingness and clocks](guides/dme-003.md) | beginner | `python-core` |
| [dme-004: SQL, row grain, keys and relational reasoning](guides/dme-004.md) | beginner | `data-engineering` |
| [dme-005: Python functions, collections and state boundaries](guides/dme-005.md) | beginner | `python-core` |
| [dme-006: Tests, invariants and evidence that can falsify a claim](guides/dme-006.md) | beginner | `python-core` |
| [dme-007: Structural schemas and semantic data contracts](guides/dme-007.md) | beginner | `data-engineering` |
| [dme-008: Source, dependency and data identities for reproducible work](guides/dme-008.md) | beginner | `python-core` |
| [dme-009: File ingestion, manifests and resumable delivery](guides/dme-009.md) | intermediate | `data-engineering` |
| [dme-010: HTTP APIs, pagination, retries and idempotency](guides/dme-010.md) | intermediate | `data-engineering` |
| [dme-011: Change-data capture events and ordered application](guides/dme-011.md) | intermediate | `python-core` |
| [dme-012: Facts, dimensions and slowly changing business meaning](guides/dme-012.md) | intermediate | `data-engineering` |
| [dme-013: JSON, CSV, Parquet and Arrow interoperability](guides/dme-013.md) | intermediate | `data-engineering` |
| [dme-014: Event time, availability time and late-known facts](guides/dme-014.md) | intermediate | `python-core` |
| [dme-015: Atomic publication and consistent consumer views](guides/dme-015.md) | intermediate | `python-core` |
| [dme-016: Data quality, deduplication and explicit quarantine](guides/dme-016.md) | intermediate | `data-engineering` |
| [dme-017: Choosing and comparing local query engines](guides/dme-017.md) | intermediate | `data-engineering` |
| [dme-018: Columnar layout, partition pruning and bounded reads](guides/dme-018.md) | intermediate | `data-engineering` |
| [dme-019: Spark partitions, shuffles and skew](guides/dme-019.md) | intermediate | `spark-local-python` |
| [dme-020: Orchestration, dependencies and safe retries](guides/dme-020.md) | intermediate | `python-core` |
| [dme-021: Transactions, idempotency and the outbox pattern](guides/dme-021.md) | intermediate | `python-core` |
| [dme-022: Backfills, overlapping windows and correction policies](guides/dme-022.md) | intermediate | `data-engineering` |
| [dme-023: Stream windows, watermarks and state lifetime](guides/dme-023.md) | intermediate | `python-core` |
| [dme-024: Checkpoints, replay and state-schema evolution](guides/dme-024.md) | intermediate | `python-core` |
| [dme-025: Object storage, object identity and conditional updates](guides/dme-025.md) | intermediate | `python-core` |
| [dme-026: Lake file organization, manifests and evolution](guides/dme-026.md) | intermediate | `data-engineering` |
| [dme-027: Table formats: snapshots, transactions and concurrency](guides/dme-027.md) | intermediate | `data-engineering` |
| [dme-028: Catalogs, discovery, ownership and access decisions](guides/dme-028.md) | intermediate | `data-engineering` |
| [dme-029: Cassandra: access paths, partition keys and consistency](guides/dme-029.md) | intermediate | `python-core` |
| [dme-030: Pinot and low-latency analytical serving](guides/dme-030.md) | intermediate | `data-engineering` |
| [dme-031: Lineage, provenance and reproducible investigations](guides/dme-031.md) | intermediate | `python-core` |
| [dme-032: Governance, minimization, retention and review](guides/dme-032.md) | intermediate | `data-engineering` |
| [dme-033: Frame an ML decision and establish a baseline](guides/dme-033.md) | intermediate | `data-engineering` |
| [dme-034: Point-in-time feature retrieval and the feature-store boundary](guides/dme-034.md) | intermediate | `data-engineering` |
| [dme-035: Feature quality and fitted transformations](guides/dme-035.md) | intermediate | `data-engineering` |
| [dme-036: Train/serve consistency and safe model interfaces](guides/dme-036.md) | intermediate | `data-engineering` |
| [dme-037: Reproducible training, snapshots and computation state](guides/dme-037.md) | advanced | `data-engineering` |
| [dme-038: Temporal evaluation, calibration and decision uncertainty](guides/dme-038.md) | advanced | `data-engineering` |
| [dme-039: Experiments, MLflow registry and acceptance decisions](guides/dme-039.md) | advanced | `data-engineering` |
| [dme-040: Artifacts, integrity and the software supply chain](guides/dme-040.md) | advanced | `python-core` |
| [dme-041: Batch and online inference as different contracts](guides/dme-041.md) | advanced | `data-engineering` |
| [dme-042: HTTP serving, concurrency and cancellation boundaries](guides/dme-042.md) | advanced | `data-engineering` |
| [dme-043: Observability, SLOs and error budgets](guides/dme-043.md) | advanced | `python-core` |
| [dme-044: Data drift, model quality and delayed labels](guides/dme-044.md) | advanced | `python-core` |
| [dme-045: Security boundaries, secrets and shared systems](guides/dme-045.md) | advanced | `python-core` |
| [dme-046: Capacity, latency and cost at the system boundary](guides/dme-046.md) | advanced | `python-core` |
| [dme-047: Incidents, retries, failure domains and degraded service](guides/dme-047.md) | advanced | `python-core` |
| [dme-048: Delivery, compatibility and rollback](guides/dme-048.md) | advanced | `data-engineering` |
| [dme-049: Capstone: a validated local data product](guides/dme-049.md) | advanced | `data-engineering` |
| [dme-050: Capstone: late data, replay and backfill repair](guides/dme-050.md) | advanced | `python-core` |
| [dme-051: Capstone: features, training, registry and inference](guides/dme-051.md) | advanced | `data-engineering` |
| [dme-052: Backup, restore and recovery objectives](guides/dme-052.md) | advanced | `python-core` |
| [dme-053: Migration between schemas, formats and consumers](guides/dme-053.md) | advanced | `data-engineering` |
| [dme-054: Operational drill: detection, rollback and learning](guides/dme-054.md) | advanced | `data-engineering` |
| [dme-055: System-design interviews grounded in constraints](guides/dme-055.md) | advanced | `python-core` |
| [dme-056: An evidence-backed engineering portfolio](guides/dme-056.md) | advanced | `python-core` |
| [dme-057: From an HTTP request to an admitted inference job](guides/dme-057.md) | intermediate | `python-core` |
| [dme-058: Bytes, subwords and the tokenizer boundary](guides/dme-058.md) | intermediate | `python-core` |
| [dme-059: Token embeddings, positions and retrieval representations](guides/dme-059.md) | intermediate | `python-core` |
| [dme-060: Safe checkpoints, startup loading and readiness](guides/dme-060.md) | intermediate | `python-core` |
| [dme-061: Device placement, transfers and precision budgets](guides/dme-061.md) | intermediate | `llm-torch-cpu` |
| [dme-062: Bounded admission, queues and capacity ownership](guides/dme-062.md) | intermediate | `python-core` |
| [dme-063: Prefill, causal attention and a correct KV cache](guides/dme-063.md) | advanced | `llm-torch-cpu` |
| [dme-064: Autoregressive decoding, sampling and stopping rules](guides/dme-064.md) | advanced | `python-core` |
| [dme-065: Batching, continuous scheduling and fairness](guides/dme-065.md) | advanced | `python-core` |
| [dme-066: Tensor layouts, fusion and attention kernels](guides/dme-066.md) | advanced | `python-core` |
| [dme-067: KV memory planning, paging and shared-prefix ownership](guides/dme-067.md) | advanced | `python-core` |
| [dme-068: Quantization and speculative decoding without exaggerated claims](guides/dme-068.md) | advanced | `python-core` |
| [dme-069: SSE, UTF-8, backpressure and explicit event readback](guides/dme-069.md) | advanced | `python-core` |
| [dme-070: Cancellation, errors and recovery without replay](guides/dme-070.md) | advanced | `python-core` |
| [dme-071: Latency metrics, profiling and workload evidence](guides/dme-071.md) | advanced | `python-core` |
| [dme-072: Operating the inference workshop and defending a release decision](guides/dme-072.md) | advanced | `python-core` |

Maintain the disjoint sources through the [authoring contract](authoring/README.md) and [book validation guide](VALIDATION.md). Existing [ML engineering](../ml-engineering/README.md), [dbt](../dbt/README.md) and [Polars](../polars/README.md) remain focused workshops with their stable lesson identities.
