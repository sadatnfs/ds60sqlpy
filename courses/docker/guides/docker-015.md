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

The classroom saves `courses/docker/lessons/docker-015.md` and holds no engine socket ([host-lab setup](../STUDY-GUIDE.md#host-lab-setup)).

**Host lab.** In a scratch directory, write a Dockerfile with `FROM python:3.12-slim`, which is already local from the fixture build, followed by the secret step from worked example 2. Build it once without `--secret` and read the failure; the step refuses to run because the mount is required. Put a synthetic value such as `not-a-real-secret` in `demo.txt`, then build with `--secret id=demo,src=demo.txt -t ds60-secret-demo`. Check two places for leaks: `docker history --no-trunc ds60-secret-demo` shows the RUN line but not the value, and `docker save ds60-secret-demo | grep -a -c not-a-real-secret` should print 0. Delete `demo.txt` and remove the image when you finish. Never rehearse this with a real token, even though nothing is printed.

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

Answer-type prompts keep their answers in the solutions file ([exercise rules](../STUDY-GUIDE.md#exercise-rules)).

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

Exercise 4 is this chapter's boundary case: Diagnose a secret copied into an output file. Search the build output and the final image layers for the secret value's location, not the value itself, before blaming the secret mount option.

Another trap is expecting a new secret value to trigger a rebuild. The contents of a secret are deliberately not part of the cache key, so if you rotate a token and rebuild, an unchanged RUN step that used the secret is served from cache, and its output still reflects whatever the old token fetched. That is usually what you want for speed, but it means a rotated credential does not prove that dependencies were downloaded again. When the step must run with the new secret, force it explicitly with `--no-cache-filter` for that stage or `--no-cache`, and confirm in the plain log that the step ran.

Never trade a safety control for a passing example ([safety rules](../STUDY-GUIDE.md#safety-rules)).

## Retrieval, transfer and next steps

**Retrieval.** Explain where the secret is visible during a `RUN --mount=type=secret` step and where it must not appear afterward.

**Transfer case.** A Dockerfile switches to `USER 10001` and then runs `RUN --mount=type=cache,target=/root/.cache/pip pip install -r requirements.txt`. Every build downloads everything again. Explain why the cache mount is not helping and how to fix it.

Then run the [retrieval loop](../STUDY-GUIDE.md#retrieval-and-cleanup) and end any host session with its cleanup.

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
