# docker-027: explanatory solutions

Compare after your own attempt or an explicit reveal. These explain the supplied teaching fixtures; they are not engine results. The mechanism is explained in `courses/docker/guides/docker-027.md`.

## Exercise 1: Predict which resources are durable.

**Expected answer:** Only the intended named volume and explicit backup files.

**Why:** Containers, peer client instances and project networks are replaceable. Do not accidentally rely on writable-layer state when describing recovery.

## Exercise 2: Change only the peer target port in a scratch copy.

**Expected evidence:** The request fails within its timeout while app remains healthy.

**Why:** The controlled fault separates internal routing from application readiness. Preserve the error rather than changing multiple network settings at once.

## Exercise 3: Build an independent restore demonstration.

**Expected evidence:** New target state equals the exported counter while source remains intact.

**Why:** Recovery evidence requires use of the restored data. A copied file existing at a path is not enough without parsing and an application-level check.

## Exercise 4: Diagnose a passing host request with failing peer request.

**Expected answer:** Inspect service DNS, network attachment and internal target port.

**Why:** The two paths share an application but have different discovery and routing. Their disagreement localizes the fault.

## Exercise 5: Explain the limits of this single-engine design.

**Expected answer:** No multi-host failover or database consistency guarantee is claimed.

**Why:** A small lab teaches the mechanisms honestly. Production requirements need additional architecture and qualification rather than a larger marketing claim.

## Exercise 6: Write a beginner operator handoff.

**Expected evidence:** Setup, evidence, failure diagnosis, backup/restore and scoped cleanup.

**Why:** A good handoff is executable by a reader with the documented prerequisites. It names state retention explicitly and avoids ambient context assumptions.

## Check your transfer

A useful answer names the exact object, the phase when a setting takes effect, the expected normal result and an observation that would disprove it. A production system additionally needs ownership, lifecycle, data recovery and operational review.
