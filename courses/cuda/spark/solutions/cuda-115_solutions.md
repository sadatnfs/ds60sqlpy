# cuda-115: explained solutions

Compare with your [worksheet](../lessons/cuda-115.md) attempt.

## Exercise 1: Draw logical versus physical plan

Logical nodes describe intent and physical nodes choose execution.

**Approach.** Draw the logical plan as intent, such as a scan, a filter and an aggregate, and the physical plan as the chosen execution, such as a file scan, a filter operator, a partial aggregate, an exchange and a final aggregate.

**Why it is correct here.** Catalyst optimizes the logical plan and then picks physical operators. Only physical nodes show where data is shuffled and which implementation runs.

**A plausible wrong approach.** Reading device placement from the logical plan fails, because logical nodes carry no device information and the plugin acts only on the physical plan.

**How to verify.** Print `explain(mode="formatted")` and match each logical step to the physical nodes that implement it.

## Exercise 2: Mark GPU candidate nodes

Use actual plugin names from the selected release.

**Approach.** Mark GPU candidate nodes using the actual operator names from the selected plugin release, such as names beginning with `Gpu`, in the synthetic plan the filter and aggregate.

**Why it is correct here.** Plugin operator names identify replaced nodes directly. Names can differ between releases, so the release documentation is the authority.

**A plausible wrong approach.** Guessing GPU placement from operator type, for example assuming all aggregates run on the GPU, ignores expression-level fallback.

**How to verify.** Count nodes with GPU names in the executed plan; the reference counts two GPU nodes in its synthetic plan.

## Exercise 3: Locate transitions

Each transition may copy or change representation.

**Approach.** Locate transitions between CPU and GPU nodes. The synthetic plan `scan CPU, filter GPU, aggregate GPU, collect CPU` has two, one into and one out of the GPU section.

**Why it is correct here.** Each transition can copy data between host and device or convert between row and columnar format, so transitions carry cost not shown by operator names.

**A plausible wrong approach.** Counting GPU nodes and ignoring transitions makes a plan with many short GPU sections look better than one long section.

**How to verify.** The reference computes `transitions == 2`. In a real plan, count the row to columnar and columnar to row nodes.

## Exercise 4: Explain lazy evaluation

An action is required for work.

**Approach.** Explain lazy evaluation: building a DataFrame with filters and aggregations creates a plan only, and an action such as `count()` or `collect()` triggers execution.

**Why it is correct here.** Spark delays work so it can optimize the whole plan. Before an action, no tasks run and no runtime metrics exist.

**A plausible wrong approach.** Timing the line that defines the DataFrame and reporting it as query time measures plan construction, which is nearly instant.

**How to verify.** Watch the Spark UI and confirm that a job appears only after the action is called.

## Exercise 5: Compare initial and final AQE plan

Inspect the final executed plan.

**Approach.** Compare the initial and final adaptive query execution plans: AQE can change join strategies or coalesce partitions during execution, so the final plan shows what ran.

**Why it is correct here.** AQE uses runtime statistics. The plan printed before execution is a starting point that may be replaced.

**A plausible wrong approach.** Citing the pre-execution plan as the executed plan can report a join strategy that never ran.

**How to verify.** After the action, read the final plan from the SQL tab in the Spark UI and compare it with the initial `explain` output.

## Exercise 6: Choose operator metrics

Use rows batches time spill and device observations together.

**Approach.** Choose operator metrics together: output rows, batches, operator time, spill bytes and GPU memory observations, so that one metric does not mislead.

**Why it is correct here.** Rows confirm correctness of scale, time shows cost, and spill reveals memory pressure. A fast operator that spilled heavily may not stay fast with larger data.

**A plausible wrong approach.** Reporting only total job time hides which operator dominates and whether spilling occurred.

**How to verify.** Collect metrics for each GPU operator from the SQL view after the action and check row counts against expectations.

## Self-check answers

1. **What is the difference between explain output and the executed SQL view?** Explain shows what Spark planned; the executed view and its metrics show what happened for a completed action.

2. **Can a CPU node coexist with useful GPU computation?** Yes. Metadata or coordination nodes can stay on the CPU while the heavy operators run on the GPU.

3. **Why count transitions in a mixed plan?** Each transition may copy data or change its representation, and that cost belongs in the measurement.

## Reference observation

Synthetic plan has two GPU nodes and two backend transitions.

Asserted by `courses/cuda/spark/references/cuda-115_cpu.py`.
