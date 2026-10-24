# k8s-013: Explanatory solutions

These answers explain the stated synthetic and scoped runtime contracts. Static checks do not prove cluster acceptance.

## Mechanism

A rollout changes a Deployment's Pod template and reconciles toward a new ReplicaSet revision. The Deployment object can retain its UID while old and new Pods coexist. A readiness failure in the candidate revision may leave old Ready backends serving traffic, so a successful request alone does not prove that the new version completed.

The stateful rollout is a host-lab contract. The browser creates and cleans a fresh workload each Run; it does not patch an existing Deployment across Runs. The provided JSON illustrates a synthetic configuration revision using the already approved fixture image and a changed message marker. It is not evidence of an image upgrade. A two-image release experiment additionally requires two separately preloaded, qualified image identities from the host receipt.

Treat the desired manifest as the durable release intent. A rollback should restore a reviewed desired state and then verify generation, updated/ready counts and application identity. Merely seeing some ready traffic can conceal that the cluster is still serving the prior revision.

## Exercise 1: Identify a template change

A template change drives a new ReplicaSet. The synthetic marker is configuration evidence, not a new image identity. The host operation must preserve the same Deployment instance to demonstrate a rollout rather than two independent creates.

**Expected:** Pod-template content changes while Deployment name/UID can remain fixed in a stateful lab.

## Exercise 2: Interpret mixed replicas

Counts can mix old and new revisions. An independent client can still reach old Pods while the desired candidate is failing readiness. Acceptance must name the intended version and its owned Ready population.

**Expected:** Candidate B incomplete despite aggregate ready traffic.

## Exercise 3: Define a failure gate

The gate prevents indefinite waiting and avoids treating a partial rollout as success. It should preserve diagnostic evidence before recovery and remain within the lease and cleanup budget.

**Expected:** Generation observed, desired updated/ready candidate counts and expected application marker are required.

## Exercise 4: Recover the desired source

Recovery is another controlled change. The report should say whether it reverted or fixed the candidate, and show the new observation rather than only the command used to request it.

**Expected:** A new generation converges to the selected intent; source and observed marker agree.

## Exercise 5: Plan a genuine image-version rehearsal

The host must provide both exact artifacts before the live rehearsal. The learner should not substitute an arbitrary registry tag or infer provenance from a version string. Keep this acceptance row unavailable if those artifacts are absent.

**Expected:** Two qualified preloaded image digests, compatible manifests and an application-version response check.

## Exercise 6: Separate final state from availability

A bounded client trace can show what its sampled requests experienced. It complements the controller proof and can reveal old-version traffic during a stalled rollout. It does not establish behavior for all clients or an entire production load profile.

**Expected:** Observed version/error samples over the transition, with no universal uptime or exact-ratio claim.

## Boundary and troubleshooting review

The single approved image can expose hello/reviewer as synthetic message markers, but that is a configuration revision rather than a different binary image. A two-image rollout needs its own provenance and preload receipt. Likewise, a few successful requests do not establish exact traffic percentages or uninterrupted availability.

Do not describe two cleaned-up browser Runs as one live rollout. The host worksheet must show the same Deployment UID across the state transition and the intended candidate identity in the final response.
