from author import author, fixture, hello, BASE, variant
import copy, json, yaml

configured = fixture("hello-configured.yaml")
author(
    9,
    """A ConfigMap stores nonsecret configuration as named key-value data. It separates configuration from an image, but it does not define how a running process notices a change. An environment variable is captured when the container process starts. A projected ConfigMap file can be refreshed by the kubelet, while the application still needs to reread or reload that file.

The contract-2 fixture consumes one synthetic message through both routes. DS60_MESSAGE references hello-config/message, and a read-only volume projects the same key to /config/message. The server reads its environment for /message and reads the file on each /file-message request. Values are restricted to hello or reviewer, so this lesson handles no credentials or arbitrary environment variables.

The browser can verify both values in a fresh one-shot Run. It cannot patch a live ConfigMap and preserve the existing Pod across Runs. The update comparison is therefore an explicit stateful host experiment or a synthetic trace, not an inference from two separately created browser workloads.""",
    [
        (
            "Read the two consumption paths",
            """ConfigMap data values are strings. The Pod environment entry uses valueFrom.configMapKeyRef with a name and key; the volume uses configMap.items to choose a key and filename. volumeMounts attaches that volume at a fixed read-only directory. The volume name connects the Pod-level declaration to the container mount, while the ConfigMap name identifies the source object in the same namespace.

The broker requires the ConfigMap and its consumer reference together, creates configuration before the workload, and refuses arbitrary names, Secret references, host paths, subPath and environment injection. A missing ConfigMap or key in a general Kubernetes workload can prevent container configuration, but the broker catches several such mismatches before sending a request.

An immutable ConfigMap is a separate Kubernetes feature; the teaching source here is mutable data under a one-shot lifecycle. Do not infer live update permission from the existence of the object. The normal worker Role has create/get/delete for its narrow workflow, not arbitrary patch/update access.""",
        ),
        (
            "Trace updates without promising an exact delay",
            """Synthetic initial state: ConfigMap=hello, process environment=hello, mounted file=hello. A host-authorized ConfigMap update changes desired data to reviewer. After the projected volume refresh is actually observed, the file can contain reviewer while the existing process environment remains hello. A replacement process created from the new configuration sees reviewer in its environment.

Volume refresh is asynchronous and depends on kubelet propagation/cache behavior. Do not promise that a file changes at a particular second. Use a bounded observation window, record when the new bytes were seen, and report an unobserved refresh honestly. A subPath mount has different update behavior and is deliberately excluded from the browser contract.

The fixture reads the file per request, so it demonstrates application rereading. An application that caches configuration at startup could continue using the old value even after the file changes. Distinguish API update, file projection, application reload and new-Pod rollout in the evidence ledger.""",
        ),
        (
            "Diagnose the layer that retained the old value",
            """If the API shows reviewer but the mounted file still says hello, investigate projection timing and mount details. If the file says reviewer but the application returns hello, investigate application caching/reload. If an environment variable remains hello in the same process, that is expected snapshot behavior rather than a broken ConfigMap.

The synthetic values and fixed endpoints are intentionally narrow. ConfigMaps are not secret storage, and base64 or a read-only mount would not make sensitive data confidential. The app\'s fresh-run checks prove the initial values it observed, not every future update or reload behavior.""",
        ),
    ],
    [
        (
            "Read a real ConfigMap and reference",
            "```yaml\n"
            + yaml.safe_dump(configured[0], sort_keys=False)
            + "```\n\nThe container references this key through configMapKeyRef and a read-only projection.",
            "The current synthetic key is message=reviewer; both fresh-process consumers should observe reviewer.",
        ),
        (
            "Compare update stages",
            """Synthetic trace: API reviewer; projected file reviewer; existing environment hello; file-reading HTTP route reviewer. After an owned rollout, new environment reviewer.""",
            "A live environment snapshot does not change merely because the ConfigMap API object changed.",
        ),
    ],
    [
        (
            "Map names and keys",
            "Trace hello-config/message through environment and volume fields.",
            "Both consumers reference the same namespaced key; mount path is read-only /config/message.",
            "Separate ConfigMap name, volume name, key and file path.",
            "These names play different roles. The volume link connects a Pod declaration to a container mount, while the key selects data from the ConfigMap. A wrong key can break configuration even if the object name exists.",
            "Mark the ConfigMap name, key, volume name and mountPath in your YAML and confirm that each reference points to an object or volume declared in the same manifest.",
        ),
        (
            "Run the initial value contract",
            "Add the hello-config ConfigMap (message: reviewer), the DS60_MESSAGE configMapKeyRef and the read-only lesson-config volume to the starter, then Run it under a freshly qualified contract-2 lease.",
            "Fresh client verifies /version plus /message=reviewer and /file-message=reviewer, then owned cleanup.",
            "Inspect application-value checks in addition to readiness.",
            "The fixed client independently checks the data visible through both application routes. A Ready Pod alone would not prove that either configuration path was consumed. The result remains a fresh one-shot observation.",
            "Confirm that the Run result shows separate passing checks for `/version`, `/message` and `/file-message`, plus cleanup of the ConfigMap, Deployment and Service you submitted.",
        ),
        (
            "Predict an environment update",
            "Keep the same process while a synthetic ConfigMap value changes from hello to reviewer.",
            "Existing environment remains hello until a new process starts.",
            "Environment variables are process-start inputs.",
            "Kubernetes does not rewrite an existing process environment when its source ConfigMap changes. Restarting or rolling out a new Pod can consume the new value, but that is a distinct state transition with new process evidence.",
            "Compare the Pod UID and restartCount before and after the change; without a new process the environment value cannot change.",
        ),
        (
            "Observe file and reload stages",
            "In an authorized stateful host lab, record API value, file bytes and application response separately.",
            "After observed projection, the file may be reviewer; application changes only if it rereads/reloads as designed.",
            "Do not use one timestamp as proof for all three layers.",
            "The fixture rereads per request, but other applications may cache. A bounded observation records actual propagation instead of assuming an exact refresh delay. If the capability is absent, retain the synthetic reasoning rather than inventing a live transcript.",
            "Your record needs three observations from three sources: an API readback, a read of the mounted file and an HTTP response, each with its own time.",
        ),
        (
            "Reject unsupported injection",
            "Try a Secret reference, hostPath, subPath or arbitrary environment variable in a scratch source.",
            "Broker rejection before API mutation; the approved fixed reference still parses.",
            "The allowlist admits only synthetic configuration paths.",
            "The lesson does not broaden the worker into an arbitrary Pod executor. A source refusal establishes the boundary before workload creation, and should not be mislabeled as a cluster configuration error.",
            "Record the refusal message for each attempted field and confirm that no create receipt exists; then Run the restored source to show it still parses.",
        ),
        (
            "Explain a safe configuration release",
            "Write a before/after record for a new message value with rollback and cleanup identities.",
            "Record includes ConfigMap version/UID, Pod generation/UID, observed routes and restored source if rollback is needed.",
            "Keep value propagation and workload rollout as separate claims.",
            "A reproducible configuration change needs the desired file plus observed application behavior. A rollback should restore the intended configuration and verify it, not merely delete objects by name or assume the old process still exists.",
            "A reviewer must be able to roll back using only identities in your record: ConfigMap UID and resourceVersion, Pod UIDs and the restored source.",
        ),
    ],
    configured,
    """
def main():
    before={'api':'hello','environment':'hello','file':'hello'}
    projected={**before,'api':'reviewer','file':'reviewer'}
    assert projected['environment']=='hello' and projected['file']=='reviewer'
    restarted={**projected,'environment':projected['api']}
    assert restarted['environment']==restarted['file']=='reviewer'
    routes={'/message':'reviewer','/file-message':'reviewer','/version':'ds60-fixture-v1'}
    assert routes['/message']==routes['/file-message'] and routes['/version']=='ds60-fixture-v1'
    print('k8s-009 synthetic configuration-lifetime checks passed; no update or API call performed')

if __name__ == "__main__":
    main()
""",
    browser=True,
    starter=hello(True),
    starter_note="The learner starter is the k8s-008 Deployment and Service without configuration; Exercise 2 asks you to add the ConfigMap and both of its consumers. ",
    capability="fixed ConfigMap initial-value checks; separate stateful update observation",
    refs=["[Kubernetes ConfigMaps](https://kubernetes.io/docs/concepts/configuration/configmap/)"],
)

