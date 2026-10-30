# docker-015: BuildKit, cache mounts and build secrets

## Level and prerequisites

Intermediate; about 100 minutes, with additional time for the optional host experiment. Direct prerequisites: `docker-014`

## Learning objectives

Design a cold-build check. Describe a dependency acquisition policy. Explain the difference between a configuration, an observed process and evidence of the application's behavior.

## Purpose, vocabulary and mental model

BuildKit is the build engine used by modern Docker tooling. It can execute a build graph, reuse cached results and make special mounts available to individual build steps. A cache mount stores reusable downloads; a secret mount provides sensitive input to a step without treating that input as an ordinary copied image file. These mounts have different purposes and lifetimes.

A secret mount reduces accidental persistence but does not make arbitrary build commands safe. A command can still print a secret or copy it into an output. The author must review what the step does. Never put credentials in ARG, ENV, a source file or a command URL simply because the final application does not use them.

Build-time network access is an external dependency. Prefer locked public inputs for the default teaching build. The fixture has no package downloads beyond its base image. This chapter uses a synthetic secret string in a separate scratch build and never needs a real registry credential.

## Anatomy and a trace you can follow

A Dockerfile RUN mount exists only for that build operation. `type=cache` selects a persistent builder cache directory. `type=secret,id=demo` selects a separately supplied secret. Read a secret only at its declared path, and do not echo its bytes. `required=true` causes a missing input to fail clearly.

Cache entries can improve speed but should not be the only copy of a required source artifact. A cold build must still produce the same intended result from declared dependencies. Treat cache as discardable acceleration, not durable application data.

## How to use this lesson

The classroom displays this guide and saves your worksheet. Its Run button does not control your Docker engine. Docker engine access is powerful host access, so the classroom deliberately receives no engine socket. Work through the supplied examples without starting anything, then use the optional host lab only in your own disposable project. Reading a command, parsing YAML and actually running the project are different forms of evidence.

Use Bash in Linux, macOS Terminal, or Ubuntu under WSL 2 on Windows. The supported engine runs Linux containers. The maintained fixture is `courses/docker/fixtures/compose-lab/`; its README explains copying it into a new ignored learner directory, checking the engine, building locally with visible logs, and using the fixed project name `ds60-docker-study`. The fixture uses port 18080 on host loopback. Stop if that project name or port belongs to unrelated work; choose a new project name consistently in your own copy. Never paste a command against a remote Docker context simply because it is currently selected.

For Dockerfile examples, create a file named `Dockerfile` in a scratch project. YAML snippets describe a fragment unless explicitly called a complete file. Text transcripts are synthetic illustrations, not claims about your machine. Do not substitute a real password, token or private registry into a checked-in example.

## Worked example / walkthrough

### Worked example 1: Inspect a cache mount

This pattern is illustrative for a Python project with an actual lock procedure.

```dockerfile
RUN --mount=type=cache,target=/root/.cache/pip \
    python -m pip --version
```

**Expected observation:** The cache directory is available to this step; it is not copied as normal application data.

### Worked example 2: Require a synthetic build secret without printing it

Use only an invented demo value in a separate scratch build.

```dockerfile
RUN --mount=type=secret,id=demo,required=true \
    test -s /run/secrets/demo
```

**Expected observation:** The build succeeds only when the named nonempty secret is supplied; the command does not reveal its content.

## Six progressive exercises

### Exercise 1: Compare a cache mount and a secret mount.

**Expected evidence:** Reusable acceleration versus sensitive transient input.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

### Exercise 2: Predict a required secret missing from the build.

**Expected evidence:** The step fails before pretending to authenticate.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

### Exercise 3: Design a cold-build check.

**Expected evidence:** Remove reliance on cache while preserving declared public inputs.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

### Exercise 4: Diagnose a secret copied into an output file.

**Expected evidence:** Mount isolation does not prevent the command from leaking bytes.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

### Exercise 5: Explain why ARG is unsuitable for a password.

**Expected evidence:** Build metadata and history can expose values.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

### Exercise 6: Describe a dependency acquisition policy.

**Expected evidence:** Locked inputs, deliberate network access and no default private credentials.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

## Common mistakes and diagnosis

Start with the smallest observation that separates two plausible causes. An image inspection answers questions about the packaged filesystem and configuration; container inspection adds runtime mounts, network attachment and exit status. An application request adds another layer of evidence. A healthy container can still serve the wrong application result. Preserve the original failure and the exact changed field before retrying.

The boundary case in this chapter is: Diagnose a secret copied into an output file. Use its expected observation, Mount isolation does not prevent the command from leaking bytes., to avoid treating a successful command as proof of the wrong claim. Keep source edits in your own copy. Do not make a container privileged, mount the engine socket, disable all checks or delete every volume to make an example succeed.

## Retrieval, transfer and next steps

Close the explanations and draw the path from source files to image to container to the observation relevant here. Reconstruct the second worked example with one different value and predict what changes. Explain which state survives process restart, container recreation and image rebuild. If none of those operations applies to this mechanism, explain why.

Before proceeding, retain six evidence records. For the optional host project, use `docker compose -p ds60-docker-study down` from the fixture copy to stop its containers and remove its ordinary network. This command preserves named volumes. Volume deletion is a separate deliberate reset of that disposable lab after a backup or export, never a general cleanup step. The fixture README describes its exact scoped reset.

## Primary references

- [Official reference 1](https://docs.docker.com/build/buildkit/)
- [Official reference 2](https://docs.docker.com/build/building/secrets/)

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
