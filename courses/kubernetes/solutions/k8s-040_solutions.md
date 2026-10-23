# k8s-040: Explanatory solutions

These answers explain the stated synthetic and scoped runtime contracts. Static checks do not prove cluster acceptance.

## Mechanism

An incident investigation turns a symptom into a testable explanation and a bounded repair. The first useful question is not which command might make the red status disappear, but which observation would distinguish the leading hypotheses. A Service timeout with healthy Pods can result from selectors, ports, network policy or the application path. Restarting every Pod changes evidence without necessarily testing any of those causes.

This chapter injects one synthetic fault: a host-controlled change to the selector of the exact owned Service. The workload remains Ready, but the Service no longer selects it. The investigator records a baseline, the symptom, endpoint/selector evidence, a conditional repair and a post-repair application check. A separate teacher may reveal the chosen fault only after the learner has formed a hypothesis.

The normal browser adapter can demonstrate bounded failures but does not offer an unrestricted fault-injection API or persistent arbitrary edits. The advanced exercise requires an exclusive lease and a fixed host action with a deadline, cancellation, exact target UID and restoration record. No unrelated namespace, Node or cluster setting is changed.

## Exercise 1: Record the baseline

The baseline makes the experiment interpretable. It should identify the exact Service and Pod identities rather than only their names, because replacement during the exercise changes the scope of the repair.

**Expected:** A connected selection graph and successful application control.

## Exercise 2: Form competing hypotheses

The hypotheses connect symptoms to mechanisms. A Ready Pod weakens some crash explanations, zero selected endpoints points toward selection, and a populated endpoint with a wrong port suggests another branch. No single symptom proves every detail.

**Expected:** Three specific evidence checks rather than a generic restart.

## Exercise 3: Interpret the supplied timeline

The controlled one-fault trace supports a narrow causal explanation. In a real incident, the same correlation would require checking concurrent changes and alternative causes rather than assuming the teacher-supplied synthetic control conditions.

**Expected:** Selector changes at 10; zero endpoints observed at 15 while readiness remains1.

## Exercise 4: Apply the minimal bounded repair

The repair should preserve unrelated fields and respect optimistic concurrency. A stale whole-object replacement risks undoing another legitimate change, while a name-only update risks modifying an unrelated replacement.

**Expected:** Owned svc-1 repaired; replacement UID causes refusal.

## Exercise 5: Verify application recovery

This check demonstrates the route works again for the observed request path. If the response still fails, the incident remains open even when the update command succeeded or the Pods were Ready throughout.

**Expected:** One endpoint and expected payload, with actual timestamps if live.

## Exercise 6: Write the review and stop conditions

The review should teach how the failure was detected and repaired, and where the experiment stops. It should preserve evidence of a failed or cancelled repair rather than converting every exercise into an assumed success story.

**Expected:** A timestamped bounded incident packet with no unsupported broad resilience claim.

## Boundary and troubleshooting review

The host operation must know how to restore its own change, including on cancellation or deadline. It should stop if the target UID changes or unrelated state would be affected. Do not broaden the fault into a node outage, policy deletion or credential change to make the lesson more dramatic.

The post-incident review explains contributing conditions and detection gaps without inventing a root cause unsupported by the trace. A finite recovery can validate this selector-repair path; it does not prove resilience to every outage or that the failure will never recur.
