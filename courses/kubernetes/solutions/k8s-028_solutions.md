# k8s-028: Explanatory solutions

These answers explain the stated synthetic and scoped runtime contracts. Static checks do not prove cluster acceptance.

## Mechanism

The intermediate capstone combines a stateless application response, a synthetic persistent marker store, reviewed configuration rendering and measured traffic policy. It is a host-lab integration exercise because the normal browser adapter does not provide the storage, CNI and stateful-update capabilities needed for the whole scenario.

The supplied manifests keep the components explicit: configured hello Deployment/Service, one StatefulSet claim template and two ingress policies. The persistent marker is a file-based synthetic datastore, not a real database service. Its writer and reader operations must be separately bounded and reviewed by the host. A correct frontend response is not evidence that the marker survived, and an unchanged marker is not evidence that network isolation works.

The capstone's acceptance packet connects those independent observations and includes a failed-change recovery. Cleanup respects the declared synthetic-data retention choice and exact resource identities. Releasing the disposable cluster is a separate lifecycle boundary that can remove node-local retained data.

## Exercise 1: Inventory capabilities

A complete plan names the missing execution surfaces rather than pretending all Kubernetes objects are interchangeable through the browser adapter. This preserves both authority and evidence quality.

**Expected:** Each capability has a qualified host receipt or is marked unavailable.

**Solution reasoning**

- **Approach:** List storage class, CNI policy support, renderer, image and owned target with a host receipt or unavailable for each.
- **Why it is correct:** Each acceptance gate depends on one of these, so an unproven capability makes its gate untestable.
- **Plausible wrong approach:** Inferring NetworkPolicy support from the presence of a policy manifest tells you nothing about the CNI.
- **How to verify:** Every row points to a receipt or reads unavailable.

## Exercise 2: Establish independent baselines

The baseline makes later differences interpretable. It should include exact resource identities and the data initialization boundary, not only a screenshot of ready Pods.

**Expected:** A source-identified baseline exists for every acceptance gate.

**Solution reasoning**

- **Approach:** Capture the application response, marker hash and both client paths before the change, each with its source.
- **Why it is correct:** A baseline taken before the change lets every later gate compare like with like.
- **Plausible wrong approach:** Capturing baselines after the change cannot show whether the change altered them.
- **How to verify:** Each baseline names a request, a hash or a client path and predates the change.

## Exercise 3: Review rendered intent

The review catches changes that a single values diff might hide. A host apply still needs scoped identity and field-ownership handling before controller/application checks.

**Expected:** No unexpected kind, namespace, image, hook or security change.

**Solution reasoning**

- **Approach:** Diff the full rendered output against the approved object list across kinds, namespaces, images, hooks and security fields.
- **Why it is correct:** The render is what will be applied, so a review of values alone could miss an added hook or a changed securityContext.
- **Plausible wrong approach:** Reviewing only the values diff assumes the templates turn values into exactly the expected fields.
- **How to verify:** No unexpected kind, namespace, image, hook or security change appears.

## Exercise 4: Inject and diagnose one change failure

A useful negative case demonstrates that the acceptance packet can reject a plausible bad release. Preserve the failed source and observed facts rather than only the eventual repaired result.

**Expected:** The intended gate fails with a discriminating condition/client result and no unrelated mutation.

**Solution reasoning**

- **Approach:** Write the boundary you expect to fail, apply the wrong probe path and compare with the first gate that fails.
- **Why it is correct:** A wrong readiness path keeps the new Pods unready, so the rollout gate should fail while data and policy stay unchanged.
- **Plausible wrong approach:** Applying the fault together with a policy change makes it impossible to tell which caused the failure.
- **How to verify:** The first failing gate matches the prediction, and no unrelated object changed.

## Exercise 5: Recover without rewriting data

Recovery evidence is strongest when the old data is inspected independently. Rewriting a constant marker after failure would make an empty volume look correct and invalidate the persistence claim.

**Expected:** Application recovers, hash remains h1, and allowed/denied paths retain their intended outcomes.

**Solution reasoning**

- **Approach:** Restore the reviewed probe, reread the marker with the reader and repeat both client paths.
- **Why it is correct:** Recovery must restore the application without touching the claim, so the hash stays h1 and policy outcomes repeat the baseline.
- **Plausible wrong approach:** Running the writer during recovery to be safe could change the marker and hide data loss.
- **How to verify:** Hash equals h1, and the allowed and denied paths match the baseline.

## Exercise 6: Hand off retention and cleanup

The packet should let another learner reproduce the failure and recovery while knowing what remains. Retained local data is not an independent backup, and releasing the owned cluster can end that retention boundary.

**Expected:** UID-aware cleanup and explicit data-retention/reclaim boundaries are reviewable.

**Solution reasoning**

- **Approach:** List removed UIDs and, separately, whether the PVC was retained and what reclaim applies.
- **Why it is correct:** Workload cleanup and data retention are separate decisions, and the claim may outlive the StatefulSet by policy.
- **Plausible wrong approach:** Saying everything was cleaned up hides whether the PVC and its bytes still exist.
- **How to verify:** Removed UIDs and the PVC retention decision are recorded separately from cluster release.

## Boundary and troubleshooting review

Application response, stored data, authorization, network enforcement and cleanup have different evidence. A single green summary cannot replace the underlying identities, checksums and client results. The fixture is bounded and synthetic, so it does not establish production database durability, HA or a universal isolation guarantee.

The offline reference checks the packet logic only. The full host capstone remains unavailable on the basic one-shot profile even though several of its individual manifests resemble supported browser sources.
