# docker-024: Rootless engines, user namespaces and host trust

## Level and prerequisites

Intermediate; about 100 minutes, with additional time for the optional host experiment. Direct prerequisites: `docker-023`

## Learning objectives

Draw the daemon-socket authority path. State a support claim for a new rootless setup. Use rootless mode, user namespace and engine socket accurately when you explain what you observed.

## Purpose, vocabulary and mental model

Rootless mode runs the engine and containers without a root daemon under the user’s identity. User namespaces map container user IDs to different host IDs. These mechanisms can reduce host privilege exposure, but they alter networking, storage and resource-control details that must be qualified on the chosen host.

Root inside a container is not automatically identical to host root under every configuration. It is also not automatically harmless. Capabilities, namespace mappings, mounts and daemon access determine what the process can do. The engine socket is especially important because an authorized client can ask the daemon to create containers with powerful host access.

The teaching application should not receive that socket. Docker lessons run as explicit host commands in a learner-owned project. Ordinary browser execution cannot install an engine, create sibling containers or inspect unrelated workloads. This separation is part of the product design.

## Anatomy and a trace you can follow

Rootless mode is an engine installation choice, not a Compose flag that magically converts an already running rootful daemon. Inspect the engine’s documented mode and test the app’s required capabilities. Do not require a learner to reconfigure their working engine for this chapter.

Compare the trust paths: browser code talks to a limited classroom endpoint; host Docker client talks to the daemon; daemon creates processes and mounts. Mounting the daemon socket into the classroom would connect those paths and expand browser code’s authority far beyond a lesson pad.

## How to use this lesson

The classroom displays this guide and saves your worksheet, `courses/docker/lessons/docker-024.md`. Its Run button does not control your Docker engine. Docker engine access is powerful host access, so the classroom deliberately receives no engine socket. Work through the supplied examples without starting anything, then use the optional host lab only in your own disposable project. Reading a command, parsing YAML and actually running the project are different forms of evidence.

Use Bash in Linux, macOS Terminal, or Ubuntu under WSL 2 on Windows. The supported engine runs Linux containers. The maintained fixture is `courses/docker/fixtures/compose-lab/`; its README explains copying it into a new ignored learner directory, checking the engine, building locally with visible logs, and using the fixed project name `ds60-docker-study`. The fixture uses port 18080 on host loopback. Stop if that project name or port belongs to unrelated work; choose a new project name consistently in your own copy. Never paste a command against a remote Docker context simply because it is currently selected.

For Dockerfile examples, create a file named `Dockerfile` in a scratch project. YAML snippets describe a fragment unless explicitly called a complete file. Text transcripts are synthetic illustrations, not claims about your machine. Do not substitute a real password, token or private registry into a checked-in example. **How to use the lessons** in the [subject README](../README.md) collects these rules in one place.

## Worked example / walkthrough

### Worked example 1: Trace authority without changing the engine

This is a conceptual flow.

```text
host user -> Docker client -> engine API -> containers and mounts
browser lesson -> bounded classroom API -> declared lesson runtime
```

**Expected observation:** The second path does not acquire the first path merely because the classroom itself uses Docker.

### Worked example 2: Identify a dangerous mount in review

Do not add this illustrative configuration.

```yaml
volumes:
  - /var/run/docker.sock:/var/run/docker.sock
```

**Expected observation:** This would expose engine control and is absent from the classroom and study app design.

## Six progressive exercises

For each exercise, name the object involved and the phase of its lifetime before changing anything, then vary only the condition the task names. Exercises that ask you to predict, explain, compare or diagnose keep their answers in the solutions file; the others show the evidence to look for.

### Exercise 1: Distinguish rootless mode from a non-root app USER.

**Hint:** Ask which process runs as root in each setup: the daemon or the app.

### Exercise 2: Predict why low-port or resource behavior may differ.

**Hint:** Ask what a rootless daemon cannot do that a root daemon can, such as binding ports below 1024.

### Exercise 3: Draw the daemon-socket authority path.

**Hint:** Follow a docker run request from the socket to the daemon to the host.

### Exercise 4: Diagnose a lesson requiring engine access from the browser.

**Hint:** Ask why the classroom never receives an engine socket.

### Exercise 5: Explain user namespace ID mapping.

**Hint:** Compare a UID inside the container with its mapped UID on the host.

### Exercise 6: State a support claim for a new rootless setup.

**Expected evidence:** Actual app build, network, storage and cleanup observations.

**Hint:** List the build, network, storage and cleanup checks you actually ran.

## Common mistakes and diagnosis

Assuming a non-root `USER` makes the engine rootless. Adding a user to the docker group without treating that as root-equivalent access. Mounting the engine socket into a container for convenience.

Exercise 4 is this chapter's boundary case: Diagnose a lesson requiring engine access from the browser. Start with the smallest observation that separates two plausible causes. An image inspection answers questions about the packaged filesystem and configuration; container inspection adds runtime mounts, network attachment and exit status; an application request adds another layer, and a healthy container can still serve the wrong result. Preserve the original failure and the exact changed field before retrying. Keep source edits in your own copy. Do not make a container privileged, mount the engine socket, disable all checks or delete every volume to make an example succeed.

## Retrieval, transfer and next steps

Close the explanations and draw the path from source files to image to container to the observation relevant here, using rootless mode, user namespace, engine socket and host trust. Reconstruct worked example 2 (Identify a dangerous mount in review) with one different value and predict what changes. Explain which state survives process restart, container recreation and image rebuild, or why none of those operations applies to this mechanism.

When a host session ends, run `docker compose -p ds60-docker-study down` from your fixture copy. It removes the project's containers and network but keeps named volumes; deleting a volume is a separate, deliberate reset described in the fixture README.

## Primary references

- [Rootless mode](https://docs.docker.com/engine/security/rootless/)
- [User namespace remapping](https://docs.docker.com/engine/security/userns-remap/)

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for docker-024: Rootless engines, user namespaces and host trust.
Read courses/docker/guides/docker-024.md and courses/docker/lessons/docker-024.md. Direct prerequisites: `docker-023`
Ask me to predict the first example, review my worksheet, and give one hint at a time.
Keep courses/docker/solutions/ closed until I attempt or explicitly request comparison.
Distinguish image metadata, container state and actual application evidence.
Do not execute host commands, change Docker contexts or delete volumes on my behalf.
Finish with a fresh transfer case and ask which evidence would falsify my explanation.
```
