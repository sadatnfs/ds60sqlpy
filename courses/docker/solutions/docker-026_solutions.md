# docker-026: explanatory solutions

Compare after your own attempt or an explicit reveal. These explain the supplied teaching fixtures; they are not engine results. The mechanism is explained in `courses/docker/guides/docker-026.md`.

## Exercise 1: Distinguish profiles and overrides.

**Expected answer:** Service selection versus model composition.

**Why:** A profile determines which optional services participate; an override modifies service and resource definitions. They can be used together but answer different questions.

## Exercise 2: Predict ordinary startup with the tools profile disabled.

**Expected answer:** The app starts and the optional client is not a persistent service.

**Why:** The profile communicates intent. An explicit run of the client remains possible, so its commands still need review.

## Exercise 3: Create an override for a public message.

**Expected evidence:** Only the intended environment value changes in the effective model.

**Why:** Keep the experiment narrow enough to inspect. Avoid mixing a message edit with mounts, privilege changes and network modifications.

## Exercise 4: Diagnose an unexpected extra port after merging.

**Expected answer:** Inspect merge behavior and the complete effective ports list.

**Why:** Do not assume a sequence was replaced. Model composition must be understood for the actual Compose version and fields used.

## Exercise 5: Explain why a profile is not access control.

**Expected answer:** Someone with engine and project access can enable it.

**Why:** Security should come from permissions and the absence of unnecessary authority, not from an optional default selection.

## Exercise 6: Write a reviewable configuration launch record.

**Expected evidence:** Ordered files, profiles, project name and safe resolved settings.

**Why:** This makes the effective deployment reproducible. Retain private values separately rather than embedding them in shared evidence.

## Check your transfer

A useful answer names the exact object, the phase when a setting takes effect, the expected normal result and an observation that would disprove it. A production system additionally needs ownership, lifecycle, data recovery and operational review.
