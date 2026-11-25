# cuda-128: explained solutions

Compare with your [worksheet](../lessons/cuda-128.md) attempt.

## Exercise 1: Compute end-to-end tradeoff

Sum all changed costs.

**Approach.** Compute the end-to-end tradeoff by summing every changed cost: the GPU query saves 30 seconds of compute but adds 40 seconds of transfers and conversions, so the net is 10 seconds slower.

**Why it is correct here.** Users wait for the whole application, not only the arithmetic. The decision must use the total, including costs the GPU path introduces.

**A plausible wrong approach.** Reporting the 30-second compute saving alone recommends a change that makes the application slower overall.

**How to verify.** The reference asserts `net == 10`. In practice, compare complete application times for both configurations on the same input.

## Exercise 2: Choose a tiny-data tool

A local CPU tool may be sufficient.

**Approach.** Choose a tiny-data tool: for an analysis that a local CPU dataframe finishes in about 0.1 seconds, use that tool rather than starting a Spark application that takes seconds just to begin.

**Why it is correct here.** Startup dominates small jobs. No kernel speedup can remove fixed overhead that is larger than the entire local computation.

**A plausible wrong approach.** Using GPU Spark for every analysis because it is available adds startup and operational overhead to jobs that never needed distribution.

**How to verify.** The reference asserts the local candidate is faster than Spark startup alone. Time both on the actual small dataset to confirm.

## Exercise 3: Separate setup and steady state

Both boundaries matter for user workflow.

**Approach.** Separate setup cost, such as application startup, executor allocation and compilation, from steady-state processing time for repeated queries.

**Why it is correct here.** A long-running service pays setup once, while a one-off job pays it every time. Both numbers matter for different usage patterns.

**A plausible wrong approach.** Reporting only steady-state throughput favors GPU Spark for interactive one-off use, where setup actually dominates.

**How to verify.** Report setup and steady-state times separately and state which applies to the intended workflow.

## Exercise 4: Include operational cost

Count maintenance compatibility and resource ownership.

**Approach.** Include operational cost: maintaining the compatibility matrix, upgrading plugin and drivers together, and owning GPU resources and their cleanup.

**Why it is correct here.** These costs recur and fall on the team running the system. A small performance gain may not justify them.

**A plausible wrong approach.** Comparing only query time ignores the work of keeping a GPU Spark stack compatible across upgrades. A Spark upgrade can be blocked until a matching plugin release exists, which delays security patches.

**How to verify.** List each recurring task with an owner and an estimate, then include it in the recommendation. Tasks without a willing owner are a risk signal in their own right.

## Exercise 5: Define a reevaluation trigger

Name data growth or changed workload support.

**Approach.** Define a reevaluation trigger, such as data growing past a stated size or the workload gaining operators the plugin supports, that would justify revisiting the decision.

**Why it is correct here.** A decision based on current data and support may change. Named triggers tell the team when to measure again.

**A plausible wrong approach.** Rejecting GPU Spark permanently ignores that the tradeoff can change, while revisiting constantly wastes effort. A trigger such as transfer time falling below compute savings ties the revisit to the exact term that decided the current outcome.

**How to verify.** Write the trigger as a measurable condition and record where its value is monitored. Include who receives the alert when the condition is met.

## Exercise 6: Write an evidence-based recommendation

Recommend the simplest qualified option and state missing evidence.

**Approach.** Write an evidence-based recommendation: choose the simplest option that meets the requirements, such as local CPU processing for small data, and state what evidence is still missing.

**Why it is correct here.** The simplest qualified option minimizes operational risk. Listing missing evidence keeps the decision open to correction.

**A plausible wrong approach.** Recommending the most powerful technology by default ignores the measured tradeoff and the operational cost. It also skips stating missing evidence, so the decision cannot be corrected when new data arrives.

**How to verify.** Check that each statement in the recommendation cites a measurement or is labeled as an assumption.

## Self-check answers

1. **Name three conditions that can make GPU Spark the wrong choice.** Tiny data, unsupported expressions, expensive transfers, external I/O, severe skew or a memory-constrained device.

2. **How does a CPU fallback installation differ from plugin operator fallback?** It is a separate ordinary Spark environment, while operator fallback happens inside a running plugin job.

3. **Why is a no-change outcome a valid result?** A good decision identifies the smallest system that solves the problem, and that can be the current one.

## Reference observation

GPU candidate adds 10 modeled seconds end to end.

Asserted by `courses/cuda/spark/references/cuda-128_cpu.py`.
