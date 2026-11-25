# docker-024: Rootless engines, user namespaces and host trust

## Level and prerequisites

Intermediate; about 100 minutes, with additional time for the optional host experiment. Direct prerequisites: `docker-023`

## Learning objectives

Draw the daemon-socket authority path. State a support claim for a new rootless setup. Use rootless mode, user namespace and engine socket accurately when you explain what you observed.

## Purpose, vocabulary and mental model

Rootless mode runs the engine and containers without a root daemon under the user’s identity. User namespaces map container user IDs to different host IDs. These mechanisms can reduce host privilege exposure, but they alter networking, storage and resource-control details that must be qualified on the chosen host.

Root inside a container is not automatically identical to host root under every configuration. It is also not automatically harmless. Capabilities, namespace mappings, mounts and daemon access determine what the process can do. The engine socket is especially important because an authorized client can ask the daemon to create containers with powerful host access.

The teaching application should not receive that socket. Docker lessons run as explicit host commands in a learner-owned project. Ordinary browser execution cannot install an engine, create sibling containers or inspect unrelated workloads. This separation is part of the product design.

### Key terms

- **Rootless mode:** Running the engine and its containers under an ordinary user identity without a root daemon.
- **User namespace:** A kernel mapping of container user IDs to different host user IDs.
- **Engine socket:** The daemon API endpoint through which any authorized client can create containers with powerful host access.
- **Host trust:** What a process may do to the host, as decided by its capabilities, ID mappings, mounts and daemon access.
- **Root inside a container:** UID 0 within a container, which is not automatically host root but is also not automatically harmless.

## Anatomy and a trace you can follow

Rootless mode is an engine installation choice, not a Compose flag that magically converts an already running rootful daemon. Inspect the engine’s documented mode and test the app’s required capabilities. Do not require a learner to reconfigure their working engine for this chapter.

Compare the trust paths: browser code talks to a limited classroom endpoint; host Docker client talks to the daemon; daemon creates processes and mounts. Mounting the daemon socket into the classroom would connect those paths and expand browser code’s authority far beyond a lesson pad.

## How to use this lesson

The classroom saves `courses/docker/lessons/docker-024.md` and holds no engine socket ([host-lab setup](../STUDY-GUIDE.md#host-lab-setup)).

**Host lab.** This lab only reads. Run `docker info --format '{{json .SecurityOptions}}'` and look for `name=rootless` or `name=userns`; on a default engine neither appears. Then compare how identities map: `docker run --rm --pull never ds60-docker-study:local cat /proc/self/uid_map` prints `0 0 4294967295` when container IDs equal host IDs, and a shifted range such as `0 100000 65536` under a user namespace. On Linux, run `id -nG` to see whether your account is in the `docker` group, and `ls -l /var/run/docker.sock` to see who owns the socket. Record each result next to a sentence saying who could control the engine. Nothing is created, so there is nothing to clean up.

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

Answer-type prompts keep their answers in the solutions file ([exercise rules](../STUDY-GUIDE.md#exercise-rules)).

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

Exercise 4 is this chapter's boundary case: Diagnose a lesson requiring engine access from the browser. Identify which step needs engine access and move it to a host worksheet the learner runs deliberately, rather than granting the browser session a socket.

A tempting compromise is mounting the engine socket read-only, as in `/var/run/docker.sock:/var/run/docker.sock:ro`. The `:ro` flag only stops the container from modifying the socket file in the filesystem; it does nothing to the API requests sent through that socket, so the container can still create a privileged container with the host's root directory mounted. A truly limited view needs a different mechanism, such as a filtering proxy that allows only specific read endpoints, and even that deserves review as a trust decision rather than a convenience setting.

Never trade a safety control for a passing example ([safety rules](../STUDY-GUIDE.md#safety-rules)).

## Retrieval, transfer and next steps

**Retrieval.** Explain from memory why mounting `/var/run/docker.sock` grants control of the host.

**Transfer case.** A CI job proposes running its image builds inside a container with the host engine socket mounted, arguing that it is only CI. What authority does the job gain, and which alternatives would you weigh?

Then run the [retrieval loop](../STUDY-GUIDE.md#retrieval-and-cleanup) and end any host session with its cleanup.

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
