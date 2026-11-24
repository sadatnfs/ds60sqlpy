# docker-035: Image size, startup latency and measurement

## Level and prerequisites

Advanced; about 120 minutes, with additional time for the optional host experiment. Direct prerequisites: `docker-034`

## Learning objectives

Design a readiness latency measurement. Write an optimization recommendation with evidence. Use image size, startup latency and layer reuse accurately when you explain what you observed.

## Purpose, vocabulary and mental model

Image size affects transfer and storage, while startup latency depends on pulling, unpacking, container creation and application initialization. These costs overlap but are not identical. A smaller image can still start slowly if it performs expensive runtime work or waits for an unavailable dependency.

Layer sharing changes the amount of new data an engine needs. The displayed total image size is not always the incremental download for an engine that already has the base layers. Compression, cache state and platform also affect measured behavior.

Optimization should preserve correctness and maintainability. Removing a certificate bundle to save space may break HTTPS. Moving dependency installation to startup makes the image look smaller while making every run slower and less reproducible. Measure the user-visible path you actually want to improve.

### Key terms

- **Image size:** The stored and transferred size of an image, which affects pulls but is only one part of startup cost.
- **Startup latency:** The time from a start request to a usable application, including pulling, unpacking, creation and initialization.
- **Incremental download:** The new layer data an engine must fetch, which is often smaller than the displayed total image size.
- **Cold cache:** A measurement condition with images or build cache missing, so transfer and initialization costs are included.
- **Warm restart:** A measurement condition with layers already present locally, so transfer cost is excluded and only startup work is timed.

## Anatomy and a trace you can follow

Compare cold and warm conditions explicitly. A cold engine or missing-image test includes transfer cost; a warm local restart does not. The course’s local workflow shows build logs so learners can see which layers are reused. Keep at least several observations and record input identity before drawing conclusions.

For a small fixture, inspect image size and measure a bounded short process or readiness interval. Do not remove shared base images or prune the user’s engine merely to manufacture a cold-cache experiment. A disposable engine or CI job is the appropriate environment for that test.

## How to use this lesson

The classroom displays this guide and saves your worksheet, `courses/docker/lessons/docker-035.md`. Its Run button does not control your Docker engine. Docker engine access is powerful host access, so the classroom deliberately receives no engine socket. Work through the supplied examples without starting anything, then use the optional host lab only in your own disposable project. Reading a command, parsing YAML and actually running the project are different forms of evidence.

Use Bash in Linux, macOS Terminal, or Ubuntu under WSL 2 on Windows. The supported engine runs Linux containers. The maintained fixture is `courses/docker/fixtures/compose-lab/`; its README explains copying it into a new ignored learner directory, checking the engine, building locally with visible logs, and using the fixed project name `ds60-docker-study`. The fixture uses port 18080 on host loopback. Stop if that project name or port belongs to unrelated work; choose a new project name consistently in your own copy. Never paste a command against a remote Docker context simply because it is currently selected.

For Dockerfile examples, create a file named `Dockerfile` in a scratch project. YAML snippets describe a fragment unless explicitly called a complete file. Text transcripts are synthetic illustrations, not claims about your machine. Do not substitute a real password, token or private registry into a checked-in example. **How to use the lessons** in the [subject README](../README.md) collects these rules in one place.

## Worked example / walkthrough

### Worked example 1: Read local image size

This is an artifact measurement, not a download benchmark.

```sh
docker image inspect ds60-docker-study:local --format "{{.Size}}"
```

**Expected observation:** A byte count for the local image representation; interpret it with layer sharing in mind.

### Worked example 2: Separate startup phases

The categories guide a measurement plan.

```text
image available? -> create container -> start process -> initialize app -> readiness passes
user request -> connect -> handler -> response
```

**Expected observation:** Measure the phase responsible for the user-visible delay rather than optimizing a different metric.

## Six progressive exercises

For each exercise, name the object involved and the phase of its lifetime before changing anything, then vary only the condition the task names. Exercises that ask you to predict, explain, compare or diagnose keep their answers in the solutions file; the others show the evidence to look for.

### Exercise 1: Compare total image size and incremental transfer.

**Hint:** Ask which layers a host already has.

### Exercise 2: Predict why runtime package installation hurts startup.

**Hint:** Count the downloads that happen at every start.

### Exercise 3: Design a readiness latency measurement.

**Expected evidence:** Fixed image, known cache condition and repeated bounded readiness timing.

**Hint:** Fix the image and cache state, then time several starts until readiness.

### Exercise 4: Diagnose a size optimization that breaks HTTPS.

**Hint:** List the runtime files HTTPS needs, such as CA certificates.

### Exercise 5: Explain why broad pruning is not an acceptable benchmark setup.

**Hint:** Ask what else on the engine uses the cache you would delete.

### Exercise 6: Write an optimization recommendation with evidence.

**Expected evidence:** Measured bottleneck, bounded change, correctness recheck and actual improvement.

**Hint:** Measure before and after the change and recheck correctness.

## Common mistakes and diagnosis

Installing packages when the container starts. Removing CA certificates or other runtime assets to save space. Pruning the whole engine before a benchmark.

Exercise 4 is this chapter's boundary case: Diagnose a size optimization that breaks HTTPS. Compare the file lists of the working and optimized images for certificate bundles and libraries before measuring size again. Preserve the original failure and the exact changed field before retrying. Do not make a container privileged, mount the engine socket, disable all checks or delete every volume to make an example succeed.

## Retrieval, transfer and next steps

Close the explanations first. List the startup phases and say which one an image size reduction can shorten. Then reconstruct worked example 2 (Separate startup phases) with one different value, predict what changes, and name which of image size, startup latency, layer reuse and measurement method the change touches.

When a host session ends, run `docker compose -p ds60-docker-study down` from your fixture copy. It removes the project's containers and network but keeps named volumes; deleting a volume is a separate, deliberate reset described in the fixture README.

## Primary references

- [Optimize cache usage in builds](https://docs.docker.com/build/cache/optimize/)
- [docker image inspect reference](https://docs.docker.com/reference/cli/docker/image/inspect/)

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for docker-035: Image size, startup latency and measurement.
Read courses/docker/guides/docker-035.md and courses/docker/lessons/docker-035.md. Direct prerequisites: `docker-034`
Ask me to predict the first example, review my worksheet, and give one hint at a time.
Keep courses/docker/solutions/ closed until I attempt or explicitly request comparison.
Distinguish image metadata, container state and actual application evidence.
Do not execute host commands, change Docker contexts or delete volumes on my behalf.
Finish with a fresh transfer case and ask which evidence would falsify my explanation.
```
