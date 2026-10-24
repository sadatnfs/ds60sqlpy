# docker-026: explanatory solutions

Compare after your own attempt or an explicit reveal. These are explanations of the supplied teaching fixtures, not fabricated engine results.

## Mechanism review

An override file changes a base Compose application model. Profiles select optional services. Both mechanisms can make one project support development, teaching and operations tasks, but they also create more possible effective configurations to review.

The effective model matters more than any one input file. Merge rules differ for scalar values, mappings and sequences. An override can unexpectedly add ports or mounts rather than replace the intended list in the way a beginner assumes. Always inspect or validate the combined model before applying it.

Profiles are not a security boundary. A service omitted from the default startup is still available when explicitly selected or enabled. Use profiles for intentional optional tools and workloads, not for hiding privileged services in a file and assuming they cannot run.

The fixture’s client has the tools profile. Ordinary `up` starts the app; an explicit tools invocation runs the peer check. For an override experiment, copy the fixture and change only a public message or unused loopback host port. Use `-f` in a fixed order and validate that same order.

Do not print a fully rendered production model containing secrets into a public log. This lesson uses synthetic public values. The goal is to explain which input supplied each final field and how a reviewer can reproduce the exact model.

## Exercise 1: Distinguish profiles and overrides.

A profile determines which optional services participate; an override modifies service and resource definitions. They can be used together but answer different questions.

**Expected:** Service selection versus model composition.

## Exercise 2: Predict ordinary startup with the tools profile disabled.

The profile communicates intent. An explicit run of the client remains possible, so its commands still need review.

**Expected:** The app starts and the optional client is not a persistent service.

## Exercise 3: Create an override for a public message.

Keep the experiment narrow enough to inspect. Avoid mixing a message edit with mounts, privilege changes and network modifications.

**Expected:** Only the intended environment value changes in the effective model.

## Exercise 4: Diagnose an unexpected extra port after merging.

Do not assume a sequence was replaced. Model composition must be understood for the actual Compose version and fields used.

**Expected:** Inspect merge behavior and the complete effective ports list.

## Exercise 5: Explain why a profile is not access control.

Security should come from permissions and the absence of unnecessary authority, not from an optional default selection.

**Expected:** Someone with engine and project access can enable it.

## Exercise 6: Write a reviewable configuration launch record.

This makes the effective deployment reproducible. Retain private values separately rather than embedding them in shared evidence.

**Expected:** Ordered files, profiles, project name and safe resolved settings.

## Check your transfer

A useful solution identifies the exact object, the phase when a setting takes effect, the expected normal result and an observation that disproves it. Repeating a command until it succeeds hides the mechanism. Change one variable, keep a failure record, and test the intended behavior again. Source examples here are small enough to inspect; a production system additionally needs ownership, lifecycle, data recovery and operational review. The host exercises are optional and must stay within the learner-created project.
