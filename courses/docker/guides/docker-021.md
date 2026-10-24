# docker-021: Backups, restores and proving data recovery

## Level and prerequisites

Intermediate; about 100 minutes, with additional time for the optional host experiment. Direct prerequisites: `docker-020`

## Learning objectives

Design a separate restore target. Produce a recovery evidence packet. Explain the difference between a configuration, an observed process and evidence of the application's behavior.

## Purpose, vocabulary and mental model

A backup is a retained copy intended for recovery. A restore is the process of reconstructing usable state from that copy. The existence of an archive file does not prove that recovery works. A useful backup procedure defines consistency, scope, identity, retention and an independent restore test.

A filesystem copy of a live database may be inconsistent even when every file is readable. Applications have their own transactional state and backup protocols. The fixture’s small JSON counter can be exported while the app is stopped, making the consistency boundary easy to explain. That procedure must not be generalized to every database.

Back up only the disposable study volume in this chapter. The main classroom’s learner progress is separate. Never use global volume pruning as part of a backup exercise, and never overwrite the only good copy while testing a restore.

## Anatomy and a trace you can follow

The fixture README includes an export using the app image’s Python standard library and a separate restore-target volume. Stop the app first, export a small JSON record to the learner copy, inspect its schema, then test restoration into a new owned volume. Record checksums and expected values without treating a checksum as proof of application semantics.

A recovery point objective describes tolerable data loss measured in time. A recovery time objective describes the acceptable time to restore service. They guide backup frequency and practice, but a local teaching experiment only measures its own small workload.

## How to use this lesson

The classroom displays this guide and saves your worksheet. Its Run button does not control your Docker engine. Docker engine access is powerful host access, so the classroom deliberately receives no engine socket. Work through the supplied examples without starting anything, then use the optional host lab only in your own disposable project. Reading a command, parsing YAML and actually running the project are different forms of evidence.

Use Bash in Linux, macOS Terminal, or Ubuntu under WSL 2 on Windows. The supported engine runs Linux containers. The maintained fixture is `courses/docker/fixtures/compose-lab/`; its README explains copying it into a new ignored learner directory, checking the engine, building locally with visible logs, and using the fixed project name `ds60-docker-study`. The fixture uses port 18080 on host loopback. Stop if that project name or port belongs to unrelated work; choose a new project name consistently in your own copy. Never paste a command against a remote Docker context simply because it is currently selected.

For Dockerfile examples, create a file named `Dockerfile` in a scratch project. YAML snippets describe a fragment unless explicitly called a complete file. Text transcripts are synthetic illustrations, not claims about your machine. Do not substitute a real password, token or private registry into a checked-in example.

## Worked example / walkthrough

### Worked example 1: Read the recovery contract

The sample values are synthetic and make no claim about your volume.

```json
{"schema_version": 1, "counter": 7}
```

**Expected observation:** A restore must preserve the schema and the counter value, not merely recreate a file with the same name.

### Worked example 2: Plan an independent restore

Use the fixture README procedure on a separate target.

```text
stop writer -> export owned volume -> validate JSON -> restore into new volume -> start reader -> compare value
```

**Expected observation:** The original volume remains untouched while the new target proves recovery.

## Six progressive exercises

### Exercise 1: Distinguish backup creation and restore acceptance.

**Expected evidence:** An archive exists versus a new instance can use recovered data.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

### Exercise 2: Predict the risk of copying a live transactional database directory.

**Expected evidence:** The copy may not represent a consistent transaction boundary.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

### Exercise 3: Design a separate restore target.

**Expected evidence:** A new owned volume with no overwrite of the source.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

### Exercise 4: Diagnose a valid checksum with invalid application data.

**Expected evidence:** Byte identity does not establish schema or semantic correctness.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

### Exercise 5: Explain RPO and RTO using the counter lab.

**Expected evidence:** Allowed lost updates and time to a usable restored instance.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

### Exercise 6: Produce a recovery evidence packet.

**Expected evidence:** Source identity, export hash, restore target, parsed value and cleanup record.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

## Common mistakes and diagnosis

Start with the smallest observation that separates two plausible causes. An image inspection answers questions about the packaged filesystem and configuration; container inspection adds runtime mounts, network attachment and exit status. An application request adds another layer of evidence. A healthy container can still serve the wrong application result. Preserve the original failure and the exact changed field before retrying.

The boundary case in this chapter is: Diagnose a valid checksum with invalid application data. Use its expected observation, Byte identity does not establish schema or semantic correctness., to avoid treating a successful command as proof of the wrong claim. Keep source edits in your own copy. Do not make a container privileged, mount the engine socket, disable all checks or delete every volume to make an example succeed.

## Retrieval, transfer and next steps

Close the explanations and draw the path from source files to image to container to the observation relevant here. Reconstruct the second worked example with one different value and predict what changes. Explain which state survives process restart, container recreation and image rebuild. If none of those operations applies to this mechanism, explain why.

Before proceeding, retain six evidence records. For the optional host project, use `docker compose -p ds60-docker-study down` from the fixture copy to stop its containers and remove its ordinary network. This command preserves named volumes. Volume deletion is a separate deliberate reset of that disposable lab after a backup or export, never a general cleanup step. The fixture README describes its exact scoped reset.

## Primary references

- [Official reference 1](https://docs.docker.com/engine/storage/volumes/#back-up-restore-or-migrate-data-volumes)

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
