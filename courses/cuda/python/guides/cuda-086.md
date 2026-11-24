# cuda-086: Capstone: an interoperable numerical pipeline

**Route:** CUDA Python and machine learning. **Stage:** intermediate. **Prerequisites:** `cuda-077`, `cuda-081`, `cuda-082`, `cuda-085`. Allow several sessions when the hardware experiment is new; the chapter is not a deadline.

## What you will be able to explain

By the end, you can **derive fitted means**, **draw owners and waits**, and **write the capstone acceptance report** with evidence. Start with the two worked cases, then use the editable CPU model to make the quantities concrete.

## Mechanism and vocabulary

Build a small normalize-and-score pipeline with an explicit schema: rows are observations, columns are features, inputs are finite, and the chosen accumulation dtype is documented. Compute means and scales from the training fixture only, preserve constant-feature behavior and keep transformed arrays on one backend where practical. A CPU oracle establishes expected values before any optimization.

The capstone adds ownership and dependency diagrams. Show which library owns each allocation, whether each interchange aliases or copies, and when the consumer may read it. Report preparation, transfer and computation separately, then report complete latency. One backend can implement the full pipeline; introducing a second library needs a reason. The deliverable includes an unchanged baseline and an explanation of one failed optimization.



### Key terms

- **Fitted statistic:** A value such as a mean or scale that is learned from data and then applied as a transform.
- **Data leakage:** Information from validation or test data that influences training or preprocessing and inflates measured quality.
- **Constant feature:** A column with zero variance, whose standardization divides by zero unless it is guarded.
- **Schema:** The required column names, order and dtypes that every data split must share.

## Worked examples

### Worked example 1

Center training rows [[1,2],[3,4]] to [[-1,-1],[1,1]]. Scoring with weights [2,-1] gives [-1,1]. The same means must be reused for later examples.

### Worked example 2

If validation means are recomputed independently, the transformation changes and can leak evaluation information. Preserve fitted preprocessing state rather than hiding it in a convenient expression.

## Portable executable model

The **CPU reference model** variant runs this bounded worked example using `python-core`. It uses only the Python standard library, small synthetic values and no network. Its purpose is to expose the arithmetic or contract behind the chapter. The separate reference includes assertions for the stated observations.

```python
rows = [[1, 2], [3, 4]]
means = [sum(row[c] for row in rows) / len(rows) for c in range(2)]
centered = [[x - m for x, m in zip(row, means, strict=True)] for row in rows]
scores = [sum(x * w for x, w in zip(row, [2, -1], strict=True)) for row in centered]
assert means == [2, 3] and scores == [-1, 1]
print("CPU pipeline oracle:", means, scores)
```

**Expected observation:** Fitted means [2,3] and scores [-1,1].

**Variable trace.** Before running the model, predict these final values; then compare:

| Variable | Final value |
|---|---|
| `rows` | `[[1, 2], [3, 4]]` |
| `means` | `[2.0, 3.0]` |
| `centered` | `[[-1.0, -1.0], [1.0, 1.0]]` |
| `scores` | `[-1.0, 1.0]` |

Treat printed timing values as synthetic whenever the program says model, fixture or trace. They are not measurements of your GPU. Before editing, predict the output; after editing, compare your observation with the exact contract that changed.

## Practice and transfer

### Exercise 1: Derive fitted means

**Trap to avoid:** Averaging along columns, the per-row means, gives `[1.5, 3.5]` and centers the wrong axis.

Show the intermediate values or the boundary that rules this route out, then record your answer in the worksheet.

### Exercise 2: Score the centered rows

**Trap to avoid:** Scoring the raw rows gives `[0, 2]`, which skips the fitted transformation.

Show the intermediate values or the boundary that rules this route out, then record your answer in the worksheet.

### Exercise 3: Add a constant column

**Trap to avoid:** Dividing by the standard deviation without a check fills the column with NaN, which spreads into the scores.

