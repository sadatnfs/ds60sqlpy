# docker-015: BuildKit, cache mounts and build secrets

## Level and prerequisites

Intermediate; about 100 minutes, with additional time for the optional host experiment. Direct prerequisites: `docker-014`

## Learning objectives

Design a cold-build check. Describe a dependency acquisition policy. Use BuildKit, cache mount and secret mount accurately when you explain what you observed.

## Purpose, vocabulary and mental model

BuildKit is the build engine used by modern Docker tooling. It can execute a build graph, reuse cached results and make special mounts available to individual build steps. A cache mount stores reusable downloads; a secret mount provides sensitive input to a step without treating that input as an ordinary copied image file. These mounts have different purposes and lifetimes.

A secret mount reduces accidental persistence but does not make arbitrary build commands safe. A command can still print a secret or copy it into an output. The author must review what the step does. Never put credentials in ARG, ENV, a source file or a command URL simply because the final application does not use them.

Build-time network access is an external dependency. Prefer locked public inputs for the default teaching build. The fixture has no package downloads beyond its base image. This chapter uses a synthetic secret string in a separate scratch build and never needs a real registry credential.

### Key terms

- **BuildKit:** The modern Docker build engine that runs a build graph, reuses cached results and provides special mounts to steps.
- **Cache mount:** A directory mounted into one build step that keeps reusable downloads between builds without adding them to a layer.
- **Secret mount:** A file mounted into one build step that exposes sensitive input without copying it into an image layer.
- **Build secret:** Sensitive build input supplied with the `--secret` option, never through `ARG`, `ENV`, a source file or a command URL.
- **Cold build:** A build with no reusable cache, which shows the full cost of every step and every external download.

## Anatomy and a trace you can follow

A Dockerfile RUN mount exists only for that build operation. `type=cache` selects a persistent builder cache directory. `type=secret,id=demo` selects a separately supplied secret. Read a secret only at its declared path, and do not echo its bytes. `required=true` causes a missing input to fail clearly. Supply the value from the host with `docker build --secret id=demo,src=./demo-secret.txt .` or `--secret id=demo,env=DEMO_SECRET`; the step reads it at `/run/secrets/demo`.

Cache entries can improve speed but should not be the only copy of a required source artifact. A cold build must still produce the same intended result from declared dependencies. Treat cache as discardable acceleration, not durable application data.

## How to use this lesson

The classroom displays this guide and saves your worksheet, `courses/docker/lessons/docker-015.md`. Its Run button does not control your Docker engine. Docker engine access is powerful host access, so the classroom deliberately receives no engine socket. Work through the supplied examples without starting anything, then use the optional host lab only in your own disposable project. Reading a command, parsing YAML and actually running the project are different forms of evidence.

Use Bash in Linux, macOS Terminal, or Ubuntu under WSL 2 on Windows. The supported engine runs Linux containers. The maintained fixture is `courses/docker/fixtures/compose-lab/`; its README explains copying it into a new ignored learner directory, checking the engine, building locally with visible logs, and using the fixed project name `ds60-docker-study`. The fixture uses port 18080 on host loopback. Stop if that project name or port belongs to unrelated work; choose a new project name consistently in your own copy. Never paste a command against a remote Docker context simply because it is currently selected.

For Dockerfile examples, create a file named `Dockerfile` in a scratch project. YAML snippets describe a fragment unless explicitly called a complete file. Text transcripts are synthetic illustrations, not claims about your machine. Do not substitute a real password, token or private registry into a checked-in example. **How to use the lessons** in the [subject README](../README.md) collects these rules in one place.

## Worked example / walkthrough

### Worked example 1: Reuse downloads with a cache mount

This pattern is illustrative for a Python project with a hash-locked requirements file.

```dockerfile
COPY requirements.lock /tmp/requirements.lock
RUN --mount=type=cache,target=/root/.cache/pip \
    python -m pip install --require-hashes -r /tmp/requirements.lock
```

**Expected observation:** A rebuild after a lock change reuses previously downloaded wheels from the cache mount; the cache directory is not part of any image layer.

### Worked example 2: Require a synthetic build secret without printing it

Use only an invented demo value in a separate scratch build.

```dockerfile
RUN --mount=type=secret,id=demo,required=true \
    test -s /run/secrets/demo
```

**Expected observation:** The build succeeds only when the named nonempty secret is supplied; the command does not reveal its content.

## Six progressive exercises

For each exercise, name the object involved and the phase of its lifetime before changing anything, then vary only the condition the task names. Exercises that ask you to predict, explain, compare or diagnose keep their answers in the solutions file; the others show the evidence to look for.

### Exercise 1: Compare a cache mount and a secret mount.

**Hint:** Ask what each mount holds and how long it should live.

### Exercise 2: Predict a required secret missing from the build.

**Hint:** Read what required=true does when no --secret is supplied.

### Exercise 3: Design a cold-build check.

**Expected evidence:** Remove reliance on cache while preserving declared public inputs.

**Hint:** Build with the cache removed and compare the result with a warm build.

### Exercise 4: Diagnose a secret copied into an output file.

**Hint:** Ask what the RUN command did with the bytes it read.

### Exercise 5: Explain why ARG is unsuitable for a password.

**Hint:** Check where build arguments appear, such as docker history and provenance.

### Exercise 6: Describe a dependency acquisition policy.

**Hint:** List what the build downloads, from where and how its identity is checked.

## Common mistakes and diagnosis

Passing a password with `--build-arg` or `ENV`. Printing or copying a mounted secret into an image file. Treating the cache mount as the only copy of a dependency.

Exercise 4 is this chapter's boundary case: Diagnose a secret copied into an output file. Search the build output and the final image layers for the secret value's location, not the value itself, before blaming the secret mount option. Preserve the original failure and the exact changed field before retrying. Do not make a container privileged, mount the engine socket, disable all checks or delete every volume to make an example succeed.

## Retrieval, transfer and next steps

Close the explanations first. Explain where the secret is visible during a `RUN --mount=type=secret` step and where it must not appear afterward. Then reconstruct worked example 2 (Require a synthetic build secret without printing it) with one different value, predict what changes, and name which of BuildKit, cache mount, secret mount, --secret and cold build the change touches.

When a host session ends, run `docker compose -p ds60-docker-study down` from your fixture copy. It removes the project's containers and network but keeps named volumes; deleting a volume is a separate, deliberate reset described in the fixture README.

## Primary references

- [BuildKit](https://docs.docker.com/build/buildkit/)
- [Build secrets](https://docs.docker.com/build/building/secrets/)

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for docker-015: BuildKit, cache mounts and build secrets.
Read courses/docker/guides/docker-015.md and courses/docker/lessons/docker-015.md. Direct prerequisites: `docker-014`
Ask me to predict the first example, review my worksheet, and give one hint at a time.
Keep courses/docker/solutions/ closed until I attempt or explicitly request comparison.
Distinguish image metadata, container state and actual application evidence.
Do not execute host commands, change Docker contexts or delete volumes on my behalf.
Finish with a fresh transfer case and ask which evidence would falsify my explanation.
```
