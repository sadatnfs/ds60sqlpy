# cuda-104: explained solutions

Compare with your [worksheet](../lessons/cuda-104.md) attempt.

## Exercise 1: Write three constraints

Use measurable limits with units.

**Approach.** Write three measurable constraints with units, such as peak memory at most 8 GiB, p95 latency at most 20 ms and held-out accuracy at least 0.9.

**Why it is correct here.** Constraints with units and thresholds can be checked mechanically against candidate measurements. Vague goals such as fast enough cannot reject any candidate.

**A plausible wrong approach.** Writing a single goal of maximizing speed ignores memory and quality, so the fastest candidate wins even when it cannot run on the device or produces worse answers.

**How to verify.** Each constraint should map to a field in the candidate records: `memory`, `latency` and `quality` in the reference fixture, with a comparison operator and threshold.

## Exercise 2: Filter infeasible candidates

Reject memory and quality violations before speed ranking.

**Approach.** Filter infeasible candidates before ranking by speed: B needs 12 GiB on an 8 GiB device and C has quality 0.80 below 0.9, so only A remains.

**Why it is correct here.** A candidate that violates a hard constraint cannot be deployed whatever its speed. B's 10 ms timing is irrelevant because the model does not fit.

**A plausible wrong approach.** Ranking all candidates by latency first and picking B, then trying to make it fit later, wastes effort and treats a hard constraint as a preference.

**How to verify.** The reference asserts `valid == ['A']`. Change B's memory to 8 and confirm it then becomes valid, showing the filter responds to the constraint.

## Exercise 3: Choose a bottleneck hypothesis

Tie a change to a trace.

**Approach.** Choose one bottleneck hypothesis tied to a trace, such as the latency dominated by host-to-device copies, and name the change that would test it.

**Why it is correct here.** A hypothesis grounded in a measured trace predicts which change should help. If the change does not move the measured stage, the hypothesis was wrong.

**A plausible wrong approach.** Making several optimizations at once without a hypothesis means any improvement cannot be attributed to a cause, and regressions get hidden by gains elsewhere.

**How to verify.** Record the trace before and after the single change and check that the targeted stage shrank while results stayed the same.

## Exercise 4: Preserve rollback

Keep the unchanged baseline runnable.

**Approach.** Preserve a rollback path: keep the unchanged baseline runnable with its configuration and recorded metrics so it can be restored if the new candidate fails.

**Why it is correct here.** A rollback provides a known-good fallback and a reference for comparing later measurements, so deployment risk stays bounded.

**A plausible wrong approach.** Replacing the baseline code in place leaves no way to reproduce earlier results or revert quickly.

**How to verify.** Run the baseline from its saved configuration and confirm it reproduces the recorded metric within tolerance.

## Exercise 5: Design failure tests

Test bounded invalid inputs and resource refusal.

**Approach.** Design failure tests with bounded invalid inputs, such as wrong dtype, oversized batch and empty input, and test that resource refusal produces a clear error.

**Why it is correct here.** A GPU service should fail predictably. Rejecting an oversized request is better than an out-of-memory crash that also affects other requests.

**A plausible wrong approach.** Testing only valid inputs leaves error paths untested, and those paths are where GPU services typically fail in production.

**How to verify.** Assert each invalid input yields a specific error and that the service still answers a valid request afterward.

## Exercise 6: State evidence gaps

Pending GPU validation must remain visible.

**Approach.** State evidence gaps explicitly: candidate measurements in the fixture are illustrative, and any GPU timing not measured on target hardware stays marked as pending validation.

**Why it is correct here.** A decision record must show which numbers were measured and which were assumed. Hiding gaps makes an unverified choice look final.

**A plausible wrong approach.** Presenting fixture numbers such as 18 ms as measured performance claims evidence that does not exist.

**How to verify.** Include a section listing each unmeasured quantity and the hardware run that would measure it, and check that no unmeasured value is labeled as measured.

## Self-check answers

1. **Why must quality be part of acceptance?** A candidate that meets latency but drops held-out accuracy below the threshold fails the task it was built for.

2. **Which bottlenecks can an optimization target?** Input preparation, transfer, arithmetic, memory traffic or communication, as shown by measurement.

3. **What can CPU-only work honestly deliver?** A working model and a decision report, with GPU execution and deployment qualification explicitly left open.

## Reference observation

Only candidate A satisfies all three constraints.

Asserted by `courses/cuda/python/references/cuda-104_cpu.py`.
