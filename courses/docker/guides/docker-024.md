# docker-024: Rootless engines, user namespaces and host trust

## Level and prerequisites

Intermediate; about 100 minutes, with additional time for the optional host experiment. Direct prerequisites: `docker-023`

## Learning objectives

Draw the daemon-socket authority path. State a support claim for a new rootless setup. Explain the difference between a configuration, an observed process and evidence of the application's behavior.

## Purpose, vocabulary and mental model

Rootless mode runs the engine and containers without a root daemon under the user’s identity. User namespaces map container user IDs to different host IDs. These mechanisms can reduce host privilege exposure, but they alter networking, storage and resource-control details that must be qualified on the chosen host.

Root inside a container is not automatically identical to host root under every configuration. It is also not automatically harmless. Capabilities, namespace mappings, mounts and daemon access determine what the process can do. The engine socket is especially important because an authorized client can ask the daemon to create containers with powerful host access.

The teaching application should not receive that socket. Docker lessons run as explicit host commands in a learner-owned project. Ordinary browser execution cannot install an engine, create sibling containers or inspect unrelated workloads. This separation is part of the product design.

## Anatomy and a trace you can follow

Rootless mode is an engine installation choice, not a Compose flag that magically converts an already running rootful daemon. Inspect the engine’s documented mode and test the app’s required capabilities. Do not require a learner to reconfigure their working engine for this chapter.

Compare the trust paths: browser code talks to a limited classroom endpoint; host Docker client talks to the daemon; daemon creates processes and mounts. Mounting the daemon socket into the classroom would connect those paths and expand browser code’s authority far beyond a lesson pad.

## How to use this lesson

The classroom displays this guide and saves your worksheet. Its Run button does not control your Docker engine. Docker engine access is powerful host access, so the classroom deliberately receives no engine socket. Work through the supplied examples without starting anything, then use the optional host lab only in your own disposable project. Reading a command, parsing YAML and actually running the project are different forms of evidence.

Use Bash in Linux, macOS Terminal, or Ubuntu under WSL 2 on Windows. The supported engine runs Linux containers. The maintained fixture is `courses/docker/fixtures/compose-lab/`; its README explains copying it into a new ignored learner directory, checking the engine, building locally with visible logs, and using the fixed project name `ds60-docker-study`. The fixture uses port 18080 on host loopback. Stop if that project name or port belongs to unrelated work; choose a new project name consistently in your own copy. Never paste a command against a remote Docker context simply because it is currently selected.

For Dockerfile examples, create a file named `Dockerfile` in a scratch project. YAML snippets describe a fragment unless explicitly called a complete file. Text transcripts are synthetic illustrations, not claims about your machine. Do not substitute a real password, token or private registry into a checked-in example.

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

### Exercise 1: Distinguish rootless mode from a non-root app USER.

**Expected evidence:** Engine privilege versus process identity inside one container.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

### Exercise 2: Predict why low-port or resource behavior may differ.

**Expected evidence:** Rootless networking and delegated controls can have limitations.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

### Exercise 3: Draw the daemon-socket authority path.

**Expected evidence:** Socket access can permit host-impacting container requests.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

### Exercise 4: Diagnose a lesson requiring engine access from the browser.

**Expected evidence:** Move it to an explicit host lab with ownership boundaries.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

### Exercise 5: Explain user namespace ID mapping.

**Expected evidence:** Container numeric IDs map to a separate host range.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

### Exercise 6: State a support claim for a new rootless setup.

**Expected evidence:** Actual app build, network, storage and cleanup observations.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

## Common mistakes and diagnosis

Start with the smallest observation that separates two plausible causes. An image inspection answers questions about the packaged filesystem and configuration; container inspection adds runtime mounts, network attachment and exit status. An application request adds another layer of evidence. A healthy container can still serve the wrong application result. Preserve the original failure and the exact changed field before retrying.

The boundary case in this chapter is: Diagnose a lesson requiring engine access from the browser. Use its expected observation, Move it to an explicit host lab with ownership boundaries., to avoid treating a successful command as proof of the wrong claim. Keep source edits in your own copy. Do not make a container privileged, mount the engine socket, disable all checks or delete every volume to make an example succeed.

## Retrieval, transfer and next steps

Close the explanations and draw the path from source files to image to container to the observation relevant here. Reconstruct the second worked example with one different value and predict what changes. Explain which state survives process restart, container recreation and image rebuild. If none of those operations applies to this mechanism, explain why.

Before proceeding, retain six evidence records. For the optional host project, use `docker compose -p ds60-docker-study down` from the fixture copy to stop its containers and remove its ordinary network. This command preserves named volumes. Volume deletion is a separate deliberate reset of that disposable lab after a backup or export, never a general cleanup step. The fixture README describes its exact scoped reset.

## Primary references

- [Official reference 1](https://docs.docker.com/engine/security/rootless/)
- [Official reference 2](https://docs.docker.com/engine/security/userns-remap/)

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
