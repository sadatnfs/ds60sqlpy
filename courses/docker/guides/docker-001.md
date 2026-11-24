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

The classroom displays this guide and saves your worksheet, `courses/docker/lessons/docker-001.md`. Its Run button does not control your Docker engine. Docker engine access is powerful host access, so the classroom deliberately receives no engine socket. Work through the supplied examples without starting anything, then use the optional host lab only in your own disposable project. Reading a command, parsing YAML and actually running the project are different forms of evidence.

Use Bash in Linux, macOS Terminal, or Ubuntu under WSL 2 on Windows. The supported engine runs Linux containers. The maintained fixture is `courses/docker/fixtures/compose-lab/`; its README explains copying it into a new ignored learner directory, checking the engine, building locally with visible logs, and using the fixed project name `ds60-docker-study`. The fixture uses port 18080 on host loopback. Stop if that project name or port belongs to unrelated work; choose a new project name consistently in your own copy. Never paste a command against a remote Docker context simply because it is currently selected.

For Dockerfile examples, create a file named `Dockerfile` in a scratch project. YAML snippets describe a fragment unless explicitly called a complete file. Text transcripts are synthetic illustrations, not claims about your machine. Do not substitute a real password, token or private registry into a checked-in example. **How to use the lessons** in the [subject README](../README.md) collects these rules in one place.

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

For each exercise, name the object involved and the phase of its lifetime before changing anything, then vary only the condition the task names. Exercises that ask you to predict, explain, compare or diagnose keep their answers in the solutions file; the others show the evidence to look for.

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

Exercise 4 is this chapter's boundary case: Explain why an exited container can still appear in docker ps -a. Compare `docker ps` with `docker ps -a` for the same container ID before deciding anything was deleted, and read the STATUS column rather than the name. Preserve the original failure and the exact changed field before retrying. Do not make a container privileged, mount the engine socket, disable all checks or delete every volume to make an example succeed.

## Retrieval, transfer and next steps

Close the explanations first. From memory, give one creation event and one removal event for each of image, container and writable layer. Then reconstruct worked example 2 (Compare image and process inventories) with one different value, predict what changes, and name which of process, image, container, writable layer and shared kernel the change touches.

When a host session ends, run `docker compose -p ds60-docker-study down` from your fixture copy. It removes the project's containers and network but keeps named volumes; deleting a volume is a separate, deliberate reset described in the fixture README.

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
