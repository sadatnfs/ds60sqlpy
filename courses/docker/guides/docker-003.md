# docker-003: The filesystem, writable layers and container lifetime

## Level and prerequisites

Beginner; about 100 minutes, with additional time for the optional host experiment. Direct prerequisites: `docker-002`

## Learning objectives

Make a restart-versus-recreate persistence table. Choose storage for user progress and transient scratch data. Explain the difference between a configuration, an observed process and evidence of the application's behavior.

## Purpose, vocabulary and mental model

A filesystem maps paths to objects such as files and directories. An image supplies initial read-only layers. A running container sees a merged view plus its own writable changes. Creating or modifying a file in that writable layer does not alter the underlying image used by other containers.

The layer belongs to that container. A restart of the same container generally retains it. Removing and recreating a container creates a different layer, even when the new process has the same name and image. Persistent application data therefore belongs on an explicit volume or other durable store, not accidentally in a disposable container’s root filesystem.

A path is meaningful inside a filesystem namespace. `/app/server.py` inside a container need not exist at that path on your laptop. A bind mount can deliberately map a host directory into a container; it also creates a path by which container processes can change host files. Later lessons treat that relationship explicitly rather than assuming all paths are interchangeable.

## Anatomy and a trace you can follow

The fixture Dockerfile sets `WORKDIR /app` and copies `server.py` there. `docker run IMAGE python -c ...` starts in that image’s configured directory unless overridden. `--read-only` makes the container root filesystem read-only, but a separately mounted temporary filesystem or volume can still be writable. This is a property of each mount, not a promise that the process has no state.

For diagnosis, first identify whether a file came from the image, the writable layer, a bind mount, a named volume or a temporary filesystem. Then ask which lifecycle operation affects that storage. Do not test persistence by deleting the learner’s real classroom volume.

## How to use this lesson

The classroom displays this guide and saves your worksheet. Its Run button does not control your Docker engine. Docker engine access is powerful host access, so the classroom deliberately receives no engine socket. Work through the supplied examples without starting anything, then use the optional host lab only in your own disposable project. Reading a command, parsing YAML and actually running the project are different forms of evidence.

Use Bash in Linux, macOS Terminal, or Ubuntu under WSL 2 on Windows. The supported engine runs Linux containers. The maintained fixture is `courses/docker/fixtures/compose-lab/`; its README explains copying it into a new ignored learner directory, checking the engine, building locally with visible logs, and using the fixed project name `ds60-docker-study`. The fixture uses port 18080 on host loopback. Stop if that project name or port belongs to unrelated work; choose a new project name consistently in your own copy. Never paste a command against a remote Docker context simply because it is currently selected.

For Dockerfile examples, create a file named `Dockerfile` in a scratch project. YAML snippets describe a fragment unless explicitly called a complete file. Text transcripts are synthetic illustrations, not claims about your machine. Do not substitute a real password, token or private registry into a checked-in example.

## Worked example / walkthrough

### Worked example 1: Inspect a packaged file

The fixture image contains the app source at its documented path.

```sh
docker run --rm --pull never ds60-docker-study:local python -c "from pathlib import Path; print(Path('/app/server.py').is_file())"
```

**Expected observation:** True; this says the file is packaged, not that the server is running.

### Worked example 2: Try a write on a read-only root

A deliberate failure demonstrates an enforcement boundary.

```sh
docker run --rm --pull never --read-only ds60-docker-study:local python -c "from pathlib import Path; Path('/app/change.txt').write_text('x')"
```

**Expected observation:** A nonzero exit and an operating-system write error; the image is unchanged.

## Six progressive exercises

### Exercise 1: Classify /app/server.py in the fixture.

**Expected evidence:** An image-provided application file.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

### Exercise 2: Predict whether a sibling container sees an unmounted new file.

**Expected evidence:** It does not share the first container writable layer.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

### Exercise 3: Make a restart-versus-recreate persistence table.

**Expected evidence:** Writable layer survives restart but not removal; volumes follow their own lifetime.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

### Exercise 4: Diagnose a missing file after compose up recreates a service.

**Expected evidence:** Check whether it was written to the old disposable layer.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

### Exercise 5: Explain why read-only plus tmpfs permits temporary writes.

**Expected evidence:** The root mount and tmpfs have different write policies.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

### Exercise 6: Choose storage for user progress and transient scratch data.

**Expected evidence:** A named volume for progress and bounded temporary storage for scratch.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

## Common mistakes and diagnosis

Start with the smallest observation that separates two plausible causes. An image inspection answers questions about the packaged filesystem and configuration; container inspection adds runtime mounts, network attachment and exit status. An application request adds another layer of evidence. A healthy container can still serve the wrong application result. Preserve the original failure and the exact changed field before retrying.

The boundary case in this chapter is: Diagnose a missing file after compose up recreates a service. Use its expected observation, Check whether it was written to the old disposable layer., to avoid treating a successful command as proof of the wrong claim. Keep source edits in your own copy. Do not make a container privileged, mount the engine socket, disable all checks or delete every volume to make an example succeed.

## Retrieval, transfer and next steps

Close the explanations and draw the path from source files to image to container to the observation relevant here. Reconstruct the second worked example with one different value and predict what changes. Explain which state survives process restart, container recreation and image rebuild. If none of those operations applies to this mechanism, explain why.

Before proceeding, retain six evidence records. For the optional host project, use `docker compose -p ds60-docker-study down` from the fixture copy to stop its containers and remove its ordinary network. This command preserves named volumes. Volume deletion is a separate deliberate reset of that disposable lab after a backup or export, never a general cleanup step. The fixture README describes its exact scoped reset.

## Primary references

- [Official reference 1](https://docs.docker.com/engine/storage/)
- [Official reference 2](https://docs.docker.com/engine/storage/drivers/)

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for docker-003: The filesystem, writable layers and container lifetime.
Read courses/docker/guides/docker-003.md and courses/docker/lessons/docker-003.md. Direct prerequisites: `docker-002`
Ask me to predict the first example, review my worksheet, and give one hint at a time.
Keep courses/docker/solutions/ closed until I attempt or explicitly request comparison.
Distinguish image metadata, container state and actual application evidence.
Do not execute host commands, change Docker contexts or delete volumes on my behalf.
Finish with a fresh transfer case and ask which evidence would falsify my explanation.
```
