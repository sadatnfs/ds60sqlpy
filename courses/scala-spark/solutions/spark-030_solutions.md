# spark-030: Explained architecture references

Compare these answers after an attempt at the [worksheet](../lessons/spark-030.md). Each answer states the mechanism, a failure case and a reviewable contract. No remote resource was contacted to author or validate this reading lesson.

## Exercises and reasoning

### Exercise 1: Assign responsibilities in three deployment diagrams

**Expected:** A role/location table for all three layouts, with collect returning to the driver wherever it runs and resource allocation assigned to the cluster manager.

In the classroom layout, the owned worker hosts the classic driver and local task execution. In client mode, the submitting environment hosts the driver while separate executor processes perform tasks. In cluster mode, the manager launches the driver in the cluster, and the submitting host is no longer the driver's filesystem or Python environment. In both remote layouts the manager allocates resources and the application driver schedules its work.

A collect action sends results to the driver, not necessarily to the user's laptop. Its 30-row bound must therefore protect the memory and result channel of the actual driver. A client-mode driver can fail when the submitting machine disappears or becomes unreachable. A cluster-mode driver can fail to import a dependency that existed only on the submitting machine. These are topology-specific failure hypotheses requiring observations at the affected process, not a claim that one deploy mode is universally superior.

**Verification evidence:** Name every role and trace a collected 30-row result to the actual driver process in each layout; identify the submitting-host-loss or remote-driver-environment failure.

### Exercise 2: Repair a driver-only input path assumption

**Expected:** An explicit data-location/distribution contract naming driver and executor visibility, authorization,30-row fixture identity and readback verification.

The submitted path is insufficient because neither the cluster driver nor the executors are known to share the submitting host's local filesystem. Do not replace it with an invented production bucket or claim that a cluster manager copies arbitrary paths. The review should propose an authorized shared URI or an explicit distribution mechanism suitable for this bounded fixture, with an owner and a content identifier.

Acceptance would check the 30-row schema and digest from the actual runtime location and demonstrate that both the driver and required task processes can read through the chosen mechanism. If the file is only a small task-side auxiliary artifact, the distribution method and task-side lookup API must be named. If it is the dataset itself, normal shared-source access is usually a clearer contract. This worksheet establishes the missing requirement; it does not perform a remote read or grant access.

**Verification evidence:** Reject automatic shared-path assumptions and list the exact host/process where existence and content must be checked.

### Exercise 3: Map dependencies to driver and executor environments

**Expected:** A matrix locating each dependency and its qualification evidence; reject a Scala 3 binary substitution and treating a native wheel as an ordinary pure-Python source zip.

TheScala jar must be compiled for the declaredScala 2.13 binary family and checked against the selectedSpark 4.0.1/JDK 17 runtime. AScala 3-suffixed artifact is not a documented substitute for this prepared profile. Driver and executor classpaths must receive the required application classes through the actual submission/package mechanism, and a local compile receipt alone does not prove remote class loading.

The purePythonrules.zip can be a candidate for a supported Python-file distribution mechanism. Imports used by driver code must work in the driver's interpreter; imports used by task code must work in executor Python processes. A native-extension wheel additionally depends on interpreter ABI, platform and shared-library compatibility, so treating it as a source zip is insufficient. A qualified image or environment-archive approach could provide those layers, but its exact versions and bounded import/task receipt are still required. The worksheet neither installs that environment nor downloads packages.

**Verification evidence:** Name compiler/binary family, Python interpreter/platform compatibility and worker import checks separately.

### Exercise 4: Review a captured connection and a retrying task

**Expected:** No connection object serialized from the driver; a defined task-side resource lifecycle if externalIO is later authorized, and a stable operation identity preventing duplicate external effects.

An open connection belongs to the driver process and is not a valid portable task argument. Replacing it with small serializable configuration addresses only transmission, not authorization or correctness. If externalIO is part of a later authorized design, task-side code needs a bounded resource lifecycle with explicit open/use/close behavior and a concurrency budget suited to the destination.

The audit write also needs an idempotency or transactional protocol keyed by stable logical operation identity. A retry can invoke the function again even when the first external write succeeded before the task failed. A task-attempt counter is not automatically the business operation key. Acceptance would inject a retry around the external-effect boundary and inspect exactly one logical destination result, while also proving connections are closed on failure. No live database or audit service is used by this worksheet.

**Verification evidence:** Explain why serializability alone would not guarantee exactly-once writes and name the cleanup and deduplication evidence needed.

### Exercise 5: Define the Connect adapter boundary honestly

**Expected:** Classic internals are not assumed available; semantic goldens are retained while a separate supported diagnostic/runtime adapter is qualified.

Spark Connect separates the client from server-side execution through a logical-plan interface. It does not expose every classicSparkContext, RDD or internalJVM handle used in the local diagnostic recipes. Keep the lessons' independent row/schema/bag goldens, but map transformations and observations to supported Connect capabilities instead of pretending _jdf is a transport-neutral interface.

A readiness contract should pin client/server versions and test required APIs, session creation and closure, cancellation of bounded work, result-size limits, authentication handling and clear errors for unsupported diagnostics. It should also verify that a failed remote action cannot be mistaken for a saved local pad or a completed lesson. The existing local classic receipt establishes none of those remote facts. Until a separately implemented and tested adapter exists, the proposed profile remains a design candidate rather than an executable classroom capability.

**Verification evidence:** List client/server version checks, API support, cancellation, result limits, authentication and cleanup receipts without claiming any already ran.

### Exercise 6: Write a reviewable deployment acceptance checklist

**Expected:** A bounded acceptance plan separating proposed configuration, artifact inspection, remote execution and production readiness; unresolved path/package/Connect gaps remain explicit.

The record should first identify the intended platform, driver placement, dependency versions, input identity, credential source, resource limits and owner. It should then attach inspected artifact hashes and compatibility checks, distinguishing them from a future bounded remote run. That run would need observed driver/executor versions, successful task-side imports, authorized input readback, exact 30-row output, bounded result transfer and cleanup/cancellation evidence.

Production readiness is a further tier involving representative data volumes, availability, monitoring, concurrency and operational rollback. The proposed remote path and native-package environment remain open requirements, and the Connect adapter remains separate work. A failure action should preserve artifacts and logs, stop only owned work and return to the last qualified implementation. The worksheet approves no deployment and starts no service; its deliverable is a concrete evidence plan that another reviewer can assess before any remote action is considered.

**Verification evidence:** Name concrete artifacts and receipts, owners and failure actions; do not mark deployment accepted based on diagram orsyntax alone.

## Evidence boundary

These explanations are design-review references. They do not establish a completed deployment, package installation, live database snapshot or remote compatibility result. A future execution must use the named bounded inputs and record its own versioned receipts. Preserve the distinction between a proposed control, an inspected configuration and an observed result.
