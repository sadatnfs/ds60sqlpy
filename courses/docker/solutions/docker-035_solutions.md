# docker-035: explanatory solutions

Compare after your own attempt or an explicit reveal. These are explanations of the supplied teaching fixtures, not fabricated engine results.

## Mechanism review

Image size affects transfer and storage, while startup latency depends on pulling, unpacking, container creation and application initialization. These costs overlap but are not identical. A smaller image can still start slowly if it performs expensive runtime work or waits for an unavailable dependency.

Layer sharing changes the amount of new data an engine needs. The displayed total image size is not always the incremental download for an engine that already has the base layers. Compression, cache state and platform also affect measured behavior.

Optimization should preserve correctness and maintainability. Removing a certificate bundle to save space may break HTTPS. Moving dependency installation to startup makes the image look smaller while making every run slower and less reproducible. Measure the user-visible path you actually want to improve.

Compare cold and warm conditions explicitly. A cold engine or missing-image test includes transfer cost; a warm local restart does not. The course’s local workflow shows build logs so learners can see which layers are reused. Keep at least several observations and record input identity before drawing conclusions.

For a small fixture, inspect image size and measure a bounded short process or readiness interval. Do not remove shared base images or prune the user’s engine merely to manufacture a cold-cache experiment. A disposable engine or CI job is the appropriate environment for that test.

## Exercise 1: Compare total image size and incremental transfer.

A displayed size is not a complete network-cost estimate. Record cache state and the actual transfer path.

**Expected:** Shared cached layers can reduce new transferred bytes.

## Exercise 2: Predict why runtime package installation hurts startup.

It also makes behavior depend on current repositories. Prepare declared dependencies in the image and keep startup focused on application initialization.

**Expected:** It adds network and dependency work to every run.

## Exercise 3: Design a readiness latency measurement.

Measure the same event each time. Process creation alone is weaker than useful app readiness.

**Expected:** Fixed image, known cache condition and repeated bounded readiness timing.

## Exercise 4: Diagnose a size optimization that breaks HTTPS.

Correctness comes first. Restore the dependency and identify safer size reductions with final-image acceptance.

**Expected:** A required runtime asset may have been removed.

## Exercise 5: Explain why broad pruning is not an acceptable benchmark setup.

Use a disposable environment when cold-cache behavior matters. A performance experiment should not damage a user’s engine state.

**Expected:** It destroys shared caches and may affect unrelated work.

## Exercise 6: Write an optimization recommendation with evidence.

A useful recommendation ties the change to the intended user experience. Avoid equating smaller bytes with universally better runtime behavior.

**Expected:** Measured bottleneck, bounded change, correctness recheck and actual improvement.

## Check your transfer

A useful solution identifies the exact object, the phase when a setting takes effect, the expected normal result and an observation that disproves it. Repeating a command until it succeeds hides the mechanism. Change one variable, keep a failure record, and test the intended behavior again. Source examples here are small enough to inspect; a production system additionally needs ownership, lifecycle, data recovery and operational review. The host exercises are optional and must stay within the learner-created project.
