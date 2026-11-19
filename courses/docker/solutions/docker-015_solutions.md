# docker-015: explanatory solutions

Compare after your own attempt or an explicit reveal. These explain the supplied teaching fixtures; they are not engine results. The mechanism is explained in `courses/docker/guides/docker-015.md`.

## Exercise 1: Compare a cache mount and a secret mount.

**Expected answer:** Reusable acceleration versus sensitive transient input.

**Why:** The two mounts solve different problems. A cache may persist across builds; a secret should be available only to the intended step and should never become a normal artifact.

## Exercise 2: Predict a required secret missing from the build.

**Expected answer:** The step fails before pretending to authenticate.

**Why:** Failing explicitly keeps the dependency visible. Silently using another credential would undermine both reproducibility and the learner’s understanding of which identity performed the operation.

## Exercise 3: Design a cold-build check.

**Expected evidence:** Remove reliance on cache while preserving declared public inputs.

**Why:** A cache hit should not supply an otherwise missing source file. A reproducible build can rebuild necessary artifacts from declared dependencies when acceleration state is absent.

## Exercise 4: Diagnose a secret copied into an output file.

**Expected answer:** Mount isolation does not prevent the command from leaking bytes.

**Why:** The build command remains responsible for what it writes and prints. Review outputs and layers rather than treating the mount option as a universal secrecy guarantee.

## Exercise 5: Explain why ARG is unsuitable for a password.

**Expected answer:** Build metadata and history can expose values.

**Why:** Arguments are configuration inputs and can appear in provenance or logs. Use the explicit secret channel and restrict the command that reads it.

## Exercise 6: Describe a dependency acquisition policy.

**Expected answer:** Locked inputs, deliberate network access and no default private credentials.

**Why:** Builds should state what they fetch and how its identity is verified. A learner must be able to distinguish a prepared offline run from the initial network-dependent acquisition.

## Check your transfer

A useful answer names the exact object, the phase when a setting takes effect, the expected normal result and an observation that would disprove it. A production system additionally needs ownership, lifecycle, data recovery and operational review.
