# k8s-028: Explanatory solutions

These answers explain the stated synthetic and scoped runtime contracts. Static checks do not prove cluster acceptance.

## Mechanism

The intermediate capstone combines a stateless application response, a synthetic persistent marker store, reviewed configuration rendering and measured traffic policy. It is a host-lab integration exercise because the normal browser adapter does not provide the storage, CNI and stateful-update capabilities needed for the whole scenario.

The supplied manifests keep the components explicit:configured hello Deployment/Service, one StatefulSet claim template and two ingress policies. The persistent marker is a file-based synthetic datastore, not a real database service. Its writer and reader operations must be separately bounded and reviewed by the host. A correct frontend response is not evidence that the marker survived, and an unchanged marker is not evidence that network isolation works.

The capstone's acceptance packet connects those independent observations and includes a failed-change recovery. Cleanup respects the declared synthetic-data retention choice and exact resource identities. Releasing the disposable cluster is a separate lifecycle boundary that can remove node-local retained data.

## Exercise 1: Inventory capabilities

A complete plan names the missing execution surfaces rather than pretending all Kubernetes objects are interchangeable through the browser adapter. This preserves both authority and evidence quality.

**Expected:** Each capability has a qualified host receipt or is marked unavailable.

## Exercise 2: Establish independent baselines

The baseline makes later differences interpretable. It should include exact resource identities and the data initialization boundary, not only a screenshot of ready Pods.

**Expected:** A source-identified baseline exists for every acceptance gate.

## Exercise 3: Review rendered intent

The review catches changes that a single values diff might hide. A host apply still needs scoped identity and field-ownership handling before controller/application checks.

**Expected:** No unexpected kind, namespace, image, hook or security change.

## Exercise 4: Inject and diagnose one change failure

A useful negative case demonstrates that the acceptance packet can reject a plausible bad release. Preserve the failed source and observed facts rather than only the eventual repaired result.

**Expected:** The intended gate fails with a discriminating condition/client result and no unrelated mutation.

## Exercise 5: Recover without rewriting data

Recovery evidence is strongest when the old data is inspected independently. Rewriting a constant marker after failure would make an empty volume look correct and invalidate the persistence claim.

**Expected:** Application recovers, hash remains h1, and allowed/denied paths retain their intended outcomes.

## Exercise 6: Hand off retention and cleanup

The packet should let another learner reproduce the failure and recovery while knowing what remains. Retained local data is not an independent backup, and releasing the owned cluster can end that retention boundary.

**Expected:** UID-aware cleanup and explicit data-retention/reclaim boundaries are reviewable.

## Boundary and troubleshooting review

Application response, stored data, authorization, network enforcement and cleanup have different evidence. A single green summary cannot replace the underlying identities, checksums and client results. The fixture is bounded and synthetic, so it does not establish production database durability, HA or a universal isolation guarantee.

The offline reference checks the packet logic only. The full host capstone remains unavailable on the basic one-shot profile even though several of its individual manifests resemble supported browser sources.
