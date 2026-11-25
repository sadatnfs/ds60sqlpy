# cuda-115: From Catalyst plans to actual GPU operators

**Route:** CUDA Python and machine learning / GPU Spark specialization. **Stage:** intermediate. **Prerequisites:** `cuda-113`, `cuda-114`.

Pacing, evidence labels and platform rules: [CUDA study guide](../../STUDY-GUIDE.md).

## Learning objectives

- Draw logical versus physical plan.
- Mark GPU candidate nodes.
- Locate transitions.
- Explain lazy evaluation.
- Compare initial and final AQE plan.
- Choose operator metrics.

## Mechanism and vocabulary

Catalyst represents a query as logical operations, applies transformations and selects physical implementations. Explain output shows what Spark planned, while an executed SQL plan and metrics show what happened for an action. Adaptive Query Execution can change a physical plan using runtime statistics, so the initial plan may differ from the final executed plan.

The plugin replaces supported physical operators with GPU-capable implementations and inserts transitions where needed. Use the release's explain diagnostics to understand why an operation stayed on CPU. Seeing one GPU node does not establish that the entire job is accelerated. Conversely, a CPU metadata or coordination node can coexist with useful GPU computation. Interpret the plan by operation and stage, then compare measured completed work.

## Read a plan as a sequence of contracts

A scan establishes a schema and row source. A filter applies a predicate, including SQL null logic. A projection chooses or computes columns. An exchange changes partition ownership. A join or aggregate combines records according to key and multiplicity rules. Each node has both a semantic contract and a physical representation. A GPU replacement must preserve the first while changing the second.

Start by drawing the logical intent without backend labels. Then inspect `explain("formatted")` in the exact Spark environment. Highlight CPU/GPU representation transitions and exchanges separately: a device transfer is not the same operation as redistribution across executors, although one stage can involve both. Add operator metrics after an action completes. If AQE is enabled, retain the final executed plan because broadcast and partition decisions may have changed.

The plugin's explain diagnostics can report why a node is not selected for GPU execution. Read the reason at the expression and dtype level. An unsupported child can change the useful acceleration region around it, and a small unsupported expression can force expensive conversions. Do not rewrite the query merely to maximize the count of GPU nodes; preserve semantics and compare complete latency.

A useful review table has columns node, semantic role, input/output representation, supported status, fallback reason, rows/batches, elapsed time and spill. This turns a screenshot into an argument. A GPU node in a planned diagram is weaker evidence than that node in an executed query with metrics, and even the executed node must be accompanied by a correct result comparison.


### Key terms

- **Catalyst:** Spark's query optimizer, which transforms logical plans and selects physical implementations.
- **Logical plan:** A description of what a query computes, independent of how it executes.
- **Columnar transition:** An operator inserted to convert between row and columnar formats around GPU operators.
- **AQE final plan:** The physical plan after Adaptive Query Execution applies runtime statistics, which can differ from the initial plan.

## Worked examples

### Worked example 1

A synthetic plan Scan -> Filter -> Aggregate can contain a GPU filter and aggregate with a CPU-side source boundary. Count transfers and conversions rather than labeling the whole query GPU-only.

### Worked example 2

A count action triggers execution; constructing a DataFrame alone is lazy. A plan printed before an action does not contain the same runtime evidence as the completed SQL execution view.

## How to run the CPU model

Edit the copy; the [reference](../references/cuda-115_cpu.py) adds assertions.

```sh
python courses/cuda/spark/lessons/cuda-115_cpu.py
```

```python
plan = [("scan", "CPU"), ("filter", "GPU"), ("aggregate", "GPU"), ("collect", "CPU")]
transitions = sum(plan[i][1] != plan[i - 1][1] for i in range(1, len(plan)))
assert transitions == 2
assert sum(device == "GPU" for _, device in plan) == 2
print("Synthetic plan worksheet:", transitions, "CPU/GPU transitions")
```

**Expected observation:** Synthetic plan has two GPU nodes and two backend transitions.

**Variable trace.** Before running the model, predict these final values; then compare:

| Variable | Final value |
|---|---|
| `transitions` | `2` |

## Practice and transfer

Record each attempt in the [worksheet](../lessons/cuda-115.md) before opening hints.

### Exercise 1: Draw logical versus physical plan

**Trap to avoid:** Reading device placement from the logical plan fails, because logical nodes carry no device information and the plugin acts only on the physical plan.

### Exercise 2: Mark GPU candidate nodes

**Trap to avoid:** Guessing GPU placement from operator type, for example assuming all aggregates run on the GPU, ignores expression-level fallback.

### Exercise 3: Locate transitions

**Trap to avoid:** Counting GPU nodes and ignoring transitions makes a plan with many short GPU sections look better than one long section.

### Exercise 4: Explain lazy evaluation

**Trap to avoid:** Timing the line that defines the DataFrame and reporting it as query time measures plan construction, which is nearly instant.

### Exercise 5: Compare initial and final AQE plan

**Trap to avoid:** Citing the pre-execution plan as the executed plan can report a join strategy that never ran.

### Exercise 6: Choose operator metrics

**Trap to avoid:** Reporting only total job time hides which operator dominates and whether spilling occurred.

## Progressive hints

Hint *k* belongs to exercise *k*; open one at a time.

1. Write the query's intent as logical nodes, then write how each node would actually be executed.
2. Find the operator names the selected plugin release uses for GPU nodes, instead of guessing from the query text.
3. Mark every place where data moves between a CPU node and a GPU node.
4. Ask which call in your code actually makes Spark run the job.
5. Compare the plan printed before the action with the one shown in the completed SQL execution view.
6. Choose metrics that together describe rows, batches, time, spill and device activity for each operator.

## Common mistakes and self-check

A common mistake is reading a plan printed before any action as evidence of what ran. Adaptive Query Execution can change the physical plan at run time, and nothing executes until an action such as count. Another is labeling a whole job GPU accelerated because one GPU node appears. Fix both by inspecting the final executed plan and its metrics after an action, operator by operator, and counting the transitions where data changes representation.

**Evidence limit:** The reference counts two GPU nodes and two backend transitions in a synthetic plan. It does not run Spark, so actual plugin operator names, AQE changes and metrics require an executed query on a prepared GPU environment.

1. What is the difference between explain output and the executed SQL view?
2. Can a CPU node coexist with useful GPU computation?
3. Why count transitions in a mixed plan?

Answers: [self-check answers](../solutions/cuda-115_solutions.md#self-check-answers).

## Primary references

- [Supported Spark operators and expression types](https://nvidia.github.io/cudf-spark/docs/supported_ops.html)

Full lists: [documentation and sources](../../STUDY-GUIDE.md#documentation-and-sources).

## Ask an AI tutor about this lesson

```text
Use the checked-in $guide-ds60sqlpy-learning skill for cuda-115: From Catalyst plans to actual GPU operators.
Read courses/cuda/spark/guides/cuda-115.md and courses/cuda/spark/lessons/cuda-115.md.
Start with my current attempt and the two worked examples, and ask which backend actually ran.
Give one progressive hint at a time. Keep the separate solution closed and do not mark
progress unless I request it. Treat synthetic timings and CPU models as model evidence,
not as GPU or cluster measurements.
```
