# cuda-024: First capstone: a reliable GPU data pipeline

## Level and prerequisites

Intermediate; about 110 minutes, plus any optional hardware experiment. Direct prerequisites: `cuda-014`, `cuda-020`, `cuda-021`, `cuda-022`, `cuda-008`

Pacing, evidence labels and platform rules for every chapter are in the [CUDA study guide](../../STUDY-GUIDE.md).

## Learning objectives

Build a multi-stage GPU data pipeline with a CPU oracle, adversarial fixtures and an honest end-to-end report.

**Scope:** Composition of validated kernels, data ownership across stages, bounded input contracts and meaningful application timing.

**Evidence to produce:** A specification, CPU oracle, adversarial fixtures, checked error paths, actual GPU output and honest end-to-end report.

## Purpose, vocabulary and mental model

A pipeline is more than a list of correct kernels. Each stage has a shape, ownership and validity contract that must match its consumer. Filtering changes count; normalization changes numeric range; histogramming assumes valid bins. Keep the count with the output buffer, and do not pass allocation capacity as the number of valid elements. First build a tiny CPU oracle, then introduce one GPU stage at a time. A useful capstone report includes cases where a CPU is preferable, because proving that a GPU exists is different from proving it helps the application.

### Key terms

- **Pipeline stage:** One transformation with its own shape, ownership and validity contract that its consumer depends on.
- **CPU oracle:** An independent, trusted CPU implementation used to judge GPU outputs.
- **Valid count:** The number of meaningful elements in a buffer, which can be smaller than its allocated capacity.
- **Adversarial fixture:** A deliberately difficult input, such as an empty, tiny or boundary-sized case, chosen to expose defects.

## How to run and study this lesson

Trace worked example 1 by hand, then run the [CPU reference](../references/cuda-024_cpu.py) from the repository root:

```sh
python courses/cuda/cpp/references/cuda-024_cpu.py
```

## Worked example 1: trace the mechanism

A synthetic event pipeline keeps nonnegative values from \([-2,1,3,-1,2]\), producing \([1,3,2]\). It computes count three, sum six and mean two. A histogram over bins 0 through 3 gives \([0,1,1,1]\). This ties compaction output count to every downstream stage.

**Why:** Compaction yields [1, 3, 2], so count 3, sum 6 and mean 2 follow, and bins 1, 2, 3 each get one value.

```python
values = [-2, 1, 3, -1, 2]
selected = [v for v in values if v >= 0]
bins = [selected.count(i) for i in range(4)]
assert selected == [1, 3, 2] and bins == [0, 1, 1, 1]
result = {"count": len(selected), "sum": sum(selected), "mean": sum(selected) / len(selected)}
assert result == {"count": 3, "sum": 6, "mean": 2.0}
print(result, bins)
```

**Expected observation:** every assertion succeeds, and the CPU model prints:

```text
{'count': 3, 'sum': 6, 'mean': 2.0} [0, 1, 1, 1]
```

**Check:** The reference asserts selected == [1, 3, 2], bins == [0, 1, 1, 1] and the result dictionary with mean 2.0.

## Worked example 2: change a meaningful condition

An empty selection from \([-4,-1]\) has count zero and sum zero, but no defined ordinary arithmetic mean. Return a named empty-result status or optional mean rather than dividing by zero. The histogram remains four zeros under this contract.

**Why:** Zero values have a defined count and sum but no ordinary mean, and the histogram is four zeros.

**Check:** Run [-4, -1] and assert count 0, sum 0, a missing mean and bins [0, 0, 0, 0].

## Six progressive exercises

### Exercise 1

Reconstruct worked example 1 on paper before running its CPU reference. Select nonnegative values from [-2, 1, 3, -1, 2], then compute count, sum, mean and four bins from the selected count only.

**Trap to avoid:** Running the aggregate kernels over the full capacity of the output buffer adds unselected garbage to the sum.

**Hint:** Start with the literal input and intermediate quantities in worked example 1.

### Exercise 2

Rework worked example 2 without copying its conclusion. Detect count zero after compaction and return an empty status or optional mean while keeping count and sum at zero.

**Trap to avoid:** Dividing sum by count anyway produces NaN for floats or a division fault for integers.

**Hint:** Identify exactly which condition changes in worked example 2.

### Exercise 3

Specify the pipeline output for \([0,0,3]\).

**Trap to avoid:** Treating zero as falsy in the predicate drops both zeros and returns count 1.

**Hint:** Use the first worked example to establish the relevant quantities, then change only the requested input.

### Exercise 4

A downstream kernel consumes capacity ten after only three items were selected. Diagnose it.

**Trap to avoid:** Zeroing the unused seven slots makes the sum correct but still corrupts count, mean and bin zero.

**Hint:** Locate the failed phase or violated dependency before proposing a repair.

### Exercise 5

Add a value 7 when only bins 0 through 3 are supported.

**Trap to avoid:** Clamping without saying so makes the histogram sum match while the distribution is wrong.

**Hint:** Check what the algorithm is allowed to read, write or assume at this boundary.

### Exercise 6

Define a fair end-to-end comparison.

**Trap to avoid:** Comparing a GPU kernel time against a CPU time that includes I/O favors whichever side omits more.

**Hint:** State the output contract and which observations are needed in the new application.

## Common mistakes and diagnosis

A tempting but incorrect claim: **Individual correct kernels necessarily compose correctly when buffers, shapes or ownership differ.** Composition adds contracts that each kernel alone never checked: valid counts, shapes and ownership must match between stages. Worked example 1 passes count three, not capacity, to the mean and histogram, and worked example 2 defines what an empty selection returns instead of dividing by zero.

## Self-check, retrieval and transfer

1. What must travel with a compacted buffer to the next stage?
2. What does the pipeline return for an empty selection?
3. Why introduce GPU stages one at a time?

Short answers are in the [separate explanations](../solutions/cuda-024_solutions.md#self-check-answers); compare only after an attempt.

## Primary references

Use the documentation that matches your prepared toolkit.

- [CUDA Programming Guide](https://docs.nvidia.com/cuda/cuda-programming-guide/)

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for cuda-024: First capstone: a reliable GPU data pipeline.
Read courses/cuda/cpp/guides/cuda-024.md and courses/cuda/cpp/lessons/cuda-024.md.
Direct prerequisites: `cuda-014`, `cuda-020`, `cuda-021`, `cuda-022`, `cuda-008`
Review my own explanation and worksheet; give one progressive hint at a time.
Keep courses/cuda/cpp/solutions/cuda-024_solutions.md and GPU references closed until I request comparison.
Treat courses/cuda/cpp/references/cuda-024_cpu.py as CPU model evidence, never a CUDA execution receipt.
Do not install drivers, download packages, run external jobs, reset devices or change my saved work without my instruction.
Ask me to explain the boundary case and which observation would disprove my answer.
```
