# docker-001: Containers, images and the process model

## Level and prerequisites

Beginner; about 100 minutes, with additional time for the optional host experiment. Direct prerequisites: None; start with the terminal and process explanations here.

## Learning objectives

Classify source code, image tag, container and volume. Explain what evidence proves a web application is serving. Use process, image and container accurately when you explain what you observed.

## Purpose, vocabulary and mental model

A process is a running program together with its memory, open files and operating-system identity. An image is a packaged filesystem plus startup configuration. A container is a running or stopped instance created from an image, with its own writable layer and isolation settings. Docker is tooling that asks a container runtime to create and manage those instances. These words name different objects with different lifetimes.

An image is not a miniature running computer. Starting two containers from one image starts two sets of processes. They initially see the same image files but acquire distinct writable changes. Stopping a container stops its processes; it does not erase the image or automatically remove named volumes. Removing an image is not a reliable or appropriate way to remove application data.

Linux containers share the engine’s Linux kernel. On macOS and a Windows WSL 2 setup, the engine lives in a Linux environment managed by the desktop product or distribution. The application therefore follows Linux process and path rules even when your browser is on another operating system. A VM isolates a whole guest kernel; a container primarily isolates processes using the host kernel. Neither word alone tells you the strength of a deployment’s security boundary.

### Key terms

- **Process:** A running program together with its memory, open files and operating-system identity.
- **Image:** A packaged, read-only filesystem plus startup configuration from which containers are created.
- **Container:** A running or stopped instance created from an image, with its own writable layer and isolation settings.
- **Writable layer:** The per-container record of file changes made on top of the image's read-only content.
- **Shared kernel:** The engine's single Linux kernel, which every container on that engine uses instead of booting a guest kernel.

## Anatomy and a trace you can follow

Read `docker run --rm IMAGE COMMAND` from left to right. `run` creates a new container and starts its main process. `--rm` asks Docker to remove that container after it exits. `IMAGE` selects a filesystem and defaults; the remaining arguments replace the default command when the image permits. This is different from `docker start NAME`, which restarts an existing container. A printed line is process output, while the exit status tells you whether that invocation reported success.

Use the maintained fixture image after its explicit build. The examples use `ds60-docker-study:local`, a local tag created by the fixture. They do not require an unknown image to be fetched. An image tag is a convenient name; later chapters explain why it is not an immutable identity.

## How to use this lesson

The classroom saves `courses/docker/lessons/docker-001.md` and holds no engine socket ([host-lab setup](../STUDY-GUIDE.md#host-lab-setup)).

**Host lab.** Build the fixture image once from your copy of `compose-lab`, run worked example 1, then repeat the arithmetic run without `--rm`: `docker run --pull never ds60-docker-study:local python -c "print('kept')"`. Now `docker ps -a --filter ancestor=ds60-docker-study:local` lists one Exited container with a generated name, while the `--rm` run left nothing behind. Remove only that container by its ID with `docker rm`, then confirm with `docker image ls ds60-docker-study` that the image is still there. You have watched three separate lifetimes: the process ended when `print` returned, the container stayed until you removed it, and the image outlives both. Nothing here publishes a port or creates a volume, so the only object left is the local image, which later lessons reuse.

## Worked example / walkthrough

### Worked example 1: Run one short process

From your copy of the compose-lab directory, build the image once, then create a disposable Python process with no published port.

```sh
docker build -t ds60-docker-study:local .
docker run --rm --pull never ds60-docker-study:local python -c "print(2 + 3)"
```

**Expected observation:** The build reports its steps and tags the image; the run prints one line containing 5 and then exits, so no long-running web service is implied.

### Worked example 2: Compare image and process inventories

Listing images and listing containers answer different questions.

```sh
docker image ls ds60-docker-study
docker ps -a --filter ancestor=ds60-docker-study:local
```

**Expected observation:** The first lists packaged images; the second lists containers created from that image, including stopped ones, and is empty after the --rm run.

## Six progressive exercises

Answer-type prompts keep their answers in the solutions file ([exercise rules](../STUDY-GUIDE.md#exercise-rules)).

### Exercise 1: Predict what remains after the short process exits.

**Hint:** List the objects the run command touched, then ask which one the --rm flag names.

### Exercise 2: Draw two containers created from one image.

**Hint:** Draw the image once, then give each container its own box for processes and changed files.

### Exercise 3: Classify source code, image tag, container and volume.

**Hint:** For each object, name the command that creates it and the command that deletes it.

### Exercise 4: Explain why an exited container can still appear in docker ps -a.

**Hint:** Compare what docker ps shows with and without -a, and ask what removes a container.

### Exercise 5: Compare a Linux container on macOS with a native macOS process.

**Hint:** Ask which kernel answers the container's system calls on a Mac.

### Exercise 6: Explain what evidence proves a web application is serving.

**Hint:** Separate what docker image ls, docker ps and an HTTP request each show.

## Common mistakes and diagnosis

Treating the image as the running program, so removing an image looks like a way to delete data. Expecting `--rm` to remove the image as well as the container. Assuming a container on macOS or Windows runs on the host's own kernel.

Exercise 4 is this chapter's boundary case: Explain why an exited container can still appear in docker ps -a. Compare `docker ps` with `docker ps -a` for the same container ID before deciding anything was deleted, and read the STATUS column rather than the name.

A related misconception is that every container boots its own small operating system. If that were true, `uname -r` inside the fixture would report a Debian kernel. Run `docker run --rm --pull never ds60-docker-study:local uname -r` and compare it with `docker info --format '{{.KernelVersion}}'`: the two match, because the container's system calls go to the engine's Linux kernel. What the `python:3.12-slim` base provides is a Debian userland, meaning files such as libraries, a shell and package metadata. So "this image is Debian" describes its files, never its kernel, and a kernel feature the engine lacks cannot be added by choosing a different base image.

Never trade a safety control for a passing example ([safety rules](../STUDY-GUIDE.md#safety-rules)).

## Retrieval, transfer and next steps

**Retrieval.** From memory, give one creation event and one removal event for each of image, container and writable layer.

**Transfer case.** A teammate runs `docker run --pull never ds60-docker-study:local python -c "open('/tmp/n','w').write('1')"` twice without `--rm`. How many containers, images and copies of `/tmp/n` exist afterwards, and what happens if they now try `docker image rm ds60-docker-study:local`?

Then run the [retrieval loop](../STUDY-GUIDE.md#retrieval-and-cleanup) and end any host session with its cleanup.

## Primary references

- [What is a container?](https://docs.docker.com/get-started/docker-concepts/the-basics/what-is-a-container/)
- [What is an image?](https://docs.docker.com/get-started/docker-concepts/the-basics/what-is-an-image/)

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for docker-001: Containers, images and the process model.
Read courses/docker/guides/docker-001.md and courses/docker/lessons/docker-001.md. Direct prerequisites: None; start with the terminal and process explanations here.
Ask me to predict the first example, review my worksheet, and give one hint at a time.
Keep courses/docker/solutions/ closed until I attempt or explicitly request comparison.
Distinguish image metadata, container state and actual application evidence.
Do not execute host commands, change Docker contexts or delete volumes on my behalf.
Finish with a fresh transfer case and ask which evidence would falsify my explanation.
```
