# Apache and open data platforms: authoring design

This maintained design reserves apache-001 through apache-088. It is not an authored admission manifest or runtime qualification. The completed route will use tutorial mode with complete worked answers and no compulsory examination.

The route begins with Python and SQL vocabulary and links existing Rust, Java, Scala/Spark, Docker, Kubernetes and dbt foundations where those skills are needed. Apache products retain their project names. Delta Sharing belongs to the Delta Lake/Linux Foundation ecosystem.

## Learning and execution contract

Each chapter explains its mechanism and syntax before the two contrasting cases below, derives relevant quantities, discusses mistakes and an answered interview question, and records the exact observation that supports its conclusion. A chapter will not infer distributed correctness from a local simulation. Prepared Python examples use actual libraries and tiny synthetic fixtures. Project-only chapters open an editable Markdown notebook containing complete commands and expected observations; the classroom does not run Docker commands.

Every product has a real-product path. Separate Docker workshops build clients inside Linux containers, expose only loopback ports, preserve project-owned volumes, and require positive, negative and restart checks. Workshops start individually and are excluded from ordinary classroom startup.

## Foundations

| ID | Chapter | Worked case A | Worked case B | Observable outcome |
| --- | --- | --- | --- | --- |
| apache-001 | A platform is a set of contracts | Trace an order from event to query result | Compare a local batch with a delayed event | Separate storage, transport, execution, catalog and governance responsibilities |
| apache-002 | Rows, columns, types and missing values | Represent money with decimal and preserve nulls | Reject an incompatible schema rather than silently coerce | Define logical types and physical representation before choosing a format |
| apache-003 | Files, objects and tables | Read projected Parquet columns | Compare a file listing with a committed table snapshot | Distinguish bytes, files, partitions, table metadata and atomic commits |
| apache-004 | Processes, networks and ownership | Resolve a Compose service name inside its network | Diagnose a host localhost versus container localhost mistake | Trace a connection through client, DNS, listener and advertised endpoint |
| apache-005 | Partitioning, ordering and skew | Hash a customer key into partitions | Measure one hot key against evenly distributed keys | Explain partition-local ordering and the cost of a shuffle |
| apache-006 | Delivery, retries and idempotence | Retry a stable event identifier | Reject two conflicting payloads with the same identifier | Specify the boundary at which a duplicate is suppressed |
| apache-007 | Time, history and reproducibility | Distinguish event, ingestion and processing time | Reconstruct a versioned fixture with late corrections | Record source version, clock and query assumptions |
| apache-008 | Evidence and operational experiments | Build a deterministic result oracle | Separate restart survival from replication availability | Design positive, negative and recovery checks without overclaiming production readiness |

## Arrow

| ID | Chapter | Worked case A | Worked case B | Observable outcome |
| --- | --- | --- | --- | --- |
| apache-009 | Arrays, buffers and null bitmaps | Inspect integer value and validity buffers | Trace a sliced array with a nonzero offset | Explain why logical length, buffer length and offset differ |
| apache-010 | Schemas, nested data and dictionaries | Build a list of structs with null children | Compare dictionary-encoded categories with plain strings | Choose a schema that preserves missingness and semantic units |
| apache-011 | Compute kernels and chunked tables | Filter and aggregate a chunked table | Demonstrate null propagation versus explicit fill | Use vector kernels without confusing a chunk boundary with a partition |
| apache-012 | IPC, streams and ownership | Round-trip record batches through an IPC stream | Read an IPC file with random batch access | Compare zero-copy opportunities with allocations at conversion boundaries |
| apache-013 | Parquet datasets and predicate pruning | Read a partitioned fixture with projection and filter | Show a filter that still requires residual evaluation | Inspect metadata and distinguish pruning from proof of row-level correctness |
| apache-014 | Language boundaries and Flight | Exchange Arrow IPC between Python and prepared Rust | Request batches from a real local Flight service | Explain C Data Interface lifetime and Flight transport without calling either a database |

