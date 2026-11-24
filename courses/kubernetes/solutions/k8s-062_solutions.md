# k8s-062: explanatory solutions

Compare after your own attempt or an explicit reveal. These explanations describe the synthetic topology and stated API contracts. They are not fabricated runtime receipts.

## Mechanism review

Startup, readiness and liveness probes answer different questions. A startup probe can allow an application time to initialize before other probe behavior begins. Readiness indicates whether the Pod should receive ordinary new traffic. Liveness asks whether restarting the container is an appropriate recovery action.

A dependency outage is not always a reason to restart every client. If a liveness check fails whenever a database is briefly unavailable, the system can create a restart storm without repairing the database. Probe design should reflect the application’s recovery capabilities and failure modes.

Graceful termination coordinates endpoint eligibility, connection draining and process shutdown. Removing readiness does not instantly terminate every existing connection or guarantee every proxy has updated. A rollout must account for propagation, in-flight requests, termination grace periods and the application’s own shutdown behavior.

Set probe paths, ports, timeouts and thresholds according to measured startup and request behavior. A failure threshold is not a proof that an application will recover by the next attempt. Keep startup allowance separate from a per-request deadline.

During a rollout, inspect desired generation, updated replicas, ready endpoints and actual responses from the intended revision. An old healthy replica can keep a Service responding while the new revision fails. A 200 response alone does not prove rollout completion.

## Exercise 1: Predict a readiness failure consequence.

Readiness and liveness are separate control signals. A temporary inability to serve need not mean the process is irrecoverable.

**Expected:** Ordinary new Service eligibility changes without necessarily restarting the container.

**Solution reasoning**

- **Approach:** Trace a failing readinessProbe to the Pod's Ready condition and its endpoint state.
- **Why it is correct:** Readiness failure removes the Pod from ready endpoints for new traffic, and only liveness failure restarts containers.
- **Plausible wrong approach:** Expecting a restart after readiness failure confuses it with a liveness probe.
- **How to verify:** The prediction says eligibility changes without a required restart.

## Exercise 2: Choose a startup allowance for a slow initializer.

Do not increase every timeout indiscriminately. Name the phase receiving the allowance.

**Expected:** A bounded measured initialization window with separate request deadlines.

**Solution reasoning**

- **Approach:** Measure initialization and set startupProbe failureThreshold times periodSeconds to cover it with a margin.
- **Why it is correct:** The startup probe holds off liveness checks until the app starts, without stretching normal request deadlines.
- **Plausible wrong approach:** Raising liveness initialDelaySeconds a lot slows detection of real hangs for the Pod's lifetime.
- **How to verify:** The window is bounded by measurement, and request deadlines stay separate.

## Exercise 3: Design a graceful shutdown timeline.

Account for propagation and existing connections. Application cleanup must fit the configured grace period.

**Expected:** Stop new work, drain bounded in-flight work and exit before forced termination.

**Solution reasoning**

- **Approach:** Order the steps as become unready, stop new work, drain in-flight work and exit before terminationGracePeriodSeconds.
- **Why it is correct:** After SIGTERM the kubelet waits for the grace period and then kills the container, so draining must finish first.
- **Plausible wrong approach:** Exiting on SIGTERM drops in-flight requests, while ignoring it ends in a forced kill.
- **How to verify:** The timeline ends before forced termination.

## Exercise 4: Diagnose 200 responses during a failed new rollout.

Old replicas can mask the failure. Preserve image and Pod identity in acceptance evidence.

**Expected:** Identify the serving revision and new-revision readiness separately.

**Solution reasoning**

- **Approach:** Identify which ReplicaSet served each response and check the new ReplicaSet's readiness.
- **Why it is correct:** A rolling update keeps old Pods serving while new ones fail readiness, so 200s can come from the old revision.
- **Plausible wrong approach:** Treating 200 responses as rollout success ignores which revision answered.
- **How to verify:** The answer names the serving revision and new-revision readiness separately.

## Exercise 5: Explain why database-dependent liveness can be harmful.

Choose probes according to recoverability. Cascading restarts can worsen an outage.

**Expected:** It may restart healthy clients without fixing the unavailable dependency.

**Solution reasoning**

- **Approach:** Show that a liveness probe that calls the database restarts the app whenever the database is down.
- **Why it is correct:** Restarting the client does not repair the dependency and adds load as restarted Pods reconnect.
- **Plausible wrong approach:** Checking dependencies in liveness to be thorough turns one outage into a restart loop.
- **How to verify:** The answer says it restarts healthy clients without fixing the dependency.

## Exercise 6: Define rollout traffic-continuity acceptance.

The complete claim includes revision identity and lifecycle behavior, not just a momentary successful request.

Consider a synthetic ten-second request already in progress when a thirty-second termination grace period begins. The app should stop admitting new work and let that request finish within its bounded drain policy. A preStop action consumes part of the same grace period, so sleeping for the entire allowance leaves no promised extra drain time. Observe the actual connection result and process termination rather than counting only Ready replicas.

**Expected:** Current revision becomes ready, expected responses succeed and old resources drain/clean up.

**Solution reasoning**

- **Approach:** Require that the new revision is ready, expected responses succeed and old Pods drain and are removed.
- **Why it is correct:** Each condition shows a different part of a clean rollout, from readiness to cleanup.
- **Plausible wrong approach:** Stopping at rollout status complete skips response evidence and leftover old resources.
- **How to verify:** The acceptance record covers readiness, responses and cleanup.
