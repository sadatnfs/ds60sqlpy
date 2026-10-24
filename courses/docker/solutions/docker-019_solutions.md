# docker-019: explanatory solutions

Compare after your own attempt or an explicit reveal. These are explanations of the supplied teaching fixtures, not fabricated engine results.

## Mechanism review

A gateway forwards traffic beyond a local network. Docker bridge networking commonly uses routing and address translation for outbound traffic. The exact host rules depend on the engine and platform. Container traffic can reach external destinations unless its configuration and surrounding policy restrict it.

An internal network reduces external connectivity for its attached network. A service attached to both an external-facing and internal network can intentionally connect two application tiers, but this is not an automatic application firewall. Review the service’s role, listener ports and credentials.

Network mode none creates a container without ordinary external networking. This is useful for a pure computation that needs no DNS or HTTP. Host networking removes a major layer of network isolation and behaves differently across environments; it is not the beginner default or a repair for a wrong port mapping.

Compose networks are named model objects. Services explicitly join the networks they require. A database can live only on `backend`, while an API joins `frontend` and `backend`. Marking `backend` internal should be tested from the actual callers and engine because host connectivity and DNS details are operational facts.

The fixture uses a single bridge for its first exercises. Sketch multi-tier designs before editing your copy. No chapter asks you to change host firewall rules, install a packet filter or disable existing security software.

## Exercise 1: Distinguish attachment from published ports.

A service can communicate with peers without publishing anything. A published port is an additional host-facing path that deserves separate review.

**Expected:** Joining a network and exposing a host socket are different operations.

## Exercise 2: Predict a pure computation with network none.

Network isolation does not prevent local arithmetic or file reads. It reveals undeclared dependencies when a program unexpectedly tries to download input.

**Expected:** It succeeds if its files and runtime are already present.

## Exercise 3: Design a frontend/backend attachment table.

A small explicit table makes unintended paths easier to notice. Avoid putting every component on every network merely for convenience.

**Expected:** Each service joins only the networks needed by its role.

## Exercise 4: Diagnose host-network mode used to hide a mapping error.

Changing the network mode can mask the symptom while broadening access. Test the original topology’s contract instead.

**Expected:** Restore the intended isolation and fix the actual address or port.

## Exercise 5: Explain why network isolation is not authentication.

An allowed caller may still be unauthorized for an operation. Sensitive services need appropriate request authentication and authorization in addition to network placement.

**Expected:** Reachability policy and application identity answer different questions.

## Exercise 6: Define outbound acceptance for an offline worker.

Offline qualification is about actual inputs and behavior. Merely disconnecting the network does not prove that all future code paths are prepared.

**Expected:** Prepared local computation succeeds and no external fetch is required.

## Check your transfer

A useful solution identifies the exact object, the phase when a setting takes effect, the expected normal result and an observation that disproves it. Repeating a command until it succeeds hides the mechanism. Change one variable, keep a failure record, and test the intended behavior again. Source examples here are small enough to inspect; a production system additionally needs ownership, lifecycle, data recovery and operational review. The host exercises are optional and must stay within the learner-created project.
