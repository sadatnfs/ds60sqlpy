# docker-038: Incident response, disk pressure and scoped cleanup

## Level and prerequisites

Advanced; about 120 minutes, with additional time for the optional host experiment. Direct prerequisites: `docker-037`

## Learning objectives

Design an incident evidence packet. Write a scoped recovery and cleanup plan. Explain the difference between a configuration, an observed process and evidence of the application's behavior.

## Purpose, vocabulary and mental model

An incident is an observed deviation from expected behavior that requires diagnosis or recovery. Disk pressure can arise from images, build cache, container writable layers, logs or volumes. These categories have different retention and ownership, so one global delete command is a poor first response.

Pruning means removing resources considered unused by a tool’s rules. Unused does not always mean unimportant to a learner. A stopped container may retain an investigation, and a detached volume may hold progress awaiting the next container. Identify the resource and intended retention before deletion.

A useful incident sequence preserves evidence, assesses current state, identifies the failing layer, applies a scoped repair and verifies recovery. If an engine VM needs restart, that can interrupt unrelated workloads. A course lesson does not authorize such a host-wide action.

## Anatomy and a trace you can follow

Use read-only inventory first. `docker system df` summarizes storage categories; project-scoped ps, image and volume inspection add ownership. Capture small results privately. Remove only resources you created and have decided to discard, using explicit names or labels checked against the project.

Routine course cleanup uses Compose down without volume deletion. A full disposable-lab reset is separately documented and should name the exact study project and volume. Build cache deletion changes performance and can affect other projects, so it is not hidden in the learner shutdown command.

## How to use this lesson

The classroom displays this guide and saves your worksheet. Its Run button does not control your Docker engine. Docker engine access is powerful host access, so the classroom deliberately receives no engine socket. Work through the supplied examples without starting anything, then use the optional host lab only in your own disposable project. Reading a command, parsing YAML and actually running the project are different forms of evidence.

Use Bash in Linux, macOS Terminal, or Ubuntu under WSL 2 on Windows. The supported engine runs Linux containers. The maintained fixture is `courses/docker/fixtures/compose-lab/`; its README explains copying it into a new ignored learner directory, checking the engine, building locally with visible logs, and using the fixed project name `ds60-docker-study`. The fixture uses port 18080 on host loopback. Stop if that project name or port belongs to unrelated work; choose a new project name consistently in your own copy. Never paste a command against a remote Docker context simply because it is currently selected.

For Dockerfile examples, create a file named `Dockerfile` in a scratch project. YAML snippets describe a fragment unless explicitly called a complete file. Text transcripts are synthetic illustrations, not claims about your machine. Do not substitute a real password, token or private registry into a checked-in example.

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

### Exercise 1: Classify disk usage by resource type.

**Expected evidence:** Images, cache, writable layers, logs and volumes.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

### Exercise 2: Predict the effect of ordinary Compose down.

**Expected evidence:** It preserves named volumes unless explicit volume deletion is requested.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

### Exercise 3: Design an incident evidence packet.

**Expected evidence:** Failure symptom, time, resource inventory and bounded relevant logs.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

### Exercise 4: Diagnose a detached volume labeled unused.

**Expected evidence:** Determine its owner and retained data purpose before deletion.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

### Exercise 5: Explain why broad engine pruning is out of scope.

**Expected evidence:** It can affect unrelated workloads and recoverable state.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

### Exercise 6: Write a scoped recovery and cleanup plan.

**Expected evidence:** Explicit targets, retained data, repair check and final ownership readback.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

## Common mistakes and diagnosis

Start with the smallest observation that separates two plausible causes. An image inspection answers questions about the packaged filesystem and configuration; container inspection adds runtime mounts, network attachment and exit status. An application request adds another layer of evidence. A healthy container can still serve the wrong application result. Preserve the original failure and the exact changed field before retrying.

The boundary case in this chapter is: Diagnose a detached volume labeled unused. Use its expected observation, Determine its owner and retained data purpose before deletion., to avoid treating a successful command as proof of the wrong claim. Keep source edits in your own copy. Do not make a container privileged, mount the engine socket, disable all checks or delete every volume to make an example succeed.

## Retrieval, transfer and next steps

Close the explanations and draw the path from source files to image to container to the observation relevant here. Reconstruct the second worked example with one different value and predict what changes. Explain which state survives process restart, container recreation and image rebuild. If none of those operations applies to this mechanism, explain why.

Before proceeding, retain six evidence records. For the optional host project, use `docker compose -p ds60-docker-study down` from the fixture copy to stop its containers and remove its ordinary network. This command preserves named volumes. Volume deletion is a separate deliberate reset of that disposable lab after a backup or export, never a general cleanup step. The fixture README describes its exact scoped reset.

## Primary references

- [Official reference 1](https://docs.docker.com/engine/manage-resources/pruning/)
- [Official reference 2](https://docs.docker.com/reference/cli/docker/system/df/)

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
