# docker-016: Multi-stage builds and runtime dependency boundaries

## Level and prerequisites

Intermediate; about 100 minutes, with additional time for the optional host experiment. Direct prerequisites: `docker-015`

## Learning objectives

Design a builder-to-runtime artifact list. Specify final-image acceptance. Explain the difference between a configuration, an observed process and evidence of the application's behavior.

## Purpose, vocabulary and mental model

A multi-stage Dockerfile uses more than one FROM instruction. Each stage has its own filesystem and configuration. A builder stage can contain compilers and tests; a final stage can copy only the artifacts required to run. This reduces unnecessary tooling in the shipped image and makes the build-to-runtime boundary inspectable.

Copying a binary is not proof that it is self-contained. Dynamically linked programs require compatible libraries and an appropriate loader. Language runtimes, certificates, timezone data and user identity can also be necessary. A tiny image that fails at startup is not an improvement over a larger correct one.

Multi-stage design is about an explicit artifact contract. Define what the build produces, what tests validate it, what the final image needs and how the final image is exercised. The runtime test must execute the final stage, because tests in the builder can pass using files or tools absent from the shipped stage.

## Anatomy and a trace you can follow

Name stages with `AS build`, then use `COPY --from=build /path /destination`. The source path refers to that stage’s filesystem, not the local host. `--target` deliberately stops at a named stage for debugging or testing. Do not accidentally distribute a debug stage containing credentials or development-only files.

The following Python example demonstrates stage selection with a text artifact; compiled-language lessons apply the same pattern to actual build output. It does not claim to reduce Python runtime size. A real optimized build requires measuring the resulting image and testing its runtime assumptions.

## How to use this lesson

The classroom displays this guide and saves your worksheet. Its Run button does not control your Docker engine. Docker engine access is powerful host access, so the classroom deliberately receives no engine socket. Work through the supplied examples without starting anything, then use the optional host lab only in your own disposable project. Reading a command, parsing YAML and actually running the project are different forms of evidence.

Use Bash in Linux, macOS Terminal, or Ubuntu under WSL 2 on Windows. The supported engine runs Linux containers. The maintained fixture is `courses/docker/fixtures/compose-lab/`; its README explains copying it into a new ignored learner directory, checking the engine, building locally with visible logs, and using the fixed project name `ds60-docker-study`. The fixture uses port 18080 on host loopback. Stop if that project name or port belongs to unrelated work; choose a new project name consistently in your own copy. Never paste a command against a remote Docker context simply because it is currently selected.

For Dockerfile examples, create a file named `Dockerfile` in a scratch project. YAML snippets describe a fragment unless explicitly called a complete file. Text transcripts are synthetic illustrations, not claims about your machine. Do not substitute a real password, token or private registry into a checked-in example.

## Worked example / walkthrough

### Worked example 1: Trace a copied artifact

A complete conceptual two-stage recipe writes a public text artifact.

```dockerfile
FROM python:3.12-slim AS build
RUN mkdir /out && printf "prepared\n" > /out/message.txt
FROM python:3.12-slim
COPY --from=build /out/message.txt /app/message.txt
CMD ["python", "-c", "print(open('/app/message.txt').read().strip())"]
```

**Expected observation:** The final container prints prepared; the final stage only receives the explicitly copied artifact.

### Worked example 2: Distinguish builder and final tests

This is a release evidence outline rather than a shell script.

```text
builder: compile -> unit tests -> /out/program
final: copy program + runtime dependencies -> start -> acceptance request
```

**Expected observation:** A builder success is followed by an actual final-image execution check.

## Six progressive exercises

### Exercise 1: Locate the filesystem used by COPY --from.

**Expected evidence:** The named build stage.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

### Exercise 2: Predict failure when a shared library is omitted.

**Expected evidence:** The final process fails even if builder tests passed.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

### Exercise 3: Design a builder-to-runtime artifact list.

**Expected evidence:** Executable or package plus explicit required runtime assets.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

### Exercise 4: Diagnose an accidentally shipped debug target.

**Expected evidence:** Inspect final stage selection and image contents.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

### Exercise 5: Explain why a smaller image is not automatically safer.

**Expected evidence:** Correct dependencies, patching and privileges still matter.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

### Exercise 6: Specify final-image acceptance.

**Expected evidence:** Run the exact final image under intended user, mounts and network.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

## Common mistakes and diagnosis

Start with the smallest observation that separates two plausible causes. An image inspection answers questions about the packaged filesystem and configuration; container inspection adds runtime mounts, network attachment and exit status. An application request adds another layer of evidence. A healthy container can still serve the wrong application result. Preserve the original failure and the exact changed field before retrying.

The boundary case in this chapter is: Diagnose an accidentally shipped debug target. Use its expected observation, Inspect final stage selection and image contents., to avoid treating a successful command as proof of the wrong claim. Keep source edits in your own copy. Do not make a container privileged, mount the engine socket, disable all checks or delete every volume to make an example succeed.

## Retrieval, transfer and next steps

Close the explanations and draw the path from source files to image to container to the observation relevant here. Reconstruct the second worked example with one different value and predict what changes. Explain which state survives process restart, container recreation and image rebuild. If none of those operations applies to this mechanism, explain why.

Before proceeding, retain six evidence records. For the optional host project, use `docker compose -p ds60-docker-study down` from the fixture copy to stop its containers and remove its ordinary network. This command preserves named volumes. Volume deletion is a separate deliberate reset of that disposable lab after a backup or export, never a general cleanup step. The fixture README describes its exact scoped reset.

## Primary references

- [Official reference 1](https://docs.docker.com/build/building/multi-stage/)

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for docker-016: Multi-stage builds and runtime dependency boundaries.
Read courses/docker/guides/docker-016.md and courses/docker/lessons/docker-016.md. Direct prerequisites: `docker-015`
Ask me to predict the first example, review my worksheet, and give one hint at a time.
Keep courses/docker/solutions/ closed until I attempt or explicitly request comparison.
Distinguish image metadata, container state and actual application evidence.
Do not execute host commands, change Docker contexts or delete volumes on my behalf.
Finish with a fresh transfer case and ask which evidence would falsify my explanation.
```