## DataFusion

| ID | Chapter | Worked case A | Worked case B | Observable outcome |
| --- | --- | --- | --- | --- |
| apache-015 | SessionContext, SQL and DataFrames | Register Arrow batches and execute a grouped query | Run the equivalent DataFrame expression | Separate plan construction from execution and materialization |
| apache-016 | Logical and physical plans | Inspect projection and predicate pushdown | Compare an aggregate before and after a selective filter | Read operators and explain why plan text is evidence rather than a stable API |
| apache-017 | Joins, SQL nulls and cardinality | Join orders to a unique dimension | Expose a duplicate dimension key that multiplies revenue | Predict join output multiplicity and missing-key semantics |
| apache-018 | Partitions, memory and spill | Control target partitions on a bounded dataset | Compare a selective scan with a sort under a memory budget | Explain why more partitions can increase overhead and peak memory |
| apache-019 | UDFs and engine extension boundaries | Register a typed scalar Python UDF | Contrast a native expression with a row callback | Explain volatility, types and optimizer visibility |
| apache-020 | Embedding an analytical engine | Build an isolated parameterized query service project | Reject an unapproved table or oversized result | Define a bounded engine API with reproducible source and resource settings |

## Ballista

| ID | Chapter | Worked case A | Worked case B | Observable outcome |
| --- | --- | --- | --- | --- |
| apache-021 | From an engine to a distributed scheduler | Run the released Python client against scheduler and executors | Compare local DataFusion with the same Ballista SQL result | Trace plan serialization, scheduling and Arrow Flight data movement |
| apache-022 | Cluster configuration and shared data paths | Query one mounted Parquet path from two executors | Fail a query whose file exists only in the client | Distinguish logical paths from filesystem visibility across processes |
| apache-023 | Stages, shuffle and task placement | Inspect distributed aggregation stages | Compare balanced groups with a hot grouping key | Explain stage barriers, shuffle files and scheduler decisions |
| apache-024 | Clients and supported language APIs | Submit from the matching Python client | Submit a Rust client against the same cluster | Respect protocol and release compatibility instead of assuming Spark API parity |
| apache-025 | Failure, retry and retained evidence | Stop an owned executor during a bounded workload | Restart an owned scheduler and characterize observed job behavior | Report precisely what recovered and what needs resubmission |
| apache-026 | Capacity and operational decisions | Compare one and two executor allocations | Bound collect and inspect history/metrics | Choose an embedded engine or a cluster from workload evidence |

## Airflow

| ID | Chapter | Worked case A | Worked case B | Observable outcome |
| --- | --- | --- | --- | --- |
| apache-027 | DAGs, tasks and data intervals | Run a TaskFlow DAG over a fixed logical interval | Show why wall-clock now changes a backfill | Distinguish scheduler time, logical date and data interval |
| apache-028 | Dependencies, retries and idempotent tasks | Write an idempotent partition output | Inject one transient task failure and inspect retry state | Keep side effects safe across retries and task clearing |
| apache-029 | Scheduling, catchup and backfills | Materialize two historical intervals | Correct one partition without recomputing unrelated history | Choose a backfill plan with explicit completeness semantics |
| apache-030 | Assets, mapping and bounded concurrency | Trigger a consumer from an updated asset | Map a bounded list with pool limits | Separate orchestration metadata from bulk data transfer |
| apache-031 | Connections, providers and security | Use a local connection reference without embedding a secret in a DAG | Reject a missing provider or invalid connection | Keep parse-time side effects and credentials outside authored code |
| apache-032 | Operations and recovery | Restart scheduler and retain metadata/history | Diagnose a stuck task from logs and state transitions | Recover the owned installation without deleting orchestration history |

## Kafka

