# k8s-026: Explanatory solutions

These answers explain the stated synthetic and scoped runtime contracts. Static checks do not prove cluster acceptance.

## Mechanism

A Deployment asks for a replica count; a DaemonSet asks for a Pod on each eligible node under its controller and placement rules. Eligibility depends on selectors, affinity, taints/tolerations and other constraints. A desired DaemonSet count therefore cannot be predicted from cluster node count alone.

The host fixture uses a restricted nonroot server with no host network, privileged mode or host mounts. It selects nodes labeled lesson.ds60sqlpy/zone=a. The normal worker does not create DaemonSets, read arbitrary Node details or patch node labels/taints. The host supplies sanitized node facts and an exclusive qualified placement scope.

The offline calculation models only the explicitly listed label and custom-taint conditions. It is not a full scheduler simulator. Resource capacity, automatic controller tolerations and runtime behavior still require actual cluster evidence.

## Exercise 1: Compare controller intent

A Deployment can place several replicas on one node unless other constraints prevent it. A DaemonSet reconciles toward node eligibility. Neither object name alone proves a particular topology.

**Expected:** Fixed replica count versus topology-derived desired placement.

**Solution reasoning**

- **Approach:** Contrast replicas 2 on the Deployment with the DaemonSet's one Pod per eligible node.
- **Why it is correct:** A Deployment's count is fixed by spec.replicas, while a DaemonSet's desired count follows how many nodes pass its placement rules.
- **Plausible wrong approach:** Expecting the DaemonSet to honor a replicas field misreads its spec, which has none.
- **How to verify:** On three nodes with two eligible, the Deployment yields 2 Pods and the DaemonSet yields 2, for different reasons.

## Exercise 2: Evaluate node labels

The first filter narrows candidates but does not finish scheduling. Keeping the stages separate helps explain why a matching node may still not receive the Pod.

**Expected:** node-a and node-c pass the label condition; node-b does not.

**Solution reasoning**

- **Approach:** Check zone=a against each node's labels one at a time.
- **Why it is correct:** A nodeSelector requires an exact key and value match, so only nodes labeled zone=a pass.
- **Plausible wrong approach:** Treating a node with zone=b as close enough, or one missing the key as a wildcard, admits node-b wrongly.
- **How to verify:** node-a yes, node-b no, node-c yes.

## Exercise 3: Evaluate the custom taint

The custom taint blocks a new Pod lacking the matching toleration. The model intentionally omits other scheduler behavior and should not be presented as a complete placement predictor.

**Expected:** Only node-a remains eligible in the simplified model.

**Solution reasoning**

- **Approach:** For node-a and node-c, compare each node's taints with the Pod's tolerations.
- **Why it is correct:** A NoSchedule taint repels any Pod lacking a matching toleration, so node-c with the dedicated taint drops out.
- **Plausible wrong approach:** Assuming DaemonSets ignore all taints overgeneralizes; their automatic tolerations cover node condition taints, not a custom dedicated taint.
- **How to verify:** Only node-a remains after both checks.

## Exercise 4: Observe actual placement

Static facts and desired status are not enough to prove a running Pod on each intended node. The live graph should identify controlled Pods and their observed placement without exposing unrelated Node data.

**Expected:** Observed eligible-node and controller evidence agree or a specific condition explains the gap.

**Solution reasoning**

- **Approach:** Compare desiredNumberScheduled, numberReady and each Pod's nodeName with your predicted node list.
- **Why it is correct:** The DaemonSet controller computes desired placement itself, so its status and Pod nodeNames show whether reality matches your model.
- **Plausible wrong approach:** Checking only numberReady equals desiredNumberScheduled could pass even if the controller chose nodes you did not predict.
- **How to verify:** Pod nodeNames match the predicted nodes, or a specific condition explains each difference.

## Exercise 5: Reject automatic node edits

Changing a shared node can affect unrelated workloads. The ordinary worker has no such permission. A dedicated host rehearsal needs explicit ownership and restoration evidence.

**Expected:** No learner Node mutation; request the correct owned capability or report unavailable placement.

**Solution reasoning**

- **Approach:** Replace the taint removal with a capability request or an unavailable placement report.
- **Why it is correct:** Node taints are shared cluster configuration, and removing one changes scheduling for every workload, not just this lab.
- **Plausible wrong approach:** Running kubectl taint with a trailing minus to make the Pod land edits a Node the learner does not own.
- **How to verify:** The proposal modifies no Node and names the request or report used instead.

## Exercise 6: Clean up the right resources

The workload may run on nodes it does not own. Cleanup must follow its resource receipt rather than deleting every node-local Pod or reverting unrelated scheduling policy.

**Expected:** Only the owned DaemonSet/controller children are removed; unrelated agents and node settings preserved.

**Solution reasoning**

- **Approach:** Delete the DaemonSet by recorded UID and confirm its child Pods go with it.
- **Why it is correct:** Child Pods carry an ownerReference to the DaemonSet, so garbage collection removes them while node labels and taints stay as they were.
- **Plausible wrong approach:** Deleting Pods by label app could remove another agent's Pods, and the DaemonSet would just recreate its own.
- **How to verify:** Owned UIDs are gone, and node labels and taints match the pre-run record.

## Boundary and troubleshooting review

Pending can result from selector mismatch, untolerated taint or insufficient requested resources. A toleration does not grant host access, and a DaemonSet is not inherently privileged. The restricted fixture demonstrates the controller shape without exposing node files or network namespaces.

The static predicate explains supplied facts only. Actual desired/ready counts and node placement must be read from the exclusive host lab. Cleanup targets the recorded DaemonSet UID and its controlled Pods, not node labels or unrelated node-local agents.