quota = {
    "apiVersion": "v1",
    "kind": "ResourceQuota",
    "metadata": {"name": "lesson-budget"},
    "spec": {"hard": {"requests.cpu": "300m", "requests.memory": "256Mi", "pods": "3"}},
}
(BASE / "fixtures/k8s-010-quota.json").write_text(json.dumps(quota, indent=2) + "\n")
author(
    10,
    """A resource request describes the capacity used for scheduling and accounting. A limit constrains runtime use under the relevant resource mechanism. A namespace quota is an admission budget across objects. These operate at different stages, so Pending, Forbidden and OOMKilled are not interchangeable symptoms.

CPU quantities such as 100m are millicores: 100m is 0.1 CPU. Memory Mi is a binary unit: 64Mi is \\(64\\times2^{20}\\) bytes. The browser admits bounded positive millicore and Mi quantities and requires requests no greater than limits. That narrow grammar is not a complete implementation of every Kubernetes quantity syntax.

The allowed source runs the small server with modest requests and limits. Quota and deliberate memory-failure experiments require a teacher-provided bounded host fixture; the current worker does not create ResourceQuotas or install a metrics stack. A source-validation refusal must remain distinct from an actual admission, scheduling or runtime observation.""",
    [
        (
            "Follow admission, scheduling and execution",
            """An admission quota can reject a new Pod or controller-created Pod before it becomes runnable. A scheduler can leave an accepted Pod Pending because no node satisfies its resource requests or placement constraints. A container can start and later exceed its memory limit, resulting in a termination reason such as OOMKilled. The investigation begins by locating the first failing phase.

CPU limits are commonly enforced by throttling, while memory limit enforcement can kill a process under pressure. A throttled application may remain Running but respond slowly. An exit code alone is not a complete memory diagnosis; inspect the recorded termination reason, events and relevant resource observations.

Requests and limits also influence quality-of-service behavior, but declaring a large limit is not a reservation of that much node capacity. Scheduler placement primarily uses requests and other constraints. Overcommitting limits can still produce contention, so source configuration must not be equated with guaranteed performance.""",
        ),
        (
            "Calculate a small namespace budget",
            """The synthetic quota permits 300m requested CPU, 256Mi requested memory and three Pods. Two replicas requesting 10m and 16Mi each consume 20m and 32Mi of those request budgets. A third verifier Pod also consumes quota according to its own requests. Count controller-created Pods and transient rollout replicas when planning a bounded lab.

The fixed adapter caps each container at 250m CPU and 128Mi memory and validates that requests do not exceed limits. That protects the teaching workload budget but does not replace cluster admission or scheduling. A namespace can have stricter external constraints, and a node can still lack available requested capacity.

A quota object is supplied as an offline JSON example. The host capability must provision and own it deliberately. Do not submit it through the Deployment/Service browser source or broaden worker permissions to make the lesson appear executable.""",
        ),
        (
            "Choose discriminating evidence",
            """FailedScheduling with insufficient CPU points to placement capacity; an admission Forbidden message naming quota points to a namespace budget; lastState.terminated.reason=OOMKilled points to runtime memory enforcement. All may result in no ready backend, but that final symptom is too broad to choose a repair.

Changing a readiness path does not fix quota or missing capacity. Increasing limits without understanding the failure can move the problem or violate the lab budget. Record a minimal justified change and verify the affected phase before claiming application recovery.""",
        ),
    ],
    [
        (
            "Convert units and sum requests",
            """Two Pods each request 10m CPU and 16Mi memory. Their combined requests are 20m and 32Mi. A memory limit of 64Mi equals 67,108,864 bytes.""",
            "The calculations use millicores and binary Mi units, not percentages or decimal megabytes.",
        ),
        (
            "Classify three failures",
            """Synthetic records: admission Forbidden/exceeded quota; Pod Pending with FailedScheduling/Insufficient cpu; container terminated with reason OOMKilled. Each requires a different next observation.""",
            "Quota, placement and runtime enforcement are three distinct failure phases.",
        ),
    ],
    [
        (
            "Read requests versus limits",
            "The starter sets requests equal to limits (100m CPU and 64Mi memory). Identify both mappings and explain their roles, then change the requests to 10m CPU and 16Mi memory.",
            "Starter requests 100m/64Mi equal its limits; the edited source keeps limits 100m/64Mi with requests 10m/16Mi. Requests influence placement and quota; limits constrain runtime use.",
            "Read both resource keys under both mappings.",
            "The fields describe different contracts. A request is not a measured usage value, and a limit is not a guaranteed reservation. Preserve the configured values alongside actual runtime evidence when diagnosing performance.",
            "Read `resources.requests` and `resources.limits` as two separate mappings in both your edited source and the reference, and state which mapping the scheduler uses for placement.",
        ),
        (
            "Calculate the replica budget",
            "Sum requests for two replicas and convert 64Mi to bytes.",
            "20m CPU, 32Mi memory and 67,108,864 bytes for 64Mi.",
            "Multiply per-container requests by the actual Pod count.",
            "Binary memory units use powers of two. Include extra clients or rollout surge Pods in a real quota calculation. A count of desired application replicas alone can understate total namespace resource use.",
            "Recompute using `spec.replicas` from the source and \\(1\\,\\text{Mi}=2^{20}\\) bytes, then compare your numbers with the assertions in the offline check script.",
        ),
        (
            "Reject invalid source budgets",
            "Compare request 200m with limit 100m in a scratch source.",
            "Broker refuses requests greater than limits before creating resources.",
            "The parser checks units, caps and ordering.",
            "This is source admission by the course adapter. It does not establish that Kubernetes scheduled or killed a Pod. The distinction keeps a local validation error from being confused with runtime resource exhaustion.",
            "Run the scratch source and record the exact refusal text; confirm that the result contains no created resource UID.",
        ),
        (
            "Diagnose quota versus scheduling",
            "Match Forbidden/exceeded quota and Pending/FailedScheduling to their stages.",
            "Admission budget versus scheduler placement, with separate minimal investigations.",
            "Ask whether the Pod was admitted and assigned to a node.",
            "Quota rejection can occur before a runnable Pod exists. Scheduling failure means an accepted Pod lacks a suitable placement. Looking only for readiness or application logs can miss both causes.",
            "For each record, answer two questions in order: was the Pod admitted, and was it assigned a node in `spec.nodeName`?",
        ),
        (
            "Interpret memory failure",
            "Review a scoped synthetic OOMKilled record and a generic exit 137 record.",
            "OOMKilled is specific memory-enforcement evidence; exit 137 alone is insufficient to prove that cause.",
            "Inspect termination reason and surrounding events.",
            "An exit code can have multiple causes. The reason field and contextual evidence narrow the diagnosis. The lesson does not authorize unbounded memory stress or changing node-wide settings.",
            "Look for `state.terminated.reason` or `lastState.terminated.reason`; an exit code without that field supports only a weaker conclusion.",
        ),
        (
            "Plan a bounded repair",
            "Write a repair for one of the three failure records and its acceptance condition.",
            "One justified source/resource change, phase-specific success evidence and owned cleanup.",
            "Avoid changing unrelated probes, images or namespace policy.",
            "A useful repair targets the observed mechanism. It should state what new evidence would confirm recovery and remain within the owned resource budget. A Ready Pod after a broad set of changes does not explain which change fixed the problem.",
            "Check that your repair changes exactly one field and that its acceptance condition names the phase that originally failed.",
        ),
    ],
    hello(),
    """
def main():
    def millicores(value):return int(value.removesuffix('m'))
    def mebibytes(value):return int(value.removesuffix('Mi'))
    requests={'cpu':'10m','memory':'16Mi'};limits={'cpu':'100m','memory':'64Mi'};replicas=2
    total_cpu=replicas*millicores(requests['cpu']);total_memory=replicas*mebibytes(requests['memory'])
    assert (total_cpu,total_memory)==(20,32) and mebibytes(limits['memory'])*2**20==67108864
    quota={'cpu_m':300,'memory_mi':256,'pods':3}
    assert total_cpu<=quota['cpu_m'] and total_memory<=quota['memory_mi'] and replicas<=quota['pods']
    scratch={'request':'200m','limit':'100m'}
    assert millicores(scratch['request'])>millicores(scratch['limit'])
    phases={'Forbidden/exceeded quota':'admission','FailedScheduling/Insufficient cpu':'scheduling','OOMKilled':'runtime'}
    assert len(set(phases.values()))==3
    print('k8s-010 synthetic unit, budget and failure-phase checks passed')

if __name__ == "__main__":
    main()
""",
    browser=True,
    starter=variant(
        hello(),
        [0, "spec", "template", "spec", "containers", 0, "resources", "requests"],
        {"cpu": "100m", "memory": "64Mi"},
    ),
    starter_note="The learner starter sets requests equal to limits; Exercise 1 asks you to set the lower reference requests. ",
    capability="fixed resource-bounded workload; separate quota/OOM host fixtures",
    refs=[
        "[Kubernetes resource management](https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/)"
    ],
)

