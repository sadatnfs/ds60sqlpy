# docker-038: Incident response, disk pressure and scoped cleanup

## Level and prerequisites

Advanced; about 120 minutes, with additional time for the optional host experiment. Direct prerequisites: `docker-037`

## Learning objectives

Design an incident evidence packet. Write a scoped recovery and cleanup plan. Use incident response, disk pressure and docker system df accurately when you explain what you observed.

## Purpose, vocabulary and mental model

An incident is an observed deviation from expected behavior that requires diagnosis or recovery. Disk pressure can arise from images, build cache, container writable layers, logs or volumes. These categories have different retention and ownership, so one global delete command is a poor first response.

Pruning means removing resources considered unused by a tool’s rules. Unused does not always mean unimportant to a learner. A stopped container may retain an investigation, and a detached volume may hold progress awaiting the next container. Identify the resource and intended retention before deletion.

A useful incident sequence preserves evidence, assesses current state, identifies the failing layer, applies a scoped repair and verifies recovery. If an engine VM needs restart, that can interrupt unrelated workloads. A course lesson does not authorize such a host-wide action.

### Key terms

- **Incident:** An observed deviation from expected behavior that requires diagnosis or recovery.
- **Disk pressure:** A shortage of free disk space caused by images, build cache, writable layers, logs or volumes.
- **`docker system df`:** A read-only command that reports disk usage by images, containers, local volumes and build cache.
- **Pruning:** Removing resources that a tool's rules consider unused, which is not the same as unimportant.
- **Scoped cleanup:** Deleting only identified resources whose ownership and retention are known, then verifying recovery.

## Anatomy and a trace you can follow

Use read-only inventory first. `docker system df` summarizes storage categories; project-scoped ps, image and volume inspection add ownership. Capture small results privately. Remove only resources you created and have decided to discard, using explicit names or labels checked against the project.

Routine course cleanup uses Compose down without volume deletion. A full disposable-lab reset is separately documented and should name the exact study project and volume. Build cache deletion changes performance and can affect other projects, so it is not hidden in the learner shutdown command.

## How to use this lesson

The classroom saves `courses/docker/lessons/docker-038.md` and holds no engine socket ([host-lab setup](../STUDY-GUIDE.md#host-lab-setup)).

**Host lab.** Assemble an evidence packet before any cleanup. Run `docker system df` and copy its table, then `docker system df -v` for per-volume sizes and the number of containers using each image. List the project's resources with `docker compose -p ds60-docker-study ps -a` and the label filter from worked example 1, and capture recent logs with `docker compose -p ds60-docker-study logs --since 10m app > ../incident-logs.txt`. Add the time, the symptom and one sentence on what you will remove and what you will keep. Then run worked example 2 and confirm with `docker volume ls --filter label=com.docker.compose.project=ds60-docker-study` that `study-data` is still listed. Start the app again with `up -d --wait`, check that `/counter` kept its value, and only then delete `../incident-logs.txt`. The packet, not the deletion, is what this lab produces.

## Worked example / walkthrough

### Worked example 1: Inspect storage before deciding

These reads do not delete resources.

```sh
docker system df
docker compose -p ds60-docker-study ps -a
docker volume ls --filter label=com.docker.compose.project=ds60-docker-study
```

**Expected observation:** Storage categories and project ownership are visible before any cleanup.

### Worked example 2: Stop only the study application

This retains its named volume.

```sh
docker compose -p ds60-docker-study down
```

**Expected observation:** The project containers and network stop; retained data remains available to a later start.

## Six progressive exercises

Answer-type prompts keep their answers in the solutions file ([exercise rules](../STUDY-GUIDE.md#exercise-rules)).

### Exercise 1: Classify disk usage by resource type.

**Hint:** Run docker system df and read each row.

### Exercise 2: Predict the effect of ordinary Compose down.

**Hint:** Compare docker compose down with and without -v.

### Exercise 3: Design an incident evidence packet.

**Expected evidence:** Failure symptom, time, resource inventory and bounded relevant logs.

**Hint:** Record the symptom, time, resource inventory and relevant logs before acting.

### Exercise 4: Diagnose a detached volume labeled unused.

**Hint:** Find who created the volume and what it holds.

### Exercise 5: Explain why broad engine pruning is out of scope.

**Hint:** Ask which other projects share the engine.

### Exercise 6: Write a scoped recovery and cleanup plan.

**Expected evidence:** Explicit targets, retained data, repair check and final ownership readback.

**Hint:** List the exact targets, what to keep, the repair check and a final readback.

## Common mistakes and diagnosis

Running `docker system prune -a --volumes` during an incident. Deleting a dangling volume without finding its owner. Cleaning up before recording evidence.

Exercise 4 is this chapter's boundary case: Diagnose a detached volume labeled unused. Read the volume's labels and creating project, and ask who owns its data, before treating unattached as unwanted.

Container logs are a disk-pressure source that `docker system df` does not report at all. Its container size column measures writable layers, while each container's log file sits beside them in the engine's data directory, and with the `json-file` driver and no rotation options it grows without limit. A chatty service can fill the disk while images and volumes look modest. Check the logging settings with `docker inspect --format '{{json .HostConfig.LogConfig}}'` on the container, and when logs are the cause, set `max-size` and `max-file` for that service, or engine-wide in the daemon configuration, rather than deleting files under the engine's directories by hand.

Never trade a safety control for a passing example ([safety rules](../STUDY-GUIDE.md#safety-rules)).

## Retrieval, transfer and next steps

**Retrieval.** Say what `docker compose down` removes and what it leaves for a separate, deliberate decision.

**Transfer case.** During an incident on a shared host the disk is 95 percent full, and `docker system df` shows several gigabytes of reclaimable build cache. Is clearing it in scope, and how do you limit the effect on others?

Then run the [retrieval loop](../STUDY-GUIDE.md#retrieval-and-cleanup) and end any host session with its cleanup.

## Primary references

- [Prune unused Docker objects](https://docs.docker.com/engine/manage-resources/pruning/)
- [docker system df reference](https://docs.docker.com/reference/cli/docker/system/df/)

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for docker-038: Incident response, disk pressure and scoped cleanup.
Read courses/docker/guides/docker-038.md and courses/docker/lessons/docker-038.md. Direct prerequisites: `docker-037`
Ask me to predict the first example, review my worksheet, and give one hint at a time.
Keep courses/docker/solutions/ closed until I attempt or explicitly request comparison.
Distinguish image metadata, container state and actual application evidence.
Do not execute host commands, change Docker contexts or delete volumes on my behalf.
Finish with a fresh transfer case and ask which evidence would falsify my explanation.
```
