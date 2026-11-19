# docker-022: explanatory solutions

Compare after your own attempt or an explicit reveal. These explain the supplied teaching fixtures; they are not engine results. The mechanism is explained in `courses/docker/guides/docker-022.md`.

## Exercise 1: Compare a CPU limit with dedicated hardware.

**Expected answer:** A quota constrains time; it does not grant exclusive cores.

**Why:** Shared scheduling and host contention remain. State the actual control rather than translating it into an unsupported performance guarantee.

## Exercise 2: Predict the effect of insufficient engine VM memory.

**Expected answer:** Container limits cannot compensate for missing host capacity.

**Why:** The VM allocation bounds the resources the engine can manage. Inspect that layer when several individually modest containers compete.

## Exercise 3: Design a controlled CPU comparison.

**Expected evidence:** Same input and image, one changed limit, several bounded measurements.

**Why:** Control enough variables to make the comparison interpretable. Keep architecture and cache state in the evidence record.

## Exercise 4: Diagnose slowness without assuming memory failure.

**Expected answer:** Compare CPU throttling, I/O, requests and memory observations.

**Why:** Multiple mechanisms produce slow responses. A memory increase is unjustified when the first failing observation is elsewhere.

## Exercise 5: Explain why a single docker stats sample is limited.

**Expected answer:** It does not capture the whole workload or historical peaks.

**Why:** Sampling frequency and timing influence what is visible. Use a bounded series and application timings when investigating an intermittent issue.

## Exercise 6: Define a safe resource stress boundary.

**Expected evidence:** Small fixed workload, timeout and owned disposable target.

**Why:** The goal is to observe a mechanism, not to consume all host resources. Stop when the named failure or performance condition is established.

## Check your transfer

A useful answer names the exact object, the phase when a setting takes effect, the expected normal result and an observation that would disprove it. A production system additionally needs ownership, lifecycle, data recovery and operational review.
