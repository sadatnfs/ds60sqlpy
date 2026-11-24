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

The classroom displays this guide and saves your worksheet, `courses/docker/lessons/docker-007.md`. Its Run button does not control your Docker engine. Docker engine access is powerful host access, so the classroom deliberately receives no engine socket. Work through the supplied examples without starting anything, then use the optional host lab only in your own disposable project. Reading a command, parsing YAML and actually running the project are different forms of evidence.

Use Bash in Linux, macOS Terminal, or Ubuntu under WSL 2 on Windows. The supported engine runs Linux containers. The maintained fixture is `courses/docker/fixtures/compose-lab/`; its README explains copying it into a new ignored learner directory, checking the engine, building locally with visible logs, and using the fixed project name `ds60-docker-study`. The fixture uses port 18080 on host loopback. Stop if that project name or port belongs to unrelated work; choose a new project name consistently in your own copy. Never paste a command against a remote Docker context simply because it is currently selected.

For Dockerfile examples, create a file named `Dockerfile` in a scratch project. YAML snippets describe a fragment unless explicitly called a complete file. Text transcripts are synthetic illustrations, not claims about your machine. Do not substitute a real password, token or private registry into a checked-in example. **How to use the lessons** in the [subject README](../README.md) collects these rules in one place.

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

For each exercise, name the object involved and the phase of its lifetime before changing anything, then vary only the condition the task names. Exercises that ask you to predict, explain, compare or diagnose keep their answers in the solutions file; the others show the evidence to look for.

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

Exercise 4 is this chapter's boundary case: Diagnose a cached step that downloads a mutable dependency. Compare the text of the cached `RUN` instruction with the bytes it downloads; an unchanged instruction can be served from cache even when the remote file changed. Preserve the original failure and the exact changed field before retrying. Do not make a container privileged, mount the engine socket, disable all checks or delete every volume to make an example succeed.

## Retrieval, transfer and next steps

Close the explanations first. Predict which build steps rerun after editing only `server.py` with the dependency file copied first. Then reconstruct worked example 2 (Compare an explicit cache bypass) with one different value, predict what changes, and name which of build cache, cache invalidation, instruction order and dependency layer the change touches.

When a host session ends, run `docker compose -p ds60-docker-study down` from your fixture copy. It removes the project's containers and network but keeps named volumes; deleting a volume is a separate, deliberate reset described in the fixture README.

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
