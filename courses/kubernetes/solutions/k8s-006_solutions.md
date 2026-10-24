# k8s-006: Explanatory solutions

These answers explain the stated synthetic and scoped runtime contracts. Static checks do not prove cluster acceptance.

## Mechanism

A Deployment describes desired application replicas and manages ReplicaSets that in turn manage Pods. A controller repeatedly compares desired and observed state and acts to reduce the difference. This reconciliation loop is why deleting one controlled Pod can lead to a replacement without editing the Deployment manifest.

The objects have distinct identities. The Deployment UID identifies the controller object, the ReplicaSet UID identifies a particular template revision's replica controller, and each Pod has its own UID. Counting two Pods without tracing ownership can accidentally include an unrelated workload. A replacement Pod can reuse a similar generated name but must have a new UID.

The browser source can establish a fresh two-replica baseline and clean it up. The deliberate Pod-deletion experiment needs a separate stateful owned host operation because the one-shot browser Run does not leave a workload behind for arbitrary later mutation. The normal worker identity does not gain Pod-delete permission from this lesson.

## Exercise 1: Draw ownership

Labels select sets but do not prove controller ownership. The graph distinguishes the application replicas from unrelated Pods that happen to share a label. Each link should come from actual readback in a live exercise or be labeled synthetic here.

**Expected:** A UID-linked graph connects exactly two owned Pods to the intended Deployment.

## Exercise 2: Compare generation evidence

The controller can report a healthy prior state while a new spec is waiting to reconcile. A verifier should require the relevant generation relationship and updated counts before claiming the current change succeeded.

**Expected:** Latest desired state not yet confirmed observed.

## Exercise 3: Establish a fresh baseline

The browser creates a new bounded baseline and then cleans it. Its receipt supports the checks it performed. The human explanation must not replace actual server-assigned UIDs with the fixture's illustrative identifiers.

**Expected:** Two Ready owned Pod UIDs and cleanup evidence, with a new Run identity.

## Exercise 4: Rehearse scoped Pod replacement

The replacement is caused by the ReplicaSet restoring desired replicas. It is not a new Deployment or necessarily a new template revision. The operation must use UID-aware targeting and preserve unrelated objects.

**Expected:** Pod set changes from{pod-1, pod-2} to{pod-2, pod-3} in the synthetic trace; live names/UIDs are recorded separately.

## Exercise 5: Reject a count-only shortcut

An unrelated Pod cannot satisfy this Deployment's desired replica contract. This negative case demonstrates why counting labels or phase values without ownership can produce a false success.

**Expected:** Raw count 2 but owned Ready count 1, so acceptance fails.

## Exercise 6: Separate recovery from availability

The control loop may restore the final desired count after a period of reduced capacity. A client trace can establish observed continuity for its sampled requests, while a final Pod snapshot cannot. Finite samples still do not prove a universal SLA.

**Expected:** A bounded client timeline and error counts are required beyond final Ready replicas.

## Boundary and troubleshooting review

Two Running Pods can both be unready, and a matching label can belong to a different controller. A stale status count can describe an older generation. Inspect ownerReferences and UIDs before interpreting counts, and preserve a negative fixture with a foreign Pod UID so a count-only checker is visibly inadequate.

A one-shot Run's final cleanup is separate from the deliberate replacement exercise. Do not claim that a Pod observed in a later Run is the replacement of a Pod from an already cleaned-up earlier Run; the Deployment itself may also be a new object.
