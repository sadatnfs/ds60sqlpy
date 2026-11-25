# docker-005: Dockerfile instructions and the first reproducible image

## Level and prerequisites

Beginner; about 100 minutes, with additional time for the optional host experiment. Direct prerequisites: `docker-004`

## Learning objectives

Write a minimal Dockerfile for a single file app. Define build and runtime acceptance separately. Use Dockerfile, FROM and COPY accurately when you explain what you observed.

## Purpose, vocabulary and mental model

A Dockerfile is a build recipe. Its instructions define a sequence of filesystem and configuration transformations. `FROM` selects the base image. `WORKDIR` selects a directory for later operations. `COPY` copies files from the build context. `RUN` executes during the build. `CMD` supplies a default command for a future container. Build-time work and runtime work are different phases.

A successful build means the build instructions completed under the builder’s inputs. It does not prove that the server starts, can write its intended volume or responds correctly. Packaging tests and runtime tests belong together. A beginner should be able to identify every file copied into the image and why it is necessary.

The maintained fixture uses only Python’s standard library, so it can teach build mechanics without a package repository. Its base image is still an external dependency during the first build. Later chapters pin immutable identities and export prepared images for disconnected use. The local tag is intentionally never pushed by a course command.

### Key terms

- **Dockerfile:** A build recipe whose instructions define a sequence of filesystem and configuration changes for an image.
- **`FROM`:** The instruction that selects the base image a build starts from.
- **`COPY`:** The instruction that copies named files from the build context into the image.
- **`CMD`:** The instruction that supplies the default command a future container runs; it does not execute during the build.
- **Image tag:** A local, human-readable name for a built image; creating one does not push anything to a registry.

## Anatomy and a trace you can follow

The final dot in `docker build -t NAME .` is the context directory, not punctuation to omit. Docker reads the Dockerfile relative to the command’s options and copies only eligible files from that context. The tag names the result locally. `--progress=plain` makes build steps and cache decisions visible in terminal logs.

Order instructions by dependency: runtime base, application directory, source copy, identity and command. Declare an unprivileged user after arranging readable files and writable data paths. `EXPOSE` documents an intended container port but does not publish it to your host.

## How to use this lesson

The classroom saves `courses/docker/lessons/docker-005.md` and holds no engine socket ([host-lab setup](../STUDY-GUIDE.md#host-lab-setup)).

**Host lab.** In a scratch directory, write the five-line Dockerfile from worked example 1 next to a copy of `server.py`, then build it with a distinct tag such as `ds60-docker-minimal:local` and `--progress=plain`. Read the log and match each numbered step to an instruction: FROM resolves a base, COPY transfers one file from the context, and CMD appears only as metadata because nothing runs at build time. Then run `docker image inspect ds60-docker-minimal:local --format '{{json .Config.Cmd}} {{json .Config.ExposedPorts}}'` to see the recorded command and the documented port, and `docker ps` to confirm that nothing is running yet. Start it with `docker run --rm -p 127.0.0.1:18081:8080 ds60-docker-minimal:local` and open the root URL. Stop it with Ctrl+C and remove the extra tag with `docker image rm` when you finish.

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

Answer-type prompts keep their answers in the solutions file ([exercise rules](../STUDY-GUIDE.md#exercise-rules)).

### Exercise 1: Sort RUN and CMD into lifecycle phases.

**Expected evidence:** RUN executes at build time; CMD describes later startup.

**Hint:** Ask which instruction runs during docker build and which is only recorded.

### Exercise 2: Explain the final context dot.

**Hint:** Ask which directory the builder receives as input.

### Exercise 3: Write a minimal Dockerfile for a single file app.

**Expected evidence:** Base, workdir, explicit source copy and foreground command.

**Hint:** Use one instruction each for the base, the working directory, the copy and the start command.

### Exercise 4: Diagnose COPY failure when a file is outside context.

**Hint:** Compare the file's path with the context directory you passed.

### Exercise 5: Explain why EXPOSE does not make `localhost:8080` work.

**Hint:** Compare EXPOSE in the Dockerfile with ports in compose.yaml.

### Exercise 6: Define build and runtime acceptance separately.

**Expected evidence:** Build succeeds, then endpoint and writable data behavior pass.

**Hint:** Write one check that passes after docker build and one that needs a running container.

## Common mistakes and diagnosis

Expecting `RUN` to start the server or `CMD` to run at build time. Copying from a path outside the build context. Treating `EXPOSE` as port publishing.

Exercise 4 is this chapter's boundary case: Diagnose COPY failure when a file is outside context. Read the build log line that names the context size and the failing `COPY` source path before moving any file or widening the context directory.

Learners also expect `docker build` to fail when the program is broken. A build only executes RUN steps; it never starts the program named by CMD. A `server.py` with a syntax error copies and builds perfectly, and the failure appears only when a container starts. If you want the build to reject broken source, add a deliberate RUN check such as `RUN python -m py_compile /app/server.py`, which runs at build time and fails the build on a syntax error. Keep in mind that this proves the file parses, not that the server answers requests, so runtime acceptance still needs its own check.

Never trade a safety control for a passing example ([safety rules](../STUDY-GUIDE.md#safety-rules)).

## Retrieval, transfer and next steps

**Retrieval.** List the Dockerfile instructions of the fixture in order and say which one changes when only the source file changes.

**Transfer case.** You add `RUN python -c "print('built')"` and `CMD ["python", "-c", "print('started')"]` to a Dockerfile, build it, and run one container. Which line appears in the build log, which appears in the container output, and how many times will each appear if you run three containers?

Then run the [retrieval loop](../STUDY-GUIDE.md#retrieval-and-cleanup) and end any host session with its cleanup.

## Primary references

- [Dockerfile reference](https://docs.docker.com/reference/dockerfile/)
- [Dockerfile overview](https://docs.docker.com/build/concepts/dockerfile/)

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
