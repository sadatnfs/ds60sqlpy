# docker-002: explanatory solutions

Compare after your own attempt or an explicit reveal. These explain the supplied teaching fixtures; they are not engine results. The mechanism is explained in `courses/docker/guides/docker-002.md`.

## Exercise 1: Predict whether docker --version proves readiness.

**Expected answer:** No; it only proves the client can run.

**Why:** The version command can use local client information. It does not need to create a server connection and therefore cannot establish permission, engine mode or available resources.

## Exercise 2: Identify the selected context and endpoint.

**Expected answer:** A locally recorded context name and an intentionally local endpoint.

**Why:** Names are user-defined and cannot by themselves prove locality. Inspect the endpoint and understand which engine owns it before any state-changing operation.

## Exercise 3: Produce a minimal setup checklist.

**Expected evidence:** Bash, local Linux engine, Compose and sufficient allocated resources.

**Why:** The language compilers come from classroom images. The host prerequisite is the engine environment; adding unrelated native toolchains makes first setup harder without solving a daemon connection problem.

## Exercise 4: Diagnose client success with daemon connection failure.

**Expected answer:** Investigate engine startup, endpoint and permission separately.

**Why:** Do not interpret an unavailable server as a broken application Dockerfile. No build has occurred yet, so change the setup layer that actually failed.

## Exercise 5: Explain where commands run on Windows.

**Expected answer:** Inside the integrated WSL 2 Ubuntu terminal.

**Why:** Linux paths and Bash quoting are part of the examples. PowerShell has different expansion and continuation syntax, so relabeling commands without changing syntax would mislead beginners.

## Exercise 6: Explain a safe response to discovering a remote context.

**Expected answer:** Stop before mutations and deliberately configure the owned local engine.

**Why:** The lesson’s authorization concerns a disposable local lab. An ambient context does not extend that ownership to a shared engine or authorize cleanup of its resources.

## Check your transfer

A useful answer names the exact object, the phase when a setting takes effect, the expected normal result and an observation that would disprove it. A production system additionally needs ownership, lifecycle, data recovery and operational review.
