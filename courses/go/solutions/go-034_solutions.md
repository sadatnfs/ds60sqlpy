# go-034: explained solutions

These are comparison material after an attempt or explicit reveal. The executable reference implements all six cases in one `main.go`.

## Mechanism

An executable is built for a target operating system and architecture. Source portability does not imply one binary runs everywhere. Go can cross-compile many pure-Go programs by choosing GOOS and GOARCH, while cgo and platform-specific dependencies introduce additional constraints. Container images package the executable and its runtime files, but still depend on a compatible kernel and architecture. A small image is useful only if certificates, time-zone needs and diagnostic requirements remain satisfied. Production shutdown must stop accepting new work, cancel or drain owned tasks within a budget, and report incomplete work honestly.

runtime.GOOS and GOARCH describe the running binary target. Build configuration uses environment variables before compilation, not source-level guesses. A multi-stage Dockerfile can compile in a toolchain image and copy the binary into a runtime stage. CGO_ENABLED=0 is appropriate for this standard-library classroom profile; it is not a universal instruction for every dependency. Use an exec-form container entrypoint so the process receives termination signals directly.

## 1. Inspect the current target

Read runtime target identifiers.

```go
check(runtime.GOOS != "" && runtime.GOARCH != "", "target")
```

**Expected:** Both identifiers are nonempty.

The values describe this executed binary. They do not establish compatibility with another platform.

## 2. Validate a supported deployment tuple

Check linux/amd64 and linux/arm64 against an explicit target set.

```go
allowed := map[string]bool{"linux/amd64": true, "linux/arm64": true}
check(allowed["linux/amd64"] && allowed["linux/arm64"], "targets")
```

**Expected:** Both tuples are admitted.

A declared target set is a configuration contract. Each image architecture still needs real build and execution evidence.

## 3. Refuse an unsupported tuple

Check an unrelated target against the same set.

```go
allowed := map[string]bool{"linux/amd64": true, "linux/arm64": true}
check(!allowed["plan9/386"], "unsupported")
```

**Expected:** The unsupported target is rejected.

Explicit rejection is clearer than silently choosing an incompatible artifact.

## 4. Model stop-accepting before drain

Transition a service state from accepting to draining to stopped.

```go
s := ServiceState{Accepting: true, Active: 2}
s.Accepting = false
check(!s.Accepting && s.Active == 2, "drain start")
s.Active = 0
check(!s.Accepting && s.Active == 0, "stopped")
```

**Expected:** No new work is admitted once draining begins.

Stopping admission and completing in-flight work are different steps. A single stopped flag cannot explain partial shutdown.

## 5. Retain unfinished work evidence

Apply a shutdown budget that ends before two tasks finish.

```go
s := ServiceState{Accepting: false, Active: 2}
s.Active--
check(s.Active == 1, "unfinished work")
```

**Expected:** The remaining task count stays visible.

A timeout must not manufacture completion. Real services should retain or report recoverable work according to their delivery guarantees.

## 6. Transfer deterministic version metadata

Format a version and source revision into a build label.

```go
label := fmt.Sprintf("%s/%s revision=%s", "lesson", "1.0", "abc123")
check(label == "lesson/1.0 revision=abc123", "version")
```

**Expected:** The result is lesson/1.0 revision=abc123.

Version metadata connects an artifact with source provenance. It should not contain a developer host path or private identity.

## Transfer after comparison

Return to your own pad and reproduce one check with a new input. Explain why the check rejects a plausible wrong implementation. Keep the distinction between a pure model, an in-process fake, and a real external system visible in your notes.
