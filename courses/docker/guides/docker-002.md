# docker-002: The Linux engine, WSL 2 and your first inspection

## Level and prerequisites

Beginner; about 100 minutes, with additional time for the optional host experiment. Direct prerequisites: `docker-001`

## Learning objectives

Produce a minimal setup checklist. Explain a safe response to discovering a remote context. Use Docker client, Docker engine and Docker context accurately when you explain what you observed.

## Purpose, vocabulary and mental model

The Docker client is the command you type. The daemon or engine receives its requests and manages containers. A context selects the endpoint to which the client connects. A local-looking terminal can be configured to operate a remote engine, so confirming the endpoint is part of ownership rather than a cosmetic setup step.

WSL 2 provides a Linux environment on Windows. The course uses its Ubuntu shell and an engine configured for Linux containers. It does not teach Windows containers or require each language compiler on Windows. On macOS, a desktop engine generally provides a Linux VM. On Linux, the engine can run on the host. These host arrangements differ, while the application’s container filesystem and runtime stay Linux-based.

The fixture needs a local engine and Compose. Compose is the client-side tool that reads a multi-service application definition. A successful client version print does not prove that the engine is running. Conversely, permission to access an engine grants substantial control over its host environment. Resolve setup through the engine’s documented user configuration rather than making a socket world-writable.

## Anatomy and a trace you can follow

`docker context show` prints the selected context name. `docker context inspect NAME` shows its endpoint configuration. `docker info` actually contacts the engine and exposes its server operating-system type and resource configuration. `docker compose version` checks the Compose plugin. Treat errors separately: an absent command, an unreachable daemon, an authorization problem and a Windows-container engine are different conditions.

Run these in the same Bash terminal you will use for the fixture. Do not change global contexts as an unexplained repair. If a context is remote, stop and select the intended local setup deliberately outside the lesson. Keep private endpoint paths and machine identifiers out of screenshots shared publicly.

## How to use this lesson

The classroom displays this guide and saves your worksheet, `courses/docker/lessons/docker-002.md`. Its Run button does not control your Docker engine. Docker engine access is powerful host access, so the classroom deliberately receives no engine socket. Work through the supplied examples without starting anything, then use the optional host lab only in your own disposable project. Reading a command, parsing YAML and actually running the project are different forms of evidence.

Use Bash in Linux, macOS Terminal, or Ubuntu under WSL 2 on Windows. The supported engine runs Linux containers. The maintained fixture is `courses/docker/fixtures/compose-lab/`; its README explains copying it into a new ignored learner directory, checking the engine, building locally with visible logs, and using the fixed project name `ds60-docker-study`. The fixture uses port 18080 on host loopback. Stop if that project name or port belongs to unrelated work; choose a new project name consistently in your own copy. Never paste a command against a remote Docker context simply because it is currently selected.

For Dockerfile examples, create a file named `Dockerfile` in a scratch project. YAML snippets describe a fragment unless explicitly called a complete file. Text transcripts are synthetic illustrations, not claims about your machine. Do not substitute a real password, token or private registry into a checked-in example. **How to use the lessons** in the [subject README](../README.md) collects these rules in one place.

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

For each exercise, name the object involved and the phase of its lifetime before changing anything, then vary only the condition the task names. Exercises that ask you to predict, explain, compare or diagnose keep their answers in the solutions file; the others show the evidence to look for.

### Exercise 1: Predict whether docker --version proves readiness.

**Hint:** Note which program prints the version and whether it needed to contact the engine.

### Exercise 2: Identify the selected context and endpoint.

**Hint:** Run docker context show, then inspect that context's endpoint.

### Exercise 3: Produce a minimal setup checklist.

**Expected evidence:** Bash, local Linux engine, Compose and sufficient allocated resources.

**Hint:** List what a lesson command needs: a shell, a reachable engine, Compose and enough memory.

### Exercise 4: Diagnose client success with daemon connection failure.

**Hint:** Compare the Client and Server sections of docker version.

### Exercise 5: Explain where commands run on Windows.

**Hint:** Ask which shell has the Linux paths and the engine integration the fixture expects.

### Exercise 6: Explain a safe response to discovering a remote context.

**Hint:** Ask whose machine a docker compose down would affect with that context selected.

## Common mistakes and diagnosis

Reading a successful `docker --version` as proof that the engine is running. Running lab commands while a remote or shared context is selected. Using PowerShell paths on Windows instead of the Ubuntu shell under WSL 2.

Exercise 4 is this chapter's boundary case: Diagnose client success with daemon connection failure. Start with the smallest observation that separates two plausible causes. An image inspection answers questions about the packaged filesystem and configuration; container inspection adds runtime mounts, network attachment and exit status; an application request adds another layer, and a healthy container can still serve the wrong result. Preserve the original failure and the exact changed field before retrying. Keep source edits in your own copy. Do not make a container privileged, mount the engine socket, disable all checks or delete every volume to make an example succeed.

## Retrieval, transfer and next steps

Close the explanations and draw the path from source files to image to container to the observation relevant here, using Docker client, Docker engine, Docker context, WSL 2 and docker info. Reconstruct worked example 2 (Distinguish client from server availability) with one different value and predict what changes. Explain which state survives process restart, container recreation and image rebuild, or why none of those operations applies to this mechanism.

When a host session ends, run `docker compose -p ds60-docker-study down` from your fixture copy. It removes the project's containers and network but keeps named volumes; deleting a volume is a separate, deliberate reset described in the fixture README.

## Primary references

- [Docker contexts](https://docs.docker.com/engine/manage-resources/contexts/)
- [Docker Desktop WSL 2 backend](https://docs.docker.com/desktop/features/wsl/)

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
