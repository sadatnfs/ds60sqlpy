# k8s-010: Explanatory solutions

These answers explain the stated synthetic and scoped runtime contracts. Static checks do not prove cluster acceptance.

## Mechanism

A resource request describes the capacity used for scheduling and accounting. A limit constrains runtime use under the relevant resource mechanism. A namespace quota is an admission budget across objects. These operate at different stages, so Pending, Forbidden and OOMKilled are not interchangeable symptoms.

CPU quantities such as 100m are millicores: 100m is 0.1 CPU. Memory Mi is a binary unit: 64Mi is \(64\times2^{20}\) bytes. The browser admits bounded positive millicore and Mi quantities and requires requests no greater than limits. That narrow grammar is not a complete implementation of every Kubernetes quantity syntax.

The allowed source runs the small server with modest requests and limits. Quota and deliberate memory-failure experiments require a teacher-provided bounded host fixture; the current worker does not create ResourceQuotas or install a metrics stack. A source-validation refusal must remain distinct from an actual admission, scheduling or runtime observation.

## Exercise 1: Read requests versus limits

The fields describe different contracts. A request is not a measured usage value, and a limit is not a guaranteed reservation. Preserve the configured values alongside actual runtime evidence when diagnosing performance.

**Expected:** Starter requests 100m/64Mi equal its limits; the edited source keeps limits 100m/64Mi with requests 10m/16Mi. Requests influence placement and quota; limits constrain runtime use.

**Solution reasoning**

- **Approach:** Read requests and limits as two mappings, note they start equal at 100m and 64Mi, then edit only the requests to 10m and 16Mi.
- **Why it is correct:** The scheduler and ResourceQuota sum requests, while the kubelet and runtime enforce limits, so lowering requests changes placement but keeps the same ceiling.
- **Plausible wrong approach:** Lowering limits instead would tighten the runtime ceiling and risk an OOM kill at 16Mi without changing anything the scheduler sees.
- **How to verify:** The edited source shows requests 10m/16Mi and limits 100m/64Mi, and the scheduler is named as the requests reader.

## Exercise 2: Calculate the replica budget

Binary memory units use powers of two. Include extra clients or rollout surge Pods in a real quota calculation. A count of desired application replicas alone can understate total namespace resource use.

**Expected:** 20m CPU, 32Mi memory and 67,108,864 bytes for 64Mi.

**Solution reasoning**

- **Approach:** Multiply each request by spec.replicas, then expand 64Mi with powers of two.
- **Why it is correct:** Two replicas at 10m and 16Mi request 20m and 32Mi, and 64 times 1,048,576 is 67,108,864 bytes.
- **Plausible wrong approach:** Using decimal megabytes gives 64,000,000 bytes, which disagrees with the Mi suffix and with the offline check.
- **How to verify:** The numbers match the assertions in the offline check script exactly.

## Exercise 3: Reject invalid source budgets

This is source admission by the course adapter. It does not establish that Kubernetes scheduled or killed a Pod. The distinction keeps a local validation error from being confused with runtime resource exhaustion.

**Expected:** Broker refuses requests greater than limits before creating resources.

**Solution reasoning**

- **Approach:** Set request 200m and limit 100m in a scratch source and submit it.
- **Why it is correct:** A request above its limit is invalid, and the course broker refuses it before any API call, so no Pod is created or scheduled.
- **Plausible wrong approach:** Reading the refusal as a scheduling failure assumes the Pod reached the scheduler, but no object exists to schedule.
- **How to verify:** The result shows the refusal text and no created resource UID.

## Exercise 4: Diagnose quota versus scheduling

Quota rejection can occur before a runnable Pod exists. Scheduling failure means an accepted Pod lacks a suitable placement. Looking only for readiness or application logs can miss both causes.

**Expected:** Admission budget versus scheduler placement, with separate minimal investigations.

**Solution reasoning**

- **Approach:** Ask first whether the Pod object was admitted, then whether spec.nodeName was set.
- **Why it is correct:** A Forbidden exceeded quota error comes from admission before the Pod exists, while Pending with FailedScheduling means the Pod exists but no node fits its requests.
- **Plausible wrong approach:** Reading container logs for either record finds nothing, because in neither case did a container start.
- **How to verify:** Quota maps to admission with no object; FailedScheduling maps to an admitted Pod with empty nodeName.

## Exercise 5: Interpret memory failure

An exit code can have multiple causes. The reason field and contextual evidence narrow the diagnosis. The lesson does not authorize unbounded memory stress or changing node-wide settings.

**Expected:** OOMKilled is specific memory-enforcement evidence; exit 137 alone is insufficient to prove that cause.

**Solution reasoning**

- **Approach:** Look for reason OOMKilled in state.terminated or lastState.terminated before interpreting exit code 137.
- **Why it is correct:** OOMKilled is set when the container exceeded its memory limit, whereas 137 only says the process received SIGKILL, which several causes produce.
- **Plausible wrong approach:** Calling every 137 an OOM kill and raising the memory limit could hide a liveness kill or an external termination.
- **How to verify:** Only the record carrying reason OOMKilled is classified as memory enforcement; the bare 137 stays unconfirmed.

## Exercise 6: Plan a bounded repair

A useful repair targets the observed mechanism. It should state what new evidence would confirm recovery and remain within the owned resource budget. A Ready Pod after a broad set of changes does not explain which change fixed the problem.

**Expected:** One justified source/resource change, phase-specific success evidence and owned cleanup.

**Solution reasoning**

- **Approach:** Choose one failure record, change exactly one field that addresses its mechanism and state acceptance in terms of the failed stage.
- **Why it is correct:** A quota failure clears when requests fit the quota, a scheduling failure when a node can fit the request, and an OOM kill when usage stays under the limit.
- **Plausible wrong approach:** Raising every request and limit at once may make the Pod Ready but cannot show which change fixed it and may exceed the namespace budget.
- **How to verify:** The diff touches one field and acceptance names admission, placement or termination reason as the observed recovery.

## Boundary and troubleshooting review

FailedScheduling with insufficient CPU points to placement capacity; an admission Forbidden message naming quota points to a namespace budget; lastState.terminated.reason=OOMKilled points to runtime memory enforcement. All may result in no ready backend, but that final symptom is too broad to choose a repair.

Changing a readiness path does not fix quota or missing capacity. Increasing limits without understanding the failure can move the problem or violate the lab budget. Record a minimal justified change and verify the affected phase before claiming application recovery.
