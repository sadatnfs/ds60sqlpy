# docker-002: The Linux engine, WSL 2 and your first inspection

## Level and prerequisites

Beginner; about 100 minutes, with additional time for the optional host experiment. Direct prerequisites: `docker-001`

## Learning objectives

Produce a minimal setup checklist. Explain a safe response to discovering a remote context. Explain the difference between a configuration, an observed process and evidence of the application's behavior.

## Purpose, vocabulary and mental model

The Docker client is the command you type. The daemon or engine receives its requests and manages containers. A context selects the endpoint to which the client connects. A local-looking terminal can be configured to operate a remote engine, so confirming the endpoint is part of ownership rather than a cosmetic setup step.

WSL 2 provides a Linux environment on Windows. The course uses its Ubuntu shell and an engine configured for Linux containers. It does not teach Windows containers or require each language compiler on Windows. On macOS, a desktop engine generally provides a Linux VM. On Linux, the engine can run on the host. These host arrangements differ, while the application’s container filesystem and runtime stay Linux-based.

The fixture needs a local engine and Compose. Compose is the client-side tool that reads a multi-service application definition. A successful client version print does not prove that the engine is running. Conversely, permission to access an engine grants substantial control over its host environment. Resolve setup through the engine’s documented user configuration rather than making a socket world-writable.

## Anatomy and a trace you can follow

`docker context show` prints the selected context name. `docker context inspect NAME` shows its endpoint configuration. `docker info` actually contacts the engine and exposes its server operating-system type and resource configuration. `docker compose version` checks the Compose plugin. Treat errors separately: an absent command, an unreachable daemon, an authorization problem and a Windows-container engine are different conditions.

Run these in the same Bash terminal you will use for the fixture. Do not change global contexts as an unexplained repair. If a context is remote, stop and select the intended local setup deliberately outside the lesson. Keep private endpoint paths and machine identifiers out of screenshots shared publicly.

## How to use this lesson

The classroom displays this guide and saves your worksheet. Its Run button does not control your Docker engine. Docker engine access is powerful host access, so the classroom deliberately receives no engine socket. Work through the supplied examples without starting anything, then use the optional host lab only in your own disposable project. Reading a command, parsing YAML and actually running the project are different forms of evidence.

Use Bash in Linux, macOS Terminal, or Ubuntu under WSL 2 on Windows. The supported engine runs Linux containers. The maintained fixture is `courses/docker/fixtures/compose-lab/`; its README explains copying it into a new ignored learner directory, checking the engine, building locally with visible logs, and using the fixed project name `ds60-docker-study`. The fixture uses port 18080 on host loopback. Stop if that project name or port belongs to unrelated work; choose a new project name consistently in your own copy. Never paste a command against a remote Docker context simply because it is currently selected.

For Dockerfile examples, create a file named `Dockerfile` in a scratch project. YAML snippets describe a fragment unless explicitly called a complete file. Text transcripts are synthetic illustrations, not claims about your machine. Do not substitute a real password, token or private registry into a checked-in example.

## Worked example / walkthrough

### Worked example 1: Inspect the selected endpoint

These reads do not start a classroom or change a context.

```sh
docker context show
docker context inspect "$(docker context show)"
docker info --format "{{.OSType}}"
docker compose version
```

**Expected observation:** The selected endpoint is your intended local engine, OSType is linux, and Compose reports its version.

### Worked example 2: Distinguish client from server availability

These two checks have different evidence strength.

```sh
docker --version
docker info
```

**Expected observation:** The first may succeed even when the engine is stopped; the second requires a working engine connection.

## Six progressive exercises

### Exercise 1: Predict whether docker --version proves readiness.

**Expected evidence:** No; it only proves the client can run.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

### Exercise 2: Identify the selected context and endpoint.

**Expected evidence:** A locally recorded context name and an intentionally local endpoint.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

### Exercise 3: Produce a minimal setup checklist.

**Expected evidence:** Bash, local Linux engine, Compose and sufficient allocated resources.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

### Exercise 4: Diagnose client success with daemon connection failure.

**Expected evidence:** Investigate engine startup, endpoint and permission separately.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

### Exercise 5: Explain where commands run on Windows.

**Expected evidence:** Inside the integrated WSL 2 Ubuntu terminal.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

### Exercise 6: Explain a safe response to discovering a remote context.

**Expected evidence:** Stop before mutations and deliberately configure the owned local engine.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

## Common mistakes and diagnosis

Start with the smallest observation that separates two plausible causes. An image inspection answers questions about the packaged filesystem and configuration; container inspection adds runtime mounts, network attachment and exit status. An application request adds another layer of evidence. A healthy container can still serve the wrong application result. Preserve the original failure and the exact changed field before retrying.

The boundary case in this chapter is: Diagnose client success with daemon connection failure. Use its expected observation, Investigate engine startup, endpoint and permission separately., to avoid treating a successful command as proof of the wrong claim. Keep source edits in your own copy. Do not make a container privileged, mount the engine socket, disable all checks or delete every volume to make an example succeed.

## Retrieval, transfer and next steps

Close the explanations and draw the path from source files to image to container to the observation relevant here. Reconstruct the second worked example with one different value and predict what changes. Explain which state survives process restart, container recreation and image rebuild. If none of those operations applies to this mechanism, explain why.

Before proceeding, retain six evidence records. For the optional host project, use `docker compose -p ds60-docker-study down` from the fixture copy to stop its containers and remove its ordinary network. This command preserves named volumes. Volume deletion is a separate deliberate reset of that disposable lab after a backup or export, never a general cleanup step. The fixture README describes its exact scoped reset.

## Primary references

- [Official reference 1](https://docs.docker.com/engine/manage-resources/contexts/)
- [Official reference 2](https://docs.docker.com/desktop/features/wsl/)

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for docker-002: The Linux engine, WSL 2 and your first inspection.
Read courses/docker/guides/docker-002.md and courses/docker/lessons/docker-002.md. Direct prerequisites: `docker-001`
Ask me to predict the first example, review my worksheet, and give one hint at a time.
Keep courses/docker/solutions/ closed until I attempt or explicitly request comparison.
Distinguish image metadata, container state and actual application evidence.
Do not execute host commands, change Docker contexts or delete volumes on my behalf.
Finish with a fresh transfer case and ask which evidence would falsify my explanation.
```
