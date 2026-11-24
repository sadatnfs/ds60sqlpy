# k8s-064: explanatory solutions

Compare after your own attempt or an explicit reveal. These explanations describe the synthetic topology and stated API contracts. They are not fabricated runtime receipts.

## Mechanism review

Troubleshooting is a sequence of discriminating observations. Start with the caller, intended name, protocol, port and expected application result. Then identify the first layer where actual behavior differs from the model. Changing several layers at once can make the symptom disappear without explaining the cause.

A useful request ladder separates name resolution, route reachability, transport connection, TLS identity, proxy routing and application semantics. Kubernetes adds controller and endpoint state that helps explain those steps. A successful test at one layer should not be promoted into a claim about every later layer.

Controlled comparisons are powerful. If direct Pod traffic succeeds but Service traffic fails, focus on selector/endpoints/data-plane differences. If an internal Service request succeeds but external traffic fails, inspect the external listener and routing path. Each comparison requires the same intended application and an owned permitted probe.

Use a hypothesis table with expected observation if true, expected observation if false and the smallest safe check. Preserve the failure before repair. Avoid broad all-namespace commands and packet captures when an exact field or short request answers the question.

A timeout is ambiguous: it can involve dropped packets, no route, DNS delay, a stalled TLS handshake or an application that never responds. A refused connection, TLS error and HTTP status narrow the phase differently. Read the actual diagnostic rather than translating every failure into service down.

## Exercise 1: Order the request ladder.

The order prevents diagnosing a later application symptom when the connection never existed.

**Expected:** DNS, route, transport, optional TLS, proxy/application route and body.

**Solution reasoning**

- **Approach:** Order the checks as DNS, route, transport, optional TLS, proxy or app route and response body.
- **Why it is correct:** Each step depends on the one before it, so the first failing rung locates the fault.
- **Plausible wrong approach:** Starting at the response body skips earlier layers that may have already failed.
- **How to verify:** The ladder lists all six rungs in order.

## Exercise 2: Interpret connection refused versus timeout.

Neither result alone uniquely identifies a root cause. Use it to choose the next discriminating check.

**Expected:** Refusal narrows listener/connectivity behavior; timeout remains broader.

**Solution reasoning**

- **Approach:** Treat a refusal as reaching a host with no listener, and a timeout as no answer from anywhere along the path.
- **Why it is correct:** A refused connection means something replied, while a timeout can come from routing, policy or a dropped packet.
- **Plausible wrong approach:** Treating both errors the same discards the information that a refusal narrows the search.
- **How to verify:** Refusal narrows the cause, and timeout stays broad.

## Exercise 3: Build a three-hypothesis table for Service failure.

A table makes diagnosis reviewable and reduces random configuration edits.

**Expected:** Selector, targetPort and data-plane hypotheses each have distinct evidence.

**Solution reasoning**

- **Approach:** Write selector, targetPort and data plane hypotheses, each with its own deciding evidence.
- **Why it is correct:** Endpoints show selector matches, a direct Pod request tests targetPort and node rules test the data plane.
- **Plausible wrong approach:** Checking one hypothesis and fixing it without testing the others can leave the real fault in place.
- **How to verify:** Each hypothesis has a distinct check.

## Exercise 4: Diagnose internal success with external failure.

Keep the working internal evidence. Do not replace healthy Pods before examining the path that differs.

**Expected:** Inspect the added external listener/routing/TLS layers.

**Solution reasoning**

- **Approach:** Look only at the layers the external path adds: listener, external routing and TLS.
- **Why it is correct:** Internal success shows the Service and Pods work, so the fault must sit in the added external layers.
- **Plausible wrong approach:** Debugging the backend after internal success repeats checks that already passed.
- **How to verify:** The diagnosis is limited to external listener, routing and TLS.

## Exercise 5: Explain why a stale successful receipt is insufficient.

Bind evidence to current identities and source. Historical success is context, not present acceptance.

**Expected:** It may belong to another revision, namespace or caller path.

**Solution reasoning**

- **Approach:** Require a fresh receipt tied to the current revision, namespace and caller path.
- **Why it is correct:** An older success may have come from a different revision, namespace or route than the one in question.
- **Plausible wrong approach:** Reusing yesterday's passing check as current evidence can hide a regression.
- **How to verify:** The receipt has a current timestamp and matches revision, namespace and caller.

## Exercise 6: Perform a single-fault incident walkthrough.

The lesson is complete when the learner can explain why the repair works and what observation would show it failed.

**Expected:** One controlled fault, preserved failure, targeted repair and rechecked invariant.

**Solution reasoning**

- **Approach:** Introduce one controlled fault, record the failure, apply one targeted fix and recheck the invariant.
- **Why it is correct:** A single fault keeps cause and effect clear, and the recheck proves the fix restored the invariant.
- **Plausible wrong approach:** Changing several settings at once makes it unclear which change fixed the failure.
- **How to verify:** The record shows one fault, its preserved failure, the repair and a passing recheck.
