# k8s-012: Explanatory solutions

These answers explain the stated synthetic and scoped runtime contracts. Static checks do not prove cluster acceptance.

## Mechanism

Troubleshooting starts by separating observations from hypotheses. A condition, event or log can narrow a failure, but no single status word explains every unavailable application. Build a short timeline from source submission through API acceptance, scheduling, container start, readiness and client behavior. Locate the first boundary that has not been established.

This worksheet compares three explicit synthetic cases:missing configuration, an incorrect readiness path and a failed finite Job. It also names which cases the browser can reproduce directly. Wrong readiness and fixed task failure have bounded current operations; the missing-config example is a host/static case because the broker rejects inconsistent ConfigMap references before apply.

The purpose is a disciplined diagnosis and minimal repair, not a collection of broad commands against every namespace. Use only the owned target and preserve relevant object UIDs so a replacement or unrelated workload cannot silently enter the evidence.

## Exercise 1: Order the evidence phases

The sequence prevents searching application logs before a container was configured or treating a Service response as guaranteed by object creation. Real timestamps can overlap across controllers, but the evidence dependencies remain useful.

**Expected:** A trace identifies the first missing or failed boundary for each case.

## Exercise 2: Diagnose missing configuration

The general Kubernetes failure occurs during container configuration. The current broker catches some inconsistent references earlier, so a browser refusal must be labeled as a different phase. The host fixture is required to observe the kubelet condition.

**Expected:** Inspect referenced ConfigMap name/key and availability; do not claim the process crashed.

## Exercise 3: Diagnose the probe path

The application can be running while the readiness URL is wrong. Changing unrelated selectors or resource limits does not explain the observed 404. A new bounded run should preserve its own source and identity receipt.

**Expected:** Change /missing to the admitted /ready path; then require new Ready and client evidence.

## Exercise 4: Diagnose finite work

The fixed task can start successfully and still fail its own contract. Increasing an unrelated Deployment count would not repair it. A retry policy also cannot turn a deterministic injected failure into a correct result without changing the intended input.

**Expected:** Task exit2 and terminal Failed condition identify the injected application outcome.

## Exercise 5: Write a minimal incident timeline

A reviewable timeline separates what was seen from what was inferred and what was actually changed. It should make a failed hypothesis useful evidence rather than erase it after a later successful attempt.

**Expected:** Each claim cites a bounded field/line and object identity; synthetic facts are labeled.

## Exercise 6: Verify recovery and cleanup

Recovery needs evidence at the failed layer plus the intended application result. Cleanup has its own identity and deadline contract, especially after timeout or cancellation. A same-name replacement must remain untouched.

**Expected:** Relevant controller/application checks pass and only recorded owned UIDs are removed.

## Boundary and troubleshooting review

A large dump of every namespace, log and Secret is not a better diagnosis and exceeds the course scope. Start from the owned source, identity and first discriminating condition. Do not turn a source-admission refusal into a fabricated cluster event or copy synthetic fixture timestamps into a live incident report.

The offline reference classifies supplied facts only. It does not discover a real incident or establish that a proposed repair was applied. Keep predicted outcomes, actual observations and confirmed recovery as separate entries.
