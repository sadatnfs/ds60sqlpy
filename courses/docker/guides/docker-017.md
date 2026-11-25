# docker-017: CPU architectures, image indexes and cross-platform builds

## Level and prerequisites

Intermediate; about 100 minutes, with additional time for the optional host experiment. Direct prerequisites: `docker-016`

## Learning objectives

Design a two-platform evidence matrix. Write an honest portability claim. Use CPU architecture, image index and --platform accurately when you explain what you observed.

## Purpose, vocabulary and mental model

An architecture is a machine instruction family such as amd64 or arm64. A Linux image can target one or several architectures. A multi-platform image index points to platform-specific images; it is not one binary that magically runs everywhere. The engine selects a compatible image based on platform metadata.

An Apple Silicon laptop commonly runs arm64 natively while many hosted runners use amd64. Emulation can run some foreign-architecture programs, but it adds cost and does not prove native performance or compatibility. A successful source build on one platform is only evidence for that platform’s produced artifact.

Cross-compilation and emulation are distinct strategies. A compiler may emit target binaries while itself running natively; an emulator executes foreign instructions. Some projects need target-specific libraries or test hosts. A release matrix must name which platforms were actually built and executed.

### Key terms

- **CPU architecture:** A machine instruction family such as `amd64` or `arm64` that a binary is compiled for.
- **Image index:** A multi-platform list that points to platform-specific images so the engine can select a compatible one.
- **Target platform:** The operating system and architecture pair, such as `linux/arm64`, requested with the `--platform` option.
- **Emulation:** Executing foreign-architecture instructions through a translator such as QEMU, which is slower and does not prove native behavior.
- **Cross-compilation:** A compiler running natively while emitting binaries for a different target architecture.

## Anatomy and a trace you can follow

BuildKit exposes platform arguments such as BUILDPLATFORM and TARGETPLATFORM. A Dockerfile may choose a native builder stage and pass the target into a compiler. Do not use these names as a substitute for correct compiler flags. A multi-platform build also needs an output strategy compatible with your image store or a deliberate export.

The course does not push images. For an optional local experiment, build one selected platform with `docker buildx build --platform linux/arm64 --load` and inspect the result. When the target differs from the host architecture, every RUN step executes under emulation: Docker Desktop includes QEMU emulation, while a Linux engine needs binfmt handlers installed first. A single-platform `--load` works with the default image store; loading a multi-platform index needs the containerd image store. Do not force a foreign platform on the ordinary classroom just to avoid investigating a missing dependency wheel.

## How to use this lesson

The classroom saves `courses/docker/lessons/docker-017.md` and holds no engine socket ([host-lab setup](../STUDY-GUIDE.md#host-lab-setup)).

**Host lab.** Record three platform facts before building anything: `uname -m` on the host, `docker info --format '{{.Architecture}}'` for the engine, and `docker image inspect ds60-docker-study:local --format '{{.Os}}/{{.Architecture}}'` for the fixture image. On most machines all three agree. If you have emulation available, build worked example 1 for the other architecture under its own tag and run `docker run --rm --pull never --platform linux/arm64 ds60-docker-study:arm64 python -c "import platform; print(platform.machine())"`, adjusting the platform to the one your host is not. The program reports the foreign machine type while the host stays unchanged. Without emulation the same run fails with `exec format error`. Remove the extra tag afterwards with `docker image rm`.

## Worked example / walkthrough

### Worked example 1: Build and inspect one target platform

From your fixture copy, build one explicit platform and read the result's platform metadata. The arm64 base image is downloaded if it is not already local.

```sh
docker buildx build --platform linux/arm64 --load -t ds60-docker-study:arm64 .
docker image inspect ds60-docker-study:arm64 --format "{{.Os}}/{{.Architecture}}"
```

**Expected observation:** linux/arm64 whatever the host is; on an amd64 host the RUN steps executed under QEMU emulation, which shows the image was packaged for arm64, not that it performs well natively.

### Worked example 2: Read the index model

These are illustrative identities, not real downloadable digests.

```text
image index
  linux/amd64 -> image A -> amd64 program
  linux/arm64 -> image B -> arm64 program
```

**Expected observation:** Each platform entry needs its own build and runtime qualification.

## Six progressive exercises

Answer-type prompts keep their answers in the solutions file ([exercise rules](../STUDY-GUIDE.md#exercise-rules)).

### Exercise 1: Predict whether Linux implies amd64.

**Hint:** Read the platform string as two separate parts.

### Exercise 2: Classify cross-compilation and emulation.

**Hint:** Ask which machine executes the target instructions.

### Exercise 3: Design a two-platform evidence matrix.

**Expected evidence:** Separate build and execution columns for amd64 and arm64.

**Hint:** Give each platform separate build and run results.

### Exercise 4: Diagnose exec format error.

**Hint:** Compare the image's architecture with the host's.

### Exercise 5: Explain why multi-platform output is not always one --load result.

**Hint:** Ask what the local image store can hold.

### Exercise 6: Write an honest portability claim.

**Expected evidence:** Name the tested platform and label other platforms unqualified.

**Hint:** Name only the platforms you actually built and ran.

## Common mistakes and diagnosis

Assuming Linux means amd64. Treating an emulated run as proof of native performance. Loading a multi-platform index into an image store that holds one platform.

Exercise 4 is this chapter's boundary case: Diagnose exec format error. Compare the image platform with the host architecture and check the executable's format before reading any application code.

A practical trap is reusing the native tag for a foreign build. If `docker buildx build --platform linux/arm64 --load -t ds60-docker-study:local .` runs on an amd64 host, the arm64 image replaces the native one under the same name. The next `docker compose up` then starts the foreign image under emulation, which may work but runs slowly, or fails with an exec format error when no emulator is installed. The cause looks like an application fault because nothing in the Compose file changed. Give each platform build its own tag, as worked example 1 does, and inspect the platform of the image a service actually uses.

Never trade a safety control for a passing example ([safety rules](../STUDY-GUIDE.md#safety-rules)).

## Retrieval, transfer and next steps

**Retrieval.** Name the image index entry the engine selects on an arm64 host and the error a mismatched binary produces.

**Transfer case.** CI on amd64 publishes an image only for `linux/amd64`, and it includes a Python package with native wheels. A teammate on an arm64 laptop pulls it. Describe what happens with and without emulation, and what the publishing team should change.

Then run the [retrieval loop](../STUDY-GUIDE.md#retrieval-and-cleanup) and end any host session with its cleanup.

## Primary references

- [Multi-platform builds](https://docs.docker.com/build/building/multi-platform/)

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for docker-017: CPU architectures, image indexes and cross-platform builds.
Read courses/docker/guides/docker-017.md and courses/docker/lessons/docker-017.md. Direct prerequisites: `docker-016`
Ask me to predict the first example, review my worksheet, and give one hint at a time.
Keep courses/docker/solutions/ closed until I attempt or explicitly request comparison.
Distinguish image metadata, container state and actual application evidence.
Do not execute host commands, change Docker contexts or delete volumes on my behalf.
Finish with a fresh transfer case and ask which evidence would falsify my explanation.
```
