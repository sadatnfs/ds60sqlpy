"""Lesson-specific teaching notes for k8s-004..042.

Shared launcher, live-read and tutor guidance lives in courses/kubernetes/STUDY-GUIDE.md
and host-labs.md; these notes carry only what differs per lesson.

run: what the host operation observes that the worksheet or browser Run cannot.
inspect: which fields of the owned object answer this lesson's prediction.
selfcheck, retrieval: lesson-specific questions.
"""

NOTES = {
    4: dict(
        run="A provisioned lab can ask the API server whether the leased identity may get Deployment hello. The Role text alone cannot answer that, because another binding in the same namespace may add permissions.",
        inspect="Compare `metadata.namespace` and `metadata.uid` with your receipt before trusting any `kubectl auth can-i` answer: a matching name with a new UID is the same-name replacement from Worked example 2. Forbidden on this get means the narrow Role grant is missing or bound elsewhere, which Exercise 4 records as an observed deny.",
        selfcheck="Why does a RoleBinding that references a ClusterRole still deny Pods in lesson-b, and what extra evidence would you need before saying the leased identity cannot list Deployments anywhere in lesson-a?",
        retrieval="Without the solution, rebuild the six-field request tuple for get on apps/deployments hello. Then explain how a second RoleBinding in the same namespace could widen the effective answer even though this Role grants only get.",
    ),
    5: dict(
        run="The Run reports whether the starter's /missing path keeps Ready False within its bound, then whether the restored /ready path passes. It cannot capture a kubelet ErrImageNeverPull, restart counts or log lines tied to one container instance.",
        inspect="For each Pod, read `status.phase`, the Ready condition, `status.containerStatuses[0].restartCount` and `metadata.uid`. Running with Ready False matches the Exercise 2 starter. A higher restartCount on the same UID is a restart; a new UID is a replacement Pod.",
        selfcheck="A Pod reports phase Running, Ready False and restartCount 0. Which of this lesson's failures (wrong readiness path, missing image, crashing process) remain possible, and which field would separate them?",
        retrieval="From memory, list the evidence that separates a container restart from a Pod replacement. Then state what the Deployment-only Run in Exercise 6 cannot prove about a client reaching the application through a Service.",
    ),
    6: dict(
        run="The Run counts owned Ready Pods for the one-replica starter or your two-replica edit, then cleans them. Deleting one Pod and watching the ReplicaSet create its successor is stateful, so the Exercise 4 replacement trace belongs to the host lab.",
        inspect="Compare `metadata.generation` with `status.observedGeneration`, then read `status.replicas`, `status.readyReplicas` and `status.updatedReplicas`. Two ready replicas while observedGeneration lags generation is the unconverged case from Worked example 1.",
        selfcheck="A namespace shows two Ready Pods labeled app=hello, but only one has an ownerReference chain to Deployment dep-a. Explain why Exercise 5 rejects this as two replicas and which graph proves it.",
        retrieval="Redraw the before and after Pod sets for the scoped replacement, {pod-1, pod-2} to {pod-2, pod-3}, and say which identity stays constant. Then describe the client timeline Exercise 6 requires beyond final Ready counts.",
    ),
    7: dict(
        run="That negative Run should time out with no ready backends and still clean up; after the restore, the client reaches the fixture through the Service. Comparing EndpointSlices across address families is a host read.",
        inspect="Read `spec.selector`, `spec.ports[0].port` and `spec.ports[0].targetPort`. targetPort should be the name http, which resolves to container port 8080 only through the Pod template. A selector of app=wrong fully explains an empty backend set.",
        selfcheck="EndpointSlices for hello list four entries across IPv4 and IPv6. How do you reduce them to a backend count, and why must that count equal the owned Ready Pod UID set rather than every Pod with matching labels?",
        retrieval="Trace the port chain from client 8080 through targetPort http to the container without notes. Then outline the second-Service transfer from Exercise 6: its selector, port, backend, client and cleanup checks.",
    ),
    9: dict(
        run="The Run checks /version, /message and /file-message once against fresh processes. Updating hello-config afterward and watching the environment stay hello while the mounted file changes is stateful, so Exercises 3 and 4 need the host lab.",
        inspect="Read `data.message` and `metadata.resourceVersion`, then compare them with what /message and /file-message return. A new resourceVersion proves the API object moved; it does not prove the projected file or the running environment changed.",
        selfcheck="After editing hello-config to reviewer, /file-message returns reviewer but /message still returns hello. Which update stage has happened, which has not, and what single action makes both routes agree?",
        retrieval="Recall which consumer reads the key at process start and which reads a projected file. Then list the release record fields from Exercise 6, including the restored source you would need for a rollback.",
    ),
    10: dict(
        run="The Run confirms that requests of 10m and 16Mi under limits of 100m and 64Mi are admitted and become Ready. A quota rejection, an unschedulable request and an OOMKilled container are separate host fixtures because each needs its own cluster condition.",
        inspect="Read `spec.template.spec.containers[0].resources` and compare requests and limits with your edit. Two replicas at 10m and 16Mi should total 20m and 32Mi of requested budget. A quota denial appears as a ReplicaSet FailedCreate event, not on this object.",
        selfcheck="A container exits with code 137. Why does that alone not prove a memory limit was hit, which field would, and how would the same workload look if the real problem were quota or placement?",
        retrieval="Without looking, convert 64Mi to bytes and total the two-replica request budget. Then describe the one justified resource change and the phase-specific success evidence Exercise 6 asks you to plan.",
    ),
    11: dict(
        run="The Run waits for hello-task to reach Complete and checks the accepted 3, rejected 2, total 35 output, or records Failed for the injected case. The suspended five-minute CronJob is provisioned separately because a one-shot Run cannot wait for a schedule.",
        inspect="Read `spec.backoffLimit`, `spec.activeDeadlineSeconds`, `status.succeeded`, `status.failed` and the Complete or Failed entry in `status.conditions`. A Failed condition with reason DeadlineExceeded points at the 20-second budget rather than the task code.",
        selfcheck="Why does restartPolicy Never not forbid a replacement Pod attempt, and what exactly does backoffLimit bound? How would you tell from the Job whether the task or the deadline failed?",
        retrieval="Recall the five finite-work controls and their edited values. Then sketch the idempotent handoff from Exercise 6: the logical-work key, commit boundary and replay policy that stop a retried task from double counting.",
    ),
    12: dict(
        run="On a provisioned host, each selected negative Run produces the real Ready False condition, missing-key event or exit 2 that the incident records only describe, so you can test whether your diagnosis survives live evidence.",
        inspect="For case A, a waiting reason of CreateContainerConfigError marks the missing ConfigMap key. For case B, a Running container with Ready False marks the probe path. Case C's exit 2 lives on the Job Pod, which this app=hello selector does not return.",
        selfcheck="A teammate proposes raising the probe timeout to fix case B. Why does the evidence not support that edit, which path change does, and what new observations must follow before the incident is closed?",
        retrieval="Rebuild the Exercise 5 timeline for one case, citing the field or log line behind each claim. Then name the recorded owned UIDs that cleanup may remove and the objects it must leave alone.",
    ),
    13: dict(
        run="A host lab can hold the Deployment across two template changes and record mixed old and new ReplicaSets with their markers. The image-version rehearsal also needs two qualified preloaded digests that the normal worker does not have.",
        inspect="Read `metadata.generation`, `status.observedGeneration`, `status.updatedReplicas` and `status.readyReplicas`, then the template marker. Generation observed with two old ready Pods and an incomplete candidate is Worked example 1; a rollback raises generation again.",
        selfcheck="After rollback to marker A, generation went from 5 to 6. Why is that a new reconciliation rather than a return to the old state, and which identities do you expect to be fresh?",
        retrieval="Without notes, write the Exercise 3 failure gate: generation observed, candidate counts and the application marker. Then explain why the transition needs version and error samples over time rather than one final snapshot.",
    ),
    14: dict(
        run="The Run assembles the Deployment, Service and both configuration consumers, then checks controller ownership, backend UID agreement and exact version and message values in one bounded pass. A fault Run and its repair are two separate Runs.",
        inspect="Extract `endpoints[].targetRef.uid` and `endpoints[].conditions.ready` from the hello slices. That set should equal the two owned Ready Pod UIDs. An empty slice with Ready Pods points at the selector; a foreign UID breaks the ownership claim.",
        selfcheck="Your capstone Run created every object and both Pods reached Running, but /file-message returned hello. Which declared check failed, and why does object creation not satisfy the routing and application contract?",
        retrieval="Reconstruct the Exercise 6 handoff from memory: source, nonsecret target identity, then controller, backend, client, failure and cleanup evidence, plus the surfaces you would mark as unqualified.",
    ),
    15: dict(
        run="The Run applies the 3-second startup delay and waits for Ready and a client response. Breaking readiness or liveness on a running Pod and watching restartCount climb needs the host lab, since a one-shot Run cleans up first.",
        inspect="Read the container's `startupProbe`, `readinessProbe` and `livenessProbe`, then `status.containerStatuses[0].restartCount` and the Ready condition. A liveness failure raises restartCount on the same Pod UID; a readiness failure leaves it alone and drops the endpoint.",
        selfcheck="A readiness path returns 404 for ten minutes. Will kubelet restart the container? Which probe would, what does the startup probe protect during the first seconds, and how does each failure show in EndpointSlices?",
        retrieval="Recall the question each of the startup, readiness and liveness probes answers. Then design the Exercise 6 policy so a deadlock restarts the process while a slow dependency only removes traffic.",
    ),
    16: dict(
        run="A host lab can run init-demo, force one application failure and show the marker in /work surviving that container restart, then delete the Pod and show a fresh volume. Reading cannot demonstrate either lifetime.",
        inspect="Read `status.initContainerStatuses[0].state`, `status.containerStatuses[0].restartCount` and `metadata.uid`. A completed prepare container with restartCount 1 and an unchanged UID matches Exercise 3; a waiting init container explains why read never started.",
        selfcheck="The read container restarted once and still found the marker, but after the Pod was deleted the marker was gone. Explain both outcomes from the emptyDir lifetime and name the storage contract that would keep it.",
        retrieval="Draw the prepare then read order and the shared /work volume from memory. Then explain the smallest repair for an init failure caused by a mount path or permission problem.",
    ),
    17: dict(
        run="The Run accepts only the fixed restricted baseline, so it never reaches Pod Security Admission with privileged: true or hostPath. Those server denials, with the namespace policy version and reason, are host observations.",
        inspect="Read the Pod-level and container `securityContext`: runAsNonRoot, runAsUser 65532, RuntimeDefault seccomp, allowPrivilegeEscalation false, readOnlyRootFilesystem and dropped capabilities. An admission denial would surface as a ReplicaSet FailedCreate event instead.",
        selfcheck="Two attempts to add hostNetwork were refused, one by the course parser and one with a pod-security message from the API server. Why is only the second admission evidence, and what does it reveal about the namespace label?",
        retrieval="Map each security field in the baseline to the mechanism it controls without notes. Then write the Exercise 6 threat statement separating API access control from network and application authorization.",
    ),
    18: dict(
        run="With an owned lease, `kubectl auth can-i --as` for the lesson ServiceAccount answers the allowed and denied matrix against the live binding, which the worksheet can predict but not confirm.",
        inspect="Read `roleRef` and `subjects` on lesson-pod-reader. The subject should be the lesson ServiceAccount in the owned namespace and roleRef the narrow Pod reader Role. Even a ClusterRole reference grants only inside this namespace through a RoleBinding.",
        selfcheck="Why does automountServiceAccountToken: false matter when the ServiceAccount can only read Pods, and what does it leave unprotected given the application's own network and authentication paths?",
        retrieval="From memory, list which requests the ServiceAccount may make and which are denied. Then describe the Exercise 5 expiry handling: what the guard refuses and when a fresh session is prepared.",
    ),
    19: dict(
        run="The teacher-owned secret observer is the only path that mounts synthetic-message; the normal worker is denied by design. Its receipts show environment and file stages and both Pod identities without exporting the decoded value.",
        inspect="This read prints only `metadata.uid`, so no data bytes reach your terminal. Forbidden from the normal worker is the expected Exercise 3 denial, not a reason to widen access. The UID ties the observer receipt to the exact synthetic object.",
        selfcheck="The observer reports environment A while the projected file shows B. Why, what would make the application use B, and why does the receipt never need the decoded bytes to prove it?",
        retrieval="Recall the five security controls around the dummy Secret. Then describe the Exercise 5 evidence that proves synthetic equality and reload behavior without collecting any real value.",
    ),
    20: dict(
        run="The Run resolves hello through cluster DNS, reaches the backend and checks the exact /version payload in one bounded path. NXDOMAIN, refused connections and 404 versus wrong-payload probes run on the host with a finite client.",
        inspect="Read `spec.selector`, `spec.ports` and `spec.clusterIP`. A missing Service makes the client name fail as NXDOMAIN; a wrong port gives a transport failure; a 404 means routing worked but the path did not match.",
        selfcheck="A client got HTTP 200 from hello, but the body was not ds60-fixture-v1. Why is this neither a DNS failure nor version verification, and which layer would you inspect first?",
        retrieval="Name the layers from memory (name resolution, transport, HTTP routing, application payload) with one failure each. Then outline the Exercise 6 host transfer with its target, client, timeout and cleanup.",
    ),
    21: dict(
        run="Only an exclusive lease with a policy-capable CNI can show the allowed and denied client paths changing when the policy lands. On a CNI without enforcement the same objects exist and nothing changes, which a worksheet cannot detect.",
        inspect="Read `spec.podSelector`, `spec.policyTypes` and `spec.ingress[].from`. Expect app=hello, Ingress only, and one peer combining podSelector and namespaceSelector. Two separate from entries would admit either peer instead of requiring both.",
        selfcheck="A default-deny policy and an allow policy both select app=hello. Why does the allowed client still connect, and why does proving it need paired client results before and after the policy?",
        retrieval="From memory, explain conjunction versus alternatives in peer selectors. Then list the Exercise 6 limits and cleanup: which owned policies are removed and which protocols or hosts remain unclaimed.",
    ),
    22: dict(
        run="The storage lease binds the lesson class, writes the marker once, replaces only the store Pod and reads the hash back. Binding, attachment and data survival are observations no worksheet can supply.",
        inspect="Read `status.phase`, `spec.volumeName`, `spec.storageClassName` and `spec.resources.requests.storage` on data-store-0. Bound with the same volumeName after Pod replacement supports Exercise 3; Pending points at the missing class or binding condition from Exercise 6.",
        selfcheck="The marker hash survived Pod replacement. Why does that not show the data would survive deleting the claim, and how do the reclaim policy and StatefulSet retention policy each change the answer?",
        retrieval="Recall the storage chain from claim template to mount path. Then explain why the writer opens the marker with mode xb and what a second writer failure proves.",
    ),
    23: dict(
        run="A host-provisioned Gateway controller is needed to see Accepted and ResolvedRefs on hello-route and to send matching and unmatched requests through the loopback TLS listener.",
        inspect="Read `spec.parentRefs`, `spec.hostnames`, `spec.rules` and `status.parents[].conditions`. Accepted and ResolvedRefs true for lesson-gateway show configuration acceptance; a missing hello backend turns ResolvedRefs false, and delivery still needs a request.",
        selfcheck="hello-route shows Accepted and ResolvedRefs true, yet requests to lesson.example.test return 503. Which layer is failing, and why do route conditions not prove the backend can serve?",
        retrieval="From memory, write the declared contract: hostname, path, gateway, backend and port. Then explain how you verify TLS against a wrong hostname without any insecure bypass flag.",
    ),
    24: dict(
        run="The prepared kustomize binary renders both overlays offline. A host lab is needed only for the server-side apply conflict, where two field managers claim spec.replicas on a live Deployment.",
        inspect="Read `metadata.managedFields` and `spec.replicas`. The manager and operation on the replicas entry show who owns the field; a conflict names the other manager, and resolving it means coordinating intent rather than forcing.",
        selfcheck="The dev and test renders differ in two fields instead of one. What does that say about the overlays, and why must you fix it before apply rather than on the cluster?",
        retrieval="Recall which file holds the base and what each overlay overrides. Then explain why an overlay that adds an unrelated namespace or an unapproved image fails the ownership review before apply.",
    ),
    25: dict(
        run="Rendering the vendored chart with the prepared helm template is offline and installs nothing. The normal worker never creates a release, so hooks, release Secrets and upgrades stay outside this lesson.",
        inspect="Compare `spec.replicas` and the container image on the live Deployment with your rendered output. A live object does not mean a Helm release exists, because this course never runs helm install.",
        selfcheck="Suppose the rendered output contains a Job annotated `helm.sh/hook: pre-install`. Why did rendering not run it, why does the course reject it anyway, and which part of the chart inventory should have caught it?",
        retrieval="From memory, inventory what the vendored chart contains and lacks. Then describe how a reviewer reproduces your render and identifies the exact owned runtime boundary.",
    ),
    26: dict(
        run="Only an exclusive multi-node fixture with sanitized node labels and the custom taint can show where node-fixture actually schedules; the worksheet evaluates the same predicate on synthetic nodes.",
        inspect="Read `status.desiredNumberScheduled`, `status.numberReady` and the template's `nodeSelector` and `tolerations`. desiredNumberScheduled should equal the eligible count from Exercise 3; a gap points at a taint, label or resource condition.",
        selfcheck="Adding a toleration for the custom taint changed the eligible count from one to two. Why, and why is the fix for zero eligible nodes never to relabel or untaint nodes yourself?",
        retrieval="Evaluate node-a, node-b and node-c against the zone label and taint from memory. Then explain what the Exercise 6 cleanup removes and what it must preserve.",
    ),
    27: dict(
        run="A qualified metrics path can supply namespace usage and request counters for the bounded ledger. Without it the capability is reported as unavailable, never as zero use.",
        inspect="Read each Pod's `metadata.uid` and `status.containerStatuses[].restartCount` alongside your ledger window. A counter drop between samples plus a restart in that window explains the Exercise 4 reset without inventing negative traffic.",
        selfcheck="For the five-request sample, recompute the error fraction and the nearest-rank p50 and p95. Why is status-only success narrower than checking each payload?",
        retrieval="Define the SLI numerator and denominator from memory. Then describe the Exercise 6 incident observation with its units, window, UIDs and one reversible diagnostic.",
    ),
    28: dict(
        run="The exclusive integration lease combines storage, network policy and a stateful change, so baselines, the injected failure and recovery are recorded against one owned set. Each gate still needs its own host receipt.",
        inspect="Read `status.readyReplicas`, `status.currentRevision` and `status.updateRevision` on store. A revision gap after the injected change shows an incomplete rollout; recovery passes only when the independent reader still reports hash h1.",
        selfcheck="A recovery plan reruns the marker writer to confirm storage works. Why does that destroy the persistence evidence, and which existing fixture should verify the data instead?",
        retrieval="From memory, list the acceptance gates in the integration packet. Then describe recovering from the injected failure without rewriting data, and which allowed and denied paths must still hold.",
    ),
    29: dict(
        run="Registering the LessonReport CRD is a host step. The learner lease then creates and deletes hello-report in its namespace and observes real schema rejections or pruning, which the offline checks only predict.",
        inspect="Read `spec.message`, `spec.replicas`, `metadata.generation` and `status.observedGeneration` on hello-report. Generation 7 with observedGeneration 6 is unreconciled even when status says ready. NotFound for the resource type means the CRD is not registered.",
        selfcheck="An instance with an unknown field was accepted, and reading it back shows the field missing. What happened under structural schema pruning, and how does that differ from a strict validation rejection?",
        retrieval="Recall which object is cluster-scoped and which is namespaced. Then explain the Exercise 6 teardown order and why removing the CRD is outside the learner's privileges.",
    ),
    30: dict(
        run="Only the preloaded controller on a host lease reconciles hello-report into a child, writes status and honors finalizers, so duplicate events, collisions and deletion can be watched rather than replayed.",
        inspect="Read `metadata.finalizers` and `status.observedGeneration` on hello-report, then the child's ownerReferences. lesson.cleanup should leave after its child is cleaned while other.cleanup stays; a child owned by a foreign UID is refused, not adopted.",
        selfcheck="The controller received the same create event three times. Why is the correct trace create, no-op, no-op, and what would a second child reveal about the reconcile logic?",
        retrieval="Rebuild the Exercise 1 state table from memory. Then explain what happens to finalizers when cleanup fails and why other.cleanup must remain.",
    ),
    31: dict(
        run="The host installs the admission policy and its binding for the labeled namespace. Only then can a mixed-image Deployment be denied by the server with a policy-specific message and no persisted revision.",
        inspect="Read `spec.template.spec.containers[].image` and `metadata.generation`. After a denied update, generation and images should be unchanged, which shows the rejected revision was never persisted.",
        selfcheck="A Deployment with one approved and one unapproved container was denied. Explain the all-container CEL logic, and why a later CrashLoopBackOff on an allowed Deployment says nothing about the policy.",
        retrieval="From memory, write the policy scope: resource, operations and namespace selector. Then list the Exercise 6 gaps, including why this is not signature verification.",
    ),
    32: dict(
        run="An exclusive multi-node lease with an allowlisted worker is needed to submit evictions, capture a denial tied to hello-budget and drain a node. Arithmetic alone cannot show any of that.",
        inspect="Read `spec.minAvailable`, `status.currentHealthy`, `status.desiredHealthy` and `status.disruptionsAllowed`. With minAvailable 1 and two healthy Pods, disruptionsAllowed should be 1; zero means an eviction submitted now will be denied.",
        selfcheck="A node crash removed both hello Pods despite hello-budget. Why did the budget not prevent it, and which kind of disruption does it actually coordinate?",
        retrieval="Recompute the allowed disruptions for two, one and zero healthy Pods from memory. Then describe how you restore the owned node state after the Exercise 4 drain.",
    ),
    33: dict(
        run="A qualified metrics API and the fixed bounded load are needed to see the autoscaler read utilization and move between one and two replicas with timestamps. Offline arithmetic gives the target, not the timing.",
        inspect="Read `status.currentMetrics`, `status.currentReplicas`, `status.desiredReplicas` and `status.conditions`. ScalingLimited true at the maximum of 2 matches the saturation case; ScalingActive false with FailedGetResourceMetric means unknown load, not zero.",
        selfcheck="Load stopped, but replicas stayed at two for several minutes. Explain the stabilization window, and why an autoscaler with missing metrics must not be read as idle.",
        retrieval="From memory, apply desired = ceil(current replicas times utilization divided by target) to the lesson's two cases. Then explain how you confirm the load fixture actually stopped.",
    ),
    34: dict(
        run="Identity-checked host edits move the hello Service selector between stable and candidate configurations, and bounded request samples show which backend answered. Replica ratios cannot reveal that.",
        inspect="Read `spec.selector` and `metadata.uid`. The selector should match only the stable backend's labels. A UID different from your receipt means the Service was replaced, so stop instead of editing it.",
        selfcheck="The candidate returned three of four valid responses within the deadline. Why does the gate reject it even though every candidate Pod was Ready, and what rollback evidence do you record?",
        retrieval="Write the Exercise 3 release gate from memory. Then explain why a one-to-three replica ratio does not give a one-to-three traffic split.",
    ),
    35: dict(
        run="The owned observer performs a real conditional update against hello-config and a bounded watch with relist, so a live conflict and an expired watch can be recorded instead of replayed.",
        inspect="Read `metadata.uid`, `metadata.resourceVersion` and `data`. A conditional update must carry the resourceVersion you just read; if the UID differs from your receipt, the object was replaced and Exercise 4 requires refusal.",
        selfcheck="Your watch failed because its history expired. Why do you relist rather than replay the missing events, and how does a bookmark help a watcher avoid that failure?",
        retrieval="From memory, contrast name, UID and resourceVersion. Then describe the bounded retry after a conflict: reread, recompute and resubmit with a capped count.",
    ),
    36: dict(
        run="A dedicated synthetic control plane is needed to take and restore an API snapshot, and the application data backup is restored separately, so both gates are observed on a target nothing else uses.",
        inspect="Read `status.phase`, `spec.volumeName` and `metadata.uid` on data-store-0 after restore. A Bound claim with a new UID shows the API object exists again, not that the marker bytes match the reference digest.",
        selfcheck="After restoring the API snapshot every Deployment is Ready, but the marker checksum fails. Why is recovery still incomplete, and which inventory was not restored?",
        retrieval="List the two backup inventories and their restore checks from memory. Then explain what must never appear in portable progress records for this drill.",
    ),
    37: dict(
        run="Two separately owned pinned stacks are needed to collect API, controller and storage compatibility receipts for each; the worksheet matrix only shows which rows are still missing.",
        inspect="Read `spec.template.spec.containers[0].image` on each stack's Deployment and compare the pinned digest with your inventory. A matching /version response with the wrong digest still blocks promotion, as in Worked example 2.",
        selfcheck="Stack B passes application tests but has no controller capability row. Why is it still unavailable, and what concrete evidence would close that row?",
        retrieval="From memory, list the exact version inputs of a pinned stack. Then write the Exercise 6 qualification conclusion limited to what was tested.",
    ),
    38: dict(
        run="Offline digest and signature checks use the vendored RSA fixture. Cluster admission that enforces signatures is a separate host qualification this lesson does not claim.",
        inspect="Read the container image on the Deployment. Only a digest reference can be joined to a signed subject; the fixture's :0.2.0 tag can move, so a signature cannot be tied to it as written.",
        selfcheck="A modified artifact keeps the same label. Why does the digest check catch it, and why does a matching digest alone say nothing about who published it?",
        retrieval="Name the four trust inputs from memory. Then explain how the tampered-byte negative proves the verifier depends on the signed content.",
    ),
    39: dict(
        run="The exclusive threat lease exercises parser, RBAC, admission and CNI controls separately, so each denial is recorded with its own layer and no single host result stands in for the others.",
        inspect="Read each Pod's `metadata.ownerReferences`, labels and `spec.serviceAccountName`. A foreign Pod with matching labels but no owned UID chain must survive cleanup, which is the defense Exercise 5 inspects.",
        selfcheck="A request was refused by the course parser. Why does that tell you nothing about whether RBAC or admission would also have stopped it, and how would you test each layer?",
        retrieval="From memory, write the actors and assets in the threat model. Then state the Exercise 6 residual assumptions about host trust and isolation.",
    ),
    40: dict(
        run="On the host lease one fixed fault changes the hello Service selector; timestamped endpoint and client samples then show the outage and the UID-bound repair.",
        inspect="Check `endpoints[].conditions.ready` in the hello slices against the Ready Pod count. Zero endpoints with one Ready Pod is the selector mismatch from Worked example 1; a changed Service UID stops the repair.",
        selfcheck="The timeline shows the selector change at 10, zero endpoints at 15 and Ready Pods throughout. Why would restarting the Pods be the wrong first move, and what would you compare instead?",
        retrieval="From memory, list the three competing hypotheses from Exercise 2. Then write the stop condition that prevents applying the repair to a replaced Service.",
    ),
    41: dict(
        run="A qualified drill on the host produces source timestamps for the start, service recovery and data verification, so the recovery time and data-loss window can be recomputed from evidence.",
        inspect="Read `status.phase` and `metadata.creationTimestamp` on data-store-0 next to the drill log. The claim's timestamp places it in the timeline but does not mark the data finish; that needs the independent marker check.",
        selfcheck="Service responses returned 90 seconds after the start, but the marker check never ran. Why can no recovery time be claimed, and what does the finish predicate require?",
        retrieval="Recompute the observed recovery time and data-loss boundary against the 120 and 30 second targets from memory. Then state the drill conclusion without a universal guarantee.",
    ),
    42: dict(
        run="The integrated lease brings platform, controller, policy, metrics, traffic, storage and recovery capabilities together, and each still needs its own receipt or an explicit unavailable row.",
        inspect="Read `metadata.generation`, `status.observedGeneration` and the conditions on hello-report alongside its child Deployment. The controller must have observed the current generation before the release marker or route evidence counts.",
        selfcheck="Your packet has a passing application request but a failed cleanup row. Why can the release still not be accepted, and what should the reviewer see?",
        retrieval="From memory, list every gate in the integrated packet in order. Then pick one and describe the timestamped incident evidence from Exercise 4 that would close it.",
    ),
}
