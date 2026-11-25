# spark-029: Restartable batch writes and data-quality contracts

A batch job that crashes halfway must not leave readers looking at half a product, and a retry must not append a second copy. Thirty rows with `value = id * 2` are staged under a run ID, validated by a SHA-256 digest and published by replacing one small `current.json` file, which is the only moment readers can see a new result.

## Level and prerequisites

Advanced; approximately 120 minutes. Direct prerequisites: `spark-028`. Pinned versions: [execution baseline](../execution-baseline.md).

## How to run this lesson

Shared run steps and profile rules: [study guide](../STUDY-GUIDE.md#run-a-paired-lesson).

Learner pads: [Scala](../lessons/spark-029.scala) and [PySpark](../lessons/spark-029.py).

Open the [explained solutions](../solutions/spark-029_solutions.md) after an attempt.

The first worked example sums the declared 30 values and prints `Declared 30-row product total=870`. The second builds receipt text for `run-a` and `run-b`, checks that each points at its own `runs/<run-id>/data` path, and prints `A publication points to one run-specific product`, which is the idea behind publishing a manifest instead of overwriting data in place.

## Learning objectives

- Make a bounded batch product repeatable without confusing overwrite, append and transactional publication.
- Validate the schema, the population `(30, 30, 0, 29, 870)` and the value rule before hashing, so the 64-character lowercase digest stays the same after `repartition(3)` and a 31-row product is rejected instead of hashed.
- Stage a run under `runs/<run-id>`, reject a run ID such as `../outside`, publish with a single replace of `current.json`, and show that an injected failure before the replace and a replay of `run-a` leave the manifest and data file count unchanged.

## Vocabulary and concepts

- **Staging product:** A run-specific output written and validated before readers are told to use it.

- **Publication manifest:** A small record naming the selected data path, run identity, schema, row count and content digest.

- **Publication point:** The operation changing which validated product a reader considers current; here it is a local atomic manifest replacement.

- **Idempotent retry:** Repeating the same logical operation without appending duplicate data or changing the intended published result.

- **Orphan staging data:** A complete or partial run directory that is not referenced by the current publication manifest.

- **Content digest:** A hash of a declared canonical representation; it identifies bytes under that convention rather than proving business correctness on its own.

Writing a dataset and publishing a dataset are separate operations. A reader should not discover a half-written product merely because a staging directory exists. This lesson writes 30 deterministic rows into a run-specific directory, validates their schema and content, then publishes a small current.json manifest. Readers consult that manifest rather than scanning every directory under runs.

The product contract is intentionally concrete: id and value are bigints, IDs 0 through 29 appear exactly once, value equals twice id, and the value total is 870. The canonical digest sorts the 30 rows by id, serializes each row through Spark's JSON representation, joins lines with a newline and no trailing newline, then hashes UTF-8 bytes with SHA-256. Both languages follow the same convention. The small full collection is explicitly bounded by the validated 30-row contract.

A digest is not a substitute for validation. A file full of incorrect rows still has a perfectly valid SHA-256. The validator therefore checks schema, population, identity range, uniqueness, missingness and the value rule before producing the digest. The staged Parquet product is read back and validated again, so the receipt describes actual persisted data rather than only an in-memory input that was intended to be written.

Each run ID is a restricted relative identifier such as run-a. Paths are constructed inside the fresh owned root; manifest metadata cannot choose an arbitrary external file. The receipt records runs/run-a/data, row count 30, the declared schema and the content digest. Validation requires the stored run identity and relative path to match the expected values before opening that fixed owned path. This makes the manifest a governed pointer rather than a general filesystem command.

Publication writes the validated receipt text to a fresh temporary manifest in the same directory as current.json, then replaces the current manifest atomically. On the prepared local filesystem, the rename is the visibility boundary. The code does not claim a distributed transaction, object-store rename guarantee, concurrent multi-writer conflict protocol or power-loss durability. Those need storage-specific semantics and often a transactional catalog or conditional compare-and-swap operation.

The failure scenario starts from a successfully published run-a. Run-b is staged and validated, but an injected error occurs after the temporary manifest is written and before replacement. The temporary manifest is cleaned in finally. The old current.json bytes must remain unchanged, and the reader must still return run-a's 30 rows. The unreferenced run-b directory is an orphan staging product, not another 30 rows in the published logical dataset.

A retry of run-a checks the existing staged receipt and data against the new input's canonical digest. It reuses that validated product rather than appending more files. Repartitioning the same input changes its physical order but not the canonical digest. Replacing current.json with the same deterministic receipt leaves the same logical publication and identical manifest bytes. A source violating the 30-row/value contract is rejected before staging or publication can modify the current pointer.

The reader validates the selected staged receipt against the published manifest before returning the DataFrame. This detects a manifest/receipt inconsistency and keeps the schema/count/digest boundary explicit. It does not make the local data directory immutable against arbitrary concurrent writers. The demonstration has one writer and a fresh namespace, so no other process is authorized to mutate its product during the run.

All run directories and manifests belong to one newly created scratch root under the worker's current directory. Cleanup removes only that root after the scenarios finish. The lesson never resets an existing checkpoint or deletes a user-selected dataset. Retaining prior products for rollback and collecting abandoned staging directories would be operational policies in a persistent service; here their lifecycle is bounded by the standalone demonstration.

This design is more precise than treating overwrite as atomic publication or treating append as an idempotent retry. It gives each phase an observable contract: input validation, staging readback, receipt validation, publication replacement, reader selection and replay. The injected failure demonstrates exactly one process-level boundary rather than claiming every crash or storage failure has been tested.

## Supplied local fixture

The program owns a fresh `.ds60-spark-029-` scratch root with a `runs/` directory inside it. The source is `spark.range(0, 30, 1, 2)` with `value = id * 2`, so the values sum to 870. Each run writes Parquet data and a `receipt.json` with the run ID, data path, row count, schema and digest, and the root-level `current.json` is the only file a reader trusts.

```scala prelude=../solutions/spark-029_solution.scala
import org.apache.spark.sql.functions._
import java.nio.file.{Files, Path, Paths, StandardOpenOption, StandardCopyOption}
import java.nio.charset.StandardCharsets
import java.security.MessageDigest
import java.util.UUID
import scala.jdk.CollectionConverters._
import com.fasterxml.jackson.databind.ObjectMapper

ownedRoot = Files.createTempDirectory(Paths.get(".").toAbsolutePath.normalize(), ".ds60-spark-029-")
Files.createDirectory(ownedRoot.resolve("runs"))
val source = spark.range(0L, 30L, 1L, 2).withColumn("value", col("id") * 2L)
```

```python prelude=../solutions/spark-029_solution.py
from pyspark.sql import functions as F
from pathlib import Path
import tempfile
import shutil
import json
import hashlib
import re
import os
import uuid

owned_root = Path(tempfile.mkdtemp(prefix=".ds60-spark-029-", dir=".")).resolve()
(owned_root / "runs").mkdir()
source = spark.range(0, 30, 1, 2).withColumn("value", F.col("id") * 2)
```

## Worked example / walkthrough

### Worked example 1

```scala
val ids = 0L until 30L
assert(ids.map(_ * 2L).sum == 870L)
println("Declared 30-row product total=870")
```

```python
ids = range(30)
assert sum(i * 2 for i in ids) == 870
print("Declared 30-row product total=870")
```

The arithmetic oracle describes the product before any writer runs. A successful write command or content hash is insufficient if the rows violate this expected identity and value contract.

### Worked example 2

```scala
val a = receiptText("run-a", "0" * 64); val b = receiptText("run-b", "0" * 64)
assert(mapper.readTree(a).get("data_path").asText() == "runs/run-a/data")
assert(a != b)
println("A publication points to one run-specific product")
```

```python
a = receipt_text("run-a", "0" * 64)
b = receipt_text("run-b", "0" * 64)
assert json.loads(a)["data_path"] == "runs/run-a/data" and a != b
print("A publication points to one run-specific product")
```

These synthetic receipt strings illustrate run identity without publishing anything. The zero digest is not accepted as data evidence; real receipts are created only after actual product validation. Distinct run paths prevent a partially written replacement from modifying the old product in place.

## Exercises

### Exercise 1: Validate the product before computing its digest

Require ordered fields id, value with bigint types, exactly 30 known unique IDs 0..29, known values equal to 2*id and total 870. Return SHA-256 of sorted Spark JSON lines joined by newline without a trailing newline.

**Expected result/shape:** A 64-character lowercase digest for the valid product. Wrong values, counts, types or identities are rejected before hashing.

**Verify:** Assert a 64-hex digest and equal digest after repartitioning; reject a 31-row source.

**Progressive hint:** Schema/count/domain checks precede the bounded 30-row canonical collection.

### Exercise 2: Stage a run and validate the persisted readback

Restrict run IDs to 1..32 lowercase letters, digits or hyphens. Validate input, write a fresh run-specific Parquet product, validate readback and save its receipt. If that run already exists, require its validated digest to match instead of appending.

**Expected result/shape:** run-a has one 30-row data product and a receipt with the declared schema/count/path/digest. Reusing it never appends another product.

**Verify:** Assert staged receipt existence and digest equality; all paths remain within the fresh owned root.

**Progressive hint:** Validate first; use error-if-exists for a new data path and a readback check before creating its receipt.

### Exercise 3: Validate a receipt against a fixed owned data path

Read a run receipt and require its run_id, data_path, row_count, schema and digest to match the declared contract and actual Parquet readback. Construct the read path from validated runId rather than trusting arbitrary receipt text.

**Expected result/shape:** Valid run-a receipt returns unchanged. A traversal-style run ID is rejected before path access.

**Verify:** Assert receipt equality and explicit rejection of../outside.

**Progressive hint:** Metadata is evidence to validate, not authority to read any path it names.

### Exercise 4: Publish only a validated run at one explicit visibility point

Validate the staged receipt, write it to a fresh temporary manifest beside current.json, and atomically replace current.json. Support an injected failure before replacement and clean any unpublished temporary manifest in finally.

**Expected result/shape:** Publishing run-a creates current.json selecting its 30-row product. No data is appended or rewritten during publication.

**Verify:** Assert the current manifest equals the validated receipt and points to run-a.

**Progressive hint:** The same-filesystem manifest replacement is the local visibility boundary; it is not a generic object-store transaction.

### Exercise 5: Keep the previous publication readable after an interrupted replacement

Read the current manifest, validate its selected run and return that product. Stage run-b, inject failure before its manifest replacement, and confirm the reader still sees run-a.

**Expected result/shape:** The injected error occurs, current.json bytes remain identical to run-a, and the published product still has 30 rows with the original digest.

**Verify:** Assert the named exception, unchanged manifest and exact published product digest; run-b staging must not enter the reader population.

**Progressive hint:** Read through the manifest, not by globbing every runs/*/data directory.

### Exercise 6: Replay the same input without appending another product

Compose stage, validate/publish and readback for a repeated run ID. Retry run-a with a different execution partition layout, then attempt an invalid 31-row product and confirm publication stays intact.

**Expected result/shape:** Manifest bytes and data-file count are unchanged by valid run-a replay; published count remains 30. Invalid input fails before changing current.json.

**Verify:** Assert digest, manifest bytes, file-count equality and negative-control rejection.

**Progressive hint:** A retry is content-aware reuse of a validated run, not append or blind overwrite.

## Common pitfalls

Do not call append an idempotent retry or assume overwrite is atomic publication. A digest cannot certify business correctness without schema and row validation. Never trust an arbitrary path in metadata or reset an unrelated checkpoint. Local atomic rename is not a portable distributed-store transaction or a power-loss durability proof. Treat unreferenced staging runs as orphans requiring an ownership-aware retention policy; do not make readers discover them through a broad directory glob.

## Self-check

- The digest function refuses a frame whose population is not `(30, 30, 0, 29, 870)`. Why check counts and values before hashing instead of hashing whatever arrives?
- Run IDs may contain only 1 to 32 lowercase letters, digits and hyphens. Which directory would `../outside` escape, and why validate the ID before opening any file?
- Exercise 5 injects a failure after the pending manifest is written but before `os.replace`. Which run does `current.json` still name, and what removes the pending file?
- Replaying `run-a` with a repartitioned source returns the same digest without adding files. Which branch of the staging function makes that possible, and what happens if the replayed content differs?

## Next step

Go on to [spark-030: Deployment topology and dependency boundaries](spark-030.md). Everything so far ran on one machine in `local[2]`; the next lesson is a reading lesson about what changes when the driver, the executors and their dependencies live in different places.

## Primary sources and official APIs

- [Spark 4.3.0 save modes and file writes](https://spark.apache.org/docs/4.3.0/sql-data-sources-load-save-functions.html)

- [Java 17 Files.move atomic-move contract](https://docs.oracle.com/en/java/javase/17/docs/api/java.base/java/nio/file/Files.html#move(java.nio.file.Path,java.nio.file.Path,java.nio.file.CopyOption...))

- [Python os.replace](https://docs.python.org/3/library/os.html#os.replace)

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning to coach me through spark-029: Restartable batch writes and data-quality contracts.
Read courses/scala-spark/guides/spark-029.md and courses/scala-spark/lessons/spark-029.py; the paired sources are courses/scala-spark/lessons/spark-029.scala and courses/scala-spark/lessons/spark-029.py.
Direct prerequisites: spark-028. Explain the schema, row grain and new Scala/Python/Spark syntax, ask me to predict a concrete result, then inspect my attempt. Give one hint at a time, review exact result and boundary evidence, and ask retrieval questions in my own words. Do not read solutions/ until I ask or have made an honest attempt.
Use only the prepared local[2] worker profile and owned job scratch. Do not download dependencies, start a remote service, reset existing checkpoints or alter unrelated learner work.
Done when all six contracts have inspected evidence and I can explain the stated assumptions and a meaningful failure case.
```
