# docker-007: explanatory solutions

Compare after your own attempt or an explicit reveal. These are explanations of the supplied teaching fixtures, not fabricated engine results.

## Mechanism review

A layer records filesystem changes from a build step. Build cache can reuse a prior result when the builder considers an instruction and its relevant inputs unchanged. Caching is a performance mechanism, not proof that a dependency is current or that a security update has been applied.

Instruction order creates a dependency chain. If a source copy changes before an expensive dependency installation, later steps may need to run again. Separating dependency metadata from frequently edited source can improve iteration. The correct split depends on the package manager and lockfile, not on memorizing one Dockerfile pattern.

A cache hit is visible in build logs. A fast build is not automatically cached, and a cache miss is not automatically a bug. Reproducibility requires identifying inputs, versions and build settings. The same text can still download different bytes if it refers to mutable remote dependencies.

Compare an unchanged rebuild with a rebuild after changing only a harmless source string in your learner copy. Record which instruction first stops being cached. A build with `--no-cache` intentionally ignores build-step cache, but it does not inherently replace every already available base image. Fetching newer bases is a separate operation.

Cache mounts, covered in the next stage, preserve download caches without baking their contents into the runtime image. Do not put real credentials into cache keys, ARG values or copied files. Build output and dependency recovery are observable concerns, so keep plain logs for your experiments.

## Exercise 1: Predict the first invalidated step after editing server.py.

The builder tracks relevant inputs. Earlier independent operations can remain reusable while operations based on changed filesystem state require new results.

**Expected:** The COPY using that file and dependent later steps.

## Exercise 2: Record evidence of a real cache hit.

Elapsed time alone is ambiguous because network and CPU vary. A named cached step ties the observation to the builder decision being studied.

**Expected:** A specific step labeled cached in plain build logs.

## Exercise 3: Reorder dependency metadata and app source conceptually.

This allows source edits to reuse dependencies when lockfiles remain unchanged. It does not justify ignoring a lockfile change or copying too little to perform a correct build.

**Expected:** Stable dependency inputs precede rapidly changing source.

## Exercise 4: Diagnose a cached step that downloads a mutable dependency.

The command can have external inputs absent from the visible file hash. Pinning and deliberate update procedures provide a stronger reproducibility story than relying on caching behavior.

**Expected:** A cache hit can preserve old bytes even with unchanged command text.

## Exercise 5: Explain no-cache versus pulling a base.

One option changes cache reuse; another changes the image resolved by the base reference. Conflating them makes debugging rebuilds needlessly expensive and hard to interpret.

**Expected:** Reexecuting build steps and refreshing a base are separate choices.

## Exercise 6: Design a build-performance experiment.

Record build identity and changed inputs so timing is interpretable. Optimize the expensive invalidated step after confirming it is actually the bottleneck.

**Expected:** Same engine and context, one controlled edit, named cache observations.

## Check your transfer

A useful solution identifies the exact object, the phase when a setting takes effect, the expected normal result and an observation that disproves it. Repeating a command until it succeeds hides the mechanism. Change one variable, keep a failure record, and test the intended behavior again. Source examples here are small enough to inspect; a production system additionally needs ownership, lifecycle, data recovery and operational review. The host exercises are optional and must stay within the learner-created project.
