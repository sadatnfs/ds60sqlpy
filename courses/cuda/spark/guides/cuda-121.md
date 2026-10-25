# cuda-121: Joins, skew and broadcast decisions

**Route:** CUDA Python and machine learning / GPU Spark specialization. **Stage:** advanced. **Prerequisites:** `cuda-117`, `cuda-120`. Allow several sessions when the hardware experiment is new; the chapter is not a deadline.

## What you will be able to explain

By the end, you can **calculate duplicate join output**, **compare broadcast and shuffle**, and **inspect final AQE decision** with evidence. Start with the two worked cases, then use the editable CPU model to make the quantities concrete.

## Mechanism and vocabulary

A join matches keys across relations; duplicate keys multiply output rows. GPU acceleration cannot remove that semantic expansion. A broadcast join replicates a small side to workers, while a shuffle join redistributes records by key. Choice depends on estimated sizes, runtime statistics, supported operators and memory. Broadcasting a relation that only appears small in stale statistics can cause pressure.

Skew concentrates rows on a few keys, creating large partitions and long tasks. Salting or repartitioning is not automatically correct: a transformation must preserve intended join multiplicity and outer-join behavior. Inspect partition sizes, output cardinality and the final adaptive plan. Keep one simple CPU oracle with duplicate and missing keys to prevent a fast but incorrect rewrite.

## Derive join cardinality before tuning it

For an inner equijoin, let \(l_k\) be the number of left records for key \(k\) and \(r_k\) the number on the right. Output cardinality is:

\[
\sum_k l_k r_k.
\]

This explains why duplicate dimension keys can unexpectedly multiply a fact table. A GPU cannot optimize away required output rows. If the application assumes a unique dimension key, validate uniqueness as an input contract. Applying `distinct` after the join is not a general repair because it can erase legitimate duplicate facts.

Broadcast avoids redistributing the large side by replicating a suitably small side, but each executor must accommodate that replicated structure and the join's live state. A shuffle join moves records to key owners. Skew can make one key dominate both memory and runtime. Inspect maximum and percentile partition sizes, not only average rows per partition.

AQE may change the chosen join using observed statistics. Record the final executed plan and compare output multiplicity before and after any rewrite. Salting a hot key requires careful duplication or redistribution of the matching side and a proof that every intended pair appears once. Outer joins add unmatched-row/null behavior, making an informal salting recipe particularly risky. Start with the tiny duplicate-key oracle, then expand only after exact semantic parity.


## Worked examples

### Worked example 1

Left keys [A, A, B] and right keys [A, A, C] produce four matches for A in an inner join. Expected cardinality is not the minimum of input lengths.

### Worked example 2

If one partition holds 900 rows and nine others hold roughly 11, the maximum task dominates the barrier despite a small average partition size.

## Portable executable model

The **CPU reference model** variant runs this bounded worked example using `python-core`. It uses only the Python standard library, small synthetic values and no network. Its purpose is to expose the arithmetic or contract behind the chapter. The separate reference includes assertions for the stated observations.

```python
left = [("A", 1), ("A", 2), ("B", 3)]
right = [("A", 10), ("A", 20), ("C", 30)]
joined = [(k, a, b) for k, a in left for r, b in right if k == r]
assert len(joined) == 4
assert {k for k, _, _ in joined} == {"A"}
print("CPU join oracle:", joined)
```

**Expected observation:** Four A matches from two-by-two duplicate keys.

Treat printed timing values as synthetic whenever the program says model, fixture or trace. They are not measurements of your GPU. Before editing, predict the output; after editing, compare your observation with the exact contract that changed.

## Scala and PySpark parity lab

Choose **Scala Spark on CPU** or **PySpark on CPU** to run the same bounded query in the ordinary Spark workers. Both use explicit schemas, local fixtures, at most two local threads, a disabled GPU SQL setting and a finally-block session stop. They assert the same expected result. These are CPU Spark observations, not GPU plugin qualification.

For external GPU comparison, retain the same relational expressions and expected result but use a separately reviewed launcher and compatibility matrix. Do not change the classroom source into an arbitrary cluster connection.

## Practice and transfer

### Exercise 1: Calculate duplicate join output

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 1 targets **calculate duplicate join output** in the examples above.

