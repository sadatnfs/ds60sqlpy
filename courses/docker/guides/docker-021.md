# docker-021: Backups, restores and proving data recovery

## Level and prerequisites

Intermediate; about 100 minutes, with additional time for the optional host experiment. Direct prerequisites: `docker-020`

## Learning objectives

Design a separate restore target. Produce a recovery evidence packet. Use backup, restore and recovery test accurately when you explain what you observed.

## Purpose, vocabulary and mental model

A backup is a retained copy intended for recovery. A restore is the process of reconstructing usable state from that copy. The existence of an archive file does not prove that recovery works. A useful backup procedure defines consistency, scope, identity, retention and an independent restore test.

A filesystem copy of a live database may be inconsistent even when every file is readable. Applications have their own transactional state and backup protocols. The fixture’s small JSON counter can be exported while the app is stopped, making the consistency boundary easy to explain. That procedure must not be generalized to every database.

Back up only the disposable study volume in this chapter. The main classroom’s learner progress is separate. Never use global volume pruning as part of a backup exercise, and never overwrite the only good copy while testing a restore.

### Key terms

- **Backup:** A retained copy of state intended for recovery.
- **Restore:** Reconstructing usable state from a backup into a chosen target.
- **Recovery test:** An independent restore followed by checks that prove a backup actually recovers the expected data.
- **Volume archive:** A tar file of a named volume's contents, made while the application is stopped.
- **Consistency boundary:** The condition, such as a stopped application, under which copied data is complete and safe to restore.

## Anatomy and a trace you can follow

The fixture README includes an export using the app image’s Python standard library and a separate restore-target volume. Stop the app first, export a small JSON record to the learner copy, inspect its schema, then test restoration into a new owned volume. Record checksums and expected values without treating a checksum as proof of application semantics.

A recovery point objective describes tolerable data loss measured in time. A recovery time objective describes the acceptable time to restore service. They guide backup frequency and practice, but a local teaching experiment only measures its own small workload.

## How to use this lesson

The classroom saves `courses/docker/lessons/docker-021.md` and holds no engine socket ([host-lab setup](../STUDY-GUIDE.md#host-lab-setup)).

**Host lab.** Follow the export and restore sections of the fixture README: stop the app, export `counter-backup.json` with noclobber, then restore it into the new `ds60-docker-study-restore` volume and run the read-only verification. Add one more check that uses the application's own validation rather than a copy of it: `docker run --rm --pull never --network none --read-only -v ds60-docker-study-restore:/data:ro ds60-docker-study:local python -c "import server; print(server.read_counter())"`. `read_counter` rejects a wrong schema version or a negative counter, so a printed number means the app would accept the file. Start the original project again with `up -d --wait` and confirm that its counter did not change. Keep the backup file and remove the restore volume only after you record both values.

## Worked example / walkthrough

### Worked example 1: Read the recovery contract

The sample values are synthetic and make no claim about your volume.

```json
{ "schema_version": 1, "counter": 7 }
```

**Expected observation:** A restore must preserve the schema and the counter value, not merely recreate a file with the same name.

### Worked example 2: Plan an independent restore

Use the fixture README procedure on a separate target.

```text
stop writer -> export owned volume -> validate JSON -> restore into new volume -> start reader -> compare value
```

**Expected observation:** The original volume remains untouched while the new target proves recovery.

## Six progressive exercises

Answer-type prompts keep their answers in the solutions file ([exercise rules](../STUDY-GUIDE.md#exercise-rules)).

### Exercise 1: Distinguish backup creation and restore acceptance.

**Hint:** Ask what an archive file proves about recovery.

### Exercise 2: Predict the risk of copying a live transactional database directory.

**Hint:** Ask what the database is doing while you copy its files.

### Exercise 3: Design a separate restore target.

**Expected evidence:** A new owned volume with no overwrite of the source.

**Hint:** Restore into a new volume and never over the source.

### Exercise 4: Diagnose a valid checksum with invalid application data.

**Hint:** Ask what a checksum compares and what the application checks.

### Exercise 5: Explain RPO and RTO using the counter lab.

**Hint:** Measure the lost increments and the minutes until a restored app works.

### Exercise 6: Produce a recovery evidence packet.

**Expected evidence:** Source identity, export hash, restore target, parsed value and cleanup record.

**Hint:** Record the source identity, archive hash, restore target and the value the app reads.

## Common mistakes and diagnosis

Copying a live database directory instead of making a consistent export. Restoring over the only good copy. Calling a backup successful without a restore test.

Exercise 4 is this chapter's boundary case: Diagnose a valid checksum with invalid application data. Parse and validate the restored file with the application's own reader; a matching checksum only shows the bytes were copied faithfully.

Another weak backup is one stored next to the data it protects. A JSON export written into the same named volume, or a volume archive kept only inside the Docker Desktop virtual disk, shares every failure of the original: `docker compose down -v`, a reset of the engine's virtual machine or a disk failure removes both at once. A backup also needs a recorded location and owner outside the engine. The fixture README writes `counter-backup.json` to the host folder, which is the minimum; a real service would also copy it off the machine and test a restore from that copy.

Never trade a safety control for a passing example ([safety rules](../STUDY-GUIDE.md#safety-rules)).

## Retrieval, transfer and next steps

**Retrieval.** List the restore steps in order and name the check that proves the restored data is usable.

**Transfer case.** A nightly job exports the counter volume while the app is still serving `POST /increment`. The exported JSON always parses. Using the fixture's write pattern, is each export consistent, and what does it still fail to guarantee?

Then run the [retrieval loop](../STUDY-GUIDE.md#retrieval-and-cleanup) and end any host session with its cleanup.

## Primary references

- [Back up, restore or migrate volumes](https://docs.docker.com/engine/storage/volumes/#back-up-restore-or-migrate-data-volumes)

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for docker-021: Backups, restores and proving data recovery.
Read courses/docker/guides/docker-021.md and courses/docker/lessons/docker-021.md. Direct prerequisites: `docker-020`
Ask me to predict the first example, review my worksheet, and give one hint at a time.
Keep courses/docker/solutions/ closed until I attempt or explicitly request comparison.
Distinguish image metadata, container state and actual application evidence.
Do not execute host commands, change Docker contexts or delete volumes on my behalf.
Finish with a fresh transfer case and ask which evidence would falsify my explanation.
```
