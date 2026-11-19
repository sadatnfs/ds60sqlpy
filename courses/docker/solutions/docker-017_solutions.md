# docker-017: explanatory solutions

Compare after your own attempt or an explicit reveal. These explain the supplied teaching fixtures; they are not engine results. The mechanism is explained in `courses/docker/guides/docker-017.md`.

## Exercise 1: Predict whether Linux implies amd64.

**Expected answer:** No; operating system and architecture are separate axes.

**Why:** Linux supports multiple instruction families. A release statement should name both dimensions rather than collapsing them into a single platform label.

## Exercise 2: Classify cross-compilation and emulation.

**Expected answer:** Producing target code versus executing foreign code.

**Why:** A cross-compiler can be native while its output is foreign. Emulation may permit execution but changes performance and cannot establish all native behavior.

## Exercise 3: Design a two-platform evidence matrix.

**Expected evidence:** Separate build and execution columns for amd64 and arm64.

**Why:** Do not fill an execution cell from an index manifest alone. The matrix should make untested combinations visible.

## Exercise 4: Diagnose exec format error.

**Expected answer:** Inspect architecture and executable format before app logic.

**Why:** A program can fail before its entry point because the kernel cannot load its format. Changing business logic or increasing memory will not fix that boundary.

## Exercise 5: Explain why multi-platform output is not always one --load result.

**Expected answer:** Exporter and image-store capabilities constrain output.

**Why:** Understand the selected build driver and local store rather than assuming every multi-platform result can be loaded identically on every engine.

## Exercise 6: Write an honest portability claim.

**Expected evidence:** Name the tested platform and label other platforms unqualified.

**Why:** Source portability is valuable but weaker than observed execution. Architecture-specific dependencies and runtime behavior need their own evidence.

## Check your transfer

A useful answer names the exact object, the phase when a setting takes effect, the expected normal result and an observation that would disprove it. A production system additionally needs ownership, lifecycle, data recovery and operational review.
