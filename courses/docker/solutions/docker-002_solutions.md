# docker-002: explanatory solutions

These answers explain teaching fixtures, not engine results; the mechanism is in [the guide](../guides/docker-002.md).

## Exercise 1: Predict whether docker --version proves readiness.

**Expected answer:** No; it only proves the client can run.

**Why:** The version command can use local client information. It does not need to create a server connection and therefore cannot establish permission, engine mode or available resources.

**Approach:** Ask which component answers the command. docker --version is printed by the client binary from its own build metadata.

**Why this is correct:** The client does not contact the daemon for that flag, so the line appears even when the engine is stopped, missing or unreachable.

**A plausible wrong approach:** Treating a printed version as a green light leads to confusing errors at the first docker build, when the client finally tries to reach the daemon socket.

**How to verify:** Stop the engine and run docker --version and docker info. The first still prints; the second reports that it cannot connect to the daemon.

## Exercise 2: Identify the selected context and endpoint.

**Expected answer:** A locally recorded context name and an intentionally local endpoint.

**Why:** Names are user-defined and cannot by themselves prove locality. Inspect the endpoint and understand which engine owns it before any state-changing operation.

**Approach:** Run docker context show for the name, then inspect that context and read its endpoint host field, rather than trusting the context label.

**Why this is correct:** Context names are arbitrary strings. The endpoint value, such as a local Unix socket path versus an ssh:// or tcp:// address, decides which engine receives commands.

**A plausible wrong approach:** Accepting a context called local at face value fails if someone pointed it at a remote host. The name stays reassuring while commands mutate a shared engine.

**How to verify:** In the docker context inspect output, the Docker endpoint Host is a local socket path such as unix:///var/run/docker.sock or a Desktop-managed socket, not a network address.

## Exercise 3: Produce a minimal setup checklist.

**Expected evidence:** Bash, local Linux engine, Compose and sufficient allocated resources.

**Why:** The language compilers come from classroom images. The host prerequisite is the engine environment; adding unrelated native toolchains makes first setup harder without solving a daemon connection problem.

**Approach:** List only what the lessons call from the host: a Bash shell, a running local Linux-container engine, the Compose plugin, and CPU, memory and disk allocated to it.

**Why this is correct:** Every program in the fixture runs inside `python:3.12-slim`, so the host never needs Python. The engine and Compose are what docker build and docker compose require.

**A plausible wrong approach:** Installing Python, Node and compilers on the host first adds work and leaves docker info failing if the engine was never started.

**How to verify:** Tick each item with a command: echo $BASH_VERSION, docker info returning OSType linux, and docker compose version printing a version line.

## Exercise 4: Diagnose client success with daemon connection failure.

**Expected answer:** Investigate engine startup, endpoint and permission separately.

**Why:** Do not interpret an unavailable server as a broken application Dockerfile. No build has occurred yet, so change the setup layer that actually failed.

**Approach:** Split the failure into three independent questions: is the engine process running, does the context point to it, and does this user have permission on its socket?

**Why this is correct:** A successful client line plus a connection error means the request never reached a daemon, so nothing about the Dockerfile has been evaluated yet.

**A plausible wrong approach:** Editing the Dockerfile or reinstalling the image in response wastes effort, because the same docker info error appears before any build input is read.

**How to verify:** Fix one layer at a time and rerun docker info after each change; success is the first time it prints server details instead of a connection error.

## Exercise 5: Explain where commands run on Windows.

**Expected answer:** Inside the integrated WSL 2 Ubuntu terminal.

**Why:** Linux paths and Bash quoting are part of the examples. PowerShell has different expansion and continuation syntax, so relabeling commands without changing syntax would mislead beginners.

**Approach:** Open the Ubuntu distribution installed under WSL 2 and run every lesson command in its Bash terminal, with the project stored in the Linux filesystem.

**Why this is correct:** The commands use $(...) substitution, double-quoted Go templates and backslash continuations, which Bash interprets as written. WSL 2 integration exposes the Linux engine there.

**A plausible wrong approach:** Pasting the same lines into PowerShell fails in subtle ways, since PowerShell uses a backtick for continuation and its own quoting rules for the {{.OSType}} template.

**How to verify:** In the WSL terminal, uname -s prints Linux and docker info --format with the OSType template prints linux, showing both shell and engine match the lessons.

## Exercise 6: Explain a safe response to discovering a remote context.

**Expected answer:** Stop before mutations and deliberately configure the owned local engine.

**Why:** The lesson’s authorization concerns a disposable local lab. An ambient context does not extend that ownership to a shared engine or authorize cleanup of its resources.

**Approach:** Pause before any create, stop or remove command, record the context name and endpoint, then switch to or create a context whose endpoint is your own local engine.

**Why this is correct:** The lesson authorizes changes to a disposable local project only. A remote endpoint belongs to someone else, whose containers and volumes the cleanup commands could delete.

**A plausible wrong approach:** Running docker compose down to test whether the remote is harmless fails as a safety check, because it already mutates the very engine you have not been authorized to use.

**How to verify:** After switching, docker context show names the local context and its inspected endpoint is a local socket, checked before running any fixture command.

## Check your transfer

They should switch to the Ubuntu terminal under WSL 2 before running any lab command. The guard is Bash syntax, and the labs assume Linux paths and Bash quoting. The successful `docker info` only proves the Windows client reached some engine; it says nothing about whether the shell can run the lab commands. In Ubuntu, the expected result is that `docker info --format '{{.OSType}}'` prints `linux` and the guard runs. If `docker context show` inside Ubuntu names a different endpoint from the one recorded earlier, that observation disproves the assumption that both shells talk to the same engine, and it must be reconciled first.
