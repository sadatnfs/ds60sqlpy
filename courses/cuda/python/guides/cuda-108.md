# cuda-108: Accelerator-aware data science pipelines

**Route:** CUDA Python and machine learning. **Stage:** advanced. **Prerequisites:** `cuda-068`, `cuda-081`, `cuda-085`. Allow several sessions when the hardware experiment is new; the chapter is not a deadline.

## What you will be able to explain

By the end, you can **compute grouped sums**, **preserve row identity**, and **distinguish cuDF from Spark acceleration** with evidence. Start with the two worked cases, then use the editable CPU model to make the quantities concrete.

## Mechanism and vocabulary

Tabular acceleration connects schemas, null masks, columnar storage, preprocessing and model inputs. RAPIDS cuDF provides GPU dataframe operations; it is not the Spark scheduling engine. A single-process cuDF pipeline differs from the cuDF plugin that replaces supported Spark physical operators. Both require compatible NVIDIA execution for their GPU paths, and both can spend time moving data across boundaries.

Preserve null semantics, category mappings and row identity when converting a dataframe into dense tensors. A missing value is not always a NaN, and an integer nullable column may require a validity mask. Fit encoders on training data and define unknown-category behavior. Compare with a CPU dataframe or simple Python oracle before measuring. The Spark specialization follows this chapter for distributed plans, resource scheduling and operations.



## Worked examples

### Worked example 1

Rows [(A,2),(A, null),(B,5)] grouped by category have non-null sums A=2 and B=5 under the declared skip-null rule. Counting rows and counting non-null values are different.

### Worked example 2

Encoding categories A->0, B->1 then seeing C requires an explicit unknown policy. Relearning category IDs independently in another partition can corrupt model features.

## Portable executable model

The **CPU reference model** variant runs this bounded worked example using `python-core`. It uses only the Python standard library, small synthetic values and no network. Its purpose is to expose the arithmetic or contract behind the chapter. The separate reference includes assertions for the stated observations.

```python
rows = [("A", 2), ("A", None), ("B", 5)]
totals = {}
counts = {}
for key, value in rows:
    totals.setdefault(key, 0)
    counts[key] = counts.get(key, 0) + 1
    if value is not None:
        totals[key] += value
assert totals == {"A": 2, "B": 5} and counts["A"] == 2
print("CPU dataframe oracle:", totals, counts)
```

**Expected observation:** Grouped sums A 2, B 5 and row count A 2.

Treat printed timing values as synthetic whenever the program says model, fixture or trace. They are not measurements of your GPU. Before editing, predict the output; after editing, compare your observation with the exact contract that changed.

## Practice and transfer

### Exercise 1: Compute grouped sums

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 1 targets **compute grouped sums** in the examples above.

### Exercise 2: Distinguish null and zero

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 2 targets **distinguish null and zero** in the examples above.

### Exercise 3: Define category mapping

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 3 targets **define category mapping** in the examples above.

### Exercise 4: Preserve row identity

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 4 targets **preserve row identity** in the examples above.

### Exercise 5: Count conversion bytes

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 5 targets **count conversion bytes** in the examples above.

### Exercise 6: Distinguish cuDF from Spark acceleration

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 6 targets **distinguish cuDF from Spark acceleration** in the examples above.

## Progressive hints

Use one hint at a time. The separate solution explains each answer after you have recorded an attempt.

1. Start from worked example 1 and mark the quantities needed for the task "Compute grouped sums".
2. Change one assumption in worked example 2 while preserving the declared contract: distinguish null and zero.
3. Trace the CPU program's variables before adding hardware behavior: define category mapping.
4. Draw producers, consumers and the exact operation boundary for the task "Preserve row identity".
5. Separate what the small fixture establishes from what the real runtime must show: count conversion bytes.
6. Write a counterexample to an overbroad claim before you distinguish cuDF from Spark acceleration.

## Common mistakes and self-review

Confusing a correct tiny example with a general implementation is the central review risk. For this chapter, challenge the assumption in worked example 2, then ask whether your change preserves the mechanism described above. If you change dtype, layout, ordering, batch size or backend, update the acceptance contract rather than silently reusing the old observation. Explain an unexpected result before trying random configuration changes.

Keep a small evidence table with columns **claim**, **input**, **expected observation**, **actual observation** and **limit**. For the first claim use `Compute grouped sums`. For the final claim use `Distinguish cuDF from Spark acceleration`. An unperformed GPU or cluster experiment remains pending even when the CPU model is correct.

## Platform and evidence contract

The reading worksheet and CPU reference model work through the ordinary Linux Docker classroom on macOS, Linux and Windows using WSL 2. They do not require an NVIDIA GPU. Their results are labeled CPU models or semantic oracles, not simulated hardware performance.

Real CUDA work needs supported NVIDIA hardware, a compatible host driver and an explicitly prepared GPU runtime. An Apple GPU does not execute CUDA kernels. PyTorch MPS on a supported native Mac, ROCm on supported AMD hardware, or other vendor backends can provide separate accelerator learning routes; they need their own package and operation qualification and are not CUDA evidence. The ordinary Linux Docker classroom does not expose native Mac MPS automatically.

Do not download packages, models or data by opening this lesson. Do not attach an engine socket, ambient cluster credentials or an arbitrary remote endpoint. A CPU pass, imported package, successful compilation, real GPU result and measured performance are distinct observations. Record the actual backend, data shape/dtype, source revision, versions and pending checks. A saved completion marker records learning progress, not hardware certification.

## Ask an AI tutor about this lesson

> I am studying `cuda-108` using `courses/cuda/python/guides/cuda-108.md` and `courses/cuda/python/lessons/cuda-108.md`. Help me reason about Accelerator-aware data science pipelines. Start with my current attempt and the two worked examples. Ask which backend actually ran, give one progressive hint, and do not reveal the separate solution or mark progress unless I request it.

## Primary references

- [PyTorch CUDA semantics](https://docs.pytorch.org/docs/2.9/notes/cuda.html)
- [TensorFlow GPU guide](https://www.tensorflow.org/guide/gpu)

Use the version-matched documentation of your prepared environment. These references describe interfaces and supported boundaries; the chapter's synthetic examples and CPU models are original teaching material.
