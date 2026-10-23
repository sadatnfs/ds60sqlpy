# k8s-022: Explanatory solutions

These answers explain the stated synthetic and scoped runtime contracts. Static checks do not prove cluster acceptance.

## Mechanism

Persistent storage separates data lifetime from a particular Pod. A PersistentVolumeClaim requests storage through an access mode, capacity and StorageClass. A PersistentVolume represents provisioned storage and its lifecycle policy. A StatefulSet adds stable Pod identity and per-replica claim naming, but it does not turn a filesystem into a backup or a complete database recovery system.

The host fixture uses a prequalified StorageClass named lesson-local and a single-replica StatefulSet store. Its claim template data produces a claim associated with store-0. The example explicitly retains claims when the StatefulSet is deleted or scaled down. The normal browser adapter does not create PVCs, StatefulSets or storage classes.

A live persistence test writes a synthetic marker once, records its checksum, replaces the application Pod by exact UID and reads the marker through a separate bounded reader. Re-running an initializer that overwrites the same marker would hide data loss, so initialization and verification must be separate operations.

## Exercise 1: Trace storage references

The manifest describes desired storage. Binding status and application access need runtime evidence. A missing class is a capability problem, not a reason to substitute an arbitrary hostPath.

**Expected:** The data claim is mounted at /data and depends on a qualified lesson-local class.

## Exercise 2: Record initial data once

An initializer that recreates the expected bytes after loss can fake persistence. The writer should refuse an existing marker or otherwise make initialization history explicit, while later readers remain read-only.

**Expected:** One initialization receipt, claim/PV identities and a known marker checksum.

## Exercise 3: Replace only the Pod

The StatefulSet can replace a Pod while reusing its claim. The before/after graph should show which identity changed and which remained, not merely a familiar Pod name.

**Expected:** New Pod UID with the intended stable ordinal and same claim binding.

## Exercise 4: Verify the marker independently

The independent read closes the application-data boundary. It catches empty or wrong storage even if the container starts successfully. This is the core persistence evidence for the tested failure.

**Expected:** Hash remains h1 in the synthetic trace; actual live bytes/hash are recorded separately.

## Exercise 5: Explain retention and reclaim

Retaining a PVC after StatefulSet deletion does not guarantee data survives node or cluster destruction. The handoff should state the chosen synthetic-data retention and eventual cleanup policy explicitly.

**Expected:** Each lifecycle boundary has its own policy; retention is not backup.

## Exercise 6: Diagnose a Pending claim

Storage setup is a separate host responsibility. A bounded lesson should report an unavailable class or incompatible mode instead of deleting data or installing a provisioner automatically.

**Expected:** No destructive claim reset; the missing capability or binding condition is identified.

## Boundary and troubleshooting review

A healthy Pod or recreated constant file does not prove old data survived. Use a marker whose initialization is not silently repeated, and keep writer/read operations separate. A Bound PVC alone does not prove the application can read the intended bytes.

Do not delete a claim as a routine repair for a Pending Pod. Inspect binding, events, access mode and ownership first. Live storage operations remain unavailable until the host capability and retention choice are explicit.
