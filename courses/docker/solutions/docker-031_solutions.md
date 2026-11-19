# docker-031: explanatory solutions

Compare after your own attempt or an explicit reveal. These explain the supplied teaching fixtures; they are not engine results. The mechanism is explained in `courses/docker/guides/docker-031.md`.

## Exercise 1: Predict what a unit test cannot prove about packaging.

**Expected answer:** Missing image files or a wrong final command can remain undetected.

**Why:** Unit tests may run in a richer host environment. Execute the final image to observe its real dependency and filesystem contract.

## Exercise 2: Separate source ZIP and image artifacts.

**Expected evidence:** Source input package versus built executable filesystem.

**Why:** They have different consumers and validation requirements. A clean archive does not establish that the image starts.

## Exercise 3: Design a parallel test partition.

**Expected evidence:** Independent groups with explicit ownership for shared fixtures.

**Why:** Parallelism is valuable only when tests do not corrupt one another’s state. Preserve required serialization for shared resources.

## Exercise 4: Diagnose rebuilding between acceptance and deployment.

**Expected answer:** The new artifact may not match the tested identity.

**Why:** Mutable dependencies and timestamps can change output. Promote the tested artifact or qualify the newly built one explicitly.

## Exercise 5: Explain cleanup after a failed CI job.

**Expected answer:** Remove job-owned runtime resources while retaining bounded diagnostic evidence.

**Why:** Failure should not leave a cluster or volume consuming resources indefinitely. Cleanup must not erase the only failure receipt or affect unrelated projects.

## Exercise 6: Write a release gate with honest limitations.

**Expected evidence:** Named actual checks on exact artifacts, plus visible skipped surfaces.

**Why:** A gate should report what ran, not infer broad acceptance from static configuration. Different engines and architectures may still require separate qualification.

## Check your transfer

A useful answer names the exact object, the phase when a setting takes effect, the expected normal result and an observation that would disprove it. A production system additionally needs ownership, lifecycle, data recovery and operational review.
