# cuda-116: Supported operations, fallback and semantic boundaries

**Route:** CUDA Python and machine learning / GPU Spark specialization. **Stage:** advanced. **Prerequisites:** `cuda-115`.

Pacing, evidence labels and platform rules: [CUDA study guide](../../STUDY-GUIDE.md).

## Learning objectives

- Classify fallback versus unavailable device.
- Find an unsupported expression.
- Count boundary costs.
- Rewrite an opaque function declaratively.
- Preserve edge semantics.
- Design a mixed-plan report.

## Mechanism and vocabulary

Support depends on operator, expression, dtype and configuration. A supported aggregate on one type may fall back on another expression or precision requirement. CPU fallback means a compatible plugin environment selects CPU execution for an unsupported part of a query. It does not mean a missing NVIDIA GPU can always initialize the enabled plugin and run normally.

For CPU-only study, use ordinary Spark with the GPU plugin disabled or absent. For GPU study, inspect supported-operator documentation for the chosen release and capture reasons such as NOT_ON_GPU diagnostics. A mixed plan may pay row/columnar conversions and device transfers repeatedly. Do not force an incompatible operator merely to increase GPU coverage; preserve semantics and measure the whole query.

## Four states that should never share one success label

**CPU baseline** means ordinary Spark runs with the GPU plugin absent or disabled. It should work on a supported CPU-only host and is the rollback and semantic comparison. **Plugin initialization failure** means the requested accelerated environment could not start correctly, perhaps because device exposure or native libraries are unavailable. That is a failure, not a successful fallback.

**Operator fallback** means a functioning plugin environment keeps an unsupported operator or expression on CPU while other supported work may use the GPU. **GPU execution** means the intended compatible operator actually ran on the device and produced an accepted result. These states require different troubleshooting and should be recorded separately in the learning notebook.

Suppose a query filters, invokes a Python UDF, then aggregates. The UDF may create a boundary even when the surrounding operators are supported. Replacing it with built-in expressions can expose the algebra to Catalyst, but only if the replacement matches null behavior, input types, overflow, timestamps and any error semantics. A mathematically similar expression can still differ under SQL's type rules.

Use the release's supported-operator list and `spark.rapids.sql.explain=NOT_ON_GPU` diagnostics as aids, not universal truths detached from versions. The published table may be generated against a particular Spark release; inspect the matching plugin and distribution notes. An explicit CPU/GPU parity test over adversarial tiny fixtures is the final semantic guard before measuring a larger workload.


### Key terms

- **CPU fallback:** Running an unsupported part of a query on the CPU inside a working GPU plugin environment.
- **Unsupported expression:** An expression or dtype the plugin release cannot execute on the GPU under the current configuration.
- **Explain diagnostics:** Plugin output that reports which operators will not run on the GPU and why.
- **CPU-only baseline:** An ordinary Spark run with the GPU plugin disabled or absent, used as the semantic reference.

## Worked examples

### Worked example 1

GPU aggregate -> CPU UDF -> GPU projection crosses the boundary twice around the UDF. Replacing the UDF with an equivalent supported expression might reduce transitions after parity tests.

### Worked example 2

A machine with no GPU should use the CPU baseline configuration. This differs from a GPU machine where one unsupported expression falls back inside an otherwise valid plugin job.

## How to run the CPU model

Edit the copy; the [reference](../references/cuda-116_cpu.py) adds assertions.

```sh
python courses/cuda/spark/lessons/cuda-116_cpu.py
```

```python
states = [
    {"gpu_visible": False, "plugin_enabled": False},
    {"gpu_visible": True, "plugin_enabled": True, "cpu_operator": True},
]
assert states[0]["plugin_enabled"] is False
assert states[1]["cpu_operator"] is True
print("CPU configuration worksheet: CPU baseline and GPU mixed plan are distinct")
```

**Expected observation:** CPU-only baseline and per-operator fallback are modeled separately.

## Practice and transfer

Record each attempt in the [worksheet](../lessons/cuda-116.md) before opening hints.

### Exercise 1: Classify fallback versus unavailable device

**Trap to avoid:** Calling a GPU-less run a fallback suggests the plugin was active and made per-operator choices, when actually it never started.

### Exercise 2: Find an unsupported expression

**Trap to avoid:** Assuming support from the operator name alone misses expression-level and type-level restrictions, which are the usual cause of fallback.

### Exercise 3: Count boundary costs

**Trap to avoid:** Assuming only the UDF runs slower and the rest stays fast ignores that the transitions stall the GPU sections on both sides.

### Exercise 4: Rewrite an opaque function declaratively

**Trap to avoid:** Rewriting with a built-in that differs on edge cases, such as whitespace or null handling, changes results while appearing equivalent.

### Exercise 5: Preserve edge semantics

**Trap to avoid:** Testing only typical values passes implementations that disagree exactly where production data is unusual.

### Exercise 6: Design a mixed-plan report

**Trap to avoid:** Reporting only the percentage of GPU operators hides which fallback is expensive. One fallback on a small lookup table may be harmless, while one on the widest projection can dominate the job.

## Progressive hints

Hint *k* belongs to exercise *k*; open one at a time.

1. Ask whether the plugin environment is valid and chose the CPU for one operator, or whether no usable GPU exists at all.
2. Check the operator, the expression and the data type against the release's supported-operator documentation.
3. Count each crossing between columnar GPU execution and row-based CPU execution, both into and out of the UDF.
4. Find a built-in expression with the same meaning as the UDF, and prove equivalence before replacing it.
5. Include nulls, overflow, strings and timestamps in the parity tests for any rewrite.
6. For each operator that stayed on the CPU, record the diagnostic reason and the transitions it caused.

## Common mistakes and self-check

A common mistake is assuming CPU fallback means a machine without a GPU can run with the plugin enabled. Fallback is a per-operator choice inside a valid plugin environment; a machine with no GPU should use the plain CPU baseline. Another mistake is forcing an incompatible operator onto the GPU to raise coverage. Fix both by keeping the two cases separate, preserving semantics with parity tests and measuring the whole query, transitions included.

**Evidence limit:** The reference models a CPU-only baseline and per-operator fallback as separate cases. It cannot produce NOT_ON_GPU diagnostics or measure conversion costs, which need the selected plugin release on a GPU host.

1. What does support depend on in the plugin?
2. Why can a mixed plan be slower than expected?
3. How should CPU-only learners run Spark in this course?

Answers: [self-check answers](../solutions/cuda-116_solutions.md#self-check-answers).

## Primary references

- [Supported Spark operators and expression types](https://nvidia.github.io/cudf-spark/docs/supported_ops.html)

Full lists: [documentation and sources](../../STUDY-GUIDE.md#documentation-and-sources).

## Ask an AI tutor about this lesson

```text
Use the checked-in $guide-ds60sqlpy-learning skill for cuda-116: Supported operations, fallback and semantic boundaries.
Read courses/cuda/spark/guides/cuda-116.md and courses/cuda/spark/lessons/cuda-116.md.
Start with my current attempt and the two worked examples, and ask which backend actually ran.
Give one progressive hint at a time. Keep the separate solution closed and do not mark
progress unless I request it. Treat synthetic timings and CPU models as model evidence,
not as GPU or cluster measurements.
```