task = fixture("hello-task.yaml")
cron = {
    "apiVersion": "batch/v1",
    "kind": "CronJob",
    "metadata": {"name": "lesson-schedule"},
    "spec": {
        "schedule": "*/5 * * * *",
        "timeZone": "Etc/UTC",
        "suspend": True,
        "concurrencyPolicy": "Forbid",
        "startingDeadlineSeconds": 60,
        "successfulJobsHistoryLimit": 1,
        "failedJobsHistoryLimit": 1,
        "jobTemplate": {"spec": copy.deepcopy(task[0]["spec"])},
    },
}
(BASE / "fixtures/k8s-011-cronjob.json").write_text(json.dumps(cron, indent=2) + "\n")
author(
    11,
    """A Job manages finite work toward a completion condition. A Deployment manages a continuing replica set. A CronJob creates Jobs according to a schedule. These controllers have different success and lifecycle meanings: an intentionally exiting task belongs in a Job, while a server that should remain available belongs in a continuing workload controller.

The fixed hello-task Job runs a deterministic synthetic calculation and exits. Its success output records three accepted rows, two rejected rows and total 35. A separate allowed failure outcome exits 2. The worker checks the Job condition, its controlled Pod identity, the task container\'s zero exit and the exact bounded JSON output before calling the success path complete.

The CronJob example is suspended and remains a host-lab/reading fixture. The browser does not accept arbitrary schedules or leave recurring workloads behind. A scheduled configuration is not evidence that a run occurred, and a completed run is not evidence that future recurrence works.""",
    [
        (
            "Read completion, retry and deadline semantics",
            """The admitted Job has completions 1, parallelism 1, restartPolicy Never, backoffLimit zero or one, and an active deadline between 5 and 30 seconds. These limits bound its intended work. A failed Pod can lead to another Pod attempt when retries are allowed; restartPolicy Never does not by itself mean the Job never retries.

Observe terminal Complete or Failed conditions and relevant counters. A nonterminal failed count can appear while a retry remains possible, so the extended adapter waits for a terminal condition. A successful count alone is insufficient if the Pod belongs to another Job or namespace. The controller UID, Run nonce, container identity and exit status form the proof chain.

Kubernetes Jobs are not a blanket exactly-once side-effect system. Controller retries and distributed failure can cause repeated starts. A production task that writes externally needs an idempotency or transactional publication strategy. The teaching task has no external side effects and uses a fixed input ledger.""",
        ),
        (
            "Understand CronJob scheduling without enabling recurrence",
            """The example schedule */5 * * * * expresses five-minute positions in the specified Etc/UTC time zone. concurrencyPolicy Forbid prevents overlapping Jobs from that CronJob under its controller policy; it does not coordinate unrelated workloads. startingDeadlineSeconds limits how late a missed schedule may be started. History limits bound retained completed Job records, not all underlying data retention.

suspend: true prevents new scheduled Jobs while the example is being reviewed. Suspending does not automatically stop an already running Job. Before cleanup, inspect active Jobs and use the owned operation\'s exact identity receipts. A host-provided recurring exercise needs observed schedule times and results across multiple occasions, not merely a valid YAML field.

Clock interpretation, time-zone support and controller availability affect recurrence. Report actual timestamps and missed-run evidence. Do not invent a universal execution second from the schedule expression.""",
        ),
        (
            "Diagnose finite-work failures",
            """A failed task exit, a deadline exceeded condition and a missing image are different failures. The fixed failure mode demonstrates application failure with bounded cleanup. A timeout of the outer operation is another boundary, with a separate cleanup reserve.

Do not hide failed attempts by reading only the most recent success counter, or claim that printing the expected text proves task correctness. The fixed reference uses independent expected counts and ties logs to a verified owned successful Pod. Written reasoning about recurrence and idempotency remains outside automatic grading.""",
        ),
    ],
    [
        (
            "Read the bounded Job",
            "```yaml\n" + yaml.safe_dump(task[0], sort_keys=False) + "```",
            "One finite task is requested, with one parallel Pod and a 20-second active deadline.",
        ),
        (
            "Separate suspended scheduling from execution",
            """The supplied CronJob JSON has schedule */5 * * * *,timeZone Etc/UTC, suspend true and Forbid concurrency. No scheduled execution is claimed by reading it.""",
            "The object describes intended recurrence, but a suspended configuration does not create new scheduled Jobs.",
        ),
    ],
    [
        (
            "Identify finite-work controls",
            "The starter Job allows one retry and a 30-second deadline. Read completions, parallelism, restartPolicy, backoffLimit and activeDeadlineSeconds, then set no retry and a 20-second deadline.",
            "Starter: 1, 1, Never, 1 and 30 seconds. Edited source: 1, 1, Never, 0 and 20 seconds.",
            "Each field controls a different part of lifecycle or work budget.",
            "A single completion is the desired successful work count, parallelism bounds concurrent Pods, and backoff controls retries after failures. The active deadline bounds duration independently of the outer app operation deadline.",
            "Quote the five values from `spec` and `spec.template.spec` of your edited source; every value must come from the YAML, not from the guide.",
        ),
        (
            "Verify exact task output",
            "Run the successful fixed task under a qualified lease.",
            "Owned Complete Job, controlled successful task Pod, exit 0 and exact accepted 3, rejected 2 and total 35 output.",
            "Inspect the identity and output checks rather than a success word.",
            "The fixed task is deterministic and has no external side effects. Its receipt connects controller state to the actual task container and a small independent ledger. It does not certify arbitrary learner code or every written exercise.",
            "Compare the output ledger field by field (accepted, rejected and total) and confirm that the task Pod is owned by this Run's Job UID.",
        ),
        (
            "Observe intentional failure",
            "Change only the allowed outcome from success to failure.",
            "Job reaches Failed; operation reports failure and cleans its owned UID.",
            "A deliberate nonzero exit is expected negative evidence.",
            "The source remains syntactically valid and the workload can start, but the task intentionally reports failure. This distinguishes runtime task failure from manifest rejection or image absence.",
            "Confirm that the Job condition is Failed, that the task container exit status is nonzero and that cleanup names the same Job UID.",
        ),
        (
            "Explain retry semantics",
            "Compare backoffLimit 0 and 1 with restartPolicy Never.",
            "At most the declared retry budget is requested; Never does not forbid a replacement Pod attempt.",
            "Separate container restart from Job retry.",
            "The Job controller can create another Pod even when the kubelet will not restart a failed container in the same Pod. Production side effects must tolerate duplicate attempts rather than assuming the controller provides exactly-once execution.",
            "Count the task Pods that each backoffLimit value can create, keeping container restarts inside one Pod out of that count.",
        ),
        (
            "Review the suspended CronJob",
            "Interpret schedule, timeZone, suspend, concurrency and starting deadline fields.",
            "A five-minute UTC schedule is configured but suspended; existing active Jobs require separate handling.",
            "Configuration and observed recurrence are different evidence.",
            "Suspension affects future scheduling. It does not erase an already running Job or prove that the schedule previously fired. A live recurring lab needs a separate host capability and multiple observed timestamps/results.",
            "Read `spec.schedule`, `spec.timeZone`, `spec.suspend`, `spec.concurrencyPolicy` and `spec.startingDeadlineSeconds` in the fixture JSON and state the effect of each one.",
        ),
        (
            "Design an idempotent handoff",
            "Describe how a real finite task would avoid publishing duplicate effects after retry.",
            "A stable logical-work key, commit boundary, replay policy and acceptance ledger are named.",
            "A Pod UID changes across attempts and is not necessarily the logical job identity.",
            "Use an application-level identity and an atomic or otherwise justified publication protocol. A final successful Job count cannot establish that an external sink received exactly one effect. The teaching task avoids that external boundary and labels the limitation.",
            "Test your design against a crash after the effect but before its acknowledgment: a retried attempt must not publish the effect a second time.",
        ),
    ],
    task,
    """
def main():
    rows=['10','0','bad','-2','25'];accepted=[int(x) for x in rows if x.isascii() and x.isdigit()]
    assert accepted==[10,0,25] and len(rows)-len(accepted)==2 and sum(accepted)==35
    spec={'completions':1,'parallelism':1,'backoffLimit':0,'activeDeadlineSeconds':20}
    assert spec['completions']==spec['parallelism']==1 and 5<=spec['activeDeadlineSeconds']<=30
    cron={'suspend':True,'timeZone':'Etc/UTC','schedule':'*/5 * * * *'}
    assert cron['suspend'] and cron['timeZone']=='Etc/UTC'
    print('k8s-011 synthetic task and schedule checks passed; no recurring workload started')

if __name__ == "__main__":
    main()
""",
    browser=True,
    starter=variant(
        variant(task, [0, "spec", "backoffLimit"], 1), [0, "spec", "activeDeadlineSeconds"], 30
    ),
    starter_note="The learner starter allows one retry and a 30-second deadline; Exercise 1 asks you to set the reference budget. ",
    capability="fixed finite Job; separately provisioned suspended CronJob review",
    refs=[
        "[Kubernetes Jobs](https://kubernetes.io/docs/concepts/workloads/controllers/job/)",
        "[Kubernetes CronJobs](https://kubernetes.io/docs/concepts/workloads/controllers/cron-jobs/)",
    ],
)

