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

The classroom saves `courses/docker/lessons/docker-013.md` and holds no engine socket ([host-lab setup](../STUDY-GUIDE.md#host-lab-setup)).

**Host lab.** Create a scratch volume with `docker volume create ds60-vol-demo` and write into it from one throwaway container: `docker run --rm --pull never -v ds60-vol-demo:/data ds60-docker-study:local python -c "open('/data/n.txt','w').write('kept')"`. Read the file back from a second, separate container with `cat /data/n.txt`. The two containers never ran at the same time, yet they shared one file, because the data lives in the volume. Next, mount the same volume at `/app` in a third run and list it with `ls /app`: only `n.txt` appears, and the packaged `server.py` is hidden for that container. Finish with `docker volume rm ds60-vol-demo`, a deliberate deletion of a scratch volume you created yourself, and leave the project's `study-data` volume and its counter untouched.

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

Answer-type prompts keep their answers in the solutions file ([exercise rules](../STUDY-GUIDE.md#exercise-rules)).

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

Exercise 4 is this chapter's boundary case: Diagnose missing code after mounting over /app. Compare the files in `/app` from the image with the files the running container shows, and read the mount table for the same path.

A quieter surprise comes from how an empty named volume is initialized. The first time an empty named volume is mounted over a path that already holds files in the image, the engine copies those files and their ownership into the volume. That is why the fixture's `/data`, owned by UID 10001 in the image, is writable in a brand new volume. After that first mount the volume is no longer empty, so a later image that ships new or changed files at the same path does not update it, and the container keeps showing the old copies. Bind mounts never perform this copy. Keep image defaults out of data paths, or let the application create missing defaults at startup.

Never trade a safety control for a passing example ([safety rules](../STUDY-GUIDE.md#safety-rules)).

## Retrieval, transfer and next steps

**Retrieval.** Predict the counter value after recreating the app with the named volume kept, and after removing that volume.

**Transfer case.** Two services in one project mount `study-data`, the app at `/data` and a reporting service at `/source:ro`. A learner removes the app container and recreates it. Does the reporting service still see `counter.json`, and what would make the file disappear for both?

Then run the [retrieval loop](../STUDY-GUIDE.md#retrieval-and-cleanup) and end any host session with its cleanup.

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
