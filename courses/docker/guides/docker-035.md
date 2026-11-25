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

The classroom saves `courses/docker/lessons/docker-035.md` and holds no engine socket ([host-lab setup](../STUDY-GUIDE.md#host-lab-setup)).

**Host lab.** Measure before optimizing. Read the local size with worked example 1, then run `docker image history ds60-docker-study:local` and compare the fixture's own steps, the `COPY server.py` and the `RUN mkdir` layers, with the base layers below them: nearly all of the bytes come from the base, so trimming `server.py` could never matter. Next time readiness. Stop the app with `docker compose -p ds60-docker-study stop app`, then run `time docker compose -p ds60-docker-study up -d --wait app`, and repeat the stop and start three times. Note the spread. The healthcheck runs its first probe about one 5-second interval after the container starts, so `--wait` cannot finish sooner than that; the healthcheck settings, not the image, set the floor of this number. Leave the app running, since nothing was removed.

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

Answer-type prompts keep their answers in the solutions file ([exercise rules](../STUDY-GUIDE.md#exercise-rules)).

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

Exercise 4 is this chapter's boundary case: Diagnose a size optimization that breaks HTTPS. Compare the file lists of the working and optimized images for certificate bundles and libraries before measuring size again.

Sizes in `docker image ls` look additive, so five images at 150 MB each seem to cost 750 MB. Images built on the same base share those layers on disk and in transfer; the column reports each image's full size, not its unique share. Judging an optimization by the sum leads people to flatten or squash images, which destroys sharing: a squashed image can be smaller on its own yet cost more total disk and download than two images that reuse one base. Use `docker system df -v` to see shared and unique sizes per image, and judge a size change by what a target host would really have to transfer given the layers it already holds.

Never trade a safety control for a passing example ([safety rules](../STUDY-GUIDE.md#safety-rules)).

## Retrieval, transfer and next steps

**Retrieval.** List the startup phases and say which one an image size reduction can shorten.

**Transfer case.** Someone proposes switching the fixture to an Alpine-based Python image to cut its size. Before agreeing, what would you measure, and which correctness checks would you rerun?

Then run the [retrieval loop](../STUDY-GUIDE.md#retrieval-and-cleanup) and end any host session with its cleanup.

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
