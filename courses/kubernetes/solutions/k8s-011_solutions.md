# k8s-011: Explanatory solutions

These answers explain the stated synthetic and scoped runtime contracts. Static checks do not prove cluster acceptance.

## Mechanism

A Job manages finite work toward a completion condition. A Deployment manages a continuing replica set. A CronJob creates Jobs according to a schedule. These controllers have different success and lifecycle meanings:an intentionally exiting task belongs in a Job, while a server that should remain available belongs in a continuing workload controller.

The fixed hello-task Job runs a deterministic synthetic calculation and exits. Its success output records three accepted rows, two rejected rows and total35. A separate allowed failure outcome exits2. The worker checks the Job condition, its controlled Pod identity, the task container's zero exit and the exact bounded JSON output before calling the success path complete.

The CronJob example is suspended and remains a host-lab/reading fixture. The browser does not accept arbitrary schedules or leave recurring workloads behind. A scheduled configuration is not evidence that a run occurred, and a completed run is not evidence that future recurrence works.

## Exercise 1: Identify finite-work controls

A single completion is the desired successful work count, parallelism bounds concurrent Pods, and backoff controls retries after failures. The active deadline bounds duration independently of the outer app operation deadline.

**Expected:** 1, 1, Never, 0 and20 seconds for the reference.

## Exercise 2: Verify exact task output

The fixed task is deterministic and has no external side effects. Its receipt connects controller state to the actual task container and a small independent ledger. It does not certify arbitrary learner code or every written exercise.

**Expected:** Owned Complete Job, controlled successful task Pod, exit0 and exact accepted3/rejected2/total35 output.

## Exercise 3: Observe intentional failure

The source remains syntactically valid and the workload can start, but the task intentionally reports failure. This distinguishes runtime task failure from manifest rejection or image absence.

**Expected:** Job reaches Failed; operation reports failure and cleans its owned UID.

## Exercise 4: Explain retry semantics

The Job controller can create another Pod even when the kubelet will not restart a failed container in the same Pod. Production side effects must tolerate duplicate attempts rather than assuming the controller provides exactly-once execution.

**Expected:** At most the declared retry budget is requested; Never does not forbid a replacement Pod attempt.

## Exercise 5: Review the suspended CronJob

Suspension affects future scheduling. It does not erase an already running Job or prove that the schedule previously fired. A live recurring lab needs a separate host capability and multiple observed timestamps/results.

**Expected:** A five-minute UTC schedule is configured but suspended; existing active Jobs require separate handling.

## Exercise 6: Design an idempotent handoff

Use an application-level identity and an atomic or otherwise justified publication protocol. A final successful Job count cannot establish that an external sink received exactly one effect. The teaching task avoids that external boundary and labels the limitation.

**Expected:** A stable logical-work key, commit boundary, replay policy and acceptance ledger are named.

## Boundary and troubleshooting review

A failed task exit, a deadline exceeded condition and a missing image are different failures. The fixed failure mode demonstrates application failure with bounded cleanup. A timeout of the outer operation is another boundary, with a separate cleanup reserve.

Do not hide failed attempts by reading only the most recent success counter, or claim that printing the expected text proves task correctness. The fixed reference uses independent expected counts and ties logs to a verified owned successful Pod. Written reasoning about recurrence and idempotency remains outside automatic grading.
