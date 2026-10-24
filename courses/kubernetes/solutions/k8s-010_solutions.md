# k8s-010: Explanatory solutions

These answers explain the stated synthetic and scoped runtime contracts. Static checks do not prove cluster acceptance.

## Mechanism

A resource request describes the capacity used for scheduling and accounting. A limit constrains runtime use under the relevant resource mechanism. A namespace quota is an admission budget across objects. These operate at different stages, so Pending, Forbidden and OOMKilled are not interchangeable symptoms.

CPU quantities such as 100m are millicores: 100m is 0.1 CPU. Memory Mi is a binary unit: 64Mi is \(64\times2^{20}\) bytes. The browser admits bounded positive millicore and Mi quantities and requires requests no greater than limits. That narrow grammar is not a complete implementation of every Kubernetes quantity syntax.

The allowed source runs the small server with modest requests and limits. Quota and deliberate memory-failure experiments require a teacher-provided bounded host fixture; the current worker does not create ResourceQuotas or install a metrics stack. A source-validation refusal must remain distinct from an actual admission, scheduling or runtime observation.

## Exercise 1: Read requests versus limits

The fields describe different contracts. A request is not a measured usage value, and a limit is not a guaranteed reservation. Preserve the configured values alongside actual runtime evidence when diagnosing performance.

**Expected:** 10m/16Mi requests and100m/64Mi limits in the baseline; requests influence placement, limits constrain runtime.

## Exercise 2: Calculate the replica budget

Binary memory units use powers of two. Include extra clients or rollout surge Pods in a real quota calculation. A count of desired application replicas alone can understate total namespace resource use.

**Expected:** 20m CPU, 32Mi memory and67, 108, 864 bytes for64Mi.

## Exercise 3: Reject invalid source budgets

This is source admission by the course adapter. It does not establish that Kubernetes scheduled or killed a Pod. The distinction keeps a local validation error from being confused with runtime resource exhaustion.

**Expected:** Broker refuses requests greater than limits before creating resources.

## Exercise 4: Diagnose quota versus scheduling

Quota rejection can occur before a runnable Pod exists. Scheduling failure means an accepted Pod lacks a suitable placement. Looking only for readiness or application logs can miss both causes.

**Expected:** Admission budget versus scheduler placement, with separate minimal investigations.

## Exercise 5: Interpret memory failure

An exit code can have multiple causes. The reason field and contextual evidence narrow the diagnosis. The lesson does not authorize unbounded memory stress or changing node-wide settings.

**Expected:** OOMKilled is specific memory-enforcement evidence; exit137 alone is insufficient to prove that cause.

## Exercise 6: Plan a bounded repair

A useful repair targets the observed mechanism. It should state what new evidence would confirm recovery and remain within the owned resource budget. A Ready Pod after a broad set of changes does not explain which change fixed the problem.

**Expected:** One justified source/resource change, phase-specific success evidence and owned cleanup.

## Boundary and troubleshooting review

FailedScheduling with insufficient CPU points to placement capacity; an admission Forbidden message naming quota points to a namespace budget; lastState.terminated.reason=OOMKilled points to runtime memory enforcement. All may result in no ready backend, but that final symptom is too broad to choose a repair.

Changing a readiness path does not fix quota or missing capacity. Increasing limits without understanding the failure can move the problem or violate the lab budget. Record a minimal justified change and verify the affected phase before claiming application recovery.