| ID | Chapter | Worked case A | Worked case B | Observable outcome |
| --- | --- | --- | --- | --- |
| apache-033 | The log, topics and partitions | Produce keyed events with the official CLI | Consume the same log with two independent groups | Distinguish a durable log from a destructive queue |
| apache-034 | Producer acknowledgements and idempotence | Compare acknowledged delivery with a failed connection | Retry using idempotent producer configuration | Explain producer IDs, sequence numbers and the scope of deduplication |
| apache-035 | Consumers, offsets and rebalances | Commit only after successful processing | Restart a consumer before committing and observe replay | Explain at-least-once processing with a concrete offset timeline |
| apache-036 | Transactions and isolation | Commit one transaction and abort another | Compare read_committed with read_uncommitted | State exactly which Kafka operations are atomic |
| apache-037 | Retention, compaction and schemas | Compare deletion retention with keyed compaction | Evolve an optional field and reject an incompatible payload | Distinguish latest state from event history and schema compatibility |
| apache-038 | KRaft, networking and operations | Inspect controller/broker roles and advertised listeners | Restart an owned broker and retain committed records | Diagnose connectivity, consumer lag and disk bounds without claiming single-node HA |

## Iceberg

| ID | Chapter | Worked case A | Worked case B | Observable outcome |
| --- | --- | --- | --- | --- |
| apache-039 | Snapshots and the table abstraction | Create a real local PyIceberg SQL catalog and append data | Read the previous snapshot after a second append | Explain metadata files, manifests and data-file references |
| apache-040 | Field IDs and schema evolution | Rename a field while retaining its identity | Reject a required-field evolution that invalidates existing data | Distinguish identity from column position or display name |
| apache-041 | Hidden partitioning and evolution | Partition by a transform and inspect planned files | Evolve the partition specification without rewriting old data | Explain residual predicates across multiple partition specs |
| apache-042 | Concurrency and optimistic commits | Commit from one table handle then detect a stale second handle | Retry after reloading against the new snapshot | Identify the catalog compare-and-swap boundary |
| apache-043 | Deletes, maintenance and retention | Perform a bounded overwrite or delete and inspect snapshots | Expire only unreferenced old state under a retained-snapshot policy | Separate logical deletion, physical cleanup and rollback promises |
| apache-044 | Catalogs and cross-engine reads | Read the same table through Hive Metastore and Spark workshop | Compare a local SQL catalog with the external metastore contract | Verify engine/version capabilities instead of treating all catalog protocols as interchangeable |

## Flink

| ID | Chapter | Worked case A | Worked case B | Observable outcome |
| --- | --- | --- | --- | --- |
| apache-045 | Streams, operators and a running job | Submit a real Java bounded stream job | Read the same event contract through Flink SQL | Trace source, transformation, sink and execution graph |
| apache-046 | Event time and watermarks | Window out-of-order events with explicit timestamps | Send an event beyond allowed lateness and inspect its route | Explain that watermarks estimate completeness rather than guarantee it |
| apache-047 | Keyed state and timers | Maintain per-customer running state | Fire an inactivity timer with event-time progress | Distinguish operator state, keyed state and timer semantics |
| apache-048 | Checkpoints and end-to-end guarantees | Complete a checkpoint and restart the job | Contrast a transactional Kafka sink with a nontransactional side effect | Bound exactly-once claims by source, state and sink participation |
| apache-049 | Backpressure and capacity | Constrain a sink and observe upstream pressure | Change parallelism while preserving compatible state | Explain bottleneck propagation, slots and partition skew |
| apache-050 | Savepoints and schema evolution | Take a savepoint and restore compatible state | Demonstrate a deliberately incompatible operator identity | Treat upgrades as state migrations with a rollback plan |

## Cassandra