### Exercise 2: Add unmatched keys

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 2 targets **add unmatched keys** in the examples above.

### Exercise 3: Identify skew

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 3 targets **identify skew** in the examples above.

### Exercise 4: Compare broadcast and shuffle

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 4 targets **compare broadcast and shuffle** in the examples above.

### Exercise 5: Design a safe rewrite

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 5 targets **design a safe rewrite** in the examples above.

### Exercise 6: Inspect final AQE decision

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 6 targets **inspect final AQE decision** in the examples above.

## Progressive hints

Use one hint at a time. The separate solution explains each answer after you have recorded an attempt.

1. Start from worked example 1 and mark the quantities needed for the task "Calculate duplicate join output".
2. Change one assumption in worked example 2 while preserving the declared contract: add unmatched keys.
3. Trace the CPU program's variables before adding hardware behavior: identify skew.
4. Draw producers, consumers and the exact operation boundary for the task "Compare broadcast and shuffle".
5. Separate what the small fixture establishes from what the real runtime must show: design a safe rewrite.
6. Write a counterexample to an overbroad claim before you inspect final AQE decision.

## Common mistakes and self-review

Confusing a correct tiny example with a general implementation is the central review risk. For this chapter, challenge the assumption in worked example 2, then ask whether your change preserves the mechanism described above. If you change dtype, layout, ordering, batch size or backend, update the acceptance contract rather than silently reusing the old observation. Explain an unexpected result before trying random configuration changes.

Keep a small evidence table with columns **claim**, **input**, **expected observation**, **actual observation** and **limit**. For the first claim use `Calculate duplicate join output`. For the final claim use `Inspect final AQE decision`. An unperformed GPU or cluster experiment remains pending even when the CPU model is correct.

## Platform and evidence contract

The reading worksheet and CPU reference model work through the ordinary Linux Docker classroom on macOS, Linux and Windows using WSL 2. They do not require an NVIDIA GPU. Their results are labeled CPU models or semantic oracles, not simulated hardware performance.

Real CUDA work needs supported NVIDIA hardware, a compatible host driver and an explicitly prepared GPU runtime. An Apple GPU does not execute CUDA kernels. PyTorch MPS on a supported native Mac, ROCm on supported AMD hardware, or other vendor backends can provide separate accelerator learning routes; they need their own package and operation qualification and are not CUDA evidence. The ordinary Linux Docker classroom does not expose native Mac MPS automatically.

Do not download packages, models or data by opening this lesson. Do not attach an engine socket, ambient cluster credentials or an arbitrary remote endpoint. A CPU pass, imported package, successful compilation, real GPU result and measured performance are distinct observations. Record the actual backend, data shape/dtype, source revision, versions and pending checks. A saved completion marker records learning progress, not hardware certification.

GPU Spark is a separate owned external workflow. The ordinary `spark-local-scala` and `spark-local-python` profiles are CPU Spark. Keep the GPU plugin disabled or absent for a CPU-only baseline. Per-operator CPU fallback inside a working GPU plugin environment is a different condition from having no compatible GPU. Never mount a host Docker socket or ambient kubeconfig into an ordinary lesson worker.

## Ask an AI tutor about this lesson

> I am studying `cuda-121` using `courses/cuda/spark/guides/cuda-121.md` and `courses/cuda/spark/lessons/cuda-121.md`. Help me reason about Joins, skew and broadcast decisions. Start with my current attempt and the two worked examples. Ask which backend actually ran, give one progressive hint, and do not reveal the separate solution or mark progress unless I request it.

## Primary references

- [cuDF Spark plugin release and compatibility matrix](https://nvidia.github.io/cudf-spark/docs/download.html)
- [Supported Spark operators and expression types](https://nvidia.github.io/cudf-spark/docs/supported_ops.html)
- [GPU Spark tuning guide](https://docs.nvidia.com/cudf-spark/latest/tuning-guide.html)
- [Apache Spark SQL performance tuning](https://spark.apache.org/docs/latest/sql-performance-tuning.html)

Use the version-matched documentation of your prepared environment. These references describe interfaces and supported boundaries; the chapter's synthetic examples and CPU models are original teaching material.
