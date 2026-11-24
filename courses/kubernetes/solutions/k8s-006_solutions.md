# k8s-006: Explanatory solutions

These answers explain the stated synthetic and scoped runtime contracts. Static checks do not prove cluster acceptance.

## Mechanism

A Deployment describes desired application replicas and manages ReplicaSets that in turn manage Pods. A controller repeatedly compares desired and observed state and acts to reduce the difference. This reconciliation loop is why deleting one controlled Pod can lead to a replacement without editing the Deployment manifest.

The objects have distinct identities. The Deployment UID identifies the controller object, the ReplicaSet UID identifies a particular template revision's replica controller, and each Pod has its own UID. Counting two Pods without tracing ownership can accidentally include an unrelated workload. A replacement Pod can reuse a similar generated name but must have a new UID.

The browser source can establish a fresh two-replica baseline and clean it up. The deliberate Pod-deletion experiment needs a separate stateful owned host operation because the one-shot browser Run does not leave a workload behind for arbitrary later mutation. The normal worker identity does not gain Pod-delete permission from this lesson.

## Exercise 1: Draw ownership

Labels select sets but do not prove controller ownership. The graph distinguishes the application replicas from unrelated Pods that happen to share a label. Each link should come from actual readback in a live exercise or be labeled synthetic here.

**Expected:** A UID-linked graph connects exactly two owned Pods to the intended Deployment.

**Solution reasoning**

- **Approach:** Walk ownerReferences upward from each Pod to its ReplicaSet and from that ReplicaSet to the Deployment, recording UIDs at each hop.
- **Why it is correct:** The `controller: true` reference is set by the ReplicaSet controller itself, so a UID chain proves ownership in a way a shared app label cannot.
- **Plausible wrong approach:** Drawing the graph from `app=hello` labels would include any unrelated Pod carrying that label and overstate the replica set.
- **How to verify:** Exactly two Pods link through one ReplicaSet UID to the intended Deployment UID, and every arrow cites the UID it follows.

## Exercise 2: Compare generation evidence

The controller can report a healthy prior state while a new spec is waiting to reconcile. A verifier should require the relevant generation relationship and updated counts before claiming the current change succeeded.

**Expected:** Latest desired state not yet confirmed observed.

**Solution reasoning**

- **Approach:** Compare metadata.generation 4 with status.observedGeneration 3 before reading readyReplicas.
- **Why it is correct:** The API server bumps generation on every spec change, and the Deployment controller copies it to observedGeneration only after processing, so 3 means spec 4 is unprocessed.
- **Plausible wrong approach:** Accepting readyReplicas 2 as success reports the health of the generation 3 template, which may differ from the spec you just applied.
- **How to verify:** The conclusion cites observedGeneration below generation and states the latest desired state is not yet observed.

## Exercise 3: Establish a fresh baseline

The browser creates a new bounded baseline and then cleans it. Its receipt supports the checks it performed. The human explanation must not replace actual server-assigned UIDs with the fixture's illustrative identifiers.

**Expected:** Two Ready owned Pod UIDs and cleanup evidence, with a new Run identity.

**Solution reasoning**

- **Approach:** Edit only spec.replicas from 1 to 2, then Run and read the result as a new baseline rather than a change to an old one.
- **Why it is correct:** The ReplicaSet controller creates one additional Pod to meet the count of 2, and the browser operation records its own Run identity and cleanup.
- **Plausible wrong approach:** Reusing the fixture's illustrative Pod names as evidence would make the result look valid without any server-assigned UID behind it.
- **How to verify:** The result lists two distinct Ready Pod UIDs and a cleanup entry carrying this Run's identity.

## Exercise 4: Rehearse scoped Pod replacement

The replacement is caused by the ReplicaSet restoring desired replicas. It is not a new Deployment or necessarily a new template revision. The operation must use UID-aware targeting and preserve unrelated objects.

**Expected:** Pod set changes from {pod-1, pod-2} to {pod-2, pod-3} in the synthetic trace; live names/UIDs are recorded separately.

**Solution reasoning**

- **Approach:** Delete exactly one recorded Pod by UID precondition, then wait a bounded time for the ReplicaSet to restore the count.
- **Why it is correct:** The ReplicaSet still wants two replicas, so it creates a new Pod from the unchanged template while the Deployment generation stays the same.
- **Plausible wrong approach:** Deleting by label selector could remove both Pods or an unrelated one, and rolling the Deployment would wrongly create a new ReplicaSet revision.
- **How to verify:** The packet shows the Deployment UID and generation unchanged, one Pod UID removed and one new UID added.

## Exercise 5: Reject a count-only shortcut

An unrelated Pod cannot satisfy this Deployment's desired replica contract. This negative case demonstrates why counting labels or phase values without ownership can produce a false success.

**Expected:** Raw count 2 but owned Ready count 1, so acceptance fails.

**Solution reasoning**

- **Approach:** Filter the list to Pods whose controller ownerReference resolves to the intended ReplicaSet UID, then count Ready ones.
- **Why it is correct:** The foreign Pod belongs to a different controller, so it cannot satisfy this ReplicaSet's replica contract even though its labels and phase match.
- **Plausible wrong approach:** Counting `app=hello` Pods in phase Running returns 2 and passes a broken Deployment that actually has only one owned replica.
- **How to verify:** Owned Ready count is 1 against a raw list length of 2, so acceptance fails.

## Exercise 6: Separate recovery from availability

The control loop may restore the final desired count after a period of reduced capacity. A client trace can establish observed continuity for its sampled requests, while a final Pod snapshot cannot. Finite samples still do not prove a universal SLA.

**Expected:** A bounded client timeline and error counts are required beyond final Ready replicas.

**Solution reasoning**

- **Approach:** Separate the final status snapshot from a time series of client requests sampled during the replacement window.
- **Why it is correct:** The Deployment status reports only the end state, while capacity was reduced between deletion and the new Pod becoming Ready.
- **Plausible wrong approach:** Citing readyReplicas 2 afterward as proof that no request failed assumes continuity the status field never measured.
- **How to verify:** Name the client timeline with timestamps, outcomes and error counts as the measurement no Deployment status field can provide.

## Boundary and troubleshooting review

Two Running Pods can both be unready, and a matching label can belong to a different controller. A stale status count can describe an older generation. Inspect ownerReferences and UIDs before interpreting counts, and preserve a negative fixture with a foreign Pod UID so a count-only checker is visibly inadequate.

A one-shot Run's final cleanup is separate from the deliberate replacement exercise. Do not claim that a Pod observed in a later Run is the replacement of a Pod from an already cleaned-up earlier Run; the Deployment itself may also be a new object.