| ID | Chapter | Worked case A | Worked case B | Observable outcome |
| --- | --- | --- | --- | --- |
| apache-051 | Query-first modeling and CQL | Create a time-bucketed partition for a concrete lookup | Show why a cross-partition ad hoc filter is expensive | Choose primary and clustering keys from access patterns |
| apache-052 | Writes, SSTables and reads | Write updates and inspect row visibility | Compare a range within one partition with many-partition access | Explain commit log, memtable, SSTable and read reconciliation |
| apache-053 | Replication and consistency levels | Run a small real multi-node optional topology | Contrast ONE and QUORUM during an owned node outage | Apply quorum reasoning only with its replication and failure assumptions |
| apache-054 | Tombstones, TTL and compaction | Expire a bounded fixture with TTL | Inspect a delete and explain repair-before-GC requirements | Connect tombstones and compaction to resurrection risk |
| apache-055 | Transactions, indexes and drivers | Use lightweight compare-and-set for one invariant | Query a Storage Attached Index with selectivity checks | Distinguish LWT, batch atomicity and ordinary last-write-wins semantics |
| apache-056 | Repair, backup and operations | Capture a snapshot and verify a restore in owned storage | Restart a node and inspect ring and pending work | Explain repair scope, consistency and restore boundaries |

## Pinot

| ID | Chapter | Worked case A | Worked case B | Observable outcome |
| --- | --- | --- | --- | --- |
| apache-057 | Segments and serving topology | Load a bounded offline segment | Query through broker and identify serving server | Explain controller, broker, server, segment and ZooKeeper roles |
| apache-058 | Kafka ingestion and real-time segments | Ingest the shared event fixture from Kafka | Observe malformed-event handling and ingestion lag | Trace consuming segments into committed segments |
| apache-059 | Indexes and query plans | Compare filtered queries with and without an inverted index | Test a range or sorted index on an appropriate column | Explain index selection and memory/storage tradeoffs |
| apache-060 | Time boundaries, hybrid tables and upserts | Combine historical offline data with fresh real-time data | Apply a versioned update with primary-key comparison | Prevent overlap double-counting and define late-update semantics |
| apache-061 | Multistage queries and capacity | Join small dimension data using the supported engine | Bound a query and inspect response exceptions | Separate analytical serving latency from batch throughput |
| apache-062 | Operations, recovery and data verification | Restart owned Pinot services and verify query results | Compare ingested counts with source event identities | Diagnose segment, schema and consumption failures without deleting state |

## Hive and Metastore

| ID | Chapter | Worked case A | Worked case B | Observable outcome |
| --- | --- | --- | --- | --- |
| apache-063 | Warehouse, catalog and execution | Create a namespace and external table in Hive | Inspect the metastore record independently of querying data | Separate HiveServer2, Metastore and storage responsibilities |
| apache-064 | Schemas, partitions and serialization | Register partition locations and read Parquet | Demonstrate a wrong type or location with a controlled failure | Explain SerDe, physical files and partition discovery |
| apache-065 | Metastore durability and clients | Persist metadata in PostgreSQL | Restart Metastore and query from a second client | Trace Thrift metadata calls without confusing them with data reads |
| apache-066 | Hive SQL and execution plans | Explain a selective aggregate over a partitioned fixture | Compare map-side assumptions with observed execution | Teach cost, statistics and execution-engine boundaries |
| apache-067 | Transactional tables and Iceberg integration | Compare Hive transactional-table semantics with Iceberg snapshots | Read a compatible Iceberg table through the prepared integration | Treat formats and commit protocols as explicit contracts |
| apache-068 | Catalog upgrades and operational recovery | Run schema verification before startup | Reject an incompatible database schema and recover from an owned backup | Plan metadata upgrades without assuming a rollback of binaries rolls back schema |

## Atlas