missing = hello()[0]
missing["spec"]["template"]["spec"]["containers"][0]["env"] = [
    {
        "name": "DS60_MESSAGE",
        "valueFrom": {"configMapKeyRef": {"name": "missing-config", "key": "message"}},
    }
]
author(
    12,
    """Troubleshooting starts by separating observations from hypotheses. A condition, event or log can narrow a failure, but no single status word explains every unavailable application. Build a short timeline from source submission through API acceptance, scheduling, container start, readiness and client behavior. Locate the first boundary that has not been established.

This worksheet compares three explicit synthetic cases: missing configuration, an incorrect readiness path and a failed finite Job. It also names which cases the browser can reproduce directly. Wrong readiness and fixed task failure have bounded current operations; the missing-config example is a host/static case because the broker rejects inconsistent ConfigMap references before apply.

The purpose is a disciplined diagnosis and minimal repair, not a collection of broad commands against every namespace. Use only the owned target and preserve relevant object UIDs so a replacement or unrelated workload cannot silently enter the evidence.""",
    [
        (
            "Read different evidence channels",
            """Conditions summarize a controller or object state, such as Ready=False or a Job Failed condition. Events describe noteworthy control-plane or kubelet actions and can expire or repeat. Logs are application/container output and may be absent if the process never started. Each channel has a different producer and timing.

A container Waiting reason CreateContainerConfigError suggests configuration assembly failed before the application process ran. An Unhealthy readiness event with an HTTP 404 from /missing suggests the process is reachable but the configured check path is wrong. A Job Failed condition after the task exits 2 points to finite application failure. The shared symptom, no ready useful result, does not make the causes interchangeable.

Record the exact field or bounded line that supports the hypothesis. A log excerpt without Pod UID/container/restart context can describe an old process. An event naming a different object UID should not be used to explain the current one.""",
        ),
        (
            "Choose the smallest discriminating repair",
            """For a missing ConfigMap key, check the source object/key and consumer reference before changing the image. For a wrong probe path, compare the declared route with the fixture\'s fixed /ready endpoint. For the injected failed Job, inspect the allowed outcome argument and the terminal condition rather than increasing replicas of an unrelated Deployment.

Change one relevant input, then verify the corresponding phase and application result. A successful create after a repair is weaker than a correct client response. A restored Ready count after a failed Job says nothing about that Job\'s data output. The acceptance condition should match the original failure mechanism.

Use a bounded observation window and retain the final state on timeout. Repeatedly increasing deadlines without new evidence can hide a permanent mismatch. Cleanup is still required after a failed experiment, and it must preserve unrelated or replaced objects.""",
        ),
        (
            "Avoid diagnosis by command volume",
            """A large dump of every namespace, log and Secret is not a better diagnosis and exceeds the course scope. Start from the owned source, identity and first discriminating condition. Do not turn a source-admission refusal into a fabricated cluster event or copy synthetic fixture timestamps into a live incident report.

The offline reference classifies supplied facts only. It does not discover a real incident or establish that a proposed repair was applied. Keep predicted outcomes, actual observations and confirmed recovery as separate entries.""",
        ),
    ],
    [
        (
            "Compare three concise incident records",
            """A: Waiting/CreateContainerConfigError and message missing ConfigMap key. B: Running with Ready=False and readiness HTTP 404 at /missing. C: Job Failed with task exit 2 and injected-failure output.""",
            "A configuration boundary, B probe mismatch, C finite task failure are distinct diagnoses.",
        ),
        (
            "Reject a misleading repair",
            """For B, a proposal changes the Service selector while leaving /missing as the readiness path. The Pod still cannot pass its readiness check even if Service labels match.""",
            "The proposed edit does not target the observed probe failure; restore /ready first and reobserve.",
        ),
    ],
    [
        (
            "Order the evidence phases",
            "Place API acceptance, scheduling, container start, readiness and client response in order.",
            "A trace identifies the first missing or failed boundary for each case.",
            "A later symptom can be caused by an earlier failure.",
            "The sequence prevents searching application logs before a container was configured or treating a Service response as guaranteed by object creation. Real timestamps can overlap across controllers, but the evidence dependencies remain useful.",
            "For each case, mark the first boundary whose evidence is missing; every later boundary in that case must be marked as not reached.",
        ),
        (
            "Diagnose missing configuration",
            "Use case A to name one minimal source/configuration check.",
            "Inspect referenced ConfigMap name/key and availability; do not claim the process crashed.",
            "Waiting before process start can leave no application log.",
            "The general Kubernetes failure occurs during container configuration. The current broker catches some inconsistent references earlier, so a browser refusal must be labeled as a different phase. The host fixture is required to observe the kubelet condition.",
            "Confirm that your check names the ConfigMap and key exactly as the Pod spec references them and does not depend on an application log.",
        ),
        (
            "Diagnose the probe path",
            "Use case B to propose and predict a one-field repair.",
            "Change /missing to the admitted /ready path; then require new Ready and client evidence.",
            "The 404 comes from the selected HTTP route.",
            "The application can be running while the readiness URL is wrong. Changing unrelated selectors or resource limits does not explain the observed 404. A new bounded run should preserve its own source and identity receipt.",
            "Your prediction must change exactly one field and name the two observations, a Ready condition and a client response, that will confirm the repair.",
        ),
        (
            "Diagnose finite work",
            "Use case C to distinguish deliberate task failure from timeout or image absence.",
            "Task exit 2 and terminal Failed condition identify the injected application outcome.",
            "Read the task command/outcome and Job condition together.",
            "The fixed task can start successfully and still fail its own contract. Increasing an unrelated Deployment count would not repair it. A retry policy also cannot turn a deterministic injected failure into a correct result without changing the intended input.",
            "Cite the Job condition and the container exit code together; a deadline would report `DeadlineExceeded` and an image problem would leave a waiting reason instead.",
        ),
        (
            "Write a minimal incident timeline",
            "Record observation, hypothesis, one change and acceptance condition for one case.",
            "Each claim cites a bounded field/line and object identity; synthetic facts are labeled.",
            "Avoid inventing elapsed times or actions not performed.",
            "A reviewable timeline separates what was seen from what was inferred and what was actually changed. It should make a failed hypothesis useful evidence rather than erase it after a later successful attempt.",
            "Every line of the timeline must cite an object identity and a bounded field or log line; delete any elapsed time or action you did not observe.",
        ),
        (
            "Verify recovery and cleanup",
            "State the post-repair evidence and exact cleanup boundary.",
            "Relevant controller/application checks pass and only recorded owned UIDs are removed.",
            "A successful apply is not the final acceptance condition.",
            "Recovery needs evidence at the failed layer plus the intended application result. Cleanup has its own identity and deadline contract, especially after timeout or cancellation. A same-name replacement must remain untouched.",
            "List the post-repair checks and the UIDs to delete; any UID absent from the original creation record must be excluded.",
        ),
    ],
    [missing],
    """
def diagnose(record):
    if record.get('waiting')=='CreateContainerConfigError':return 'configuration'
    if record.get('probe_path')=='/missing' and record.get('http')==404:return 'readiness-path'
    if record.get('job_condition')=='Failed' and record.get('exit')==2:return 'finite-task'
    return 'insufficient-evidence'

def main():
    cases=[{'waiting':'CreateContainerConfigError'},{'probe_path':'/missing','http':404},{'job_condition':'Failed','exit':2}]
    assert [diagnose(x) for x in cases]==['configuration','readiness-path','finite-task']
    assert diagnose({'phase':'Running'})=='insufficient-evidence'
    print('k8s-012 synthetic triage checks passed; no live incident was inspected')

if __name__ == "__main__":
    main()
""",
    capability="paired synthetic incident analysis and selected bounded negative Runs",
    refs=[
        "[Kubernetes Pod lifecycle](https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/)"
    ],
)

