# docker-035: Image size, startup latency and measurement

## Level and prerequisites

Advanced; about 120 minutes, with additional time for the optional host experiment. Direct prerequisites: `docker-034`

## Learning objectives

Design a readiness latency measurement. Write an optimization recommendation with evidence. Explain the difference between a configuration, an observed process and evidence of the application's behavior.

## Purpose, vocabulary and mental model

Image size affects transfer and storage, while startup latency depends on pulling, unpacking, container creation and application initialization. These costs overlap but are not identical. A smaller image can still start slowly if it performs expensive runtime work or waits for an unavailable dependency.

Layer sharing changes the amount of new data an engine needs. The displayed total image size is not always the incremental download for an engine that already has the base layers. Compression, cache state and platform also affect measured behavior.

Optimization should preserve correctness and maintainability. Removing a certificate bundle to save space may break HTTPS. Moving dependency installation to startup makes the image look smaller while making every run slower and less reproducible. Measure the user-visible path you actually want to improve.

## Anatomy and a trace you can follow

Compare cold and warm conditions explicitly. A cold engine or missing-image test includes transfer cost; a warm local restart does not. The course’s local workflow shows build logs so learners can see which layers are reused. Keep at least several observations and record input identity before drawing conclusions.

For a small fixture, inspect image size and measure a bounded short process or readiness interval. Do not remove shared base images or prune the user’s engine merely to manufacture a cold-cache experiment. A disposable engine or CI job is the appropriate environment for that test.

## How to use this lesson

The classroom displays this guide and saves your worksheet. Its Run button does not control your Docker engine. Docker engine access is powerful host access, so the classroom deliberately receives no engine socket. Work through the supplied examples without starting anything, then use the optional host lab only in your own disposable project. Reading a command, parsing YAML and actually running the project are different forms of evidence.

Use Bash in Linux, macOS Terminal, or Ubuntu under WSL 2 on Windows. The supported engine runs Linux containers. The maintained fixture is `courses/docker/fixtures/compose-lab/`; its README explains copying it into a new ignored learner directory, checking the engine, building locally with visible logs, and using the fixed project name `ds60-docker-study`. The fixture uses port 18080 on host loopback. Stop if that project name or port belongs to unrelated work; choose a new project name consistently in your own copy. Never paste a command against a remote Docker context simply because it is currently selected.

For Dockerfile examples, create a file named `Dockerfile` in a scratch project. YAML snippets describe a fragment unless explicitly called a complete file. Text transcripts are synthetic illustrations, not claims about your machine. Do not substitute a real password, token or private registry into a checked-in example.

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

### Exercise 1: Compare total image size and incremental transfer.

**Expected evidence:** Shared cached layers can reduce new transferred bytes.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

### Exercise 2: Predict why runtime package installation hurts startup.

**Expected evidence:** It adds network and dependency work to every run.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

### Exercise 3: Design a readiness latency measurement.

**Expected evidence:** Fixed image, known cache condition and repeated bounded readiness timing.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

### Exercise 4: Diagnose a size optimization that breaks HTTPS.

**Expected evidence:** A required runtime asset may have been removed.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

### Exercise 5: Explain why broad pruning is not an acceptable benchmark setup.

**Expected evidence:** It destroys shared caches and may affect unrelated work.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

### Exercise 6: Write an optimization recommendation with evidence.

**Expected evidence:** Measured bottleneck, bounded change, correctness recheck and actual improvement.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

## Common mistakes and diagnosis

Start with the smallest observation that separates two plausible causes. An image inspection answers questions about the packaged filesystem and configuration; container inspection adds runtime mounts, network attachment and exit status. An application request adds another layer of evidence. A healthy container can still serve the wrong application result. Preserve the original failure and the exact changed field before retrying.

The boundary case in this chapter is: Diagnose a size optimization that breaks HTTPS. Use its expected observation, A required runtime asset may have been removed., to avoid treating a successful command as proof of the wrong claim. Keep source edits in your own copy. Do not make a container privileged, mount the engine socket, disable all checks or delete every volume to make an example succeed.

## Retrieval, transfer and next steps

Close the explanations and draw the path from source files to image to container to the observation relevant here. Reconstruct the second worked example with one different value and predict what changes. Explain which state survives process restart, container recreation and image rebuild. If none of those operations applies to this mechanism, explain why.

Before proceeding, retain six evidence records. For the optional host project, use `docker compose -p ds60-docker-study down` from the fixture copy to stop its containers and remove its ordinary network. This command preserves named volumes. Volume deletion is a separate deliberate reset of that disposable lab after a backup or export, never a general cleanup step. The fixture README describes its exact scoped reset.

## Primary references

- [Official reference 1](https://docs.docker.com/build/cache/optimize/)
- [Official reference 2](https://docs.docker.com/reference/cli/docker/image/inspect/)

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
