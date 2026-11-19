# docker-004: explanatory solutions

Compare after your own attempt or an explicit reveal. These explain the supplied teaching fixtures; they are not engine results. The mechanism is explained in `courses/docker/guides/docker-004.md`.

## Exercise 1: Predict what happens when the main process exits.

**Expected answer:** The container enters an exited state.

**Why:** A container is not a VM with an independent background boot lifecycle. Its main process lifecycle drives the container state even if a script attempted to background work.

## Exercise 2: Compare exec-form and shell-form startup.

**Expected answer:** An argument array versus an intervening shell.

**Why:** The difference affects expansion and process hierarchy. It is not a claim that every shell command is wrong, but shell wrappers must intentionally forward signals and wait for children.

## Exercise 3: Write a four-step graceful shutdown sequence.

**Expected evidence:** Stop new work, bound draining, close owned resources, exit.

**Why:** An unbounded drain can prevent shutdown forever. Resource cleanup should be explicit, and data correctness may need a transaction or recovery protocol beyond closing file handles.

## Exercise 4: Diagnose a service kept alive only by sleep.

**Expected answer:** The alive container does not prove the application is healthy.

**Why:** The sleep process can make a status look running while the real server has crashed. Measure the application’s endpoint and actual process rather than adding a liveness placeholder.

## Exercise 5: Explain why exit 137 is not a complete OOM diagnosis.

**Expected answer:** It identifies a termination pattern, not its unique cause.

**Why:** A user or timeout can also send a kill signal. Correlate termination state with OOMKilled and relevant events before recommending memory changes.

## Exercise 6: Design a shutdown acceptance check for a writer.

**Expected evidence:** Bounded stop, consistent persisted record and restart recovery.

**Why:** The important observation is what readers see after recovery. A clean exit code is useful but cannot by itself prove that a partially written application record is valid.

## Check your transfer

A useful answer names the exact object, the phase when a setting takes effect, the expected normal result and an observation that would disprove it. A production system additionally needs ownership, lifecycle, data recovery and operational review.