revision = hello(True)
revision[0]["spec"]["template"]["metadata"]["annotations"] = {"lesson-revision": "B"}
revision[0]["spec"]["template"]["spec"]["containers"][0]["env"] = [
    {"name": "DS60_MESSAGE", "value": "reviewer"}
]
author(
    13,
    """A rollout changes a Deployment\'s Pod template and reconciles toward a new ReplicaSet revision. The Deployment object can retain its UID while old and new Pods coexist. A readiness failure in the candidate revision may leave old Ready backends serving traffic, so a successful request alone does not prove that the new version completed.

The stateful rollout is a host-lab contract. The browser creates and cleans a fresh workload each Run; it does not patch an existing Deployment across Runs. The provided JSON illustrates a synthetic configuration revision using the already approved fixture image and a changed message marker. It is not evidence of an image upgrade. A two-image release experiment additionally requires two separately preloaded, qualified image identities from the host receipt.

Treat the desired manifest as the durable release intent. A rollback should restore a reviewed desired state and then verify generation, updated/ready counts and application identity. Merely seeing some ready traffic can conceal that the cluster is still serving the prior revision.""",
    [
        (
            "Follow generations and ReplicaSets",
            """metadata.generation changes when the relevant desired spec changes. status.observedGeneration reports what the controller has processed. The Deployment revision annotation and ReplicaSet ownership track rollout history, but a revision number is not an image digest or application version by itself.

During a rolling update, the old ReplicaSet can retain ready Pods while the new template creates Pods that are not ready. updatedReplicas may describe the candidate count even when readyReplicas still includes old replicas. Compare actual Pod template/image/configuration identity and controller ownership to interpret the aggregate counts.

The synthetic revision marker B changes a Pod-template annotation and message input. It can demonstrate a template rollout in a prepared stateful scope. If the lesson is extended to image versions, record exact preloaded image digests and verify the route reporting application version; do not invent a tag or pull a new image during the exercise.""",
        ),
        (
            "Recover declaratively and verify the intended version",
            """Suppose desired generation 5 introduces a bad readiness path. The controller has observed 5, but updated replicas are 2 and ready candidate replicas are 0 while two old Pods remain ready. A client may still receive the old version. The correct acceptance condition requires the new intended revision to become healthy, not merely any successful response.

A recovery can restore the last verified manifest or apply a corrected candidate. Record which choice was made and the resulting new generation. The server assigns identities and revision details; do not edit status fields into source to make a report look converged. Retain the before/after desired files and observed Pod UIDs.

Bound the rollout wait and define failure gates. A progress deadline or failed readiness condition is useful evidence, not a reason to change unrelated cluster settings. Cleanup or retention follows the host capability\'s recorded resource identities.""",
        ),
        (
            "Separate configuration, image and traffic claims",
            """The single approved image can expose hello/reviewer as synthetic message markers, but that is a configuration revision rather than a different binary image. A two-image rollout needs its own provenance and preload receipt. Likewise, a few successful requests do not establish exact traffic percentages or uninterrupted availability.

Do not describe two cleaned-up browser Runs as one live rollout. The host worksheet must show the same Deployment UID across the state transition and the intended candidate identity in the final response.""",
        ),
    ],
    [
        (
            "Read a mixed rollout snapshot",
            """Synthetic desired generation 5, observedGeneration 5, updatedReplicas 2, old ready Pod UIDs {old-a, old-b}, new ready set empty. Client returns marker A.""",
            "The controller observed the change, but candidate B is not accepted; old traffic can still succeed.",
        ),
        (
            "Restore verified intent",
            """Restore the reviewed A template as a new desired generation 6. Observe generation 6, owned Ready Pods matching A and the expected marker. Do not claim generation returned to 4 or that old Pod UIDs were resurrected.""",
            "Rollback is a new reconciliation to restored intent, with fresh observed identities.",
        ),
    ],
    [
        (
            "Identify a template change",
            "Compare revision A with the supplied B annotation/message example.",
            "Pod-template content changes while Deployment name/UID can remain fixed in a stateful lab.",
            "Distinguish metadata outside the Pod template from fields that trigger new Pods.",
            "A template change drives a new ReplicaSet. The synthetic marker is configuration evidence, not a new image identity. The host operation must preserve the same Deployment instance to demonstrate a rollout rather than two independent creates.",
            "Check whether each changed field lies under `spec.template`; only a Pod-template change creates a new ReplicaSet.",
        ),
        (
            "Interpret mixed replicas",
            "Analyze the generation 5 snapshot with old Ready and new unready Pods.",
            "Candidate B incomplete despite aggregate ready traffic.",
            "Trace each Pod to its ReplicaSet and template identity.",
            "Counts can mix old and new revisions. An independent client can still reach old Pods while the desired candidate is failing readiness. Acceptance must name the intended version and its owned Ready population.",
            "Map every Pod to its ReplicaSet through ownerReferences and count Ready Pods per pod-template-hash, not in aggregate.",
        ),
        (
            "Define a failure gate",
            "Set a bounded wait and explicit candidate acceptance conditions.",
            "Generation observed, desired updated/ready candidate counts and expected application marker are required.",
            "A timeout should report which condition failed.",
            "The gate prevents indefinite waiting and avoids treating a partial rollout as success. It should preserve diagnostic evidence before recovery and remain within the lease and cleanup budget.",
            "Each condition in your gate must be testable by one readback or request and must report its own failure when the wait expires.",
        ),
        (
            "Recover the desired source",
            "Restore the last verified manifest or repair the candidate, then reobserve.",
            "A new generation converges to the selected intent; source and observed marker agree.",
            "Do not fabricate status or assume old UIDs return.",
            "Recovery is another controlled change. The report should say whether it reverted or fixed the candidate, and show the new observation rather than only the command used to request it.",
            "Confirm that `status.observedGeneration` equals the new `metadata.generation` and that the observed application marker matches the source you restored.",
        ),
        (
            "Plan a genuine image-version rehearsal",
            "Specify the additional evidence needed to roll between two binaries.",
            "Two qualified preloaded image digests, compatible manifests and an application-version response check.",
            "A changed message in one image is not a binary upgrade.",
            "The host must provide both exact artifacts before the live rehearsal. The learner should not substitute an arbitrary registry tag or infer provenance from a version string. Keep this acceptance row unavailable if those artifacts are absent.",
            "Your list must name two image digests and a response check that distinguishes the binaries; a message change in one image fails this check.",
        ),
        (
            "Separate final state from availability",
            "Write what a client timeline can add to the final rollout snapshot.",
            "Observed version/error samples over the transition, with no universal uptime or exact-ratio claim.",
            "The final Ready count omits intermediate request behavior.",
            "A bounded client trace can show what its sampled requests experienced. It complements the controller proof and can reveal old-version traffic during a stalled rollout. It does not establish behavior for all clients or an entire production load profile.",
            "Name the sampling interval, the per-sample result and the error count; a single final readback cannot satisfy this list.",
        ),
    ],
    revision,
    """
def main():
    mixed={'generation':5,'observed':5,'updated':2,'new_ready':0,'old_ready':2,'marker':'A'}
    assert mixed['observed']==mixed['generation'] and mixed['old_ready']==2
    assert not (mixed['new_ready']==2 and mixed['marker']=='B')
    restored={'generation':6,'observed':6,'ready':2,'marker':'A'}
    assert restored['generation']>mixed['generation'] and restored['marker']=='A'
    print('k8s-013 synthetic rollout/rollback reasoning passed; no live update performed')

if __name__ == "__main__":
    main()
""",
    capability="stateful owned rollout/recovery; separately qualified image-version rehearsal",
    refs=[
        "[Kubernetes Deployment rollout behavior](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/)"
    ],
)

