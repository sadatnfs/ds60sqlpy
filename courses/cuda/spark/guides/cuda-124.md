# cuda-124: Python UDFs, pandas APIs and GPU-aware ML boundaries

**Route:** CUDA Python and machine learning / GPU Spark specialization. **Stage:** advanced. **Prerequisites:** `cuda-116`, `cuda-118`.

Pacing, evidence labels and platform rules: [CUDA study guide](../../STUDY-GUIDE.md).

## Learning objectives

- Classify four APIs.
- Replace an equivalent simple UDF.
- Explain Arrow limits.
- Define GPU-aware UDF ownership.
- Distinguish SQL and ML acceleration.
- Design quality parity tests.

## Mechanism and vocabulary

Spark SQL expressions, Python UDFs, pandas UDFs, pandas API on Spark and GPU dataframe libraries are different execution surfaces. Arrow can improve interchange for vectorized UDFs without making their body GPU code. A GPU-aware UDF must explicitly manage supported packages, device assignment, batch size and transfers under a reviewed contract. Ordinary plugin enablement does not rewrite arbitrary Python algorithms.

GPU-accelerated machine-learning integrations such as Spark RAPIDS ML are separate from SQL operator acceleration. Estimator support, semantics and release compatibility need their own validation. A training job inside each partition can duplicate work or oversubscribe a device if resource ownership is unclear. Keep preprocessing, distributed SQL and training responsibilities explicit, and compare model quality as well as elapsed time.

## Avoid the GPU-UDF shortcut trap

A common mistake is to create a GPU model or dataframe inside every UDF call. That can repeatedly initialize contexts, transfer tiny batches and duplicate model storage. Even when each call is numerically correct, the process and batching design can overwhelm the useful GPU work. A vectorized UDF changes batching, but still needs explicit resource ownership and package compatibility.

A declarative built-in expression gives Catalyst visibility into algebra and types. Prefer it when it expresses the same contract. When a genuinely custom GPU operation is needed, define per-worker initialization, bounded batch sizes, device assignment, input/output schema, null policy and cleanup. Do not let every partition choose device zero independently on a multi-executor host.

Machine-learning training is another boundary. A SQL acceleration plugin does not automatically coordinate gradient collectives across Spark tasks. Separate GPU-aware ML integrations can provide reviewed estimator behavior, but they need their own supported algorithms, versions and quality comparisons. The curriculum therefore links the Spark specialization to the PyTorch/TensorFlow distribution chapters without treating one scheduler as a drop-in replacement for the other.

For the included null-preserving doubling example, the built-in expression and reference function agree on integers and missing values. The next meaningful test adds type boundaries and verifies the output schema. Only after that should a real Spark plan be inspected for supported acceleration. This sequence makes correctness visible before any GPU configuration is introduced.


### Key terms

- **Python UDF:** A row-at-a-time Python function called from Spark, which the GPU plugin does not translate.
- **Pandas UDF:** A vectorized Python function that receives Arrow-backed batches as pandas objects.
- **Pandas API on Spark:** A pandas-like interface that compiles to Spark plans rather than running pandas code directly.
- **GPU-aware UDF:** A UDF that explicitly manages GPU packages, device assignment, batch size and transfers under a reviewed contract.

## Worked examples

### Worked example 1

A built-in multiplication expression is visible in the relational plan. A Python UDF returning x*2 may hide the same algebra behind a process boundary and block equivalent optimization.

### Worked example 2

Calling a GPU library from every partition does not automatically coordinate multi-GPU training. Each task needs a defined device share and bounded memory contract.

## How to run the CPU model

Edit the copy; the [reference](../references/cuda-124_cpu.py) adds assertions.

```sh
python courses/cuda/spark/lessons/cuda-124_cpu.py
```

```python
values = [1, None, 3]


def expression(x):
    return None if x is None else x * 2


expected = [2, None, 6]
assert [expression(x) for x in values] == expected
print("CPU expression parity oracle:", expected)
```

**Expected observation:** Null-preserving expression produces [2, None, 6].

**Variable trace.** Before running the model, predict these final values; then compare:

| Variable | Final value |
|---|---|
| `values` | `[1, None, 3]` |
| `expected` | `[2, None, 6]` |

## Practice and transfer

Record each attempt in the [worksheet](../lessons/cuda-124.md) before opening hints.

### Exercise 1: Classify four APIs

**Trap to avoid:** Treating a pandas UDF as equivalent to a built-in because it is vectorized ignores the process boundary and serialization that still surround it.

### Exercise 2: Replace an equivalent simple UDF

**Trap to avoid:** Replacing a UDF that maps null to 0 with the built-in, which keeps null, changes results while appearing to be the same arithmetic.

### Exercise 3: Explain Arrow limits

**Trap to avoid:** Assuming that enabling Arrow moves UDF work to the GPU confuses data format with execution location.

### Exercise 4: Define GPU-aware UDF ownership

**Trap to avoid:** Calling a GPU library from every partition with no device assignment risks oversubscription and out-of-memory errors that appear only at higher concurrency.

### Exercise 5: Distinguish SQL and ML acceleration

**Trap to avoid:** Reporting the whole pipeline as accelerated because the SQL plan shows GPU operators omits the training step.

### Exercise 6: Design quality parity tests

**Trap to avoid:** Comparing a GPU model trained on a different split with a CPU model attributes data differences to the backend.

## Progressive hints

Hint *k* belongs to exercise *k*; open one at a time.

1. List the execution surfaces and say for each whether the work runs as Spark operators, a Python process or a local library.
2. Check that the built-in expression returns null for a null input and keeps the same result type as the UDF.
3. Ask what Arrow changes about moving data into a pandas UDF and what it leaves unchanged about where the body runs.
4. Write down which device a GPU-aware UDF uses, how large each batch is and how memory is released afterward.
5. Ask whether enabling SQL operator acceleration also accelerates a machine learning estimator.
6. Use the same split, target, metric and preprocessing for both training paths before comparing time.

## Common mistakes and self-check

A common mistake is wrapping simple algebra such as `x*2` in a Python UDF. The expression disappears behind a process boundary and blocks optimization that a built-in expression would allow. Another is calling a GPU library from every partition without a resource contract, which can oversubscribe a device. Fix both by preferring built-in expressions whose null and type semantics match, and by giving GPU-aware UDFs an explicit device share, batch size and cleanup plan.

**Evidence limit:** The reference produces the null-preserving result `[2, None, 6]` in Python. It does not run pandas UDFs, Spark RAPIDS ML or a GPU library, so their execution surfaces and compatibility must be validated separately.

1. Does Arrow make a pandas UDF's body run on the GPU?
2. Why are SQL and ML acceleration validated separately?
3. Why compare model quality as well as elapsed time?

Answers: [self-check answers](../solutions/cuda-124_solutions.md#self-check-answers).

## Primary references

- [Supported Spark operators and expression types](https://nvidia.github.io/cudf-spark/docs/supported_ops.html)

Full lists: [documentation and sources](../../STUDY-GUIDE.md#documentation-and-sources).

## Ask an AI tutor about this lesson

```text
Use the checked-in $guide-ds60sqlpy-learning skill for cuda-124: Python UDFs, pandas APIs and GPU-aware ML boundaries.
Read courses/cuda/spark/guides/cuda-124.md and courses/cuda/spark/lessons/cuda-124.md.
Start with my current attempt and the two worked examples, and ask which backend actually ran.
Give one progressive hint at a time. Keep the separate solution closed and do not mark
progress unless I request it. Treat synthetic timings and CPU models as model evidence,
not as GPU or cluster measurements.
```
