# k8s-036: Explanatory solutions

These answers explain the stated synthetic and scoped runtime contracts. Static checks do not prove cluster acceptance.

## Mechanism

Kubernetes stores API state in its control-plane data store. An etcd snapshot can preserve that stored state, including object specifications and potentially sensitive values. It does not automatically copy the bytes inside an application's persistent volume. A restored Deployment or PVC object and a restored application file are therefore different recovery outcomes.

This chapter uses two synthetic inventories: an API snapshot describing a workload and its claim, and an independent data backup containing a marker. A complete recovery exercise must inspect both. A PVC can exist after API restoration while the underlying data is absent, inaccessible or from a different point in time. Likewise, correct bytes alone do not prove the application or its access controls were restored correctly.

Actual snapshot and restore operations are host-owned procedures for a dedicated synthetic cluster. The course worker does not gain etcd credentials or control-plane filesystem access. Snapshots may contain Secrets even when this particular exercise uses dummy data, so private backup material never belongs in portable progress exports, lesson fixtures or chat output.

## Exercise 1: Build the source inventory

The API data store records Kubernetes state, while workload data can live in a separate storage system. Treating the claim object as the file backup confuses a reference to storage with the contents of that storage.

**Expected:** Two distinct sources and restore checks.

## Exercise 2: Record a synthetic data checksum

Recomputing both expected and actual from the restored file would make the check meaningless. The expected digest belongs to the captured backup record, and the read-only verification must inspect the restored application path.

**Expected:** Equal bytes match; changed bytes fail the reference digest.

## Exercise 3: Define consistency assumptions

The fixture deliberately holds data constant so the learner can isolate restoration boundaries. A real database requires its own consistency and recovery design, which cannot be inferred from a successful marker copy.

**Expected:** No claim of database-consistent backup or log replay.

## Exercise 4: Evaluate the partial restore

The separate failure row prevents a misleading success report. It also points to the correct repair path: investigate or repeat the qualified data restoration, rather than merely restarting an already Ready Pod.

**Expected:** Overall recovery fails until both API and data gates pass.

## Exercise 5: Protect backup material

Operational evidence should identify the procedure and outcome without copying the source of sensitive data. Access, encryption and retention belong to the host backup contract and are distinct from the classroom checksum exercise.

**Expected:** No snapshots or secrets in portable progress; only bounded metadata and synthetic checksums.

## Exercise 6: Review target isolation and cleanup

The host must prove the intended destination before executing a restore and retain a recovery path for failures. The lesson worksheet alone never authorizes arbitrary control-plane changes or deletion of unrelated volumes.

**Expected:** No restore into an ambient or shared target; exact owned cleanup.

## Boundary and troubleshooting review

If the API object exists but the marker hash is wrong, recovery has not met the application-data contract. If the marker is correct but the Service route is broken, recovery has not met the serving contract. A Ready Pod alone proves neither complete restoration nor acceptable data loss.

Never use a live production snapshot as a convenient classroom fixture. The synthetic rehearsal makes scope visible while avoiding personal or organizational data. A passed rehearsal establishes the tested procedure and version combination, not universal restore compatibility.
