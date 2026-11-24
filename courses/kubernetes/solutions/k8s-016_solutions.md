# k8s-016: Explanatory solutions

These answers explain the stated synthetic and scoped runtime contracts. Static checks do not prove cluster acceptance.

## Mechanism

An ordinary init container completes before the application containers start. It can prepare a synthetic file or validate a prerequisite. An emptyDir volume belongs to the Pod lifetime and can be shared by its containers. Restarting an application container normally preserves that volume, while replacing the Pod creates a different emptyDir.

The supplied real Pod manifest is an explicit host-lab example. The browser adapter does not admit initContainers, emptyDir or arbitrary command bodies. A teacher must review the exact fixed commands and provide the owned capability before live use. The finite example writes the Pod UID into a marker, then deliberately makes the reader fail once and succeed on its next container attempt.

The marker makes lifetime observable: it matches the same Pod UID across the application restart and changes when a new Pod is created. A constant hello marker alone would be weaker evidence because a new init container could recreate identical bytes after replacement.

## Exercise 1: Draw container order

The init container supplies the file dependency. If it never completes successfully, the application cannot demonstrate the read path. The ordering is a Kubernetes lifecycle contract, not a sleep inserted into application code.

**Expected:** prepare completes before read starts.

**Solution reasoning**

- **Approach:** Read the Pod spec's initContainers list, then containers, and mark prepare as a gate in front of read.
- **Why it is correct:** The kubelet runs init containers to completion one at a time and starts application containers only after every init container exits 0.
- **Plausible wrong approach:** Expecting prepare and read to start together, like two entries in containers, predicts that read may find no file yet.
- **How to verify:** initContainerStatuses shows prepare terminated with exit 0 before read appears running in containerStatuses.

## Exercise 2: Trace the shared volume

The mount links the containers to one Pod-owned volume. Read-only root filesystems do not prohibit a separately admitted writable volume. The scope is still synthetic and bounded, with no host personal path.

**Expected:** Both containers access the same /work emptyDir within one Pod.

**Solution reasoning**

- **Approach:** Follow the name work from spec.volumes to the volumeMounts of both prepare and read.
- **Why it is correct:** An emptyDir is created once per Pod, so every mount that references the same volume name sees the same directory at /work.
- **Plausible wrong approach:** Assuming each container gets its own copy because its filesystem is separate would predict read finds nothing the init container wrote.
- **How to verify:** One emptyDir named work exists, and both mounts reference that name with mountPath /work.

## Exercise 3: Observe one application restart

The first application exit 2 triggers OnFailure restart. Its marker and flag remain in the Pod volume, so the next attempt can distinguish itself. Actual timing and status must be observed rather than copied from this trace.

**Expected:** Same Pod UID/marker across the failed first and successful next application attempt.

**Solution reasoning**

- **Approach:** Run the teacher fixture once and compare Pod UID, marker and restartCount across both application attempts.
- **Why it is correct:** A container restart happens inside the same Pod, so the emptyDir and the marker written by prepare survive while restartCount increments.
- **Plausible wrong approach:** Expecting prepare to rerun and write a new marker treats a container restart as a Pod restart.
- **How to verify:** Pod UID and marker match across attempts, and only restartCount changed.

## Exercise 4: Compare a new Pod

The init step writes the new UID, which differentiates recreated bytes from persistent storage. This avoids falsely claiming that a constant marker survived when it was merely generated again.

**Expected:** New Pod UID, new marker and fresh attempt sequence.

**Solution reasoning**

- **Approach:** Delete only the recorded owned Pod through the host capability and read the replacement.
- **Why it is correct:** A new Pod gets a new UID and a new emptyDir, so prepare runs again and writes a fresh marker.
- **Plausible wrong approach:** Expecting the old marker to persist assumes emptyDir lives outside the Pod, which it does not.
- **How to verify:** UID and marker both differ, and the old marker is nowhere in the new record.

## Exercise 5: Diagnose an init failure

The first failed stage is initialization. Correct the declared shared path or intended nonroot access in the owned fixture, then verify the init exit and application output. Broad privilege changes are not a justified diagnosis.

**Expected:** Application absence is explained by init failure; the smallest mount/permission repair is identified.

**Solution reasoning**

- **Approach:** Start with prepare's state and reason, then name the single mount or permission fix.
- **Why it is correct:** If an init container fails, the kubelet never starts the application container, so read's absence follows from prepare.
- **Plausible wrong approach:** Debugging the read container as a second fault chases a container that never started and has no logs.
- **How to verify:** The init state shows the failure reason, and the proposed repair touches one mount or permission.

## Exercise 6: State the storage limit

A successful container restart proves only continuity within that Pod lifetime. A backup must survive the relevant failure independently and be restored/verified. The example intentionally stops short of that claim.

**Expected:** emptyDir lifetime is tied to the Pod; durability and independent recovery require later storage/backup contracts.

**Solution reasoning**

- **Approach:** Name Pod deletion as the end of the marker and point to a PersistentVolumeClaim and a separate backup as the later contracts.
- **Why it is correct:** emptyDir is removed when the Pod leaves its node, so nothing written there survives replacement, and no copy exists elsewhere.
- **Plausible wrong approach:** Calling the shared file persistent because it survived a container restart confuses container lifetime with Pod lifetime.
- **How to verify:** The answer names Pod deletion and a later storage or backup mechanism that would survive it.

## Boundary and troubleshooting review

If the init container fails, the application may never start; inspect initContainerStatuses rather than expecting application logs. If the marker cannot be written, inspect the volume mount and nonroot permissions before relaxing the security context globally. A missing file in the application can indicate a different mount name or path.

The offline script checks a lifetime model only. A live claim needs the actual UID and restart/log evidence. Neither a persisted marker in emptyDir nor a successful Pod restart is a backup or proof of PVC behavior.
