# k8s-049: explanatory solutions

Attempt each exercise first, then compare ([study guide](../STUDY-GUIDE.md#solutions-and-the-ai-tutor)).

## Mechanism review

EndpointSlices describe sets of network endpoints associated with a Service. They include addresses, ports and condition information, and can reference the Pod supplying an endpoint. The controller uses them to scale endpoint management beyond one monolithic object. A Service can have several slices, so reading only the first is incomplete.

Readiness influences whether a Pod should receive ordinary new Service traffic under the relevant routing behavior. Running is a process phase and does not imply Ready. Endpoint conditions ready, serving and terminating describe related but distinct lifecycle facts. Under the API contract, an omitted ready or serving condition is interpreted as true, and omitted terminating as false. For Pod-backed endpoints, serving follows the Pod Ready condition. Ordinary ready generally expresses serving and not terminating, with documented overrides.

Identity matters during replacement. A new Pod can reuse a familiar name pattern but has a new UID. To prove traffic eligibility belongs to the intended revision, join endpoint target references to current Pod UIDs and inspect actual application behavior. A stale IP list from an earlier run is insufficient.

The following table distinguishes common condition states. It is a contract-reading exercise, not a fabricated runtime result.

| Endpoint state | serving | terminating | ordinary ready |
| --- | --- | --- | --- |
| Serving normally | true | false | true |
| App not ready | false | false | false |
| Still serving while terminating | true | true | false |
| All three conditions omitted | interpreted true | interpreted false | interpreted true |

For publishNotReadyAddresses, ready can be forced true even when ordinary application readiness is false. A proxy may use serving terminating endpoints for draining/fallback when all available endpoints are terminating. These exceptions mean ready alone is not a universal application-health oracle. The ordinary synthetic fixture uses explicit true/false readiness and no publishNotReadyAddresses override.

Select slices by the standard service-name label and aggregate all returned endpoints of the relevant address family and port. Match targetRef.uid where supplied, rather than assuming an address uniquely identifies the expected Pod forever. Preserve slice ownership and resource versions in a diagnostic record.

The fixture includes two endpoint observations, one ready and one not ready. The offline checker classifies them, but actual routing remains an owned runtime observation. Do not manually mark a controller-owned endpoint ready to bypass an app readiness failure.

## Exercise 1: Predict the ready endpoint set.

Filter on the stated condition and retain identity. Counting all addresses would overstate eligible capacity.

**Expected:** Only the endpoint referencing pod-a.

**Solution reasoning**

- **Approach:** Read each endpoint's conditions.ready field in the slice and keep only those marked true.
- **Why it is correct:** Only ready endpoints receive new connections, and in the fixture only the endpoint referencing pod-a is ready.
- **Plausible wrong approach:** Counting every endpoint listed in the slice would include backends that are not eligible for traffic.
- **How to verify:** The ready set contains exactly the endpoint referencing pod-a.

## Exercise 2: Aggregate endpoints across two slices.

Large Services can be split across slices. A first-item assumption loses backends.

**Expected:** The result includes every relevant slice without duplicate identities.

**Solution reasoning**

- **Approach:** Select every EndpointSlice carrying the Service's kubernetes.io/service-name label and merge their endpoints.
- **Why it is correct:** A Service can be split across several slices, so reading only one gives a partial backend set.
- **Plausible wrong approach:** Reading the first slice returned, or concatenating without deduplicating by target reference, gives a wrong count.
- **How to verify:** The merged list covers all relevant slices with no repeated Pod identity.

## Exercise 3: Join eligible endpoint references to current Pod UIDs.

The UID relation is stronger than a familiar name or IP. It supports replacement and revision reasoning.

**Expected:** Every accepted backend belongs to the intended current workload.

**Solution reasoning**

- **Approach:** Match each eligible endpoint's targetRef UID against the UIDs of the current Pods.
- **Why it is correct:** A Pod name can be reused by a replacement, while the UID identifies the exact object the endpoint points to.
- **Plausible wrong approach:** Joining on Pod name alone could accept a stale reference to a deleted Pod with the same name.
- **How to verify:** Every accepted backend UID belongs to a current Pod of the intended workload.

## Exercise 4: Diagnose Running but no ready endpoints.

The process exists, but eligibility has not been established. Recreating the Service is not automatically the right repair.

**Expected:** Inspect readiness and selector/controller observations.

**Solution reasoning**

- **Approach:** Check the Pod's Ready condition and readiness probe, then compare its labels with the Service selector.
- **Why it is correct:** Running only means containers started; a failing readiness probe or a selector mismatch keeps the Pod out of ready endpoints.
- **Plausible wrong approach:** Restarting the Pod because it is Running but unused repeats startup without finding the failing check.
- **How to verify:** The diagnosis names the readiness result and the selector match status.

## Exercise 5: Explain terminating and serving conditions carefully.

Traffic handling can depend on policy and implementation. State the exact condition and observed route rather than flattening all lifecycle states.

**Expected:** They inform draining behavior and are not identical Boolean synonyms.

**Solution reasoning**

- **Approach:** Describe terminating as the Pod being deleted and serving as whether it still passes readiness.
- **Why it is correct:** During graceful shutdown an endpoint can be terminating yet still serving, which lets proxies drain existing traffic.
- **Plausible wrong approach:** Treating terminating as a synonym for not ready would discard a backend that can still finish in-flight work.
- **How to verify:** The answer keeps the two conditions separate and ties them to draining.

## Exercise 6: Prove a replacement backend is actually used.

Control-plane readiness is necessary evidence but does not alone prove the client reached that backend.

**Expected:** New UID eligibility plus a fresh source-bound application response.

**Solution reasoning**

- **Approach:** Confirm the new Pod's UID is an eligible endpoint, then send a fresh request that reports its serving identity.
- **Why it is correct:** Endpoint eligibility shows the proxy may choose the Pod, and a response bound to its identity shows it actually did.
- **Plausible wrong approach:** A successful response alone could come from an older backend that is still eligible.
- **How to verify:** The record pairs the new UID in the ready set with a fresh response from that UID.
