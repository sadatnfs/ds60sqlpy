# cuda-123: explained solutions

These answers explain the six practice tasks. CPU reference programs are mathematical or semantic checks, not proof of CUDA execution.

## Exercise 1: Calculate partition averages

Divide rows by partitions.

**Approach.** Calculate partition averages: one million rows over 100 partitions averages 10000 rows, and over 10 partitions averages 100000.

**Why it is correct here.** Fewer partitions mean more rows per task, which raises per-task memory and can cause spills even though scheduling overhead falls.

**A plausible wrong approach.** Reducing partitions to cut scheduling overhead without checking per-task memory can turn a working job into a spilling one.

**How to verify.** The reference asserts both averages. Compare with actual task input sizes in the Spark UI.

## Exercise 2: Explain skew beyond averages

Report tails and maximum sizes.

**Approach.** Explain skew beyond averages: report the maximum and tail of partition sizes, since one large partition sets the stage time.

**Why it is correct here.** An average of 10000 rows can hide a single partition of 200000, and that task runs much longer than the rest.

**A plausible wrong approach.** Reporting only the average leaves skew invisible. Adding partitions does not fix skew either, because a hot key still lands in one partition however many there are.

**How to verify.** Collect per-task input rows and report median, 95th percentile and maximum. A maximum several times the median marks a stage worth investigating for key skew.

## Exercise 3: Capture final AQE plan

Inspect after the action.

**Approach.** Capture the final AQE plan after the action, since adaptive execution may coalesce small partitions or split large ones at runtime.

**Why it is correct here.** The partition counts in the initial plan may not be the ones that ran.

**A plausible wrong approach.** Reporting partition counts from the pre-execution plan can describe a configuration AQE changed. Coalescing may reduce 200 shuffle partitions to a handful, which changes per-task memory considerably.

**How to verify.** Read the final plan from the SQL tab and record partition counts per stage. Record the AQE advisory partition size alongside, since it drives the coalescing result.

## Exercise 4: Define cache policy

Use equivalent cold or warm states.

**Approach.** Define a cache policy with equivalent states for both runs, either both cold or both warm with the same data cached.

**Why it is correct here.** Reading cached data is faster than downloading or reading from disk, so a warm GPU run against a cold CPU run measures caching, not execution.

**A plausible wrong approach.** Comparing those runs reports a speedup partly caused by the cache, as the reference rejects for unmatched cache states.

**How to verify.** Record cache state for each run and reject comparisons where the states differ. Clearing caches or restarting the application before cold runs, and running a discarded warm-up before warm runs, makes the states reproducible.

## Exercise 5: Choose semantic and performance fixtures

Tiny bounded correctness data and representative measured data serve different purposes.

**Approach.** Choose fixtures for different purposes: tiny bounded data for semantic correctness and representative data sizes for performance measurement.

**Why it is correct here.** Tiny data finishes quickly and exercises edge cases, but its timings are dominated by overhead.

**A plausible wrong approach.** Reporting performance from the tiny correctness fixture gives timings that say nothing about production scale. At a few rows, Spark job scheduling dominates and both backends look the same, or the GPU looks slower.

**How to verify.** Label each fixture by purpose and use only the representative one for timing claims. Run the correctness fixture on both backends too, so the representative timings are known to come from equivalent computations.

## Exercise 6: Separate estimated and observed speedup

Predictions remain predictions until executed.

**Approach.** Separate estimated and observed speedup: an estimate from a model remains a prediction until a run on target hardware measures it.

**Why it is correct here.** Estimates guide which experiments to run, while observations support claims. Keeping them separate prevents treating predictions as results.

**A plausible wrong approach.** Writing an estimated 3 times speedup into a report as achieved presents unverified data as fact. Readers then plan hardware purchases or migrations around a number nobody measured.

**How to verify.** Mark each speedup in the report as estimated or observed, and for observed values cite the run. If an observation disagrees with the estimate, keep both and note which model assumption failed.

## Reference observation

Partition averages 10000 and 100000; unmatched cache states rejected.

The reference file is `courses/cuda/spark/references/cuda-123_cpu.py`. It includes deterministic assertions. These assertions establish the supplied bounded CPU example; hardware execution and architecture-specific performance remain separate checks.
