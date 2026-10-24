# docker-017: CPU architectures, image indexes and cross-platform builds

## Level and prerequisites

Intermediate; about 100 minutes, with additional time for the optional host experiment. Direct prerequisites: `docker-016`

## Learning objectives

Design a two-platform evidence matrix. Write an honest portability claim. Explain the difference between a configuration, an observed process and evidence of the application's behavior.

## Purpose, vocabulary and mental model

An architecture is a machine instruction family such as amd64 or arm64. A Linux image can target one or several architectures. A multi-platform image index points to platform-specific images; it is not one binary that magically runs everywhere. The engine selects a compatible image based on platform metadata.

An Apple Silicon laptop commonly runs arm64 natively while many hosted runners use amd64. Emulation can run some foreign-architecture programs, but it adds cost and does not prove native performance or compatibility. A successful source build on one platform is only evidence for that platform’s produced artifact.

Cross-compilation and emulation are distinct strategies. A compiler may emit target binaries while itself running natively; an emulator executes foreign instructions. Some projects need target-specific libraries or test hosts. A release matrix must name which platforms were actually built and executed.

## Anatomy and a trace you can follow

BuildKit exposes platform arguments such as BUILDPLATFORM and TARGETPLATFORM. A Dockerfile may choose a native builder stage and pass the target into a compiler. Do not use these names as a substitute for correct compiler flags. A multi-platform build also needs an output strategy compatible with your image store or a deliberate export.

The course does not push images. For an optional local experiment, build one selected platform with `--load` when supported and inspect the result. Do not force a foreign platform on the ordinary classroom just to avoid investigating a missing dependency wheel.

## How to use this lesson

The classroom displays this guide and saves your worksheet. Its Run button does not control your Docker engine. Docker engine access is powerful host access, so the classroom deliberately receives no engine socket. Work through the supplied examples without starting anything, then use the optional host lab only in your own disposable project. Reading a command, parsing YAML and actually running the project are different forms of evidence.

Use Bash in Linux, macOS Terminal, or Ubuntu under WSL 2 on Windows. The supported engine runs Linux containers. The maintained fixture is `courses/docker/fixtures/compose-lab/`; its README explains copying it into a new ignored learner directory, checking the engine, building locally with visible logs, and using the fixed project name `ds60-docker-study`. The fixture uses port 18080 on host loopback. Stop if that project name or port belongs to unrelated work; choose a new project name consistently in your own copy. Never paste a command against a remote Docker context simply because it is currently selected.

For Dockerfile examples, create a file named `Dockerfile` in a scratch project. YAML snippets describe a fragment unless explicitly called a complete file. Text transcripts are synthetic illustrations, not claims about your machine. Do not substitute a real password, token or private registry into a checked-in example.

## Worked example / walkthrough

### Worked example 1: Inspect architecture evidence

Read an already built local image.

```sh
docker image inspect ds60-docker-study:local --format "{{.Os}}/{{.Architecture}}"
```

**Expected observation:** A platform such as linux/arm64 or linux/amd64, matching the actual local build result.

### Worked example 2: Read the index model

These are illustrative identities, not real downloadable digests.

```text
image index
  linux/amd64 -> image A -> amd64 program
  linux/arm64 -> image B -> arm64 program
```

**Expected observation:** Each platform entry needs its own build and runtime qualification.

## Six progressive exercises

### Exercise 1: Predict whether Linux implies amd64.

**Expected evidence:** No; operating system and architecture are separate axes.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

### Exercise 2: Classify cross-compilation and emulation.

**Expected evidence:** Producing target code versus executing foreign code.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

### Exercise 3: Design a two-platform evidence matrix.

**Expected evidence:** Separate build and execution columns for amd64 and arm64.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

### Exercise 4: Diagnose exec format error.

**Expected evidence:** Inspect architecture and executable format before app logic.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

### Exercise 5: Explain why multi-platform output is not always one --load result.

**Expected evidence:** Exporter and image-store capabilities constrain output.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

### Exercise 6: Write an honest portability claim.

**Expected evidence:** Name the tested platform and label other platforms unqualified.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

## Common mistakes and diagnosis

Start with the smallest observation that separates two plausible causes. An image inspection answers questions about the packaged filesystem and configuration; container inspection adds runtime mounts, network attachment and exit status. An application request adds another layer of evidence. A healthy container can still serve the wrong application result. Preserve the original failure and the exact changed field before retrying.

The boundary case in this chapter is: Diagnose exec format error. Use its expected observation, Inspect architecture and executable format before app logic., to avoid treating a successful command as proof of the wrong claim. Keep source edits in your own copy. Do not make a container privileged, mount the engine socket, disable all checks or delete every volume to make an example succeed.

## Retrieval, transfer and next steps

Close the explanations and draw the path from source files to image to container to the observation relevant here. Reconstruct the second worked example with one different value and predict what changes. Explain which state survives process restart, container recreation and image rebuild. If none of those operations applies to this mechanism, explain why.

Before proceeding, retain six evidence records. For the optional host project, use `docker compose -p ds60-docker-study down` from the fixture copy to stop its containers and remove its ordinary network. This command preserves named volumes. Volume deletion is a separate deliberate reset of that disposable lab after a backup or export, never a general cleanup step. The fixture README describes its exact scoped reset.

## Primary references

- [Official reference 1](https://docs.docker.com/build/building/multi-platform/)

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
