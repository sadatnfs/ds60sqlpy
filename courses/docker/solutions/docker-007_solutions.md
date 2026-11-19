# docker-007: explanatory solutions

Compare after your own attempt or an explicit reveal. These explain the supplied teaching fixtures; they are not engine results. The mechanism is explained in `courses/docker/guides/docker-007.md`.

## Exercise 1: Predict the first invalidated step after editing server.py.

**Expected answer:** The COPY using that file and dependent later steps.

**Why:** The builder tracks relevant inputs. Earlier independent operations can remain reusable while operations based on changed filesystem state require new results.

## Exercise 2: Record evidence of a real cache hit.

**Expected evidence:** A specific step labeled cached in plain build logs.

**Why:** Elapsed time alone is ambiguous because network and CPU vary. A named cached step ties the observation to the builder decision being studied.

## Exercise 3: Reorder dependency metadata and app source conceptually.

**Expected evidence:** Stable dependency inputs precede rapidly changing source.

**Why:** This allows source edits to reuse dependencies when lockfiles remain unchanged. It does not justify ignoring a lockfile change or copying too little to perform a correct build.

## Exercise 4: Diagnose a cached step that downloads a mutable dependency.

**Expected answer:** A cache hit can preserve old bytes even with unchanged command text.

**Why:** The command can have external inputs absent from the visible file hash. Pinning and deliberate update procedures provide a stronger reproducibility story than relying on caching behavior.

## Exercise 5: Explain no-cache versus pulling a base.

**Expected answer:** Reexecuting build steps and refreshing a base are separate choices.

**Why:** One option changes cache reuse; another changes the image resolved by the base reference. Conflating them makes debugging rebuilds needlessly expensive and hard to interpret.

## Exercise 6: Design a build-performance experiment.

**Expected evidence:** Same engine and context, one controlled edit, named cache observations.

**Why:** Record build identity and changed inputs so timing is interpretable. Optimize the expensive invalidated step after confirming it is actually the bottleneck.

## Check your transfer

A useful answer names the exact object, the phase when a setting takes effect, the expected normal result and an observation that would disprove it. A production system additionally needs ownership, lifecycle, data recovery and operational review.
