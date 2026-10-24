# docker-034: Application migrations and durable state versioning

## Level and prerequisites

Advanced; about 120 minutes, with additional time for the optional host experiment. Direct prerequisites: `docker-033`

## Learning objectives

Design a v1-to-v2 synthetic record conversion. Write a migration release plan. Explain the difference between a configuration, an observed process and evidence of the application's behavior.

## Purpose, vocabulary and mental model

A migration changes stored data or schema from one version to another. Replacing an application image can require such a change, but image rollback does not automatically reverse data migration. Code version and data version are related state machines with different reversibility.

A safe migration procedure identifies the starting schema, validates preconditions, creates a consistent backup, performs a bounded transition and verifies the new invariant. Concurrent old and new application instances complicate this because both may read or write the same data during replacement.

The fixture counter includes a schema_version field so learners can discuss this boundary without a full database. The course does not run destructive migrations on the main classroom’s progress store. Work on copied synthetic records and a separate disposable restore target.

## Anatomy and a trace you can follow

An expand-and-contract approach first adds a compatible representation, allows both versions to work, migrates data and only later removes the old representation. It costs temporary complexity but can reduce deployment downtime. A tiny offline app may instead choose a documented maintenance window and an exclusive migration.

Atomic file replacement can prevent a partially written JSON file from appearing, but it is not a general distributed transaction. Define locking and single-writer assumptions explicitly. Backups and rollback commands must match the data protocol, not just the image tag.

## How to use this lesson

The classroom displays this guide and saves your worksheet. Its Run button does not control your Docker engine. Docker engine access is powerful host access, so the classroom deliberately receives no engine socket. Work through the supplied examples without starting anything, then use the optional host lab only in your own disposable project. Reading a command, parsing YAML and actually running the project are different forms of evidence.

Use Bash in Linux, macOS Terminal, or Ubuntu under WSL 2 on Windows. The supported engine runs Linux containers. The maintained fixture is `courses/docker/fixtures/compose-lab/`; its README explains copying it into a new ignored learner directory, checking the engine, building locally with visible logs, and using the fixed project name `ds60-docker-study`. The fixture uses port 18080 on host loopback. Stop if that project name or port belongs to unrelated work; choose a new project name consistently in your own copy. Never paste a command against a remote Docker context simply because it is currently selected.

For Dockerfile examples, create a file named `Dockerfile` in a scratch project. YAML snippets describe a fragment unless explicitly called a complete file. Text transcripts are synthetic illustrations, not claims about your machine. Do not substitute a real password, token or private registry into a checked-in example.

## Worked example / walkthrough

### Worked example 1: Read a versioned teaching record

This is synthetic stored state.

```json
{"schema_version":1,"counter":7}
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

### Exercise 1: Predict whether image rollback reverses a schema change.

**Expected evidence:** It does not automatically restore previous data.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

### Exercise 2: Identify migration preconditions.

**Expected evidence:** Known schema version, exclusive or compatible writers and a verified backup.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

### Exercise 3: Design a v1-to-v2 synthetic record conversion.

**Expected evidence:** Preserve counter value and set a validated new schema version.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

### Exercise 4: Diagnose an old reader failing after deployment rollback.

**Expected evidence:** The data format may have advanced beyond its compatibility.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

### Exercise 5: Explain atomic file replacement limits.

**Expected evidence:** It avoids partial file visibility under stated local assumptions, not all concurrent-write races.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

### Exercise 6: Write a migration release plan.

**Expected evidence:** Preconditions, backup, transition, validation, compatible rollback and cleanup.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

## Common mistakes and diagnosis

Start with the smallest observation that separates two plausible causes. An image inspection answers questions about the packaged filesystem and configuration; container inspection adds runtime mounts, network attachment and exit status. An application request adds another layer of evidence. A healthy container can still serve the wrong application result. Preserve the original failure and the exact changed field before retrying.

The boundary case in this chapter is: Diagnose an old reader failing after deployment rollback. Use its expected observation, The data format may have advanced beyond its compatibility., to avoid treating a successful command as proof of the wrong claim. Keep source edits in your own copy. Do not make a container privileged, mount the engine socket, disable all checks or delete every volume to make an example succeed.

## Retrieval, transfer and next steps

Close the explanations and draw the path from source files to image to container to the observation relevant here. Reconstruct the second worked example with one different value and predict what changes. Explain which state survives process restart, container recreation and image rebuild. If none of those operations applies to this mechanism, explain why.

Before proceeding, retain six evidence records. For the optional host project, use `docker compose -p ds60-docker-study down` from the fixture copy to stop its containers and remove its ordinary network. This command preserves named volumes. Volume deletion is a separate deliberate reset of that disposable lab after a backup or export, never a general cleanup step. The fixture README describes its exact scoped reset.

## Primary references

- [Official reference 1](https://docs.docker.com/engine/storage/volumes/)
- [Official reference 2](https://www.postgresql.org/docs/current/backup.html)

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
