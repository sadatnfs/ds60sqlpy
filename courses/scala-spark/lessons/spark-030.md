# spark-030: Learner architecture worksheet

Read the [guide](../guides/spark-030.md). These are sanitized reasoning fixtures, not executable deployment instructions. Retain an independent answer and the evidence supporting it for each task.

## Worked example / walkthrough

### Worked example 1: A local path that does not cross the boundary

```text
Driver host: /driver-local/input.parquet exists
Executor host: same path absent
Task: read that path directly inside executor code
Expected observation: path availability is not established on the executor
```

The existence check proves only one host's local state. The corrected design must specify authorized shared storage or an explicit bounded distribution mechanism and verify it where the task runs. It must not claim that client deploy mode alone makes the file shared.

### Worked example 2: A classic diagnostic that needs a new adapter

```text
Existing lesson: frame._jdf.queryExecution().executedPlan()
Proposed client: Spark Connect
Available evidence: local classic worker receipt only
Review result: Connect diagnostic path is unimplemented and unqualified
```

The logical transformation may have a supported Connect equivalent while the internal JVM inspection does not. Keep the useful semantic oracle, replace the diagnostic boundary through supported capabilities, and qualify that adapter separately before presenting it as runnable.

## Exercises

### Exercise 1: Assign responsibilities in three deployment diagrams

Annotate the local, client-mode and cluster-mode diagrams with driver location, executor/task execution, resource allocation and result collection. Explain one failure introduced by moving the driver.

**Inputs/evidence:** For spark-030 Exercise 1, The three diagrams and the proposal stating cluster deploy mode.

**Expected result/shape:** For spark-030 Exercise 1, A role/location table for all three layouts, with collect returning to the driver wherever it runs and resource allocation assigned to the cluster manager.

**Verify:** Name every role and trace a collected 30-row result to the actual driver process in each layout; identify the submitting-host-loss or remote-driver-environment failure.

**Progressive hint:** Deploy mode changes driver placement; the cluster manager and executors do not become synonyms for the driver.

### Exercise 2: Repair a driver-only input path assumption

Review the proposed/driver-local/input.parquet path. State the visibility problem and specify a bounded replacement contract without choosing or contacting a real service.

**Inputs/evidence:** For spark-030 Exercise 2, The input path in the sanitized proposal and evidence that the file exists only on the submitting machine.

**Expected result/shape:** For spark-030 Exercise 2, An explicit data-location/distribution contract naming driver and executor visibility, authorization,30-row fixture identity and readback verification.

**Verify:** Reject automatic shared-path assumptions and list the exact host/process where existence and content must be checked.

**Progressive hint:** A path string is interpreted in a filesystem namespace; identical spelling does not imply identical storage.

### Exercise 3: Map dependencies to driver and executor environments

Produce a dependency matrix for the Scala jar, purePythonrules.zip, a hypothetical native-extension wheel and JDK/Spark runtime. State which proposed substitution is unsupported.

**Inputs/evidence:** For spark-030 Exercise 3, Spark 4.0.1, Scala binary 2.13, JDK 17, course_2.13.jar, rules.zip and an unqualified native-extension wheel.

**Expected result/shape:** For spark-030 Exercise 3, A matrix locating each dependency and its qualification evidence; reject a Scala 3 binary substitution and treating a native wheel as an ordinary pure-Python source zip.

**Verify:** Name compiler/binary family, Python interpreter/platform compatibility and worker import checks separately.

**Progressive hint:** A source archive can distribute modules without supplying an interpreter or native shared libraries.

### Exercise 4: Review a captured connection and a retrying task

Reject a task closure that captures an open driver database connection and writes one audit row per invocation. Propose separate serialization, lifecycle and idempotency contracts.

**Inputs/evidence:** For spark-030 Exercise 4, An open driver connection captured by a task function and evidence that a failed task can be retried.

**Expected result/shape:** For spark-030 Exercise 4, No connection object serialized from the driver; a defined task-side resource lifecycle if externalIO is later authorized, and a stable operation identity preventing duplicate external effects.

**Verify:** Explain why serializability alone would not guarantee exactly-once writes and name the cleanup and deduplication evidence needed.

**Progressive hint:** Task execution can repeat. Resource process ownership and external-write logical identity are separate issues.

### Exercise 5: Define the Connect adapter boundary honestly

Classify which existing classic capabilities can be assumed in a proposedConnect profile, and list the compatibility and lifecycle tests required before exposing it as ready.

**Inputs/evidence:** For spark-030 Exercise 5, The existing _jdf/queryExecution and RDD-based diagnostic helpers, plus the proposed remote logical-plan client.

**Expected result/shape:** For spark-030 Exercise 5, Classic internals are not assumed available; semantic goldens are retained while a separate supported diagnostic/runtime adapter is qualified.

**Verify:** List client/server version checks, API support, cancellation, result limits, authentication and cleanup receipts without claiming any already ran.

**Progressive hint:** A server URL does not implement the missing API and lifecycle boundary.

### Exercise 6: Write a reviewable deployment acceptance checklist

Turn the sanitized proposal into a go/no-go review record with explicit evidence tiers and rollback ownership. Keep the worksheet read-only.

**Inputs/evidence:** For spark-030 Exercise 6, All previous design findings, the 30-row/schema/digest contract and only an existing local classic runtime receipt.

**Expected result/shape:** For spark-030 Exercise 6, A bounded acceptance plan separating proposed configuration, artifact inspection, remote execution and production readiness; unresolved path/package/Connect gaps remain explicit.

**Verify:** Name concrete artifacts and receipts, owners and failure actions; do not mark deployment accepted based on diagram orsyntax alone.

**Progressive hint:** A checked configuration is useful evidence but is not a completed remote run.
