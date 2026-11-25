# docker-035: explanatory solutions

These answers explain teaching fixtures, not engine results; the mechanism is in [the guide](../guides/docker-035.md).

## Exercise 1: Compare total image size and incremental transfer.

**Expected answer:** Shared cached layers can reduce new transferred bytes.

**Why:** A displayed size is not a complete network-cost estimate. Record cache state and the actual transfer path.

**Approach:** Separate the size reported by image inspect from the bytes actually downloaded when some layers are already cached.

**Why this is correct:** If the `python:3.12-slim` layers are already local, a new fixture build transfers only its small layers.

**A plausible wrong approach:** Estimating download cost from the full reported size overstates transfer for machines with the base cached.

**How to verify:** Record which layers were present before the pull and the bytes transferred.

## Exercise 2: Predict why runtime package installation hurts startup.

**Expected answer:** It adds network and dependency work to every run.

**Why:** It also makes behavior depend on current repositories. Prepare declared dependencies in the image and keep startup focused on application initialization.

**Approach:** Count what a pip install at startup adds: network fetches, dependency resolution and file writes on every run.

**Why this is correct:** Startup now depends on a package index being reachable and serving the same versions.

**A plausible wrong approach:** Installing at startup to keep the image small makes each start slower and can fail offline.

**How to verify:** Compare readiness time and offline behavior for an image with the packages built in against one installing at start.

## Exercise 3: Design a readiness latency measurement.

**Expected evidence:** Fixed image, known cache condition and repeated bounded readiness timing.

**Why:** Measure the same event each time. Process creation alone is weaker than useful app readiness.

**Approach:** Time from container create to the first healthy /healthz response, using the same image and cache state, repeated several times.

**Why this is correct:** Readiness is what users wait for; process start alone misses server setup.

**A plausible wrong approach:** Timing only docker run returning measures container creation, not when the app can answer.

**How to verify:** The record lists image ID, cache state and each repeated timing.

## Exercise 4: Diagnose a size optimization that breaks HTTPS.

**Expected answer:** A required runtime asset may have been removed.

**Why:** Correctness comes first. Restore the dependency and identify safer size reductions with final-image acceptance.

**Approach:** Check whether the slimmer image dropped CA certificates or similar files that TLS clients need.

**Why this is correct:** Correct behavior outranks size, so a smaller image that fails HTTPS is a regression.

**A plausible wrong approach:** Disabling certificate checks to make the request work trades a security control for fewer bytes.

**How to verify:** Restore the missing file, rerun the HTTPS request in the final image, and look for other reductions.

## Exercise 5: Explain why broad pruning is not an acceptable benchmark setup.

**Expected answer:** It destroys shared caches and may affect unrelated work.

**Why:** Use a disposable environment when cold-cache behavior matters. A performance experiment should not damage a user’s engine state.

**Approach:** Run cold-cache measurements on a separate engine or VM, not after pruning the learner's shared engine.

**Why this is correct:** Pruning removes caches and images other projects rely on, which is damage unrelated to the experiment.

**A plausible wrong approach:** Running docker system prune -a before each timing run costs everyone else their cached images.

**How to verify:** The cold run happens in a disposable environment, and the main engine's image list is unchanged.

## Exercise 6: Write an optimization recommendation with evidence.

**Expected evidence:** Measured bottleneck, bounded change, correctness recheck and actual improvement.

**Why:** A useful recommendation ties the change to the intended user experience. Avoid equating smaller bytes with universally better runtime behavior.

**Approach:** Name the measured bottleneck, the one change made, the correctness recheck and the measured gain.

**Why this is correct:** Tying the change to a measured user delay shows why the change was worth it.

**A plausible wrong approach:** Recommending the smallest possible base because smaller is faster skips the measurement.

**How to verify:** The recommendation cites before and after timings for the same event and a passing acceptance run.

## Check your transfer

Measure the transfer a target host would actually need, given which base layers it already holds, and readiness with the same `--wait` method, since a new base shares nothing cached. Alpine uses musl rather than glibc, so rerun the health, host and peer requests, an increment, and the export and restore commands, and check that any later HTTPS client still finds a CA bundle. Accept only a measured gain with identical behavior. If readiness time does not move, the healthcheck interval, not image size, was the limit.
