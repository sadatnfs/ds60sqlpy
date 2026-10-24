# docker-006: Build context, .dockerignore and accidental data exposure

## Level and prerequisites

Beginner; about 100 minutes, with additional time for the optional host experiment. Direct prerequisites: `docker-005`

## Learning objectives

Design a context inventory for the fixture. Describe source and image privacy acceptance. Explain the difference between a configuration, an observed process and evidence of the application's behavior.

## Purpose, vocabulary and mental model

The build context is the set of files a builder may use. A `.dockerignore` file removes matching paths from that input. This reduces transfer size and prevents accidental inclusion of caches, learner data, credentials and repository history. It is a packaging boundary, not a substitute for reviewing the Dockerfile and resulting image.

A Dockerfile can accidentally copy too much with `COPY . .`. Even if a later instruction deletes a secret, the earlier image layer may retain it. The safe design is to avoid supplying sensitive data as ordinary layer input at all. Build secrets use a separate mechanism covered later; runtime secrets use another lifecycle again.

The fixture keeps its context tiny: server source, Dockerfile, Compose definition and ignore rules. Learner notes and progress live outside the source image. Different builders can run remotely, so context minimization also makes it easier to know which files leave your machine when building against a selected endpoint.

## Anatomy and a trace you can follow

Ignore patterns are evaluated relative to the build context. Negated patterns can include an otherwise ignored path, and ordering can matter. Use a simple allowlist or a short reviewed exclude list for a small teaching project. Do not assume `.gitignore` automatically controls Docker build inputs.

Inspect the actual image after a representative build. A source manifest can assert intended exclusions, while an image file listing demonstrates what was packaged. Avoid printing secret content while verifying absence; inspect names or expected safe inventory instead.

## How to use this lesson

The classroom displays this guide and saves your worksheet. Its Run button does not control your Docker engine. Docker engine access is powerful host access, so the classroom deliberately receives no engine socket. Work through the supplied examples without starting anything, then use the optional host lab only in your own disposable project. Reading a command, parsing YAML and actually running the project are different forms of evidence.

Use Bash in Linux, macOS Terminal, or Ubuntu under WSL 2 on Windows. The supported engine runs Linux containers. The maintained fixture is `courses/docker/fixtures/compose-lab/`; its README explains copying it into a new ignored learner directory, checking the engine, building locally with visible logs, and using the fixed project name `ds60-docker-study`. The fixture uses port 18080 on host loopback. Stop if that project name or port belongs to unrelated work; choose a new project name consistently in your own copy. Never paste a command against a remote Docker context simply because it is currently selected.

For Dockerfile examples, create a file named `Dockerfile` in a scratch project. YAML snippets describe a fragment unless explicitly called a complete file. Text transcripts are synthetic illustrations, not claims about your machine. Do not substitute a real password, token or private registry into a checked-in example.

## Worked example / walkthrough

### Worked example 1: Define a small ignore boundary

These are illustrative rules for the learner copy.

```text
.git
.learning
.env
*.log
__pycache__
*.pyc
```

**Expected observation:** Those paths are unavailable to COPY from this context; source files needed by the app remain available.

### Worked example 2: Prefer explicit source copying

Explicit paths make packaging intent visible.

```dockerfile
COPY server.py /app/server.py
```

**Expected observation:** Only the named app file is copied by this instruction; unrelated project files are not implicitly included.

## Six progressive exercises

### Exercise 1: Predict whether .gitignore protects Docker context.

**Expected evidence:** No automatic equivalence exists.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

### Exercise 2: Identify three private paths to exclude.

**Expected evidence:** Environment files, learner data and repository history.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

### Exercise 3: Design a context inventory for the fixture.

**Expected evidence:** A short list of necessary public build inputs.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

### Exercise 4: Explain why deleting a secret in a later layer is insufficient.

**Expected evidence:** The earlier layer can retain the copied bytes.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

### Exercise 5: Check that an ignored required source produces a useful failure.

**Expected evidence:** COPY fails instead of silently borrowing a host file.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

### Exercise 6: Describe source and image privacy acceptance.

**Expected evidence:** Review inputs, build recipe and safe final file inventory.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

## Common mistakes and diagnosis

Start with the smallest observation that separates two plausible causes. An image inspection answers questions about the packaged filesystem and configuration; container inspection adds runtime mounts, network attachment and exit status. An application request adds another layer of evidence. A healthy container can still serve the wrong application result. Preserve the original failure and the exact changed field before retrying.

The boundary case in this chapter is: Explain why deleting a secret in a later layer is insufficient. Use its expected observation, The earlier layer can retain the copied bytes., to avoid treating a successful command as proof of the wrong claim. Keep source edits in your own copy. Do not make a container privileged, mount the engine socket, disable all checks or delete every volume to make an example succeed.

## Retrieval, transfer and next steps

Close the explanations and draw the path from source files to image to container to the observation relevant here. Reconstruct the second worked example with one different value and predict what changes. Explain which state survives process restart, container recreation and image rebuild. If none of those operations applies to this mechanism, explain why.

Before proceeding, retain six evidence records. For the optional host project, use `docker compose -p ds60-docker-study down` from the fixture copy to stop its containers and remove its ordinary network. This command preserves named volumes. Volume deletion is a separate deliberate reset of that disposable lab after a backup or export, never a general cleanup step. The fixture README describes its exact scoped reset.

## Primary references

- [Official reference 1](https://docs.docker.com/build/concepts/context/)
- [Official reference 2](https://docs.docker.com/reference/dockerfile/#dockerignore-file)

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for docker-006: Build context, .dockerignore and accidental data exposure.
Read courses/docker/guides/docker-006.md and courses/docker/lessons/docker-006.md. Direct prerequisites: `docker-005`
Ask me to predict the first example, review my worksheet, and give one hint at a time.
Keep courses/docker/solutions/ closed until I attempt or explicitly request comparison.
Distinguish image metadata, container state and actual application evidence.
Do not execute host commands, change Docker contexts or delete volumes on my behalf.
Finish with a fresh transfer case and ask which evidence would falsify my explanation.
```
