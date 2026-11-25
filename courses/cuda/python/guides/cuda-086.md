# cuda-086: Capstone: an interoperable numerical pipeline

**Route:** CUDA Python and machine learning. **Stage:** intermediate. **Prerequisites:** `cuda-077`, `cuda-081`, `cuda-082`, `cuda-085`.

Pacing, evidence labels and platform rules: [CUDA study guide](../../STUDY-GUIDE.md).

## Learning objectives

- Derive fitted means.
- Score the centered rows.
- Add a constant column.
- Draw owners and waits.
- Design train-validation separation.
- Write the capstone acceptance report.

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

## How to run the CPU model

Edit the copy; the [reference](../references/cuda-086_cpu.py) adds assertions.

```sh
python courses/cuda/python/lessons/cuda-086_cpu.py
```

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

## Practice and transfer

Record each attempt in the [worksheet](../lessons/cuda-086.md) before opening hints.

### Exercise 1: Derive fitted means

**Trap to avoid:** Averaging along columns, the per-row means, gives `[1.5, 3.5]` and centers the wrong axis.

### Exercise 2: Score the centered rows

**Trap to avoid:** Scoring the raw rows gives `[0, 2]`, which skips the fitted transformation.

### Exercise 3: Add a constant column

**Trap to avoid:** Dividing by the standard deviation without a check fills the column with NaN, which spreads into the scores.

### Exercise 4: Draw owners and waits

**Trap to avoid:** Drawing only the computation steps without owners loses track of when buffers can be freed.

### Exercise 5: Design train-validation separation

**Trap to avoid:** Fitting on the concatenated train and validation data is a subtler leak with the same effect: validation scores look better than they would on truly unseen rows.

### Exercise 6: Write the capstone acceptance report

**Trap to avoid:** Reporting a single speedup number leaves out correctness and the scope of the claim, so readers cannot tell whether transfers were timed or whether the means were reused.

## Progressive hints

Hint *k* belongs to exercise *k*; open one at a time.

1. Average each column of the two training rows separately.
2. Subtract the fitted means from each row, then take the dot product with `[2, -1]`.
3. Ask what a zero standard deviation does to division, and what scale value the schema should declare instead.
4. For each array, name the library that allocated it, whether each handoff copies or aliases, and who reads it last.
5. Ask which statistics a validation row may use, and where they must come from.
6. List what a reviewer needs to accept the run: values, tolerances, timing boundaries and unsupported cases.

## Common mistakes and self-check

The typical capstone mistake is refitting preprocessing on validation data. Recomputing means independently changes the transformation and leaks evaluation information, so scores are no longer comparable. Another mistake is mixing libraries without a reason, which adds copies, ownership questions and waits. Fix both by fitting means and scales once on the training fixture, saving that state and reusing it, keeping the pipeline on one backend where practical, and documenting every allocation owner and handoff.

**Misconception:** If the pipeline's final scores match the CPU oracle, the capstone is complete. **Correction:** Matching scores show the arithmetic is right for this fixture, but the capstone also asks which library owns each allocation, whether each handoff aliases or copies and when the consumer may read. A pipeline can produce correct scores while copying the data three times, or while reading a buffer before its producer finished on another stream. Report the ownership diagram and separate preparation, transfer and compute timings alongside the equality check.

**Evidence limit:** The reference fits means `[2, 3]` and scores `[-1, 1]` on a two-row fixture with plain Python. It establishes expected values, not interchange behavior or latency, which require running the pipeline on a supported backend.

1. Why establish a CPU oracle before optimizing the pipeline?
2. How should a constant feature be handled?
3. Why report preparation, transfer and computation separately?

Answers: [self-check answers](../solutions/cuda-086_solutions.md#self-check-answers).

## Primary references

- [DLPack Python specification](https://dmlc.github.io/dlpack/latest/python_spec.html)

Full lists: [documentation and sources](../../STUDY-GUIDE.md#documentation-and-sources).

## Ask an AI tutor about this lesson

```text
Use the checked-in $guide-ds60sqlpy-learning skill for cuda-086: Capstone: an interoperable numerical pipeline.
Read courses/cuda/python/guides/cuda-086.md and courses/cuda/python/lessons/cuda-086.md.
Start with my current attempt and the two worked examples, and ask which backend actually ran.
Give one progressive hint at a time. Keep the separate solution closed and do not mark
progress unless I request it. Treat synthetic timings and CPU models as model evidence,
not as GPU or cluster measurements.
```
