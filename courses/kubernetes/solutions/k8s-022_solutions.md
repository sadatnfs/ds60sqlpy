# k8s-022: Explanatory solutions

These answers explain the stated synthetic and scoped runtime contracts. Static checks do not prove cluster acceptance.

## Mechanism

Persistent storage separates data lifetime from a particular Pod. A PersistentVolumeClaim requests storage through an access mode, capacity and StorageClass. A PersistentVolume represents provisioned storage and its lifecycle policy. A StatefulSet adds stable Pod identity and per-replica claim naming, but it does not turn a filesystem into a backup or a complete database recovery system.

The host fixture uses a prequalified StorageClass named lesson-local and a single-replica StatefulSet store. Its claim template data produces a claim associated with store-0. The example explicitly retains claims when the StatefulSet is deleted or scaled down. The normal browser adapter does not create PVCs, StatefulSets or storage classes.

A live persistence test writes a synthetic marker once, records its checksum, replaces the application Pod by exact UID and reads the marker through a separate bounded reader. Re-running an initializer that overwrites the same marker would hide data loss, so initialization and verification must be separate operations.

## Exercise 1: Trace storage references

The manifest describes desired storage. Binding status and application access need runtime evidence. A missing class is a capability problem, not a reason to substitute an arbitrary hostPath.

**Expected:** The data claim is mounted at /data and depends on a qualified lesson-local class.

**Solution reasoning**

- **Approach:** Follow volumeClaimTemplates name data to the volumeMounts entry and storageClassName to the class.
- **Why it is correct:** The StatefulSet creates one claim per ordinal from the template, and the mount with the same name places it at /data.
- **Plausible wrong approach:** Adding a separate PersistentVolumeClaim and referencing it from the Pod template would make all replicas share one claim.
- **How to verify:** Each link cites a field: template name, mountPath /data and storageClassName.

## Exercise 2: Record initial data once

An initializer that recreates the expected bytes after loss can fake persistence. The writer should refuse an existing marker or otherwise make initialization history explicit, while later readers remain read-only.

**Expected:** One initialization receipt, claim/PV identities and a known marker checksum.

**Solution reasoning**

- **Approach:** Run the writer once with exclusive create and record claim UID, PV name and SHA-256.
- **Why it is correct:** Exclusive create fails if the marker already exists, so a second run cannot silently overwrite the initial data.
- **Plausible wrong approach:** Writing with plain overwrite would hide an accidental second run behind a new hash.
- **How to verify:** One receipt holds claim UID, bound PV and marker hash.

## Exercise 3: Replace only the Pod

The StatefulSet can replace a Pod while reusing its claim. The before/after graph should show which identity changed and which remained, not merely a familiar Pod name.

**Expected:** New Pod UID with the intended stable ordinal and same claim binding.

**Solution reasoning**

- **Approach:** Delete only the recorded Pod and compare UID, ordinal name and claim before and after.
- **Why it is correct:** The StatefulSet recreates the same ordinal name and reattaches the same claim, while the Pod gets a new UID.
- **Plausible wrong approach:** Scaling the StatefulSet down and up to replace the Pod changes more than one Pod and is not the minimal operation.
- **How to verify:** Only the Pod UID changed; name and claim binding are the same.

## Exercise 4: Verify the marker independently

The independent read closes the application-data boundary. It catches empty or wrong storage even if the container starts successfully. This is the core persistence evidence for the tested failure.

**Expected:** Hash remains h1 in the synthetic trace; actual live bytes/hash are recorded separately.

**Solution reasoning**

- **Approach:** Run only the read-only reader and hash the marker it reads.
- **Why it is correct:** If the claim was reattached, the bytes are unchanged and the hash equals h1.
- **Plausible wrong approach:** Running the writer again to check the file would recreate the evidence you are trying to verify.
- **How to verify:** The reader hash equals the recorded initialization hash, with live values kept separate.

## Exercise 5: Explain retention and reclaim

Retaining a PVC after StatefulSet deletion does not guarantee data survives node or cluster destruction. The handoff should state the chosen synthetic-data retention and eventual cleanup policy explicitly.

**Expected:** Each lifecycle boundary has its own policy; retention is not backup.

**Solution reasoning**

- **Approach:** For each deletion, name the deleted object and the policy that decides what happens next.
- **Why it is correct:** StatefulSet claim retention governs the PVC when the StatefulSet or replicas are removed, and the PV reclaim policy governs the volume when the claim is deleted.
- **Plausible wrong approach:** Calling Retain a backup ignores that the data still lives on one volume with no independent copy.
- **How to verify:** Each deletion cites claim retention or PV reclaim, and retention is distinguished from backup.

## Exercise 6: Diagnose a Pending claim

Storage setup is a separate host responsibility. A bounded lesson should report an unavailable class or incompatible mode instead of deleting data or installing a provisioner automatically.

**Expected:** No destructive claim reset; the missing capability or binding condition is identified.

**Solution reasoning**

- **Approach:** Read PVC events and binding status, then check the StorageClass provisioner, capacity and topology.
- **Why it is correct:** A Pending claim means no volume was bound, and the event usually names the missing class, capacity or zone.
- **Plausible wrong approach:** Deleting and recreating the claim discards the evidence and returns to the same Pending state.
- **How to verify:** The check uses class, events or binding status and leaves the claim in place.

## Boundary and troubleshooting review

A healthy Pod or recreated constant file does not prove old data survived. Use a marker whose initialization is not silently repeated, and keep writer/read operations separate. A Bound PVC alone does not prove the application can read the intended bytes.

Do not delete a claim as a routine repair for a Pending Pod. Inspect binding, events, access mode and ownership first. Live storage operations remain unavailable until the host capability and retention choice are explicit.
