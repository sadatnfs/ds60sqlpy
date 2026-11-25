# docker-003: The filesystem, writable layers and container lifetime

## Level and prerequisites

Beginner; about 100 minutes, with additional time for the optional host experiment. Direct prerequisites: `docker-002`

## Learning objectives

Make a restart-versus-recreate persistence table. Choose storage for user progress and transient scratch data. Use image layers, writable layer and container lifetime accurately when you explain what you observed.

## Purpose, vocabulary and mental model

A filesystem maps paths to objects such as files and directories. An image supplies initial read-only layers. A running container sees a merged view plus its own writable changes. Creating or modifying a file in that writable layer does not alter the underlying image used by other containers.

The layer belongs to that container. A restart of the same container generally retains it. Removing and recreating a container creates a different layer, even when the new process has the same name and image. Persistent application data therefore belongs on an explicit volume or other durable store, not accidentally in a disposable container’s root filesystem.

A path is meaningful inside a filesystem namespace. `/app/server.py` inside a container need not exist at that path on your laptop. A bind mount can deliberately map a host directory into a container; it also creates a path by which container processes can change host files. Later lessons treat that relationship explicitly rather than assuming all paths are interchangeable.

### Key terms

- **Image layers:** The read-only filesystem layers an image supplies, shared unchanged by every container created from it.
- **Merged view:** The single filesystem a container sees, combining the image layers with its own writable changes.
- **Container lifetime:** The span from creation to removal; a restart keeps the writable layer, while removal and recreation discard it.
- **Read-only root filesystem:** A runtime setting that refuses writes to packaged paths, so only explicit mounts remain writable.

## Anatomy and a trace you can follow

The fixture Dockerfile sets `WORKDIR /app` and copies `server.py` there. `docker run IMAGE python -c ...` starts in that image’s configured directory unless overridden. `--read-only` makes the container root filesystem read-only, but a separately mounted temporary filesystem or volume can still be writable. This is a property of each mount, not a promise that the process has no state.

For diagnosis, first identify whether a file came from the image, the writable layer, a bind mount, a named volume or a temporary filesystem. Then ask which lifecycle operation affects that storage. Do not test persistence by deleting the learner’s real classroom volume.

## How to use this lesson

The classroom saves `courses/docker/lessons/docker-003.md` and holds no engine socket ([host-lab setup](../STUDY-GUIDE.md#host-lab-setup)).

**Host lab.** Use a named throwaway container to see the writable layer directly: `docker run --name ds60-layer-demo --pull never ds60-docker-study:local python -c "open('/tmp/w.txt','w').write('1')"`. Then `docker diff ds60-layer-demo` lists `A /tmp/w.txt`, an addition recorded only in that container's layer. Remove it with `docker rm ds60-layer-demo` and the change is gone while the image is untouched. Next, start the fixture project and run `docker compose -p ds60-docker-study exec app sh -c 'echo note > /tmp/note; touch /app/x'`. The `/tmp` write succeeds because Compose mounts a tmpfs there, and `touch` fails because the root filesystem is read-only. After `docker compose -p ds60-docker-study restart app` the note is gone, since a tmpfs lives in memory and is cleared when the container stops, while `/counter` still reports the value kept in the `/data` volume.

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

Answer-type prompts keep their answers in the solutions file ([exercise rules](../STUDY-GUIDE.md#exercise-rules)).

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

Exercise 4 is this chapter's boundary case: Diagnose a missing file after compose up recreates a service. Record the container ID from `docker compose ps -q app` before and after `up`, then note which path the missing file was written to, so the evidence separates recreation from a bad write.

A tempting rescue after losing a file is `docker commit`, which turns a container's writable layer into a new image. It does preserve the file, but it also bakes in whatever else the layer holds: scratch output, caches, perhaps a credential typed during debugging. The result has no Dockerfile recipe, so nobody can rebuild or review it, and data in volumes is not included at all. The correction is to separate the two kinds of change: application code changes go into the Dockerfile and a rebuild, while data that must survive recreation goes into a named volume mounted at a known path.

Never trade a safety control for a passing example ([safety rules](../STUDY-GUIDE.md#safety-rules)).

## Retrieval, transfer and next steps

**Retrieval.** Predict whether a file written to `/tmp` in the container survives `restart`, `up --force-recreate` and an image rebuild.

**Transfer case.** A service writes uploads to `/app/uploads` with no volume and no `read_only`. Yesterday the uploads survived `docker compose restart`. Today, after editing an environment value and running `docker compose up -d`, they are gone. Explain both observations and propose one change.

Then run the [retrieval loop](../STUDY-GUIDE.md#retrieval-and-cleanup) and end any host session with its cleanup.

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
