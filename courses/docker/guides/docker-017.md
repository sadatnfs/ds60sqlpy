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

The classroom displays this guide and saves your worksheet, `courses/docker/lessons/docker-017.md`. Its Run button does not control your Docker engine. Docker engine access is powerful host access, so the classroom deliberately receives no engine socket. Work through the supplied examples without starting anything, then use the optional host lab only in your own disposable project. Reading a command, parsing YAML and actually running the project are different forms of evidence.

Use Bash in Linux, macOS Terminal, or Ubuntu under WSL 2 on Windows. The supported engine runs Linux containers. The maintained fixture is `courses/docker/fixtures/compose-lab/`; its README explains copying it into a new ignored learner directory, checking the engine, building locally with visible logs, and using the fixed project name `ds60-docker-study`. The fixture uses port 18080 on host loopback. Stop if that project name or port belongs to unrelated work; choose a new project name consistently in your own copy. Never paste a command against a remote Docker context simply because it is currently selected.

For Dockerfile examples, create a file named `Dockerfile` in a scratch project. YAML snippets describe a fragment unless explicitly called a complete file. Text transcripts are synthetic illustrations, not claims about your machine. Do not substitute a real password, token or private registry into a checked-in example. **How to use the lessons** in the [subject README](../README.md) collects these rules in one place.

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

For each exercise, name the object involved and the phase of its lifetime before changing anything, then vary only the condition the task names. Exercises that ask you to predict, explain, compare or diagnose keep their answers in the solutions file; the others show the evidence to look for.

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

Exercise 4 is this chapter's boundary case: Diagnose exec format error. Compare the image platform with the host architecture and check the executable's format before reading any application code. Preserve the original failure and the exact changed field before retrying. Do not make a container privileged, mount the engine socket, disable all checks or delete every volume to make an example succeed.

## Retrieval, transfer and next steps

Close the explanations first. Name the image index entry the engine selects on an arm64 host and the error a mismatched binary produces. Then reconstruct worked example 2 (Read the index model) with one different value, predict what changes, and name which of CPU architecture, image index, --platform, emulation and cross-compilation the change touches.

When a host session ends, run `docker compose -p ds60-docker-study down` from your fixture copy. It removes the project's containers and network but keeps named volumes; deleting a volume is a separate, deliberate reset described in the fixture README.

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
