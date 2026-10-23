# Scala and Spark content status

Updated 23 October 2026. The course currently has **42 of 42 authored lessons**, with 69 executable language references and three reading chapters. Source presence, executable-reference success, and learner understanding remain separate claims. This content author has performed no Docker or database-engine operations, package installation, Git staging, commits or pushes.

## Current ownership and authored scope

Existing pilots 001, 002, 003 and 013 are preserved, including the PySpark013 variant and its typed verifier. New 004-010 provide Scala foundations; 011-029 provide paired Scala/PySpark data, execution and batch-product lessons; 030 is a deployment architecture worksheet; 031-034 provide paired finite-streaming foundations. The second writer completed 035-042, including the JDBC reading lesson040. All eight advanced rows and their artifacts are merged into the shared manifest. Existing pilot rows remain preserved.

Every new runnable lesson includes two worked examples, six distinct tasks with expected results, progressive hints and verification, separate learner stubs and executable references, explained solutions, and a fixed case ledger. New verification IDs remain null until a trusted learner verifier is registered. Reference assertions are not a hidden grader or evidence of mastery. The reading lessons contain substantive diagrams, sanitized proposals, independent worksheets and explained references without remote execution.

## Execution and lifecycle contract

The prepared baseline is Spark4.0.1, Scala binary2.13, JDK17 and Python3.12. Earlier design documents proposed another version tuple; those proposals are not runtime receipts. Runnable Spark programs use the fixed local[2] profiles, disabled UI, loopback driver binding, explicit schemas, UTC, and bounded offline fixtures. They do not assume pandas, PyArrow, JDBC drivers, Kafka, a remote cluster or cloud credentials.

File and streaming examples create only fresh owned roots beneath the current job directory. They preserve source/checkpoint identity within a scenario, use separate namespaces for incompatible or independent queries, await finite queries with deadlines, and stop queries in finally. The introductory streaming sequence also checks that queries are inactive before deleting scratch and preserves scratch if cleanup cannot establish that condition. Session shutdown still runs. Memory sinks are explicitly inspection-only; local atomic manifests are explicitly single-writer process-level demonstrations, not distributed transactions or power-loss proofs.

## Content and independent-oracle evidence

The latest combined focused suite passed **205 tests in 3.13 seconds**: 82 statistics-book checks, 33 Python/SQL deepening checks, and 90 Spark content/fixture/lifecycle checks. The three owned test files previously passed Ruff and strict MyPy; the final unchanged tests remain part of the parent quality gates. The Spark suite independently checks collection/rejection ledgers, revenue identity and missingness, nested child/placeholder counts, timezone boundaries, deterministic winners, duplicate bags, capstone arithmetic, canonical publication digests, half-open join pairs, advanced replay cases, and explicit bounded query lifecycle.

A prose-only editorial pass corrected joined words and punctuation in 58 guide/reference documents. Every code fence and frozen executable source remained unchanged. Runtime source hashes therefore remain comparable with the existing receipts.

## Runtime evidence

Root reported actual prepared-worker acceptance for Scala foundations004-010 and both language variants011-012 and014-029. The 021-022 receipts include actual scan plans, Exchange metrics and job-group task evidence. The 023-029 receipts include broadcast eligibility, adaptive plans, Parquet layouts, Python UDF execution, cache cleanup and staged publication rollback. Relevant files are under work/ with names spark-batch-021-022-{scala,python}-acceptance.jsonl and spark-batch-023-029-{scala,python}-acceptance.jsonl.

Direct readback of current standardized receipts confirms successful matching source hashes for both language variants031-039 and041-042. The031 receipt verifies finite input/progress and batch-equivalent output. The032 receipt includes the observed far-late drop and watermark progression. The035 receipt verifies same-checkpoint recovery and separate replay. The corrected036 references use strict semantic JSON field comparison, preserving integer-width independence while checking exact payload values. The037 scenarios separately reconcile raw fixture rows, filtered scans and committed results. The039 receipts report actual task/partition observations without claiming cluster performance.

An audit across standardized source-hash receipts found **69 matching successful executable variants out of 69**. The parent source-consolidation batches now also cover the eight earlier pilot/foundation variants with current hashes. Direct readback of work/current-reference-evidence.json confirms all69 records are qualified and all69 hashes match the present sources. The final six variants,033,041 and042 in both languages, now pass with matching hashes in work/spark-final-033-041-042-{python,scala}-acceptance.jsonl. Together with the earlier parent-qualified pilot/foundation runs, the complete authored executable route has observed prepared-worker acceptance.

Lesson033 was repaired from observed engine evidence. Its accepted branch reported two input rows and its quarantine branch one for the first three-row raw fixture. Spark4.0.1 filter pushdown reduced those reported scan counts. The lesson now asserts that exact branch-scoped metric behavior while independently counting the literal raw source and reconciling output identity bags. It preserves the deduplication, NULL quarantine and state-eviction checks. Both revised references now have successful matching final execution receipts. Earlier diagnostic output is retained as the failure evidence that motivated the repair, not relabeled as a passing run.

## Important teaching boundaries

- Plans and configuration are distinct from actual metrics. Serialized Exchange dataSize is not labeled remote network bytes, and no tiny elapsed-time result is presented as a cluster speedup.
- Broadcast hints do not repair multiplicity, establish sufficient memory, or guarantee eligibility for every join type.
- Persistence registration, materialization, reuse and cleanup are separately observed, including an injected failure.
- Watermarks use event-time progress and provide a one-sided lateness guarantee. Pending windows and delayed outer rows are kept separate from lost input.
- Deduplication uses business identity, preserves equal-valued distinct events, quarantines missing IDs, and does not promise perpetual memory after state removal.
- Source recovery, event deduplication and external-sink idempotency are different contracts. Local publication and foreachBatch demonstrations state their tested failure boundaries.

## Integration boundary

Content authoring, all42 manifest rows, focused content checks and prepared-worker reference qualification are complete. The final consolidated hash inventory covers69 of69 language references, including the earlier pilot/foundation variants. All repaired or newly advanced references have matching current hashes. Source and reference success still do not certify learner mastery or cluster-scale production behavior. Root owns browser delivery, generated classroom artifacts and whole-repository acceptance. No further executable Spark edits are pending from this author.
