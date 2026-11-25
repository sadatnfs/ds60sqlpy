# docker-007: Layers, cache invalidation and efficient rebuilds

## Level and prerequisites

Beginner; about 100 minutes, with additional time for the optional host experiment. Direct prerequisites: `docker-006`

## Learning objectives

Reorder dependency metadata and app source conceptually. Design a build-performance experiment. Use build cache, cache invalidation and instruction order accurately when you explain what you observed.

## Purpose, vocabulary and mental model

A layer records filesystem changes from a build step. Build cache can reuse a prior result when the builder considers an instruction and its relevant inputs unchanged. Caching is a performance mechanism, not proof that a dependency is current or that a security update has been applied.

Instruction order creates a dependency chain. If a source copy changes before an expensive dependency installation, later steps may need to run again. Separating dependency metadata from frequently edited source can improve iteration. The correct split depends on the package manager and lockfile, not on memorizing one Dockerfile pattern.

A cache hit is visible in build logs. A fast build is not automatically cached, and a cache miss is not automatically a bug. Reproducibility requires identifying inputs, versions and build settings. The same text can still download different bytes if it refers to mutable remote dependencies.

### Key terms

- **Layer:** The recorded filesystem changes produced by one build step.
- **Build cache:** Stored results of earlier build steps that the builder reuses when an instruction and its inputs are unchanged.
- **Cache invalidation:** The point where a changed instruction or input forces that step and every later step to run again.
- **Instruction order:** The sequence of Dockerfile steps, which decides how much work a single changed input invalidates.
- **Dependency layer:** A layer built from dependency metadata such as a lockfile, placed before frequently edited source so it stays cached.

## Anatomy and a trace you can follow

Compare an unchanged rebuild with a rebuild after changing only a harmless source string in your learner copy. Record which instruction first stops being cached. A build with `--no-cache` intentionally ignores build-step cache, but it does not inherently replace every already available base image. Fetching newer bases is a separate operation.

Cache mounts, covered in the next stage, preserve download caches without baking their contents into the runtime image. Do not put real credentials into cache keys, ARG values or copied files. Build output and dependency recovery are observable concerns, so keep plain logs for your experiments.

## How to use this lesson

The classroom saves `courses/docker/lessons/docker-007.md` and holds no engine socket ([host-lab setup](../STUDY-GUIDE.md#host-lab-setup)).

**Host lab.** Run worked example 1 twice and note which numbered steps say `CACHED` the second time. Then change one comment in `server.py` and build again: the base and WORKDIR steps stay cached, and the `COPY server.py` step and everything after it rerun. Next, add a harmless `RUN echo dependencies` line above the COPY and build twice more; it caches after its first run, and an edit to `server.py` no longer invalidates it. That ordering is the whole trick of dependency layers. Finish with worked example 2 and compare its total time with the cached build. Record each step label and its cache status rather than wall-clock durations, which vary with the engine. Delete the extra RUN line afterwards so your copy matches the fixture again.

## Worked example / walkthrough

### Worked example 1: Observe an unchanged rebuild

Use the same copied context and local tag.

```sh
docker build --progress=plain -t ds60-docker-study:local .
docker build --progress=plain -t ds60-docker-study:local .
```

**Expected observation:** The second build commonly reports cached unchanged steps; exact durations depend on the engine.

### Worked example 2: Compare an explicit cache bypass

This is an optional rebuild, not a general repair for every error.

```sh
docker build --no-cache --progress=plain -t ds60-docker-study:local .
```

**Expected observation:** Build steps run again; this does not by itself establish a newer base image or a different application result.

## Six progressive exercises

Answer-type prompts keep their answers in the solutions file ([exercise rules](../STUDY-GUIDE.md#exercise-rules)).

### Exercise 1: Predict the first invalidated step after editing server.py.

**Hint:** Find the first instruction whose inputs include server.py.

### Exercise 2: Record evidence of a real cache hit.

**Expected evidence:** A specific step labeled cached in plain build logs.

**Hint:** Build twice with --progress=plain and compare the step lines.

### Exercise 3: Reorder dependency metadata and app source conceptually.

**Expected evidence:** Stable dependency inputs precede rapidly changing source.

**Hint:** Ask which files change on most edits and which change rarely.

### Exercise 4: Diagnose a cached step that downloads a mutable dependency.

**Hint:** Ask what the cache key of a RUN step includes and what it leaves out.

### Exercise 5: Explain no-cache versus pulling a base.

**Hint:** Compare what --no-cache and --pull each refresh.

### Exercise 6: Design a build-performance experiment.

**Expected evidence:** Same engine and context, one controlled edit, named cache observations.

**Hint:** Change one input at a time and record which steps rebuild.

## Common mistakes and diagnosis

Copying the whole source tree before installing dependencies, so every edit reinstalls them. Assuming a cached download step fetched fresh bytes. Using `--no-cache` when the stale part was the base image.

Exercise 4 is this chapter's boundary case: Diagnose a cached step that downloads a mutable dependency. Compare the text of the cached `RUN` instruction with the bytes it downloads; an unchanged instruction can be served from cache even when the remote file changed.

A further trap is believing that `docker build --pull` and `--no-cache` are the same refresh. `--pull` asks the engine to check the registry for a newer base image before building, while `--no-cache` reruns every instruction against whatever base is already local. A security fix in the base image therefore needs `--pull`, and a stale download inside a RUN step needs either a changed instruction or `--no-cache`. When you need both, use both, and record the resolved base digest from the build log so you can show which base the new image actually used.

Never trade a safety control for a passing example ([safety rules](../STUDY-GUIDE.md#safety-rules)).

## Retrieval, transfer and next steps

**Retrieval.** Predict which build steps rerun after editing only `server.py` with the dependency file copied first.

**Transfer case.** A Dockerfile copies `requirements.txt`, runs `pip install`, and then copies the source tree. You edit only `app/views.py`. Then, separately, you add a new package to `requirements.txt`. Which steps rerun in each case, and why?

Then run the [retrieval loop](../STUDY-GUIDE.md#retrieval-and-cleanup) and end any host session with its cleanup.

## Primary references

- [Docker build cache](https://docs.docker.com/build/cache/)
- [Build cache invalidation](https://docs.docker.com/build/cache/invalidation/)

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for docker-007: Layers, cache invalidation and efficient rebuilds.
Read courses/docker/guides/docker-007.md and courses/docker/lessons/docker-007.md. Direct prerequisites: `docker-006`
Ask me to predict the first example, review my worksheet, and give one hint at a time.
Keep courses/docker/solutions/ closed until I attempt or explicitly request comparison.
Distinguish image metadata, container state and actual application evidence.
Do not execute host commands, change Docker contexts or delete volumes on my behalf.
Finish with a fresh transfer case and ask which evidence would falsify my explanation.
```
