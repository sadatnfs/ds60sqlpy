# docker-035: explanatory solutions

Compare after your own attempt or an explicit reveal. These explain the supplied teaching fixtures; they are not engine results. The mechanism is explained in `courses/docker/guides/docker-035.md`.

## Exercise 1: Compare total image size and incremental transfer.

**Expected answer:** Shared cached layers can reduce new transferred bytes.

**Why:** A displayed size is not a complete network-cost estimate. Record cache state and the actual transfer path.

## Exercise 2: Predict why runtime package installation hurts startup.

**Expected answer:** It adds network and dependency work to every run.

**Why:** It also makes behavior depend on current repositories. Prepare declared dependencies in the image and keep startup focused on application initialization.

## Exercise 3: Design a readiness latency measurement.

**Expected evidence:** Fixed image, known cache condition and repeated bounded readiness timing.

**Why:** Measure the same event each time. Process creation alone is weaker than useful app readiness.

## Exercise 4: Diagnose a size optimization that breaks HTTPS.

**Expected answer:** A required runtime asset may have been removed.

**Why:** Correctness comes first. Restore the dependency and identify safer size reductions with final-image acceptance.

## Exercise 5: Explain why broad pruning is not an acceptable benchmark setup.

**Expected answer:** It destroys shared caches and may affect unrelated work.

**Why:** Use a disposable environment when cold-cache behavior matters. A performance experiment should not damage a user’s engine state.

## Exercise 6: Write an optimization recommendation with evidence.

**Expected evidence:** Measured bottleneck, bounded change, correctness recheck and actual improvement.

**Why:** A useful recommendation ties the change to the intended user experience. Avoid equating smaller bytes with universally better runtime behavior.

## Check your transfer

A useful answer names the exact object, the phase when a setting takes effect, the expected normal result and an observation that would disprove it. A production system additionally needs ownership, lifecycle, data recovery and operational review.
