# docker-001: Containers, images and the process model

## Level and prerequisites

Beginner; about 100 minutes, with additional time for the optional host experiment. Direct prerequisites: None; start with the terminal and process explanations here.

## Learning objectives

Classify source code, image tag, container and volume. Explain what evidence proves a web application is serving. Explain the difference between a configuration, an observed process and evidence of the application's behavior.

## Purpose, vocabulary and mental model

A process is a running program together with its memory, open files and operating-system identity. An image is a packaged filesystem plus startup configuration. A container is a running or stopped instance created from an image, with its own writable layer and isolation settings. Docker is tooling that asks a container runtime to create and manage those instances. These words name different objects with different lifetimes.

An image is not a miniature running computer. Starting two containers from one image starts two sets of processes. They initially see the same image files but acquire distinct writable changes. Stopping a container stops its processes; it does not erase the image or automatically remove named volumes. Removing an image is not a reliable or appropriate way to remove application data.

Linux containers share the engine’s Linux kernel. On macOS and a Windows WSL 2 setup, the engine lives in a Linux environment managed by the desktop product or distribution. The application therefore follows Linux process and path rules even when your browser is on another operating system. A VM isolates a whole guest kernel; a container primarily isolates processes using the host kernel. Neither word alone tells you the strength of a deployment’s security boundary.

## Anatomy and a trace you can follow

Read `docker run --rm IMAGE COMMAND` from left to right. `run` creates a new container and starts its main process. `--rm` asks Docker to remove that container after it exits. `IMAGE` selects a filesystem and defaults; the remaining arguments replace the default command when the image permits. This is different from `docker start NAME`, which restarts an existing container. A printed line is process output, while the exit status tells you whether that invocation reported success.

Use the maintained fixture image after its explicit build. The examples use `ds60-docker-study:local`, a local tag created by the fixture. They do not require an unknown image to be fetched. An image tag is a convenient name; later chapters explain why it is not an immutable identity.

## How to use this lesson

The classroom displays this guide and saves your worksheet. Its Run button does not control your Docker engine. Docker engine access is powerful host access, so the classroom deliberately receives no engine socket. Work through the supplied examples without starting anything, then use the optional host lab only in your own disposable project. Reading a command, parsing YAML and actually running the project are different forms of evidence.

Use Bash in Linux, macOS Terminal, or Ubuntu under WSL 2 on Windows. The supported engine runs Linux containers. The maintained fixture is `courses/docker/fixtures/compose-lab/`; its README explains copying it into a new ignored learner directory, checking the engine, building locally with visible logs, and using the fixed project name `ds60-docker-study`. The fixture uses port 18080 on host loopback. Stop if that project name or port belongs to unrelated work; choose a new project name consistently in your own copy. Never paste a command against a remote Docker context simply because it is currently selected.

For Dockerfile examples, create a file named `Dockerfile` in a scratch project. YAML snippets describe a fragment unless explicitly called a complete file. Text transcripts are synthetic illustrations, not claims about your machine. Do not substitute a real password, token or private registry into a checked-in example.

## Worked example / walkthrough

### Worked example 1: Run one short process

After building the fixture image, this creates a disposable Python process with no published port.

```sh
docker run --rm --pull never ds60-docker-study:local python -c "print(2 + 3)"
```

**Expected observation:** One line containing 5, followed by process exit; no long-running web service is implied.

### Worked example 2: Compare image and process inventories

Listing images and listing containers answer different questions.

```sh
docker image ls ds60-docker-study
docker ps -a --filter label=com.docker.compose.project=ds60-docker-study
```

**Expected observation:** The first lists packaged images; the second lists only containers owned by the named Compose project, including stopped ones.

## Six progressive exercises

### Exercise 1: Predict what remains after the short process exits.

**Expected evidence:** The local image remains; the --rm container is removed.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

### Exercise 2: Draw two containers created from one image.

**Expected evidence:** One shared image description, two process groups and two writable layers.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

### Exercise 3: Classify source code, image tag, container and volume.

**Expected evidence:** Four objects with separate creation and deletion events.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

### Exercise 4: Explain why an exited container can still appear in docker ps -a.

**Expected evidence:** Stopped state is distinct from object removal.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

### Exercise 5: Compare a Linux container on macOS with a native macOS process.

**Expected evidence:** The container calls a Linux kernel in the engine environment.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

### Exercise 6: Explain what evidence proves a web application is serving.

**Expected evidence:** A running process plus a bounded HTTP request and expected response.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

## Common mistakes and diagnosis

Start with the smallest observation that separates two plausible causes. An image inspection answers questions about the packaged filesystem and configuration; container inspection adds runtime mounts, network attachment and exit status. An application request adds another layer of evidence. A healthy container can still serve the wrong application result. Preserve the original failure and the exact changed field before retrying.

The boundary case in this chapter is: Explain why an exited container can still appear in docker ps -a. Use its expected observation, Stopped state is distinct from object removal., to avoid treating a successful command as proof of the wrong claim. Keep source edits in your own copy. Do not make a container privileged, mount the engine socket, disable all checks or delete every volume to make an example succeed.

## Retrieval, transfer and next steps

Close the explanations and draw the path from source files to image to container to the observation relevant here. Reconstruct the second worked example with one different value and predict what changes. Explain which state survives process restart, container recreation and image rebuild. If none of those operations applies to this mechanism, explain why.

Before proceeding, retain six evidence records. For the optional host project, use `docker compose -p ds60-docker-study down` from the fixture copy to stop its containers and remove its ordinary network. This command preserves named volumes. Volume deletion is a separate deliberate reset of that disposable lab after a backup or export, never a general cleanup step. The fixture README describes its exact scoped reset.

## Primary references

- [Official reference 1](https://docs.docker.com/get-started/docker-concepts/the-basics/what-is-a-container/)
- [Official reference 2](https://docs.docker.com/get-started/docker-concepts/the-basics/what-is-an-image/)

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
