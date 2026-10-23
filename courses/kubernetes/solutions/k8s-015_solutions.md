# k8s-015: Explanatory solutions

These answers explain the stated synthetic and scoped runtime contracts. Static checks do not prove cluster acceptance.

## Mechanism

Startup, readiness and liveness probes answer different questions. Startup asks whether initialization has completed. Readiness asks whether this container should currently receive normal Service traffic. Liveness asks whether the container should be restarted after repeated failed checks. One endpoint can be used for several probes, but that does not make their control effects identical.

The contract-2 fixture exposes /startup, /ready and /live as separate fixed paths. A synthetic three-second startup delay makes /startup temporarily return503 while the process exists. Once a configured startup probe succeeds, the kubelet begins the normal liveness/readiness behavior. The healthy browser source is a bounded initial-state demonstration; detailed restart-count and transient-unreadiness comparisons require stateful host observations.

A probe is an operational policy about recovery and traffic. An expensive or dependency-sensitive liveness check can restart a healthy process during a downstream outage. A readiness check can remove traffic without restarting the container. Choose the intended effect before choosing a URL.

## Exercise 1: Name each question

The same HTTP status can trigger different effects depending on which probe consumed it. The lesson is about those controller/kubelet policies rather than treating health as one undifferentiated Boolean.

**Expected:** Initialization gate, traffic eligibility and restart policy are distinguished.

## Exercise 2: Run the healthy delayed fixture

The fixture and probe are deliberately finite. A successful initial run supports that observed startup/readiness path under the qualified environment, but not a universal initialization duration or all later liveness behavior.

**Expected:** Startup delay is configured3; controller/backend/client checks eventually establish the observed healthy baseline.

## Exercise 3: Trace readiness removal

A readiness failure can stop normal Service selection while the process remains alive. Recovery should be shown at the routing/application boundary, not inferred from the fact that the container never exited.

**Expected:** No direct restart claim; new Ready/endpoint/client observations are required after repair.

## Exercise 4: Trace liveness restart

Liveness can restart a container inside an existing Pod. Its ephemeral volumes may therefore have different lifetime behavior from a new Pod, which the next chapter examines.

**Expected:** Same Pod UID with increased container restartCount.

## Exercise 5: Predict a wrong fixed path

The source remains inside the allowlist but requests a deliberately failing check. Depending on the observed window, the operation can show waiting, restarts or failure; the evidence should identify the phase and not overclaim a deterministic schedule.

**Expected:** The wrong path returns404; the actual bounded result and cleanup must be recorded rather than inventing a fixed timing.

## Exercise 6: Choose a production probe policy

A liveness policy should target failures restart can plausibly resolve. Readiness can withhold traffic while preserving the process. The correct policy depends on application behavior and measured recovery evidence, not this fixture's three-second value.

**Expected:** A concrete design separates process-deadlock detection from traffic readiness and dependency behavior.

## Boundary and troubleshooting review

Do not use a remote dependency check as liveness merely because it is convenient:restarting every caller may amplify the dependency outage. Do not call a Running Pod ready or assume a successful startup probe means all future requests succeed. A startup success is an initial milestone; readiness and liveness continue to have distinct roles.

A source change alone is not evidence that the kubelet used the intended probe. Observe the current Pod template and identity, then the relevant conditions/events/restart counts. Preserve the bounded cleanup result even for an intentionally unhealthy configuration.
