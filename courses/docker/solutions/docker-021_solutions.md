# docker-021: explanatory solutions

Compare after your own attempt or an explicit reveal. These explain the supplied teaching fixtures; they are not engine results. The mechanism is explained in `courses/docker/guides/docker-021.md`.

## Exercise 1: Distinguish backup creation and restore acceptance.

**Expected answer:** An archive exists versus a new instance can use recovered data.

**Why:** The latter catches missing files, invalid formats and wrong ownership that a successful copy can hide.

## Exercise 2: Predict the risk of copying a live transactional database directory.

**Expected answer:** The copy may not represent a consistent transaction boundary.

**Why:** Databases can coordinate several files and buffered writes. Use their documented backup mechanism instead of assuming a file copy captures a valid snapshot.

## Exercise 3: Design a separate restore target.

**Expected evidence:** A new owned volume with no overwrite of the source.

**Why:** The test should not destroy the only working state. Keeping the source untouched also makes comparison and rollback possible.

## Exercise 4: Diagnose a valid checksum with invalid application data.

**Expected answer:** Byte identity does not establish schema or semantic correctness.

**Why:** A checksum proves a relationship between byte sequences. The application must still parse and validate the data it will use.

## Exercise 5: Explain RPO and RTO using the counter lab.

**Expected answer:** Allowed lost updates and time to a usable restored instance.

**Why:** Name the workload and measurement period. A small local result cannot be advertised as a production recovery guarantee for larger or different data.

## Exercise 6: Produce a recovery evidence packet.

**Expected evidence:** Source identity, export hash, restore target, parsed value and cleanup record.

**Why:** The packet ties the copy to a particular source and proves independent use. Cleanup should remove only the disposable restore resources after review.

## Check your transfer

A useful answer names the exact object, the phase when a setting takes effect, the expected normal result and an observation that would disprove it. A production system additionally needs ownership, lifecycle, data recovery and operational review.
