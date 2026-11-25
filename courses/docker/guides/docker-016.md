# docker-016: Multi-stage builds and runtime dependency boundaries

## Level and prerequisites

Intermediate; about 100 minutes, with additional time for the optional host experiment. Direct prerequisites: `docker-015`

## Learning objectives

Design a builder-to-runtime artifact list. Specify final-image acceptance. Use multi-stage build, build stage and COPY --from accurately when you explain what you observed.

## Purpose, vocabulary and mental model

A multi-stage Dockerfile uses more than one FROM instruction. Each stage has its own filesystem and configuration. A builder stage can contain compilers and tests; a final stage can copy only the artifacts required to run. This reduces unnecessary tooling in the shipped image and makes the build-to-runtime boundary inspectable.

Copying a binary is not proof that it is self-contained. Dynamically linked programs require compatible libraries and an appropriate loader. Language runtimes, certificates, timezone data and user identity can also be necessary. A tiny image that fails at startup is not an improvement over a larger correct one.

Multi-stage design is about an explicit artifact contract. Define what the build produces, what tests validate it, what the final image needs and how the final image is exercised. The runtime test must execute the final stage, because tests in the builder can pass using files or tools absent from the shipped stage.

### Key terms

- **Multi-stage build:** A Dockerfile with more than one `FROM` instruction, where each stage has its own filesystem and configuration.
- **Builder stage:** A stage that holds the compilers, tools and tests needed to produce an artifact but not to run it.
- **`COPY --from`:** The instruction form that copies a chosen artifact from an earlier stage into the current one.
- **Final stage:** The shipped runtime image, which should contain only what the artifact needs to start and run.
- **Target stage:** A named stage selected with the `--target` build option, which deliberately stops the build there for debugging or testing.

## Anatomy and a trace you can follow

Name stages with `AS build`, then use `COPY --from=build /path /destination`. The source path refers to that stage’s filesystem, not the local host. `--target` deliberately stops at a named stage for debugging or testing. Do not accidentally distribute a debug stage containing credentials or development-only files.

The following Python example demonstrates stage selection with a text artifact; compiled-language lessons apply the same pattern to actual build output. It does not claim to reduce Python runtime size. A real optimized build requires measuring the resulting image and testing its runtime assumptions.

## How to use this lesson

The classroom saves `courses/docker/lessons/docker-016.md` and holds no engine socket ([host-lab setup](../STUDY-GUIDE.md#host-lab-setup)).

**Host lab.** Save worked example 1 as a Dockerfile in a scratch directory and build it twice: once normally as `ds60-stage-final` and once with `--target build` as `ds60-stage-build`. Run both with `ls /out /app`. The build-stage image has `/out/message.txt` and no `/app/message.txt`; the final image has the reverse, which shows that only the named file crossed the stage boundary. Then run the final image with no command override and confirm that it prints `prepared`. Compare `docker image ls ds60-stage-*`: the sizes are close because both stages start from the same base, a useful reminder that multi-stage builds shrink images only when the build stage carries tools the final stage leaves out. Remove both tags when you finish.

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

Answer-type prompts keep their answers in the solutions file ([exercise rules](../STUDY-GUIDE.md#exercise-rules)).

### Exercise 1: Locate the filesystem used by COPY --from.

**Expected evidence:** The named build stage.

**Hint:** Find the FROM line with the matching AS name.

### Exercise 2: Predict failure when a shared library is omitted.

**Hint:** Ask in which stage the program finally runs.

### Exercise 3: Design a builder-to-runtime artifact list.

**Expected evidence:** Executable or package plus explicit required runtime assets.

**Hint:** List everything the final process opens when it starts and runs.

### Exercise 4: Diagnose an accidentally shipped debug target.

**Hint:** Check which stage the build targeted and list the final image's files.

### Exercise 5: Explain why a smaller image is not automatically safer.

**Hint:** List security properties that do not depend on size.

### Exercise 6: Specify final-image acceptance.

**Expected evidence:** Run the exact final image under intended user, mounts and network.

**Hint:** Run the exact final image with its real user, mounts and network.

## Common mistakes and diagnosis

Testing only in the builder stage and shipping a runtime that lacks a library. Building the wrong `--target`. Assuming a small image is automatically patched and unprivileged.

Exercise 4 is this chapter's boundary case: Diagnose an accidentally shipped debug target. Read the `--target` flag and the final stage name in the build command, then list the shipped image's files to see which stage produced it.

A maintenance trap is naming stages by number. `COPY --from=0` refers to the first stage in the file, so when someone later inserts a new stage at the top, for example to fetch test data, the same line silently copies from a different stage. Sometimes the build fails because the path is missing, and sometimes it succeeds with the wrong file. Name every stage with `AS` and copy by name, as in `COPY --from=build`, so reordering cannot change which filesystem is read. Name external images explicitly too, rather than relying on a stage that happens to start from them.

Never trade a safety control for a passing example ([safety rules](../STUDY-GUIDE.md#safety-rules)).

## Retrieval, transfer and next steps

**Retrieval.** List what the final stage copies from the builder and what it deliberately leaves behind.

**Transfer case.** A program is compiled in a `golang` build stage and copied into a `scratch` final image. Running the final image fails with `no such file or directory` for the program, even though `docker export` shows the file is present. What is missing?

Then run the [retrieval loop](../STUDY-GUIDE.md#retrieval-and-cleanup) and end any host session with its cleanup.

## Primary references

- [Multi-stage builds](https://docs.docker.com/build/building/multi-stage/)

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
