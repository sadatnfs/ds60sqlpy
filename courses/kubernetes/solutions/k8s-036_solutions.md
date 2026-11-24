# k8s-036: Explanatory solutions

These answers explain the stated synthetic and scoped runtime contracts. Static checks do not prove cluster acceptance.

## Mechanism

Kubernetes stores API state in its control-plane data store. An etcd snapshot can preserve that stored state, including object specifications and potentially sensitive values. It does not automatically copy the bytes inside an application's persistent volume. A restored Deployment or PVC object and a restored application file are therefore different recovery outcomes.

This chapter uses two synthetic inventories: an API snapshot describing a workload and its claim, and an independent data backup containing a marker. A complete recovery exercise must inspect both. A PVC can exist after API restoration while the underlying data is absent, inaccessible or from a different point in time. Likewise, correct bytes alone do not prove the application or its access controls were restored correctly.

Actual snapshot and restore operations are host-owned procedures for a dedicated synthetic cluster. The course worker does not gain etcd credentials or control-plane filesystem access. Snapshots may contain Secrets even when this particular exercise uses dummy data, so private backup material never belongs in portable progress exports, lesson fixtures or chat output.

## Exercise 1: Build the source inventory

The API data store records Kubernetes state, while workload data can live in a separate storage system. Treating the claim object as the file backup confuses a reference to storage with the contents of that storage.

**Expected:** Two distinct sources and restore checks.

**Solution reasoning**

- **Approach:** List each item, where its bytes live and which backup captures them.
- **Why it is correct:** API objects live in etcd and appear in a control plane snapshot, while the marker lives on the volume and needs a data backup.
- **Plausible wrong approach:** Assuming an etcd snapshot includes PVC contents restores the claim object with no data behind it.
- **How to verify:** Two sources and two restore checks are named.

## Exercise 2: Record a synthetic data checksum

Recomputing both expected and actual from the restored file would make the check meaningless. The expected digest belongs to the captured backup record, and the read-only verification must inspect the restored application path.

**Expected:** Equal bytes match; changed bytes fail the reference digest.

**Solution reasoning**

- **Approach:** Compute SHA-256 of the fixed and changed marker and compare each with the reference digest.
- **Why it is correct:** Any byte change produces a different digest, so only the unchanged marker matches.
- **Plausible wrong approach:** Comparing file sizes would pass a same-length change.
- **How to verify:** The fixed marker matches the reference, and the changed one does not.

## Exercise 3: Define consistency assumptions

The fixture deliberately holds data constant so the learner can isolate restoration boundaries. A real database requires its own consistency and recovery design, which cannot be inferred from a successful marker copy.

**Expected:** No claim of database-consistent backup or log replay.

**Solution reasoning**

- **Approach:** State what makes the immutable marker easy to back up and name a live database property it lacks.
- **Why it is correct:** A file that never changes has no in-flight writes, so a copy at any moment is consistent.
- **Plausible wrong approach:** Treating a file copy of a running database as consistent ignores open transactions and unflushed pages.
- **How to verify:** The answer names a property such as concurrent writes and makes no database consistency claim.

## Exercise 4: Evaluate the partial restore

The separate failure row prevents a misleading success report. It also points to the correct repair path: investigate or repeat the qualified data restoration, rather than merely restarting an already Ready Pod.

**Expected:** Overall recovery fails until both API and data gates pass.

**Solution reasoning**

- **Approach:** Evaluate the API gate and data gate separately and combine with AND.
- **Why it is correct:** Restored objects with wrong data are not a recovery, so both gates must pass.
- **Plausible wrong approach:** Reporting partial success because objects returned hides that the data is wrong.
- **How to verify:** API passes, data fails and overall recovery fails.

## Exercise 5: Protect backup material

Operational evidence should identify the procedure and outcome without copying the source of sensitive data. Access, encryption and retention belong to the host backup contract and are distinct from the classroom checksum exercise.

**Expected:** No snapshots or secrets in portable progress; only bounded metadata and synthetic checksums.

**Solution reasoning**

- **Approach:** Mark snapshots and credentials private and allow only bounded metadata and synthetic checksums in progress.
- **Why it is correct:** Snapshots contain every Secret in the cluster, so sharing one exposes credentials beyond this lesson.
- **Plausible wrong approach:** Attaching the snapshot as proof of backup publishes all stored Secrets.
- **How to verify:** Each item is classified, and no snapshot or secret is shareable.

## Exercise 6: Review target isolation and cleanup

The host must prove the intended destination before executing a restore and retain a recovery path for failures. The lesson worksheet alone never authorizes arbitrary control-plane changes or deletion of unrelated volumes.

**Expected:** No restore into an ambient or shared target; exact owned cleanup.

**Solution reasoning**

- **Approach:** Name the dedicated source and destination and list exact identities for disposal.
- **Why it is correct:** Restoring into a shared cluster could overwrite objects owned by others, and exact identities bound the cleanup.
- **Plausible wrong approach:** Restoring into the current kubeconfig context targets whatever cluster happens to be active.
- **How to verify:** The destination is dedicated and owned, and disposal names exact identities.

## Boundary and troubleshooting review

If the API object exists but the marker hash is wrong, recovery has not met the application-data contract. If the marker is correct but the Service route is broken, recovery has not met the serving contract. A Ready Pod alone proves neither complete restoration nor acceptable data loss.

Never use a live production snapshot as a convenient classroom fixture. The synthetic rehearsal makes scope visible while avoiding personal or organizational data. A passed rehearsal establishes the tested procedure and version combination, not universal restore compatibility.
