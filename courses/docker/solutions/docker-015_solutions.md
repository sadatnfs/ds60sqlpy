# docker-015: explanatory solutions

Compare after your own attempt or an explicit reveal. These are explanations of the supplied teaching fixtures, not fabricated engine results.

## Mechanism review

BuildKit is the build engine used by modern Docker tooling. It can execute a build graph, reuse cached results and make special mounts available to individual build steps. A cache mount stores reusable downloads; a secret mount provides sensitive input to a step without treating that input as an ordinary copied image file. These mounts have different purposes and lifetimes.

A secret mount reduces accidental persistence but does not make arbitrary build commands safe. A command can still print a secret or copy it into an output. The author must review what the step does. Never put credentials in ARG, ENV, a source file or a command URL simply because the final application does not use them.

Build-time network access is an external dependency. Prefer locked public inputs for the default teaching build. The fixture has no package downloads beyond its base image. This chapter uses a synthetic secret string in a separate scratch build and never needs a real registry credential.

A Dockerfile RUN mount exists only for that build operation. `type=cache` selects a persistent builder cache directory. `type=secret,id=demo` selects a separately supplied secret. Read a secret only at its declared path, and do not echo its bytes. `required=true` causes a missing input to fail clearly.

Cache entries can improve speed but should not be the only copy of a required source artifact. A cold build must still produce the same intended result from declared dependencies. Treat cache as discardable acceleration, not durable application data.

## Exercise 1: Compare a cache mount and a secret mount.

The two mounts solve different problems. A cache may persist across builds; a secret should be available only to the intended step and should never become a normal artifact.

**Expected:** Reusable acceleration versus sensitive transient input.

## Exercise 2: Predict a required secret missing from the build.

Failing explicitly keeps the dependency visible. Silently using another credential would undermine both reproducibility and the learner’s understanding of which identity performed the operation.

**Expected:** The step fails before pretending to authenticate.

## Exercise 3: Design a cold-build check.

A cache hit should not supply an otherwise missing source file. A reproducible build can rebuild necessary artifacts from declared dependencies when acceleration state is absent.

**Expected:** Remove reliance on cache while preserving declared public inputs.

## Exercise 4: Diagnose a secret copied into an output file.

The build command remains responsible for what it writes and prints. Review outputs and layers rather than treating the mount option as a universal secrecy guarantee.

**Expected:** Mount isolation does not prevent the command from leaking bytes.

## Exercise 5: Explain why ARG is unsuitable for a password.

Arguments are configuration inputs and can appear in provenance or logs. Use the explicit secret channel and restrict the command that reads it.

**Expected:** Build metadata and history can expose values.

## Exercise 6: Describe a dependency acquisition policy.

Builds should state what they fetch and how its identity is verified. A learner must be able to distinguish a prepared offline run from the initial network-dependent acquisition.

**Expected:** Locked inputs, deliberate network access and no default private credentials.

## Check your transfer

A useful solution identifies the exact object, the phase when a setting takes effect, the expected normal result and an observation that disproves it. Repeating a command until it succeeds hides the mechanism. Change one variable, keep a failure record, and test the intended behavior again. Source examples here are small enough to inspect; a production system additionally needs ownership, lifecycle, data recovery and operational review. The host exercises are optional and must stay within the learner-created project.
