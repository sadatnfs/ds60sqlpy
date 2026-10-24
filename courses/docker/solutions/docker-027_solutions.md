# docker-027: explanatory solutions

Compare after your own attempt or an explicit reveal. These are explanations of the supplied teaching fixtures, not fabricated engine results.

## Mechanism review

This capstone adds peer discovery, constrained execution and a recovery test to the first app. The system still fits on one page: app serves JSON and owns its counter volume; client observes app through service DNS; the browser observes the loopback-published endpoint. Keeping these paths small makes failures explainable.

A recoverable system is more than a system that restarts. It has an identified durable state, a consistency boundary, a backup, an independent restore target and a bounded procedure to regain useful behavior. A second-tier client must also handle a dependency being temporarily unavailable without replaying unsafe writes.

Your deliverable is a short operator guide plus evidence, not a collection of screenshots. A future reader should know which project the commands affect, which volume contains state, how to inspect a failure, and what they can remove without losing the retained counter.

Work only in the copied fixture. Verify host and peer requests, record the non-root user and read-only configuration, export the stopped app’s counter, restore into a distinct target and compare. A deliberately wrong service port in a scratch client should fail with a bounded transport error.

Do not broaden the project into a real database cluster for this exercise. The purpose is to integrate mechanisms already learned, then clearly state the limitations that a database, public endpoint or multi-host deployment would add.

## Exercise 1: Predict which resources are durable.

Containers, peer client instances and project networks are replaceable. Do not accidentally rely on writable-layer state when describing recovery.

**Expected:** Only the intended named volume and explicit backup files.

## Exercise 2: Change only the peer target port in a scratch copy.

The controlled fault separates internal routing from application readiness. Preserve the error rather than changing multiple network settings at once.

**Expected:** The request fails within its timeout while app remains healthy.

## Exercise 3: Build an independent restore demonstration.

Recovery evidence requires use of the restored data. A copied file existing at a path is not enough without parsing and an application-level check.

**Expected:** New target state equals the exported counter while source remains intact.

## Exercise 4: Diagnose a passing host request with failing peer request.

The two paths share an application but have different discovery and routing. Their disagreement localizes the fault.

**Expected:** Inspect service DNS, network attachment and internal target port.

## Exercise 5: Explain the limits of this single-engine design.

A small lab teaches the mechanisms honestly. Production requirements need additional architecture and qualification rather than a larger marketing claim.

**Expected:** No multi-host failover or database consistency guarantee is claimed.

## Exercise 6: Write a beginner operator handoff.

A good handoff is executable by a reader with the documented prerequisites. It names state retention explicitly and avoids ambient context assumptions.

**Expected:** Setup, evidence, failure diagnosis, backup/restore and scoped cleanup.

## Check your transfer

A useful solution identifies the exact object, the phase when a setting takes effect, the expected normal result and an observation that disproves it. Repeating a command until it succeeds hides the mechanism. Change one variable, keep a failure record, and test the intended behavior again. Source examples here are small enough to inspect; a production system additionally needs ownership, lifecycle, data recovery and operational review. The host exercises are optional and must stay within the learner-created project.
