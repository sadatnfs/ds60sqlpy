# docker-019: explanatory solutions

Compare after your own attempt or an explicit reveal. These explain the supplied teaching fixtures; they are not engine results. The mechanism is explained in `courses/docker/guides/docker-019.md`.

## Exercise 1: Distinguish attachment from published ports.

**Expected answer:** Joining a network and exposing a host socket are different operations.

**Why:** A service can communicate with peers without publishing anything. A published port is an additional host-facing path that deserves separate review.

## Exercise 2: Predict a pure computation with network none.

**Expected answer:** It succeeds if its files and runtime are already present.

**Why:** Network isolation does not prevent local arithmetic or file reads. It reveals undeclared dependencies when a program unexpectedly tries to download input.

## Exercise 3: Design a frontend/backend attachment table.

**Expected evidence:** Each service joins only the networks needed by its role.

**Why:** A small explicit table makes unintended paths easier to notice. Avoid putting every component on every network merely for convenience.

## Exercise 4: Diagnose host-network mode used to hide a mapping error.

**Expected answer:** Restore the intended isolation and fix the actual address or port.

**Why:** Changing the network mode can mask the symptom while broadening access. Test the original topology’s contract instead.

## Exercise 5: Explain why network isolation is not authentication.

**Expected answer:** Reachability policy and application identity answer different questions.

**Why:** An allowed caller may still be unauthorized for an operation. Sensitive services need appropriate request authentication and authorization in addition to network placement.

## Exercise 6: Define outbound acceptance for an offline worker.

**Expected evidence:** Prepared local computation succeeds and no external fetch is required.

**Why:** Offline qualification is about actual inputs and behavior. Merely disconnecting the network does not prove that all future code paths are prepared.

## Check your transfer

A useful answer names the exact object, the phase when a setting takes effect, the expected normal result and an observation that would disprove it. A production system additionally needs ownership, lifecycle, data recovery and operational review.