Show the intermediate values or the boundary that rules this route out, then record your answer in the worksheet.

### Exercise 4: Draw owners and waits

**Trap to avoid:** Drawing only the computation steps without owners loses track of when buffers can be freed.

Show the intermediate values or the boundary that rules this route out, then record your answer in the worksheet.

### Exercise 5: Design train-validation separation

**Trap to avoid:** Fitting on the concatenated train and validation data is a subtler leak with the same effect: validation scores look better than they would on truly unseen rows.

Show the intermediate values or the boundary that rules this route out, then record your answer in the worksheet.

### Exercise 6: Write the capstone acceptance report

**Trap to avoid:** Reporting a single speedup number leaves out correctness and the scope of the claim, so readers cannot tell whether transfers were timed or whether the means were reused.

Show the intermediate values or the boundary that rules this route out, then record your answer in the worksheet.

## Progressive hints

Use one hint at a time. The separate solution explains each answer after you have recorded an attempt.

1. Start from worked example 1 and mark the quantities needed for the task "Derive fitted means".
2. Change one assumption in worked example 2 while preserving the declared contract: score the centered rows.
3. Trace the CPU program's variables before adding hardware behavior: add a constant column.
4. Draw producers, consumers and the exact operation boundary for the task "Draw owners and waits".
5. Separate what the small fixture establishes from what the real runtime must show: design train-validation separation.
6. Write a counterexample to an overbroad claim before you write the capstone acceptance report.

## Common mistakes and self-review

Confusing a correct tiny example with a general implementation is the central review risk. For this chapter, challenge the assumption in worked example 2, then ask whether your change preserves the mechanism described above. If you change dtype, layout, ordering, batch size or backend, update the acceptance contract rather than silently reusing the old observation. Explain an unexpected result before trying random configuration changes.

Keep a small evidence table with columns **claim**, **input**, **expected observation**, **actual observation** and **limit**. For the first claim use `Derive fitted means`. For the final claim use `Write the capstone acceptance report`. An unperformed GPU or cluster experiment remains pending even when the CPU model is correct.

## Platform and evidence contract

The reading worksheet and CPU reference model work through the ordinary Linux Docker classroom on macOS, Linux and Windows using WSL 2. They do not require an NVIDIA GPU. Their results are labeled CPU models or semantic oracles, not simulated hardware performance.

Real CUDA work needs supported NVIDIA hardware, a compatible host driver and an explicitly prepared GPU runtime. An Apple GPU does not execute CUDA kernels. PyTorch MPS on a supported native Mac, ROCm on supported AMD hardware, or other vendor backends can provide separate accelerator learning routes; they need their own package and operation qualification and are not CUDA evidence. The ordinary Linux Docker classroom does not expose native Mac MPS automatically.

Do not download packages, models or data by opening this lesson. Do not attach an engine socket, ambient cluster credentials or an arbitrary remote endpoint. A CPU pass, imported package, successful compilation, real GPU result and measured performance are distinct observations. Record the actual backend, data shape/dtype, source revision, versions and pending checks. A saved completion marker records learning progress, not hardware certification.

## Primary references

- [DLPack Python specification](https://dmlc.github.io/dlpack/latest/python_spec.html)
- [CuPy interoperability](https://docs.cupy.dev/en/stable/user_guide/interoperability.html)

Use the version-matched documentation of your prepared environment. These references describe interfaces and supported boundaries; the chapter's synthetic examples and CPU models are original teaching material.

## Ask an AI tutor about this lesson

```text
Use the checked-in $guide-ds60sqlpy-learning skill for cuda-086: Capstone: an interoperable numerical pipeline.
Read courses/cuda/python/guides/cuda-086.md and courses/cuda/python/lessons/cuda-086.md.
Start with my current attempt and the two worked examples, and ask which backend actually ran.
Give one progressive hint at a time. Keep the separate solution closed and do not mark
progress unless I request it. Treat synthetic timings and CPU models as model evidence,
not as GPU or cluster measurements.
```
