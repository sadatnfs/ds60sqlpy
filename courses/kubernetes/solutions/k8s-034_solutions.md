# k8s-034: Explanatory solutions

These answers explain the stated synthetic and scoped runtime contracts. Static checks do not prove cluster acceptance.

## Mechanism

A rollout creates or replaces workload replicas; a traffic change determines which ready backends receive requests. Those operations are related but different. A Deployment can finish creating a candidate while the Service still selects only the stable release. Conversely, broadening a selector can send requests to a candidate before the team has collected the intended application evidence.

The host fixture has hello-stable and hello-candidate Deployments with distinct release labels. Both use the same preloaded0.2 image, but /message returns hello or reviewer through a fixed environment value. This is a configuration-release rehearsal. It does not demonstrate a binary image upgrade, and /version remains the legacy fixture version string for both. A real two-image rehearsal requires separately qualified, preloaded image identities.

A release gate states what must be true before changing traffic and what triggers rollback. For this small fixture, require the expected candidate marker, zero unexpected payloads and zero errors in a declared finite request sample. That sample is evidence about the observed requests, not a proof of all future behavior or an exact traffic-share guarantee.

## Exercise 1: Distinguish binary and configuration versions

A useful experiment must name what changed. Calling this a binary upgrade would claim a version transition that never happened. The marker still provides a valid way to trace routing to two different configured backends.

**Expected:** Same binary version; different synthetic configuration markers.

## Exercise 2: Predict selected backends

Readiness cannot override a label mismatch. The candidate can be healthy yet receive no Service traffic, which is often intentional before a controlled cutover and explains why Pod checks and Service checks answer different questions.

**Expected:** Stable matches and candidate does not.

## Exercise 3: Predeclare the release gate

The gate must be chosen before examining the candidate results. Retain exact sample semantics so a reviewer can tell whether retries hid failures or whether only successful responses were counted.

**Expected:** A concrete gate that can fail independently of Ready replicas.

## Exercise 4: Reject the failing candidate

A finite negative result is actionable because it violates the declared rule. Retrying until four successes appear would change the experiment and conceal the failure rate observed during the original window.

**Expected:** Failure with one error; do not proceed to promotion.

## Exercise 5: Restore and verify stable traffic

The rollback sequence needs an application confirmation through the same path users would take. A selector still pointing to deleted candidate Pods can leave no endpoints even though the stable Deployment remains healthy.

**Expected:** Correct Service identity and four observed hello responses.

## Exercise 6: Explain ratio and evidence limits

The final review should identify the routing mechanism, sample size and remaining uncertainty. A real weighted canary or binary release would require additional qualified capabilities and separate evidence.

**Expected:** Replica ratio does not establish an exact traffic ratio or production reliability.

## Boundary and troubleshooting review

The two markers represent different configuration values in the same binary. Keep that distinction visible in the release packet. A successful finite sample cannot establish production capacity, error probability zero or exact canary ratios.

If the candidate fails, retain its observations and restore the verified path. Do not loosen the gate after seeing a failure merely to label the release successful. Predeclare acceptable conditions and record any later policy revision as a separate decision.
