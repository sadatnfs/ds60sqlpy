# k8s-040: Explanatory solutions

These answers explain the stated synthetic and scoped runtime contracts. Static checks do not prove cluster acceptance.

## Mechanism

An incident investigation turns a symptom into a testable explanation and a bounded repair. The first useful question is not which command might make the red status disappear, but which observation would distinguish the leading hypotheses. A Service timeout with healthy Pods can result from selectors, ports, network policy or the application path. Restarting every Pod changes evidence without necessarily testing any of those causes.

This chapter injects one synthetic fault: a host-controlled change to the selector of the exact owned Service. The workload remains Ready, but the Service no longer selects it. The investigator records a baseline, the symptom, endpoint/selector evidence, a conditional repair and a post-repair application check. A separate teacher may reveal the chosen fault only after the learner has formed a hypothesis.

The normal browser adapter can demonstrate bounded failures but does not offer an unrestricted fault-injection API or persistent arbitrary edits. The advanced exercise requires an exclusive lease and a fixed host action with a deadline, cancellation, exact target UID and restoration record. No unrelated namespace, Node or cluster setting is changed.

## Exercise 1: Record the baseline

The baseline makes the experiment interpretable. It should identify the exact Service and Pod identities rather than only their names, because replacement during the exercise changes the scope of the repair.

**Expected:** A connected selection graph and successful application control.

**Solution reasoning**

- **Approach:** Capture selector, Pod label, endpoint count and a successful request before the fault.
- **Why it is correct:** A healthy baseline makes a later zero endpoint count meaningful as a change.
- **Plausible wrong approach:** Starting evidence after the fault leaves no record of what worked.
- **How to verify:** The baseline has a successful request and the pre-change endpoint count.

## Exercise 2: Form competing hypotheses

The hypotheses connect symptoms to mechanisms. A Ready Pod weakens some crash explanations, zero selected endpoints points toward selection, and a populated endpoint with a wrong port suggests another branch. No single symptom proves every detail.

**Expected:** Three specific evidence checks rather than a generic restart.

**Solution reasoning**

- **Approach:** For crash, selector mismatch and targetPort mismatch, name the observation that would differ.
- **Why it is correct:** A crash raises restartCount, a selector mismatch empties endpoints with Pods still Ready, and a targetPort mismatch keeps endpoints but refuses connections.
- **Plausible wrong approach:** Restarting the Pods to see what happens tests none of the three and destroys evidence.
- **How to verify:** Each hypothesis has one distinguishing observation.

## Exercise 3: Interpret the supplied timeline

The controlled one-fault trace supports a narrow causal explanation. In a real incident, the same correlation would require checking concurrent changes and alternative causes rather than assuming the teacher-supplied synthetic control conditions.

**Expected:** Selector changes at 10; zero endpoints observed at 15 while readiness remains 1.

**Solution reasoning**

- **Approach:** Find the selector change time and the first observation of its effect separately.
- **Why it is correct:** The selector changed at 10 and zero endpoints appeared at 15 while readiness stayed 1, which points at selection.
- **Plausible wrong approach:** Reading readiness 1 as healthy service ignores that no endpoint selects the Ready Pod.
- **How to verify:** Change at 10, first supporting observation at 15.

## Exercise 4: Apply the minimal bounded repair

The repair should preserve unrelated fields and respect optimistic concurrency. A stale whole-object replacement risks undoing another legitimate change, while a name-only update risks modifying an unrelated replacement.

**Expected:** Owned svc-1 repaired; replacement UID causes refusal.

**Solution reasoning**

- **Approach:** Read the Service UID and resourceVersion, then restore the verified selector with that precondition.
- **Why it is correct:** The precondition makes the write fail if svc-1 was replaced or changed since the read.
- **Plausible wrong approach:** Applying the old manifest unconditionally would overwrite a replacement Service.
- **How to verify:** svc-1 is repaired, and a replaced UID causes refusal.

## Exercise 5: Verify application recovery

This check demonstrates the route works again for the observed request path. If the response still fails, the incident remains open even when the update command succeeded or the Pods were Ready throughout.

**Expected:** One endpoint and expected payload, with actual timestamps if live.

**Solution reasoning**

- **Approach:** Read the endpoint list and a Service response after the repair, each timestamped.
- **Why it is correct:** One endpoint and the expected payload show selection and the application both recovered.
- **Plausible wrong approach:** Checking only the selector field confirms the write, not that traffic flows.
- **How to verify:** One endpoint and the expected payload appear with timestamps.

## Exercise 6: Write the review and stop conditions

The review should teach how the failure was detected and repaired, and where the experiment stops. It should preserve evidence of a failed or cancelled repair rather than converting every exercise into an assumed success story.

**Expected:** A timestamped bounded incident packet with no unsupported broad resilience claim.

**Solution reasoning**

- **Approach:** Summarize cause, evidence, repair, preserved state and what remains uncertain.
- **Why it is correct:** A bounded packet lets reviewers check each claim and see what was not ruled out.
- **Plausible wrong approach:** Concluding the service is now resilient generalizes one repaired fault to all faults.
- **How to verify:** The packet contains all five parts and no broad resilience claim.

## Boundary and troubleshooting review

The host operation must know how to restore its own change, including on cancellation or deadline. It should stop if the target UID changes or unrelated state would be affected. Do not broaden the fault into a node outage, policy deletion or credential change to make the lesson more dramatic.

The post-incident review explains contributing conditions and detection gaps without inventing a root cause unsupported by the trace. A finite recovery can validate this selector-repair path; it does not prove resilience to every outage or that the failure will never recur.
