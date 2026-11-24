# k8s-011: Explanatory solutions

These answers explain the stated synthetic and scoped runtime contracts. Static checks do not prove cluster acceptance.

## Mechanism

A Job manages finite work toward a completion condition. A Deployment manages a continuing replica set. A CronJob creates Jobs according to a schedule. These controllers have different success and lifecycle meanings: an intentionally exiting task belongs in a Job, while a server that should remain available belongs in a continuing workload controller.

The fixed hello-task Job runs a deterministic synthetic calculation and exits. Its success output records three accepted rows, two rejected rows and total 35. A separate allowed failure outcome exits 2. The worker checks the Job condition, its controlled Pod identity, the task container's zero exit and the exact bounded JSON output before calling the success path complete.

The CronJob example is suspended and remains a host-lab/reading fixture. The browser does not accept arbitrary schedules or leave recurring workloads behind. A scheduled configuration is not evidence that a run occurred, and a completed run is not evidence that future recurrence works.

## Exercise 1: Identify finite-work controls

A single completion is the desired successful work count, parallelism bounds concurrent Pods, and backoff controls retries after failures. The active deadline bounds duration independently of the outer app operation deadline.

**Expected:** Starter: 1, 1, Never, 1 and 30 seconds. Edited source: 1, 1, Never, 0 and 20 seconds.

**Solution reasoning**

- **Approach:** Read completions and parallelism from spec, restartPolicy from the Pod template, then backoffLimit and activeDeadlineSeconds, and edit the last two.
- **Why it is correct:** The starter needs one success, runs one Pod at a time, never restarts in place, allows one retry and stops at 30 seconds; the edit sets backoffLimit 0 and 20 seconds.
- **Plausible wrong approach:** Setting restartPolicy to OnFailure to remove retries moves restarts into the Pod rather than removing them.
- **How to verify:** Quoted values read 1, 1, Never, 0 and 20 seconds from your edited YAML.

## Exercise 2: Verify exact task output

The fixed task is deterministic and has no external side effects. Its receipt connects controller state to the actual task container and a small independent ledger. It does not certify arbitrary learner code or every written exercise.

**Expected:** Owned Complete Job, controlled successful task Pod, exit 0 and exact accepted 3, rejected 2 and total 35 output.

**Solution reasoning**

- **Approach:** Run the success outcome and compare the output ledger against the expected values field by field.
- **Why it is correct:** The fixed task is deterministic, so a correct run prints accepted 3, rejected 2 and total 35 and exits 0.
- **Plausible wrong approach:** Trusting the Complete condition without reading the ledger could accept a task that exited 0 with wrong totals.
- **How to verify:** Ledger fields match exactly and the task Pod's controller ownerReference is this Run's Job UID.

## Exercise 3: Observe intentional failure

The source remains syntactically valid and the workload can start, but the task intentionally reports failure. This distinguishes runtime task failure from manifest rejection or image absence.

**Expected:** Job reaches Failed; operation reports failure and cleans its owned UID.

**Solution reasoning**

- **Approach:** Change only the outcome value to failure and Run it.
- **Why it is correct:** The manifest is still valid and the container starts, so the Job controller records a nonzero exit and marks the Job Failed when backoff is exhausted.
- **Plausible wrong approach:** Treating Failed as a manifest problem sends you to the YAML, yet the API accepted it and the container ran.
- **How to verify:** The Job condition is Failed, the container exit code is nonzero and cleanup names the same Job UID.

## Exercise 4: Explain retry semantics

The Job controller can create another Pod even when the kubelet will not restart a failed container in the same Pod. Production side effects must tolerate duplicate attempts rather than assuming the controller provides exactly-once execution.

**Expected:** At most the declared retry budget is requested; Never does not forbid a replacement Pod attempt.

**Solution reasoning**

- **Approach:** Count new Pods per backoffLimit value, keeping restartPolicy Never in mind.
- **Why it is correct:** With Never, each failed attempt is a separate Pod, so backoffLimit 0 allows one Pod and backoffLimit 1 allows up to two.
- **Plausible wrong approach:** Reading Never as no retries at all confuses kubelet restarts within a Pod with Job controller retries across Pods.
- **How to verify:** Expect at most one task Pod at backoffLimit 0 and at most two at backoffLimit 1, with restartCount staying 0 in each.

## Exercise 5: Review the suspended CronJob

Suspension affects future scheduling. It does not erase an already running Job or prove that the schedule previously fired. A live recurring lab needs a separate host capability and multiple observed timestamps/results.

**Expected:** A five-minute UTC schedule is configured but suspended; existing active Jobs require separate handling.

**Solution reasoning**

- **Approach:** Read schedule, timeZone, suspend, concurrencyPolicy and startingDeadlineSeconds from the fixture and state each effect.
- **Why it is correct:** The five-minute schedule in UTC is defined, but suspend true stops new Jobs from being created, and existing Jobs keep running.
- **Plausible wrong approach:** Assuming suspend deletes active Jobs or proves past runs would mistake a future scheduling switch for cleanup or history.
- **How to verify:** Each field is named with its effect and the conclusion says no new Job starts while suspended.

## Exercise 6: Design an idempotent handoff

Use an application-level identity and an atomic or otherwise justified publication protocol. A final successful Job count cannot establish that an external sink received exactly one effect. The teaching task avoids that external boundary and labels the limitation.

**Expected:** A stable logical-work key, commit boundary, replay policy and acceptance ledger are named.

**Solution reasoning**

- **Approach:** Give each logical unit of work a stable key and publish its effect through a check that rejects a key already committed.
- **Why it is correct:** The Job controller may start a second Pod after an attempt that already wrote its effect, so the sink must dedupe on the key.
- **Plausible wrong approach:** Relying on backoffLimit 0 to prevent duplicates fails because a node loss or deadline can still yield a second Pod.
- **How to verify:** Simulate a crash after the write and before the acknowledgment; the retry finds the key and publishes nothing new.

## Boundary and troubleshooting review

A failed task exit, a deadline exceeded condition and a missing image are different failures. The fixed failure mode demonstrates application failure with bounded cleanup. A timeout of the outer operation is another boundary, with a separate cleanup reserve.

Do not hide failed attempts by reading only the most recent success counter, or claim that printing the expected text proves task correctness. The fixed reference uses independent expected counts and ties logs to a verified owned successful Pod. Written reasoning about recurrence and idempotency remains outside automatic grading.
