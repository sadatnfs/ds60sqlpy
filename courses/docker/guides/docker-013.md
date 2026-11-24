# docker-013: Named volumes, bind mounts and persistence experiments

## Level and prerequisites

Beginner; about 100 minutes, with additional time for the optional host experiment. Direct prerequisites: `docker-012`

## Learning objectives

Build a persistence evidence table. Choose a safe cleanup policy for progress. Use named volume, bind mount and persistence accurately when you explain what you observed.

## Purpose, vocabulary and mental model

A named volume is storage managed by the engine and mounted into containers. A bind mount maps an explicitly chosen host path into a container. A temporary filesystem is volatile storage usually backed by memory. The choice determines ownership, portability, backup and what survives container replacement.

The fixture stores its counter in a named volume mounted at `/data`. Its application code is in the image. This separation lets the app container be replaced without losing the counter. A bind mount is useful for editing a local project, but it gives container processes direct access to the chosen host files with the mount’s permissions.

Mounting a directory over an image path hides the image content at that location while the mount is present. A bind mount hides the packaged directory without copying its files into the host directory. Docker-managed volumes have an important initialization exception: when an empty volume is mounted over existing image content, Docker copies that content into it by default unless volume-nocopy is selected. A nonempty mounted volume hides the packaged content. Distinguish those cases before diagnosing missing or unexpectedly seeded files.

### Key terms

- **Named volume:** Engine-managed storage, mounted into containers, that survives container removal and recreation.
- **Bind mount:** A mapping of an explicitly chosen host path into a container, giving its processes direct access to those host files.
- **Temporary filesystem:** Volatile storage, usually backed by memory, that disappears when the container stops.
- **Container recreation:** Removing a container and creating a new one, which discards its writable layer but keeps mounted volumes.
- **`volume-nocopy`:** A mount option that stops Docker from seeding an empty named volume with the image content at its mount path.

## Anatomy and a trace you can follow

A Compose service can mount `study-data:/data`, with `study-data` declared in the top-level `volumes` section. Compose assigns a project-scoped volume name unless configured otherwise. The fixture’s app treats an absent counter.json as an initial count of zero and updates that file through an atomic replace under a process-local lock. It does not create an exclusive marker file. The separate restore command uses exclusive file creation to refuse overwriting an existing restore target.

Use POST `/increment` only within the disposable lab to intentionally change the teaching counter; GET `/counter` reads it without mutation. Record a value, recreate only the app container, and verify that the value did not reset. Rebuilding an image is unnecessary for this test, because the question concerns storage lifetime.

## How to use this lesson

The classroom displays this guide and saves your worksheet, `courses/docker/lessons/docker-013.md`. Its Run button does not control your Docker engine. Docker engine access is powerful host access, so the classroom deliberately receives no engine socket. Work through the supplied examples without starting anything, then use the optional host lab only in your own disposable project. Reading a command, parsing YAML and actually running the project are different forms of evidence.

Use Bash in Linux, macOS Terminal, or Ubuntu under WSL 2 on Windows. The supported engine runs Linux containers. The maintained fixture is `courses/docker/fixtures/compose-lab/`; its README explains copying it into a new ignored learner directory, checking the engine, building locally with visible logs, and using the fixed project name `ds60-docker-study`. The fixture uses port 18080 on host loopback. Stop if that project name or port belongs to unrelated work; choose a new project name consistently in your own copy. Never paste a command against a remote Docker context simply because it is currently selected.

For Dockerfile examples, create a file named `Dockerfile` in a scratch project. YAML snippets describe a fragment unless explicitly called a complete file. Text transcripts are synthetic illustrations, not claims about your machine. Do not substitute a real password, token or private registry into a checked-in example. **How to use the lessons** in the [subject README](../README.md) collects these rules in one place.

## Worked example / walkthrough

### Worked example 1: Declare separate application data

The volume is owned by this Compose project.

```yaml
services:
  app:
    volumes:
      - study-data:/data
volumes:
  study-data: {}
```

**Expected observation:** The mounted data is independent of the app container writable layer.

### Worked example 2: Recreate the app while retaining its volume

Record the counter before and after in the browser.

```sh
docker compose -p ds60-docker-study up -d --force-recreate --wait app
```

**Expected observation:** The container ID changes; the same mounted counter persists and can continue increasing.

## Six progressive exercises

For each exercise, name the object involved and the phase of its lifetime before changing anything, then vary only the condition the task names. Exercises that ask you to predict, explain, compare or diagnose keep their answers in the solutions file; the others show the evidence to look for.

### Exercise 1: Predict data retention after app recreation.

**Hint:** Ask whether the new container mounts the same named volume.

### Exercise 2: Compare named volume and bind mount ownership.

**Hint:** Ask who creates and manages the storage location in each case.

### Exercise 3: Build a persistence evidence table.

**Expected evidence:** Before value, old/new container IDs, volume identity and after value.

**Hint:** Record the counter, the container ID and the volume name before and after.

### Exercise 4: Diagnose missing code after mounting over /app.

**Hint:** List the mounts and ask what happens to image files under a mount point.

### Exercise 5: Explain why changing project names may look like data loss.

**Hint:** Run docker volume ls and compare the volume names for both projects.

### Exercise 6: Choose a safe cleanup policy for progress.

**Hint:** Separate routine stopping from a deliberate data reset.

## Common mistakes and diagnosis

Mounting a host directory over `/app` and hiding the packaged code. Changing the project name and then looking for data in the new, empty volume. Deleting volumes as part of routine cleanup.

Exercise 4 is this chapter's boundary case: Diagnose missing code after mounting over /app. Compare the files in `/app` from the image with the files the running container shows, and read the mount table for the same path. Preserve the original failure and the exact changed field before retrying. Do not make a container privileged, mount the engine socket, disable all checks or delete every volume to make an example succeed.

## Retrieval, transfer and next steps

Close the explanations first. Predict the counter value after recreating the app with the named volume kept, and after removing that volume. Then reconstruct worked example 2 (Recreate the app while retaining its volume) with one different value, predict what changes, and name which of named volume, bind mount, persistence and container recreation the change touches.

When a host session ends, run `docker compose -p ds60-docker-study down` from your fixture copy. It removes the project's containers and network but keeps named volumes; deleting a volume is a separate, deliberate reset described in the fixture README.

## Primary references

- [Volumes](https://docs.docker.com/engine/storage/volumes/)
- [Bind mounts](https://docs.docker.com/engine/storage/bind-mounts/)

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for docker-013: Named volumes, bind mounts and persistence experiments.
Read courses/docker/guides/docker-013.md and courses/docker/lessons/docker-013.md. Direct prerequisites: `docker-012`
Ask me to predict the first example, review my worksheet, and give one hint at a time.
Keep courses/docker/solutions/ closed until I attempt or explicitly request comparison.
Distinguish image metadata, container state and actual application evidence.
Do not execute host commands, change Docker contexts or delete volumes on my behalf.
Finish with a fresh transfer case and ask which evidence would falsify my explanation.
```
