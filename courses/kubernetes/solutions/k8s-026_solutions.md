# k8s-026: Explanatory solutions

These answers explain the stated synthetic and scoped runtime contracts. Static checks do not prove cluster acceptance.

## Mechanism

A Deployment asks for a replica count; a DaemonSet asks for a Pod on each eligible node under its controller and placement rules. Eligibility depends on selectors, affinity, taints/tolerations and other constraints. A desired DaemonSet count therefore cannot be predicted from cluster node count alone.

The host fixture uses a restricted nonroot server with no host network, privileged mode or host mounts. It selects nodes labeled lesson.ds60sqlpy/zone=a. The normal worker does not create DaemonSets, read arbitrary Node details or patch node labels/taints. The host supplies sanitized node facts and an exclusive qualified placement scope.

The offline calculation models only the explicitly listed label and custom-taint conditions. It is not a full scheduler simulator. Resource capacity, automatic controller tolerations and runtime behavior still require actual cluster evidence.

## Exercise 1: Compare controller intent

A Deployment can place several replicas on one node unless other constraints prevent it. A DaemonSet reconciles toward node eligibility. Neither object name alone proves a particular topology.

**Expected:** Fixed replica count versus topology-derived desired placement.

## Exercise 2: Evaluate node labels

The first filter narrows candidates but does not finish scheduling. Keeping the stages separate helps explain why a matching node may still not receive the Pod.

**Expected:** node-a and node-c pass the label condition; node-b does not.

## Exercise 3: Evaluate the custom taint

The custom taint blocks a new Pod lacking the matching toleration. The model intentionally omits other scheduler behavior and should not be presented as a complete placement predictor.

**Expected:** Only node-a remains eligible in the simplified model.

## Exercise 4: Observe actual placement

Static facts and desired status are not enough to prove a running Pod on each intended node. The live graph should identify controlled Pods and their observed placement without exposing unrelated Node data.

**Expected:** Observed eligible-node and controller evidence agree or a specific condition explains the gap.

## Exercise 5: Reject automatic node edits

Changing a shared node can affect unrelated workloads. The ordinary worker has no such permission. A dedicated host rehearsal needs explicit ownership and restoration evidence.

**Expected:** No learner Node mutation; request the correct owned capability or report unavailable placement.

## Exercise 6: Clean up the right resources

The workload may run on nodes it does not own. Cleanup must follow its resource receipt rather than deleting every node-local Pod or reverting unrelated scheduling policy.

**Expected:** Only the owned DaemonSet/controller children are removed; unrelated agents and node settings preserved.

## Boundary and troubleshooting review

Pending can result from selector mismatch, untolerated taint or insufficient requested resources. A toleration does not grant host access, and a DaemonSet is not inherently privileged. The restricted fixture demonstrates the controller shape without exposing node files or network namespaces.

The static predicate explains supplied facts only. Actual desired/ready counts and node placement must be read from the exclusive host lab. Cleanup targets the recorded DaemonSet UID and its controlled Pods, not node labels or unrelated node-local agents.
