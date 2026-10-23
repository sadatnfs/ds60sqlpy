# k8s-016: Explanatory solutions

These answers explain the stated synthetic and scoped runtime contracts. Static checks do not prove cluster acceptance.

## Mechanism

An ordinary init container completes before the application containers start. It can prepare a synthetic file or validate a prerequisite. An emptyDir volume belongs to the Pod lifetime and can be shared by its containers. Restarting an application container normally preserves that volume, while replacing the Pod creates a different emptyDir.

The supplied real Pod manifest is an explicit host-lab example. The browser adapter does not admit initContainers, emptyDir or arbitrary command bodies. A teacher must review the exact fixed commands and provide the owned capability before live use. The finite example writes the Pod UID into a marker, then deliberately makes the reader fail once and succeed on its next container attempt.

The marker makes lifetime observable:it matches the same Pod UID across the application restart and changes when a new Pod is created. A constant hello marker alone would be weaker evidence because a new init container could recreate identical bytes after replacement.

## Exercise 1: Draw container order

The init container supplies the file dependency. If it never completes successfully, the application cannot demonstrate the read path. The ordering is a Kubernetes lifecycle contract, not a sleep inserted into application code.

**Expected:** prepare completes before read starts.

## Exercise 2: Trace the shared volume

The mount links the containers to one Pod-owned volume. Read-only root filesystems do not prohibit a separately admitted writable volume. The scope is still synthetic and bounded, with no host personal path.

**Expected:** Both containers access the same /work emptyDir within one Pod.

## Exercise 3: Observe one application restart

The first application exit2 triggers OnFailure restart. Its marker and flag remain in the Pod volume, so the next attempt can distinguish itself. Actual timing and status must be observed rather than copied from this trace.

**Expected:** Same Pod UID/marker across the failed first and successful next application attempt.

## Exercise 4: Compare a new Pod

The init step writes the new UID, which differentiates recreated bytes from persistent storage. This avoids falsely claiming that a constant marker survived when it was merely generated again.

**Expected:** New Pod UID, new marker and fresh attempt sequence.

## Exercise 5: Diagnose an init failure

The first failed stage is initialization. Correct the declared shared path or intended nonroot access in the owned fixture, then verify the init exit and application output. Broad privilege changes are not a justified diagnosis.

**Expected:** Application absence is explained by init failure; the smallest mount/permission repair is identified.

## Exercise 6: State the storage limit

A successful container restart proves only continuity within that Pod lifetime. A backup must survive the relevant failure independently and be restored/verified. The example intentionally stops short of that claim.

**Expected:** emptyDir lifetime is tied to the Pod; durability and independent recovery require later storage/backup contracts.

## Boundary and troubleshooting review

If the init container fails, the application may never start; inspect initContainerStatuses rather than expecting application logs. If the marker cannot be written, inspect the volume mount and nonroot permissions before relaxing the security context globally. A missing file in the application can indicate a different mount name or path.

The offline script checks a lifetime model only. A live claim needs the actual UID and restart/log evidence. Neither a persisted marker in emptyDir nor a successful Pod restart is a backup or proof of PVC behavior.
