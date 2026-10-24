# docker-021: explanatory solutions

Compare after your own attempt or an explicit reveal. These are explanations of the supplied teaching fixtures, not fabricated engine results.

## Mechanism review

A backup is a retained copy intended for recovery. A restore is the process of reconstructing usable state from that copy. The existence of an archive file does not prove that recovery works. A useful backup procedure defines consistency, scope, identity, retention and an independent restore test.

A filesystem copy of a live database may be inconsistent even when every file is readable. Applications have their own transactional state and backup protocols. The fixture’s small JSON counter can be exported while the app is stopped, making the consistency boundary easy to explain. That procedure must not be generalized to every database.

Back up only the disposable study volume in this chapter. The main classroom’s learner progress is separate. Never use global volume pruning as part of a backup exercise, and never overwrite the only good copy while testing a restore.

The fixture README includes an export using the app image’s Python standard library and a separate restore-target volume. Stop the app first, export a small JSON record to the learner copy, inspect its schema, then test restoration into a new owned volume. Record checksums and expected values without treating a checksum as proof of application semantics.

A recovery point objective describes tolerable data loss measured in time. A recovery time objective describes the acceptable time to restore service. They guide backup frequency and practice, but a local teaching experiment only measures its own small workload.

## Exercise 1: Distinguish backup creation and restore acceptance.

The latter catches missing files, invalid formats and wrong ownership that a successful copy can hide.

**Expected:** An archive exists versus a new instance can use recovered data.

## Exercise 2: Predict the risk of copying a live transactional database directory.

Databases can coordinate several files and buffered writes. Use their documented backup mechanism instead of assuming a file copy captures a valid snapshot.

**Expected:** The copy may not represent a consistent transaction boundary.

## Exercise 3: Design a separate restore target.

The test should not destroy the only working state. Keeping the source untouched also makes comparison and rollback possible.

**Expected:** A new owned volume with no overwrite of the source.

## Exercise 4: Diagnose a valid checksum with invalid application data.

A checksum proves a relationship between byte sequences. The application must still parse and validate the data it will use.

**Expected:** Byte identity does not establish schema or semantic correctness.

## Exercise 5: Explain RPO and RTO using the counter lab.

Name the workload and measurement period. A small local result cannot be advertised as a production recovery guarantee for larger or different data.

**Expected:** Allowed lost updates and time to a usable restored instance.

## Exercise 6: Produce a recovery evidence packet.

The packet ties the copy to a particular source and proves independent use. Cleanup should remove only the disposable restore resources after review.

**Expected:** Source identity, export hash, restore target, parsed value and cleanup record.

## Check your transfer

A useful solution identifies the exact object, the phase when a setting takes effect, the expected normal result and an observation that disproves it. Repeating a command until it succeeds hides the mechanism. Change one variable, keep a failure record, and test the intended behavior again. Source examples here are small enough to inspect; a production system additionally needs ownership, lifecycle, data recovery and operational review. The host exercises are optional and must stay within the learner-created project.
