# k8s-015: Explanatory solutions

These answers explain the stated synthetic and scoped runtime contracts. Static checks do not prove cluster acceptance.

## Mechanism

Startup, readiness and liveness probes answer different questions. Startup asks whether initialization has completed. Readiness asks whether this container should currently receive normal Service traffic. Liveness asks whether the container should be restarted after repeated failed checks. One endpoint can be used for several probes, but that does not make their control effects identical.

The contract-2 fixture exposes /startup, /ready and /live as separate fixed paths. A synthetic three-second startup delay makes /startup temporarily return 503 while the process exists. Once a configured startup probe succeeds, the kubelet begins the normal liveness/readiness behavior. The healthy browser source is a bounded initial-state demonstration; detailed restart-count and transient-unreadiness comparisons require stateful host observations.

A probe is an operational policy about recovery and traffic. An expensive or dependency-sensitive liveness check can restart a healthy process during a downstream outage. A readiness check can remove traffic without restarting the container. Choose the intended effect before choosing a URL.

## Exercise 1: Name each question

The same HTTP status can trigger different effects depending on which probe consumed it. The lesson is about those controller/kubelet policies rather than treating health as one undifferentiated Boolean.

**Expected:** Initialization gate, traffic eligibility and restart policy are distinguished.

**Solution reasoning**

- **Approach:** For each probe, name the component that acts on failure and the action it takes.
- **Why it is correct:** Startup failure past its threshold kills the container, readiness failure removes the Pod from endpoints and liveness failure restarts the container.
- **Plausible wrong approach:** Treating all three as one health flag would predict a restart for a readiness failure, which never restarts anything.
- **How to verify:** Three different actions are listed: gate later probes, withhold traffic, restart.

## Exercise 2: Run the healthy delayed fixture

The fixture and probe are deliberately finite. A successful initial run supports that observed startup/readiness path under the qualified environment, but not a universal initialization duration or all later liveness behavior.

**Expected:** Startup delay is configured 3; controller/backend/client checks eventually establish the observed healthy baseline.

**Solution reasoning**

- **Approach:** Add the delay variable and both probes, compute the startup budget, then Run.
- **Why it is correct:** The startupProbe allows 1 times 10 equals 10 seconds, more than the 3-second delay, and liveness only begins after startup succeeds.
- **Plausible wrong approach:** Putting failureThreshold 2 on the startupProbe would give 2 seconds, so the kubelet would kill the container before /startup ever succeeds.
- **How to verify:** Configured budget 10 seconds exceeds delay 3, and observed times are reported separately.

## Exercise 3: Trace readiness removal

A readiness failure can stop normal Service selection while the process remains alive. Recovery should be shown at the routing/application boundary, not inferred from the fact that the container never exited.

**Expected:** No direct restart claim; new Ready/endpoint/client observations are required after repair.

**Solution reasoning**

- **Approach:** Classify case A as a readiness failure and list the recovery evidence it would need.
- **Why it is correct:** Readiness failure only removes the Pod from EndpointSlices; the container keeps running with the same restartCount.
- **Plausible wrong approach:** Expecting a restart and waiting for restartCount to change watches the wrong field.
- **How to verify:** The answer cites a Ready condition change and an endpoint or client observation, not a restart.

## Exercise 4: Trace liveness restart

Liveness can restart a container inside an existing Pod. Its ephemeral volumes may therefore have different lifetime behavior from a new Pod, which the next chapter examines.

**Expected:** Same Pod UID with increased container restartCount.

**Solution reasoning**

- **Approach:** Compare Pod UID and restartCount between the two case B records.
- **Why it is correct:** A liveness failure makes the kubelet restart the container inside the same Pod, so UID stays and restartCount increases.
- **Plausible wrong approach:** Calling it a replacement would expect a new UID and a reset count, neither of which appears.
- **How to verify:** UID is identical and restartCount went up by at least one.

## Exercise 5: Predict a wrong fixed path

The source remains inside the allowlist but requests a deliberately failing check. Depending on the observed window, the operation can show waiting, restarts or failure; the evidence should identify the phase and not overclaim a deterministic schedule.

**Expected:** The wrong path returns 404; the actual bounded result and cleanup must be recorded rather than inventing a fixed timing.

**Solution reasoning**

- **Approach:** Change one probe path to /missing in a scratch copy, Run it and record what the bounded result actually shows.
- **Why it is correct:** /missing returns 404, so a startup or liveness probe on it fails, but how many restarts or how long depends on timing you must observe.
- **Plausible wrong approach:** Writing a fixed failure time from periodSeconds alone invents a measurement the result never contained.
- **How to verify:** The record holds the actual Run outcome and cleanup and no unobserved timing.

## Exercise 6: Choose a production probe policy

A liveness policy should target failures restart can plausibly resolve. Readiness can withhold traffic while preserving the process. The correct policy depends on application behavior and measured recovery evidence, not this fixture's three-second value.

**Expected:** A concrete design separates process-deadlock detection from traffic readiness and dependency behavior.

**Solution reasoning**

- **Approach:** Reserve liveness for states a restart fixes, such as a deadlock, and route dependency outages to readiness or degraded responses.
- **Why it is correct:** Restarting every caller during a database outage adds cold starts without restoring the dependency.
- **Plausible wrong approach:** Making liveness call the downstream dependency would restart every replica at once during that outage.
- **How to verify:** The policy restarts only for repairable local failures and changes readiness or behavior for dependency loss.

## Boundary and troubleshooting review

Do not use a remote dependency check as liveness merely because it is convenient: restarting every caller may amplify the dependency outage. Do not call a Running Pod ready or assume a successful startup probe means all future requests succeed. A startup success is an initial milestone; readiness and liveness continue to have distinct roles.

A source change alone is not evidence that the kubelet used the intended probe. Observe the current Pod template and identity, then the relevant conditions/events/restart counts. Preserve the bounded cleanup result even for an intentionally unhealthy configuration.
