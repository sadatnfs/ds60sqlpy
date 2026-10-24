# docker-005: Dockerfile instructions and the first reproducible image

## Level and prerequisites

Beginner; about 100 minutes, with additional time for the optional host experiment. Direct prerequisites: `docker-004`

## Learning objectives

Write a minimal Dockerfile for a single file app. Define build and runtime acceptance separately. Explain the difference between a configuration, an observed process and evidence of the application's behavior.

## Purpose, vocabulary and mental model

A Dockerfile is a build recipe. Its instructions define a sequence of filesystem and configuration transformations. `FROM` selects the base image. `WORKDIR` selects a directory for later operations. `COPY` copies files from the build context. `RUN` executes during the build. `CMD` supplies a default command for a future container. Build-time work and runtime work are different phases.

A successful build means the build instructions completed under the builder’s inputs. It does not prove that the server starts, can write its intended volume or responds correctly. Packaging tests and runtime tests belong together. A beginner should be able to identify every file copied into the image and why it is necessary.

The maintained fixture uses only Python’s standard library, so it can teach build mechanics without a package repository. Its base image is still an external dependency during the first build. Later chapters pin immutable identities and export prepared images for disconnected use. The local tag is intentionally never pushed by a course command.

## Anatomy and a trace you can follow

The final dot in `docker build -t NAME .` is the context directory, not punctuation to omit. Docker reads the Dockerfile relative to the command’s options and copies only eligible files from that context. The tag names the result locally. `--progress=plain` makes build steps and cache decisions visible in terminal logs.

Order instructions by dependency: runtime base, application directory, source copy, identity and command. Declare an unprivileged user after arranging readable files and writable data paths. `EXPOSE` documents an intended container port but does not publish it to your host.

## How to use this lesson

The classroom displays this guide and saves your worksheet. Its Run button does not control your Docker engine. Docker engine access is powerful host access, so the classroom deliberately receives no engine socket. Work through the supplied examples without starting anything, then use the optional host lab only in your own disposable project. Reading a command, parsing YAML and actually running the project are different forms of evidence.

Use Bash in Linux, macOS Terminal, or Ubuntu under WSL 2 on Windows. The supported engine runs Linux containers. The maintained fixture is `courses/docker/fixtures/compose-lab/`; its README explains copying it into a new ignored learner directory, checking the engine, building locally with visible logs, and using the fixed project name `ds60-docker-study`. The fixture uses port 18080 on host loopback. Stop if that project name or port belongs to unrelated work; choose a new project name consistently in your own copy. Never paste a command against a remote Docker context simply because it is currently selected.

For Dockerfile examples, create a file named `Dockerfile` in a scratch project. YAML snippets describe a fragment unless explicitly called a complete file. Text transcripts are synthetic illustrations, not claims about your machine. Do not substitute a real password, token or private registry into a checked-in example.

## Worked example / walkthrough

### Worked example 1: Read the complete minimal recipe

The actual fixture adds a data directory and non-root identity.

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY server.py /app/server.py
EXPOSE 8080
CMD ["python", "server.py"]
```

**Expected observation:** Build creates an image containing the program; port 8080 is documented but remains unpublished.

### Worked example 2: Build from the copied fixture

Run from your own compose-lab copy, after engine inspection.

```sh
docker build --progress=plain -t ds60-docker-study:local .
```

**Expected observation:** Visible build logs finish successfully and the local tag appears in image inspection; no registry upload occurs.

## Six progressive exercises

### Exercise 1: Sort RUN and CMD into lifecycle phases.

**Expected evidence:** RUN executes at build time; CMD describes later startup.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

### Exercise 2: Explain the final context dot.

**Expected evidence:** It selects the current directory as build input.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

### Exercise 3: Write a minimal Dockerfile for a single file app.

**Expected evidence:** Base, workdir, explicit source copy and foreground command.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

### Exercise 4: Diagnose COPY failure when a file is outside context.

**Expected evidence:** Change the owned project layout or explicit context intentionally.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

### Exercise 5: Explain why EXPOSE does not make localhost:8080 work.

**Expected evidence:** It is metadata; port publishing is a runtime configuration.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

### Exercise 6: Define build and runtime acceptance separately.

**Expected evidence:** Build succeeds, then endpoint and writable data behavior pass.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

## Common mistakes and diagnosis

Start with the smallest observation that separates two plausible causes. An image inspection answers questions about the packaged filesystem and configuration; container inspection adds runtime mounts, network attachment and exit status. An application request adds another layer of evidence. A healthy container can still serve the wrong application result. Preserve the original failure and the exact changed field before retrying.

The boundary case in this chapter is: Diagnose COPY failure when a file is outside context. Use its expected observation, Change the owned project layout or explicit context intentionally., to avoid treating a successful command as proof of the wrong claim. Keep source edits in your own copy. Do not make a container privileged, mount the engine socket, disable all checks or delete every volume to make an example succeed.

## Retrieval, transfer and next steps

Close the explanations and draw the path from source files to image to container to the observation relevant here. Reconstruct the second worked example with one different value and predict what changes. Explain which state survives process restart, container recreation and image rebuild. If none of those operations applies to this mechanism, explain why.

Before proceeding, retain six evidence records. For the optional host project, use `docker compose -p ds60-docker-study down` from the fixture copy to stop its containers and remove its ordinary network. This command preserves named volumes. Volume deletion is a separate deliberate reset of that disposable lab after a backup or export, never a general cleanup step. The fixture README describes its exact scoped reset.

## Primary references

- [Official reference 1](https://docs.docker.com/reference/dockerfile/)
- [Official reference 2](https://docs.docker.com/build/concepts/dockerfile/)

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for docker-005: Dockerfile instructions and the first reproducible image.
Read courses/docker/guides/docker-005.md and courses/docker/lessons/docker-005.md. Direct prerequisites: `docker-004`
Ask me to predict the first example, review my worksheet, and give one hint at a time.
Keep courses/docker/solutions/ closed until I attempt or explicitly request comparison.
Distinguish image metadata, container state and actual application evidence.
Do not execute host commands, change Docker contexts or delete volumes on my behalf.
Finish with a fresh transfer case and ask which evidence would falsify my explanation.
```
