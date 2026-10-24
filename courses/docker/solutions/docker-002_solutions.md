# docker-002: explanatory solutions

Compare after your own attempt or an explicit reveal. These are explanations of the supplied teaching fixtures, not fabricated engine results.

## Mechanism review

The Docker client is the command you type. The daemon or engine receives its requests and manages containers. A context selects the endpoint to which the client connects. A local-looking terminal can be configured to operate a remote engine, so confirming the endpoint is part of ownership rather than a cosmetic setup step.

WSL 2 provides a Linux environment on Windows. The course uses its Ubuntu shell and an engine configured for Linux containers. It does not teach Windows containers or require each language compiler on Windows. On macOS, a desktop engine generally provides a Linux VM. On Linux, the engine can run on the host. These host arrangements differ, while the application’s container filesystem and runtime stay Linux-based.

The fixture needs a local engine and Compose. Compose is the client-side tool that reads a multi-service application definition. A successful client version print does not prove that the engine is running. Conversely, permission to access an engine grants substantial control over its host environment. Resolve setup through the engine’s documented user configuration rather than making a socket world-writable.

`docker context show` prints the selected context name. `docker context inspect NAME` shows its endpoint configuration. `docker info` actually contacts the engine and exposes its server operating-system type and resource configuration. `docker compose version` checks the Compose plugin. Treat errors separately: an absent command, an unreachable daemon, an authorization problem and a Windows-container engine are different conditions.

Run these in the same Bash terminal you will use for the fixture. Do not change global contexts as an unexplained repair. If a context is remote, stop and select the intended local setup deliberately outside the lesson. Keep private endpoint paths and machine identifiers out of screenshots shared publicly.

## Exercise 1: Predict whether docker --version proves readiness.

The version command can use local client information. It does not need to create a server connection and therefore cannot establish permission, engine mode or available resources.

**Expected:** No; it only proves the client can run.

## Exercise 2: Identify the selected context and endpoint.

Names are user-defined and cannot by themselves prove locality. Inspect the endpoint and understand which engine owns it before any state-changing operation.

**Expected:** A locally recorded context name and an intentionally local endpoint.

## Exercise 3: Produce a minimal setup checklist.

The language compilers come from classroom images. The host prerequisite is the engine environment; adding unrelated native toolchains makes first setup harder without solving a daemon connection problem.

**Expected:** Bash, local Linux engine, Compose and sufficient allocated resources.

## Exercise 4: Diagnose client success with daemon connection failure.

Do not interpret an unavailable server as a broken application Dockerfile. No build has occurred yet, so change the setup layer that actually failed.

**Expected:** Investigate engine startup, endpoint and permission separately.

## Exercise 5: Explain where commands run on Windows.

Linux paths and Bash quoting are part of the examples. PowerShell has different expansion and continuation syntax, so relabeling commands without changing syntax would mislead beginners.

**Expected:** Inside the integrated WSL 2 Ubuntu terminal.

## Exercise 6: Explain a safe response to discovering a remote context.

The lesson’s authorization concerns a disposable local lab. An ambient context does not extend that ownership to a shared engine or authorize cleanup of its resources.

**Expected:** Stop before mutations and deliberately configure the owned local engine.

## Check your transfer

A useful solution identifies the exact object, the phase when a setting takes effect, the expected normal result and an observation that disproves it. Repeating a command until it succeeds hides the mechanism. Change one variable, keep a failure record, and test the intended behavior again. Source examples here are small enough to inspect; a production system additionally needs ownership, lifecycle, data recovery and operational review. The host exercises are optional and must stay within the learner-created project.