| ID | Chapter | Worked case A | Worked case B | Observable outcome |
| --- | --- | --- | --- | --- |
| apache-069 | Types, entities and metadata identity | Create custom dataset and process type definitions | Create two entity versions with stable qualified names | Distinguish a type, entity, relationship and classification |
| apache-070 | Lineage as recorded relationships | Record a process with input and output datasets | Query lineage and show an intentionally missing edge | Explain that recorded lineage is evidence only for instrumented operations |
| apache-071 | Classifications and discovery | Attach a classification to a synthetic dataset | Search by type and classification then remove it | Separate metadata labels from enforcement in a data engine |
| apache-072 | Hooks, notifications and integration | Inspect a supported Hive hook or explicit API ingest path | Retry a duplicate notification without inventing duplicate assets | Define provenance and delivery boundaries of metadata ingestion |
| apache-073 | Authorization and governance workflows | Compare permitted and rejected local API requests | Document a classification review and owner decision | Keep policy intention distinct from actual enforcement |
| apache-074 | Graph, indexes and recovery | Restart the owned Atlas backing services | Verify entity and lineage survival and diagnose index lag | Understand graph storage, search indexes and backup consistency |

## Delta Sharing

| ID | Chapter | Worked case A | Worked case B | Observable outcome |
| --- | --- | --- | --- | --- |
| apache-075 | An open sharing protocol | List shares, schemas and tables from the real reference server | Reject an invalid recipient credential | Distinguish Delta Sharing from an Apache project and from Delta table storage |
| apache-076 | Metadata, file URLs and read paths | Fetch a bounded table through the Python client | Inspect metadata response and actual file reads separately | Trace control-plane authorization and data-plane retrieval |
| apache-077 | Snapshots, predicates and consistency | Read a pinned table version | Compare a server predicate hint with client-side correctness checks | Keep predicate pushdown and access control conceptually separate |
| apache-078 | Recipients and credential boundaries | Use a fixture-only short-lived profile | Rotate or invalidate access and observe rejection | Avoid embedding recipient credentials in notebooks or published source |
| apache-079 | History, changes and compatible readers | Read supported table history or changes from the pinned server | Reject an unsupported protocol or feature explicitly | Negotiate capabilities rather than assuming every client reads every Delta feature |
| apache-080 | Operating a bounded sharing service | Restart the real server and retain the shared table | Test missing data-file and unavailable-server failures | Distinguish persisted data, share configuration and client retry behavior |

## Integration and capstones

| ID | Chapter | Worked case A | Worked case B | Observable outcome |
| --- | --- | --- | --- | --- |
| apache-081 | Batch lakehouse with reproducible snapshots | Materialize a bounded event batch into Iceberg | Compare Spark and DataFusion reads through supported paths | Produce an evidence bundle with schema, snapshot and result identity |
| apache-082 | Streaming analytical serving | Move Kafka events through Flink to Pinot | Inject a duplicate and late correction and reconcile counts | Document the guarantee at each source/state/sink boundary |
| apache-083 | Orchestrated backfills and live data | Use Airflow to correct a historical partition | Keep a live event stream independent of the backfill | Separate orchestration intervals from event-time semantics |
| apache-084 | Catalog and governance integration | Register Hive/Iceberg assets and process lineage in Atlas | Compare metadata classification with an actual denied data access | Show where governance information ends and enforcement begins |
| apache-085 | Sharing a versioned data product | Publish one bounded Delta table through the reference server | Validate recipient access and reproducible table version | Specify a consumer contract with provenance and revocation limits |
| apache-086 | Failure and recovery game day | Restart a stateful service and compare durable evidence | Break one owned configuration then restore it | Write a recovery report distinguishing loss, duplication and unavailability |
| apache-087 | Capacity, costs and architectural tradeoffs | Measure CPU, memory, storage and latency on a small workload | Contrast embedded, batch, streaming and serving alternatives | Extrapolate carefully and separate measured results from capacity forecasts |
| apache-088 | An auditable data-platform capstone | Build one selected end-to-end path with source-bound receipts | Independently verify its failure and restart behavior | Deliver a reproducible design, implementation, runbook and evidence dossier |
