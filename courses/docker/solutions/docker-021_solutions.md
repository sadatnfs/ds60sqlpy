# docker-021: explanatory solutions

Compare after your own attempt or an explicit reveal. These explain the supplied teaching fixtures; they are not engine results. The mechanism is explained in `courses/docker/guides/docker-021.md`.

## Exercise 1: Distinguish backup creation and restore acceptance.

**Expected answer:** An archive exists versus a new instance can use recovered data.

**Why:** The latter catches missing files, invalid formats and wrong ownership that a successful copy can hide.

**Approach:** Separate the two events: making an archive of study-data, and starting a fresh service that reads restored data correctly.

**Why this is correct:** Only the second proves recovery, because it exercises read_counter's schema and type checks on the restored file.

**A plausible wrong approach:** Calling the job done when the archive file exists misses a truncated or wrongly owned counter.json.

**How to verify:** Start a reader on the restored volume; GET /counter returns the expected value with schema_version 1.

## Exercise 2: Predict the risk of copying a live transactional database directory.

**Expected answer:** The copy may not represent a consistent transaction boundary.

**Why:** Databases can coordinate several files and buffered writes. Use their documented backup mechanism instead of assuming a file copy captures a valid snapshot.

**Approach:** Recall that transactional databases keep data across several files and in memory, with their own logging.

**Why this is correct:** A file copy taken mid-write can capture files from different moments, which the database may reject or misread.

**A plausible wrong approach:** Using tar on a live database directory because it worked for counter.json ignores that the fixture writes one file atomically.

**How to verify:** Use the database's own dump or backup command, then restore it into a new instance and query it.

## Exercise 3: Design a separate restore target.

**Expected evidence:** A new owned volume with no overwrite of the source.

**Why:** The test should not destroy the only working state. Keeping the source untouched also makes comparison and rollback possible.

**Approach:** Create a new volume with a distinct name, restore the archive into it, and mount it in a separate container.

**Why this is correct:** The source volume stays intact, so if the restore is bad the original is still the working state.

**A plausible wrong approach:** Restoring over the live study-data volume to test risks destroying the only good copy.

**How to verify:** docker volume ls shows both volumes, and the source's counter is unchanged after the test.

## Exercise 4: Diagnose a valid checksum with invalid application data.

**Expected answer:** Byte identity does not establish schema or semantic correctness.

**Why:** A checksum proves a relationship between byte sequences. The application must still parse and validate the data it will use.

**Approach:** Separate byte integrity from meaning: a matching checksum shows the archive equals the source, not that the source was valid.

**Why this is correct:** If counter.json already held a negative counter, the copy matches and read_counter still raises on start.

**A plausible wrong approach:** Trusting the checksum and skipping startup lets an invalid file pass every backup check.

**How to verify:** Start the reader on the restored volume; validation either succeeds or reports the invalid counter state.

## Exercise 5: Explain RPO and RTO using the counter lab.

**Expected answer:** Allowed lost updates and time to a usable restored instance.

**Why:** Name the workload and measurement period. A small local result cannot be advertised as a production recovery guarantee for larger or different data.

**Approach:** Define RPO as how many increments may be lost (backup interval) and RTO as how long from failure to a working /counter.

**Why this is correct:** With a backup taken after counter 7 and two more increments before failure, the restored value is 7 and two updates are lost.

**A plausible wrong approach:** Quoting a local RTO of seconds as a production guarantee ignores larger data and different storage.

**How to verify:** Time the restore from start to a successful GET /counter and record the counter gap together with the workload.

## Exercise 6: Produce a recovery evidence packet.

**Expected evidence:** Source identity, export hash, restore target, parsed value and cleanup record.

**Why:** The packet ties the copy to a particular source and proves independent use. Cleanup should remove only the disposable restore resources after review.

**Approach:** Record the source volume name, the archive hash, the restore volume name, the counter value read back and the cleanup commands run.

**Why this is correct:** The hash ties the archive to the source; the parsed value proves use; the cleanup entry shows only disposable resources were removed.

**A plausible wrong approach:** Deleting the restore volume before review leaves nothing to check if someone questions the result.

**How to verify:** A reviewer can match each field and see that only the restore volume was removed after sign-off.

## Check your transfer

A useful answer names the exact object, the phase when a setting takes effect, the expected normal result and an observation that would disprove it. A production system additionally needs ownership, lifecycle, data recovery and operational review.
