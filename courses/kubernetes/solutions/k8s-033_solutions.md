# k8s-033: Explanatory solutions

These answers explain the stated synthetic and scoped runtime contracts. Static checks do not prove cluster acceptance.

## Mechanism

Horizontal Pod Autoscaling changes a workload's desired replica count using observed metrics and a declared target. It is a feedback loop: measure, compare, choose a desired count, then wait for workload and metrics observations to reflect the change. The extra Pods are not instantaneous capacity, and CPU load is not the same thing as business demand or response-time quality.

This example uses CPU utilization relative to CPU requests. If a Pod requests 100m and uses50m, its utilization for that resource is50 percent. Changing the request to200m while leaving usage 50m changes the ratio to25 percent. A request is therefore part of the autoscaling model as well as a scheduling input. An absent metric is unavailable evidence, not a zero-load observation.

The supplied HPA uses autoscaling/v2, targets Deployment hello, and limits replicas to1 through 2. It requires a qualified metrics API path and a host-provided bounded load generator. The basic module fixture has no such qualification. Its fast HTTP handler is useful for service checks, but arbitrary traffic against it must not be presented as a reliable CPU scaling experiment.

## Exercise 1: Calculate request-relative utilization

The same measured CPU use can lead to different utilization ratios when requests change. This explains why tuning requests changes both scheduling commitments and autoscaling behavior, and why units must be recorded.

**Expected:** 50 percent and25 percent respectively.

## Exercise 2: Apply the ideal formula

The proportional model scales count according to the demand ratio. It is useful for understanding the direction and approximate magnitude, while controller safeguards and incomplete measurements can alter the actual action.

**Expected:** Unclipped recommendations2 and1.

## Exercise 3: Recognize saturation at the maximum

The HPA can be operating exactly as configured while failing to meet latency or throughput needs. Report the bound and observed application performance instead of equating a stable count with success.

**Expected:** Ideal4, configured maximum 2; capacity adequacy remains unproven.

## Exercise 4: Diagnose missing metrics

The denominator requests and the metrics supply must both be valid. The appropriate response is to inspect the declared host capability and conditions, not to fabricate a low-utilization sample or widen the learner credential.

**Expected:** Unknown load, with a qualified metrics-path investigation.

## Exercise 5: Observe a bounded live step

The observation chain exposes delays and failures. A desired count of2 with only one ready Pod is incomplete capacity expansion, and a load generator reaching its own limit can also distort interpretation.

**Expected:** Timestamped transitions within declared ranges and deadline, not an exact scaling second.

## Exercise 6: Explain stabilization and stop

Stabilization deliberately avoids reacting to every temporary dip. The final packet should preserve metrics freshness, bounded workload settings and application evidence so another reader can understand the scope of the observed behavior.

**Expected:** Reasoned delay explanation and confirmed load termination; no production sizing claim.

## Boundary and troubleshooting review

Use the host-provided fixed load duration, request concurrency and stop limit in an exclusive lease. Record metrics API health, per-Pod requests, sample timestamps and HPA conditions. Define a permissible range and deadline rather than an exact transition second. Stop if the load exceeds the lesson resource budget or the target identity changes.

If metrics are missing, preserve the unavailable condition and fix the qualified measurement path. Do not report zero utilization, remove resource requests to silence a warning or install a metrics component from the learner pad. A single successful scaling step does not establish production sizing, cost efficiency or stability under all workloads.
