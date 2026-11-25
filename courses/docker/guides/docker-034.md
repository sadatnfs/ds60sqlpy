# docker-034: Application migrations and durable state versioning

## Level and prerequisites

Advanced; about 120 minutes, with additional time for the optional host experiment. Direct prerequisites: `docker-033`

## Learning objectives

Design a v1-to-v2 synthetic record conversion. Write a migration release plan. Use migration, schema version and rollback accurately when you explain what you observed.

## Purpose, vocabulary and mental model

A migration changes stored data or schema from one version to another. Replacing an application image can require such a change, but image rollback does not automatically reverse data migration. Code version and data version are related state machines with different reversibility.

A safe migration procedure identifies the starting schema, validates preconditions, creates a consistent backup, performs a bounded transition and verifies the new invariant. Concurrent old and new application instances complicate this because both may read or write the same data during replacement.

The fixture counter includes a schema_version field so learners can discuss this boundary without a full database. The course does not run destructive migrations on the main classroom’s progress store. Work on copied synthetic records and a separate disposable restore target.

### Key terms

- **Migration:** A change that moves stored data or a schema from one version to another.
- **Schema version:** A stored marker, such as the fixture's `schema_version` field, that tells code which data format it is reading.
- **Rollback:** Returning to an earlier image, which does not automatically reverse a data migration.
- **Durable state:** Data that outlives containers and images and therefore carries its own version and recovery needs.
- **Precondition:** A fact about the starting schema or data that a migration verifies before changing anything.

## Anatomy and a trace you can follow

An expand-and-contract approach first adds a compatible representation, allows both versions to work, migrates data and only later removes the old representation. It costs temporary complexity but can reduce deployment downtime. A tiny offline app may instead choose a documented maintenance window and an exclusive migration.

Atomic file replacement can prevent a partially written JSON file from appearing, but it is not a general distributed transaction. Define locking and single-writer assumptions explicitly. Backups and rollback commands must match the data protocol, not just the image tag.

## How to use this lesson

The classroom saves `courses/docker/lessons/docker-034.md` and holds no engine socket ([host-lab setup](../STUDY-GUIDE.md#host-lab-setup)).

**Host lab.** Practice reading the version marker without changing live data. After at least one increment, print the stored record with `docker compose -p ds60-docker-study exec app python -c "print(open('/data/counter.json').read())"`; it shows `{"schema_version": 1, "counter": N}`. Then rehearse a v1-to-v2 conversion on a copy only: take the README export into `counter-backup.json`, and on the host run `python3 -c "import json; v=json.load(open('counter-backup.json')); assert v['schema_version'] == 1; print(json.dumps({'schema_version': 2, 'counter': v['counter'], 'unit': 'increments'}))"`. The fixture's `read_counter()` accepts only `schema_version` 1, so it would refuse this v2 record with its invalid-state error, which is exactly what a rolled-back v1 reader does when it meets migrated data. Nothing here wrote to `study-data`; delete `counter-backup.json` afterward.

## Worked example / walkthrough

### Worked example 1: Read a versioned teaching record

This is synthetic stored state.

```json
{ "schema_version": 1, "counter": 7 }
```

**Expected observation:** The reader checks the version before interpreting fields.

### Worked example 2: Plan a compatible transition

No live data is modified by this outline.

```text
v1 reader/writer -> v2 reader accepts v1 and v2 -> migrate owned data
-> verify v2 -> retire v1 compatibility after rollback window
```

**Expected observation:** A rollback plan must state which code versions can still read the stored data.

## Six progressive exercises

Answer-type prompts keep their answers in the solutions file ([exercise rules](../STUDY-GUIDE.md#exercise-rules)).

### Exercise 1: Predict whether image rollback reverses a schema change.

**Hint:** Ask whether rolling back an image changes files in the volume.

### Exercise 2: Identify migration preconditions.

**Hint:** List what must be true before the first record changes.

### Exercise 3: Design a v1-to-v2 synthetic record conversion.

**Expected evidence:** Preserve counter value and set a validated new schema version.

**Hint:** Convert one record and check every field of the result.

### Exercise 4: Diagnose an old reader failing after deployment rollback.

**Hint:** Compare the format the old reader expects with the data now stored.

### Exercise 5: Explain atomic file replacement limits.

**Hint:** Ask what an atomic rename protects against and what it does not.

### Exercise 6: Write a migration release plan.

**Expected evidence:** Preconditions, backup, transition, validation, compatible rollback and cleanup.

**Hint:** Order the backup, migration, validation and rollback steps.

## Common mistakes and diagnosis

Rolling back the image and expecting the data to roll back too. Migrating without a verified backup. Letting old and new writers run against incompatible formats.

Exercise 4 is this chapter's boundary case: Diagnose an old reader failing after deployment rollback. Read the version marker in the stored data and compare it with the versions the rolled-back reader accepts before restarting it again.

A migration that runs automatically when a container starts looks convenient: every new image upgrades whatever it finds. With more than one container able to start against the same volume, two migrators can read v1 at once and both write, and a crashed half-migration is retried on every restart with nobody watching. It also ties an irreversible data step to an image rollout that people expect to be cheap to undo. Run the migration as a separate, explicit one-off job, for example a `run --rm --no-deps` command while the service is stopped and after the backup is verified, and let the application at startup only check that the version it finds is one it supports.

Never trade a safety control for a passing example ([safety rules](../STUDY-GUIDE.md#safety-rules)).

## Retrieval, transfer and next steps

**Retrieval.** Recall the order of the compatible transition and the point after which rollback needs a migration back.

**Transfer case.** A v2 release migrated the counter file, then a bug forced a rollback to the v1 image, which now exits at startup. What are your options, and which one keeps every write?

Then run the [retrieval loop](../STUDY-GUIDE.md#retrieval-and-cleanup) and end any host session with its cleanup.

## Primary references

- [Volumes](https://docs.docker.com/engine/storage/volumes/)
- [PostgreSQL backup and restore](https://www.postgresql.org/docs/current/backup.html)

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for docker-034: Application migrations and durable state versioning.
Read courses/docker/guides/docker-034.md and courses/docker/lessons/docker-034.md. Direct prerequisites: `docker-033`
Ask me to predict the first example, review my worksheet, and give one hint at a time.
Keep courses/docker/solutions/ closed until I attempt or explicitly request comparison.
Distinguish image metadata, container state and actual application evidence.
Do not execute host commands, change Docker contexts or delete volumes on my behalf.
Finish with a fresh transfer case and ask which evidence would falsify my explanation.
```
