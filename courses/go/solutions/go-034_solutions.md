# go-034: explained solutions

Compare after an attempt ([using solutions](../STUDY-GUIDE.md#use-the-solutions)). `courses/go/solutions/go-034_solution.go` implements all six cases.

## Mechanism

An executable is built for a target operating system and architecture. Source portability does not imply one binary runs everywhere. Go can cross-compile many pure-Go programs by choosing GOOS and GOARCH, while cgo and platform-specific dependencies introduce additional constraints. Container images package the executable and its runtime files, but still depend on a compatible kernel and architecture. A small image is useful only if certificates, time-zone needs and diagnostic requirements remain satisfied. Production shutdown must stop accepting new work, cancel or drain owned tasks within a budget, and report incomplete work honestly.

runtime.GOOS and GOARCH describe the running binary target. Build configuration uses environment variables before compilation, not source-level guesses. A multi-stage Dockerfile can compile in a toolchain image and copy the binary into a runtime stage. CGO_ENABLED=0 is appropriate for this standard-library classroom profile; it is not a universal instruction for every dependency. Use an exec-form container entrypoint so the process receives termination signals directly.

## 1. Inspect the current target: predict an edited check

Copy worked example 1, change `check(runtime.GOOS != "" && runtime.GOARCH != "", "target")` to `check(runtime.GOOS == "" && runtime.GOARCH != "", "target")` inside its check and predict whether it still passes; then restore it.

The unchanged code is worked example 1:

```go
check(runtime.GOOS != "" && runtime.GOARCH != "", "target")
```

**Expected:** The edited check panics with `target` even though `runtime.GOOS != "" && runtime.GOARCH != ""` still holds.

**Verify:** Restoring `check(runtime.GOOS != "" && runtime.GOARCH != "", "target")` makes the check pass again with the worked observation: both identifiers are nonempty.

The values describe this executed binary. They do not establish compatibility with another platform.

## 2. Validate the running deployment tuple: debug a regression

A one-token regression in worked example 2 makes a line read `allowed := map[string]bool{"linux/amd64": true, "linux/arm65": true}`. Repair it without changing the check.

The unchanged code is worked example 2:

```go
allowed := map[string]bool{"linux/amd64": true, "linux/arm64": true}
target := runtime.GOOS + "/" + runtime.GOARCH
check(allowed[target], "running target")
```

**Expected:** The defective run panics with `running target`; after restoring `allowed := map[string]bool{"linux/amd64": true, "linux/arm64": true}`, the running Linux tuple is admitted.

**Verify:** The failing run shows message `running target`; after the repair `allowed[target]` holds again.

A declared target set is a configuration contract, and the classroom worker is a Linux container on amd64 or arm64, so its own tuple must be in the set. Each additional image architecture still needs its own build and execution evidence.

## 3. Refuse an unsupported tuple

Check plan9/386 and an incomplete linux tuple with the same lookup, keeping linux/arm64 as the control.

```go
allowed := map[string]bool{"linux/amd64": true, "linux/arm64": true}
supported := func(goos, goarch string) bool { return allowed[goos+"/"+goarch] }
check(!supported("plan9", "386") && !supported("linux", "") && supported("linux", "arm64"), "unsupported")
```

**Expected:** Both unsupported tuples are rejected while linux/arm64 is admitted.

**Verify:** Your solution must keep `!supported("plan9", "386") && !supported("linux", "") && supported("linux", "arm64")` true. Control: changing `allowed := map[string]bool{"linux/amd64": true, "linux/arm64": true}` to `allowed := map[string]bool{"linux/amd64": true, "linux/arm65": true}` panics with message `unsupported`; revert it.

Explicit rejection is clearer than silently choosing an incompatible artifact. The admitted control proves the lookup is not simply rejecting everything.

## 4. Model stop-accepting before drain

Start with two active tasks, drain the service, try to admit a third task, then finish both tasks.

```go
s := ServiceState{Accepting: true, Active: 2}
s.Drain()
check(!s.Admit() && s.Active == 2, "drain start")
s.Finish()
s.Finish()
check(!s.Accepting && s.Active == 0, "stopped")
```

**Expected:** The third task is refused once draining begins, and the service stops only after both tasks finish.

**Verify:** Your solution must keep `!s.Admit() && s.Active == 2` true. Control: changing `s := ServiceState{Accepting: true, Active: 2}` to `s := ServiceState{Accepting: true, Active: 3}` panics with message `drain start`; revert it.

Stopping admission and completing in-flight work are different steps. A single stopped flag cannot explain partial shutdown.

## 5. Retain unfinished work evidence

Admit one more task to a service already running one, drain it, and allow a shutdown budget of one completion.

```go
s := ServiceState{Accepting: true, Active: 1}
check(s.Admit() && s.Active == 2, "admitted")
s.Drain()
budget := 1
for i := 0; i < budget; i++ {
	s.Finish()
}
check(s.Active == 1, "unfinished work")
```

**Expected:** One of the two tasks remains unfinished and visible.

**Verify:** Your solution must keep `s.Active == 1` true. Control: changing `for i := 0; i < budget; i++ {` to `for i := 0; i <= budget; i++ {` panics with message `unfinished work`; revert it.

A timeout must not manufacture completion. Real services should retain or report recoverable work according to their delivery guarantees.

## 6. Transfer deterministic version metadata

Format a version and source revision into a build label.

```go
label := fmt.Sprintf("%s/%s revision=%s", "lesson", "1.0", "abc123")
check(label == "lesson/1.0 revision=abc123", "version")
```

**Expected:** The result is lesson/1.0 revision=abc123.

**Verify:** Your solution must keep `label == "lesson/1.0 revision=abc123"` true. Control: changing `label := fmt.Sprintf("%s/%s revision=%s", "lesson", "1.0", "abc123")` to `label := fmt.Sprintf("%s/%s revision=%s", "lesson", "2.0", "abc123")` panics with message `version`; revert it.

Version metadata connects an artifact with source provenance. It should not contain a developer host path or private identity.

## Transfer after comparison

A Kubernetes Pod receives SIGTERM, then a grace period, then SIGKILL. Map this lesson onto it: stop accepting, let readiness fail so traffic moves elsewhere, finish in-flight work within the budget and log what was abandoned. Build images for the cluster's architecture, and embed a version and revision so a running Pod can report which build it is.
