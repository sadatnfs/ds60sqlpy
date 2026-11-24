# k8s-033: Explanatory solutions

These answers explain the stated synthetic and scoped runtime contracts. Static checks do not prove cluster acceptance.

## Mechanism

Horizontal Pod Autoscaling changes a workload's desired replica count using observed metrics and a declared target. It is a feedback loop: measure, compare, choose a desired count, then wait for workload and metrics observations to reflect the change. The extra Pods are not instantaneous capacity, and CPU load is not the same thing as business demand or response-time quality.

This example uses CPU utilization relative to CPU requests. If a Pod requests 100m and uses 50m, its utilization for that resource is 50 percent. Changing the request to 200m while leaving usage 50m changes the ratio to 25 percent. A request is therefore part of the autoscaling model as well as a scheduling input. An absent metric is unavailable evidence, not a zero-load observation.

The supplied HPA uses autoscaling/v2, targets Deployment hello, and limits replicas to 1 through 2. It requires a qualified metrics API path and a host-provided bounded load generator. The basic module fixture has no such qualification. Its fast HTTP handler is useful for service checks, but arbitrary traffic against it must not be presented as a reliable CPU scaling experiment.

## Exercise 1: Calculate request-relative utilization

The same measured CPU use can lead to different utilization ratios when requests change. This explains why tuning requests changes both scheduling commitments and autoscaling behavior, and why units must be recorded.

**Expected:** 50 percent and 25 percent respectively.

**Solution reasoning**

- **Approach:** Divide 50m usage by each Pod's CPU request and convert to percent.
- **Why it is correct:** HPA utilization is measured against requests, so 50m over 100m is 50 percent and over 200m is 25 percent.
- **Plausible wrong approach:** Dividing by the limit gives a lower utilization and a smaller scaling recommendation.
- **How to verify:** The two results are 50 percent and 25 percent.

## Exercise 2: Apply the ideal formula

The proportional model scales count according to the demand ratio. It is useful for understanding the direction and approximate magnitude, while controller safeguards and incomplete measurements can alter the actual action.

**Expected:** Unclipped recommendations 2 and 1.

**Solution reasoning**

- **Approach:** Compute current times observed over target, then take the ceiling.
- **Why it is correct:** 1 times 80 over 50 is 1.6, rounded up to 2; 2 times 20 over 50 is 0.8, rounded up to 1.
- **Plausible wrong approach:** Rounding to the nearest integer would give 2 and 1 here but fails for values like 1.2, where the HPA rounds up to 2.
- **How to verify:** The unclipped recommendations are 2 and 1.

## Exercise 3: Recognize saturation at the maximum

The HPA can be operating exactly as configured while failing to meet latency or throughput needs. Report the bound and observed application performance instead of equating a stable count with success.

**Expected:** Ideal 4, configured maximum 2; capacity adequacy remains unproven.

**Solution reasoning**

- **Approach:** Compute 1 times 200 over 50 and compare with maxReplicas.
- **Why it is correct:** The ideal is 4, but the HPA clamps to maxReplicas 2, so the workload may stay overloaded.
- **Plausible wrong approach:** Reading 2 replicas at maximum as sufficient capacity assumes the cap matched the load.
- **How to verify:** Ideal 4, capped 2, and the answer says capacity is unproven.

## Exercise 4: Diagnose missing metrics

The denominator requests and the metrics supply must both be valid. The appropriate response is to inspect the declared host capability and conditions, not to fabricate a low-utilization sample or widen the learner credential.

**Expected:** Unknown load, with a qualified metrics-path investigation.

**Solution reasoning**

- **Approach:** Read the ScalingActive condition and its reason, then investigate the metrics path.
- **Why it is correct:** When the metric is unavailable the HPA cannot compute a recommendation and leaves replicas unchanged.
- **Plausible wrong approach:** Treating the missing metric as zero load would predict a scale down that does not happen.
- **How to verify:** The condition reason is quoted, and no value is invented for the metric.

## Exercise 5: Observe a bounded live step

The observation chain exposes delays and failures. A desired count of 2 with only one ready Pod is incomplete capacity expansion, and a load generator reaching its own limit can also distort interpretation.

**Expected:** Timestamped transitions within declared ranges and deadline, not an exact scaling second.

**Solution reasoning**

- **Approach:** Tabulate sample time, desired replicas, ready replicas and request result during the fixed load.
- **Why it is correct:** Desired changes when the HPA reacts and ready changes later when Pods pass readiness, so both are needed.
- **Plausible wrong approach:** Quoting the exact second scaling occurred claims precision the sampling interval cannot provide.
- **How to verify:** Each row falls inside the declared range and deadline.

## Exercise 6: Explain stabilization and stop

Stabilization deliberately avoids reacting to every temporary dip. The final packet should preserve metrics freshness, bounded workload settings and application evidence so another reader can understand the scope of the observed behavior.

**Expected:** Reasoned delay explanation and confirmed load termination; no production sizing claim.

**Solution reasoning**

- **Approach:** Quote the scale down stabilization window from behavior and confirm the load process stopped.
- **Why it is correct:** The HPA keeps the highest recommendation over the window, so replicas fall only after it passes.
- **Plausible wrong approach:** Calling the slow scale down a bug ignores the configured window that causes it.
- **How to verify:** The window value is quoted, the load end is recorded and no production sizing is claimed.

## Boundary and troubleshooting review

Use the host-provided fixed load duration, request concurrency and stop limit in an exclusive lease. Record metrics API health, per-Pod requests, sample timestamps and HPA conditions. Define a permissible range and deadline rather than an exact transition second. Stop if the load exceeds the lesson resource budget or the target identity changes.

If metrics are missing, preserve the unavailable condition and fix the qualified measurement path. Do not report zero utilization, remove resource requests to silence a warning or install a metrics component from the learner pad. A single successful scaling step does not establish production sizing, cost efficiency or stability under all workloads.
