# cuda-128: When GPU Spark is the wrong tool

**Route:** CUDA Python and machine learning / GPU Spark specialization. **Stage:** advanced. **Prerequisites:** `cuda-123`, `cuda-126`, `cuda-127`.

Pacing, evidence labels and platform rules: [CUDA study guide](../../STUDY-GUIDE.md).

## Learning objectives

- Compute end-to-end tradeoff.
- Choose a tiny-data tool.
- Separate setup and steady state.
- Include operational cost.
- Define a reevaluation trigger.
- Write an evidence-based recommendation.

## Mechanism and vocabulary

A good acceleration decision includes a credible no-change outcome. Tiny data, unsupported expressions, expensive transfers, external I/O, severe skew or a memory-constrained device can make CPU Spark or a single-process dataframe the better choice. Distributed scheduling overhead can dominate a workload that fits comfortably in one local process. GPU capability is one input to architecture, not a requirement to use it.

Compare total completion time, resource cost, operational complexity and output quality under actual constraints. Maintain a CPU fallback installation separately from plugin operator fallback. Revisit the decision when data size, workload mix or hardware changes. The final review should identify the smallest supported system that solves the problem and the evidence that would justify expanding it.



### Key terms

- **No-change outcome:** A credible decision to keep the existing CPU approach when acceleration does not pay off.
- **Steady-state cost:** Recurring time per run after setup, compared separately from one-time startup cost.
- **Operational complexity:** The ongoing effort to deploy, monitor and support a system, which counts toward total cost.
- **Reevaluation trigger:** A recorded condition, such as data growth or a new release, that justifies revisiting the decision.

## Worked examples

### Worked example 1

A local CPU dataframe finishes a tiny analysis in 0.1 seconds while Spark startup takes several seconds. No kernel speedup can erase startup for a one-off job without changing the execution model.

### Worked example 2

A GPU query saves 30 seconds of compute but adds 40 seconds of transfers and conversions. The complete application loses 10 seconds despite faster arithmetic.

## How to run the CPU model

Edit the copy; the [reference](../references/cuda-128_cpu.py) adds assertions.

```sh
python courses/cuda/spark/lessons/cuda-128_cpu.py
```

```python
saved_compute, added_transfer = 30, 40
net = added_transfer - saved_compute
assert net == 10
candidates = {"local_cpu": 0.1, "spark_startup_only": 3.0}
assert candidates["local_cpu"] < candidates["spark_startup_only"]
print("CPU architecture decision: GPU candidate adds", net, "seconds")
```

**Expected observation:** GPU candidate adds 10 modeled seconds end to end.

**Variable trace.** Before running the model, predict these final values; then compare:

| Variable | Final value |
|---|---|
| `saved_compute` | `30` |
| `added_transfer` | `40` |
| `net` | `10` |
| `candidates` | `{'local_cpu': 0.1, 'spark_startup_only': 3.0}` |

## Practice and transfer

Record each attempt in the [worksheet](../lessons/cuda-128.md) before opening hints.

### Exercise 1: Compute end-to-end tradeoff

**Trap to avoid:** Reporting the 30-second compute saving alone recommends a change that makes the application slower overall.

### Exercise 2: Choose a tiny-data tool

**Trap to avoid:** Using GPU Spark for every analysis because it is available adds startup and operational overhead to jobs that never needed distribution.

### Exercise 3: Separate setup and steady state

**Trap to avoid:** Reporting only steady-state throughput favors GPU Spark for interactive one-off use, where setup actually dominates.

### Exercise 4: Include operational cost

**Trap to avoid:** Comparing only query time ignores the work of keeping a GPU Spark stack compatible across upgrades. A Spark upgrade can be blocked until a matching plugin release exists, which delays security patches.

### Exercise 5: Define a reevaluation trigger

**Trap to avoid:** Rejecting GPU Spark permanently ignores that the tradeoff can change, while revisiting constantly wastes effort. A trigger such as transfer time falling below compute savings ties the revisit to the exact term that decided the current outcome.

### Exercise 6: Write an evidence-based recommendation

**Trap to avoid:** Recommending the most powerful technology by default ignores the measured tradeoff and the operational cost. It also skips stating missing evidence, so the decision cannot be corrected when new data arrives.

## Progressive hints

Hint *k* belongs to exercise *k*; open one at a time.

1. Add every cost that changes, including transfers and conversions, not only compute time.
2. Compare the job's run time with the startup cost of a distributed engine.
3. Ask how often a user pays startup and how much of the workflow is steady-state work.
4. Include maintenance, compatibility tracking and resource ownership in the comparison.
5. Name a data size or workload change that would make you repeat this evaluation.
6. Recommend the simplest option that meets the constraints and say what evidence is still missing.

## Common mistakes and self-check

A common mistake is treating GPU acceleration as the goal instead of a candidate. In worked example 2 a GPU query saves 30 seconds of compute but adds 40 seconds of transfers and conversions, so the application loses 10 seconds. Another mistake is choosing Spark for tiny data where startup outweighs the work. Fix both by comparing total completion time, resource cost, operational complexity and quality, and by keeping a CPU fallback installation alongside any plugin deployment.

**Misconception:** If a cluster has GPUs, every Spark job on it should run with the plugin enabled. **Correction:** The hardware may already be paid for, but enabling the plugin for every job adds compatibility tracking, release upgrades, fallback diagnosis and memory tuning to all of them, and jobs with tiny data or unsupported operators can get slower. Enable it per workload where measured end-to-end results improve, and keep the remaining jobs on ordinary CPU Spark with a recorded reason.

**Evidence limit:** The reference computes a 10-second end-to-end loss from modeled costs. It measures nothing, so a real recommendation needs timings, costs and quality checks under the actual data size, workload mix and hardware.

1. Name three conditions that can make GPU Spark the wrong choice.
2. How does a CPU fallback installation differ from plugin operator fallback?
3. Why is a no-change outcome a valid result?

Answers: [self-check answers](../solutions/cuda-128_solutions.md#self-check-answers).

## Primary references

- [Apache Spark SQL performance tuning](https://spark.apache.org/docs/latest/sql-performance-tuning.html)

Full lists: [documentation and sources](../../STUDY-GUIDE.md#documentation-and-sources).

## Ask an AI tutor about this lesson

```text
Use the checked-in $guide-ds60sqlpy-learning skill for cuda-128: When GPU Spark is the wrong tool.
Read courses/cuda/spark/guides/cuda-128.md and courses/cuda/spark/lessons/cuda-128.md.
Start with my current attempt and the two worked examples, and ask which backend actually ran.
Give one progressive hint at a time. Keep the separate solution closed and do not mark
progress unless I request it. Treat synthetic timings and CPU models as model evidence,
not as GPU or cluster measurements.
```
