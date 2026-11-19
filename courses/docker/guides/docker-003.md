# docker-003: The filesystem, writable layers and container lifetime

## Level and prerequisites

Beginner; about 100 minutes, with additional time for the optional host experiment. Direct prerequisites: `docker-002`

## Learning objectives

Make a restart-versus-recreate persistence table. Choose storage for user progress and transient scratch data. Use image layers, writable layer and container lifetime accurately when you explain what you observed.

## Purpose, vocabulary and mental model

A filesystem maps paths to objects such as files and directories. An image supplies initial read-only layers. A running container sees a merged view plus its own writable changes. Creating or modifying a file in that writable layer does not alter the underlying image used by other containers.

The layer belongs to that container. A restart of the same container generally retains it. Removing and recreating a container creates a different layer, even when the new process has the same name and image. Persistent application data therefore belongs on an explicit volume or other durable store, not accidentally in a disposable container’s root filesystem.

A path is meaningful inside a filesystem namespace. `/app/server.py` inside a container need not exist at that path on your laptop. A bind mount can deliberately map a host directory into a container; it also creates a path by which container processes can change host files. Later lessons treat that relationship explicitly rather than assuming all paths are interchangeable.

## Anatomy and a trace you can follow

The fixture Dockerfile sets `WORKDIR /app` and copies `server.py` there. `docker run IMAGE python -c ...` starts in that image’s configured directory unless overridden. `--read-only` makes the container root filesystem read-only, but a separately mounted temporary filesystem or volume can still be writable. This is a property of each mount, not a promise that the process has no state.

For diagnosis, first identify whether a file came from the image, the writable layer, a bind mount, a named volume or a temporary filesystem. Then ask which lifecycle operation affects that storage. Do not test persistence by deleting the learner’s real classroom volume.

## How to use this lesson

The classroom displays this guide and saves your worksheet, `courses/docker/lessons/docker-003.md`. Its Run button does not control your Docker engine. Docker engine access is powerful host access, so the classroom deliberately receives no engine socket. Work through the supplied examples without starting anything, then use the optional host lab only in your own disposable project. Reading a command, parsing YAML and actually running the project are different forms of evidence.

Use Bash in Linux, macOS Terminal, or Ubuntu under WSL 2 on Windows. The supported engine runs Linux containers. The maintained fixture is `courses/docker/fixtures/compose-lab/`; its README explains copying it into a new ignored learner directory, checking the engine, building locally with visible logs, and using the fixed project name `ds60-docker-study`. The fixture uses port 18080 on host loopback. Stop if that project name or port belongs to unrelated work; choose a new project name consistently in your own copy. Never paste a command against a remote Docker context simply because it is currently selected.

For Dockerfile examples, create a file named `Dockerfile` in a scratch project. YAML snippets describe a fragment unless explicitly called a complete file. Text transcripts are synthetic illustrations, not claims about your machine. Do not substitute a real password, token or private registry into a checked-in example. **How to use the lessons** in the [subject README](../README.md) collects these rules in one place.

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

For each exercise, name the object involved and the phase of its lifetime before changing anything, then vary only the condition the task names. Exercises that ask you to predict, explain, compare or diagnose keep their answers in the solutions file; the others show the evidence to look for.

### Exercise 1: Classify /app/server.py in the fixture.

**Hint:** Find the Dockerfile instruction that put the file there.

### Exercise 2: Predict whether a sibling container sees an unmounted new file.

**Hint:** Ask where the first container wrote the file and whether anything is shared.

### Exercise 3: Make a restart-versus-recreate persistence table.

**Expected evidence:** Writable layer survives restart but not removal; volumes follow their own lifetime.

**Hint:** Use three columns: the writable layer, a named volume and tmpfs.

### Exercise 4: Diagnose a missing file after compose up recreates a service.

**Hint:** Compare the container IDs before and after compose up.

### Exercise 5: Explain why read-only plus tmpfs permits temporary writes.

**Hint:** List the mounts in the container and the write policy of each.

### Exercise 6: Choose storage for user progress and transient scratch data.

**Hint:** Ask how long each kind of data must survive and who may delete it.

## Common mistakes and diagnosis

Writing important data to the container's writable layer and losing it when Compose recreates the service. Expecting a file created in one container to appear in another without a shared mount. Removing `read_only` instead of adding a tmpfs for scratch files.

Exercise 4 is this chapter's boundary case: Diagnose a missing file after compose up recreates a service. Start with the smallest observation that separates two plausible causes. An image inspection answers questions about the packaged filesystem and configuration; container inspection adds runtime mounts, network attachment and exit status; an application request adds another layer, and a healthy container can still serve the wrong result. Preserve the original failure and the exact changed field before retrying. Keep source edits in your own copy. Do not make a container privileged, mount the engine socket, disable all checks or delete every volume to make an example succeed.

## Retrieval, transfer and next steps

Close the explanations and draw the path from source files to image to container to the observation relevant here, using image layers, writable layer, container lifetime and read-only root filesystem. Reconstruct worked example 2 (Try a write on a read-only root) with one different value and predict what changes. Explain which state survives process restart, container recreation and image rebuild, or why none of those operations applies to this mechanism.

When a host session ends, run `docker compose -p ds60-docker-study down` from your fixture copy. It removes the project's containers and network but keeps named volumes; deleting a volume is a separate, deliberate reset described in the fixture README.

## Primary references

- [Storage overview](https://docs.docker.com/engine/storage/)
- [Storage drivers](https://docs.docker.com/engine/storage/drivers/)

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