author(
    14,
    """The beginner capstone assembles a stateless service from a Deployment, a Service and a ConfigMap, then verifies the application through a bounded client Job. Each component solves a different problem: the Deployment maintains replicas, the Service selects and routes, the ConfigMap supplies synthetic data, and the client observes the resulting HTTP contract.

The current browser source is a complete admitted contract-2 resource set. Its one-shot execution can check controller convergence, owned Ready Pod identities, unique Service backends, version response and both configuration-consumption paths. It then removes only recorded owned UIDs. The six-task capstone also requires predictions, error analysis and a reviewable evidence packet, which are not automatically graded by process success.

A stateless fixture has no persistent application data to preserve, but identity and cleanup still matter. A same-name object created by another run is not yours to delete. The capstone includes a controlled selector or task failure so the learner can demonstrate that a wrong mechanism is rejected rather than merely collect a green status.""",
    [
        (
            "Connect intent to independent observations",
            """The desired set requests two replicas, app=hello selection, Service port 8080 and message reviewer. The API assigns UIDs. The Deployment controller and ReplicaSet create Pods, which pass readiness. EndpointSlices identify the eligible Pod targets. A fresh client then asks for version and message values through the Service.

Each link can fail independently. A ConfigMap can exist without being consumed, a Service can exist without matching backends, and a Ready Pod can serve an unexpected route or payload. The reference checks the precise UID sets and fixed response values rather than treating object count as application correctness.

The worker adds owner and Run-nonce labels and reserves cleanup time separately from work. It can reconcile an uncertain create response only when the object proves the same nonce. This means a failed request can still require cleanup, but an unrelated object is preserved.""",
        ),
        (
            "Review a useful failure and recovery packet",
            """Choose one bounded fault: wrong Service selector, wrong readiness path or the separate finite-task failure fixture. Predict the first expected failing check. Run it only through the admitted operation or a named host capability, retain the actual result, and repair only the relevant source field.

A new one-shot Run creates new object identities after the old run cleaned up. Compare semantic intent and outcomes while keeping those identities separate. Do not claim that the repaired run patched a retained resource unless a stateful capability actually did that.

The handoff packet contains desired source, nonsecret lease identity, observed UIDs/generations, backend UID set, client results, failure classification and cleanup outcome. Another learner should be able to reproduce the finite scenario and understand what remains unqualified.""",
        ),
        (
            "Keep capstone acceptance bounded",
            """A passed fixture does not establish production capacity, high availability, network policy enforcement or persistence. It proves the observed owned synthetic service contract under the qualified runtime. Written ownership reasoning and the chosen negative case remain part of the learning evidence.

Do not export private kubeconfigs or fabricate cleanup from a missing browser page. If cleanup cannot be proved, retain the private recovery receipt and identify the remaining object rather than deleting all similarly named resources.""",
        ),
    ],
    [
        (
            "Trace the complete positive packet",
            """Synthetic packet: desired 2, observed generation matches, Ready UIDs {p1, p2}, ready endpoint UIDs {p1, p2}, version ds60-fixture-v1, environment reviewer, file reviewer, recorded cleanup UIDs all absent afterward.""",
            "All declared controller, routing, application-value and cleanup checks agree.",
        ),
        (
            "Reject a plausible false success",
            """The Service exists and two Pods are Running, but its selector is app=wrong and ready endpoint set is empty. A copied version string in notes is not a fresh client result.""",
            "The routing/application contract fails despite object creation and process phase.",
        ),
    ],
    [
        (
            "Review the complete desired set",
            "The starter is the k8s-008 Deployment and Service without configuration. Add hello-config (message: reviewer) with its environment and read-only volume consumers, then explain the purpose and references of ConfigMap, Deployment and Service before Run.",
            "Two replicas, matching app labels, fixed port chain and both message consumers are identified.",
            "Draw the references and distinguish them from ownership.",
            "The source graph predicts how data and traffic should flow. It does not supply server-assigned UIDs or prove that controllers acted. Those observations belong in the later receipt.",
            "Draw each reference as an arrow labelled with the field that creates it (selector, configMapKeyRef or volume name); none of these arrows is an ownerReference.",
        ),
        (
            "Establish controller ownership",
            "Observe desired/updated/ready state and the Deployment-to-ReplicaSet-to-Pod UID chain.",
            "Exactly two owned Ready Pod identities for the intended generation.",
            "Count only after verifying identity relationships.",
            "A matching label or raw Pod count is insufficient. The capstone needs the controller graph so unrelated resources cannot satisfy the desired replica claim.",
            "Check that the owned Pod UIDs in the Run result belong to the Deployment's current ReplicaSet and that there are exactly two of them.",
        ),
        (
            "Verify routing and values",
            "Compare ready endpoint UIDs and fresh client responses with the fixed contract.",
            "UID sets match; version and both message values are exact.",
            "Read application values independently from readiness.",
            "The client test closes a different boundary from controller status. It verifies that traffic reaches the expected fixture through the Service and that configuration is visible at the application layer.",
            "Compare the endpoint UID set with the owned Ready Pod UID set, then compare each response body with the fixed contract.",
        ),
        (
            "Inject one bounded fault",
            "Predict and run one admitted selector/probe/task negative case.",
            "The named check fails within budget and cleanup still targets only owned UIDs.",
            "Change one field and keep the original prediction.",
            "The negative case demonstrates sensitivity to a plausible error. It is useful even when failure is expected, provided the result is not mislabeled as a successful service. Keep runtime phase and cleanup evidence together.",
            "Write the prediction before the Run and confirm that the failed check is the one you predicted; cleanup must still list only this Run's UIDs.",
        ),
        (
            "Repair and compare a fresh run",
            "Restore the relevant field and execute a new bounded operation.",
            "The intended checks pass with new actual resource identities.",
            "Do not reuse old UIDs or claim an in-place update.",
            "Because the browser cleans every Run, the repaired scenario is a new creation. Comparing the source change and resulting checks explains the mechanism without inventing a stateful transition.",
            "Confirm that every UID in the second Run differs from the first Run and that the previously failing check now passes.",
        ),
        (
            "Hand off acceptance and limits",
            "Prepare the finite service packet for a second learner.",
            "Source, nonsecret target identity, controller/backend/client/failure/cleanup evidence and unqualified surfaces are explicit.",
            "Separate what was requested, observed and inferred.",
            "A good handoff is reproducible and bounded. It should let the reviewer see why a wrong selector failed and why the repaired service passed, while preserving privacy and avoiding unsupported production or recurrence claims.",
            "Ask a second learner to locate the evidence for each claim using your packet alone; any claim they cannot locate is an unsupported inference.",
        ),
    ],
    configured,
    """
def main():
    ready={'p1','p2'};endpoints={'p1','p2'}
    responses={'version':'ds60-fixture-v1','environment':'reviewer','file':'reviewer'}
    assert ready==endpoints and len(ready)==2
    assert responses=={'version':'ds60-fixture-v1','environment':'reviewer','file':'reviewer'}
    assert set()!=ready
    created={'cm-uid','dep-uid','svc-uid','client-uid'};deleted=set(created)
    assert created==deleted and 'replacement-uid' not in deleted
    print('k8s-014 synthetic capstone evidence checks passed; no runtime acceptance fabricated')

if __name__ == "__main__":
    main()
""",
    browser=True,
    starter=hello(True),
    starter_note="The learner starter omits the configuration objects; Exercise 1 asks you to assemble the complete desired set before Run. ",
    capability="bounded contract-2 stateless-service capstone",
    refs=[
        "[Kubernetes Services](https://kubernetes.io/docs/concepts/services-networking/service/)",
        "[Kubernetes ConfigMaps](https://kubernetes.io/docs/concepts/configuration/configmap/)",
    ],
)
