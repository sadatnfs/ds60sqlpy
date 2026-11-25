# cuda-107: Python-accessible CUDA library algorithms

**Route:** CUDA Python and machine learning. **Stage:** advanced. **Prerequisites:** `cuda-082`, `cuda-085`.

Pacing, evidence labels and platform rules: [CUDA study guide](../../STUDY-GUIDE.md).

## Learning objectives

- Trace stable sorting.
- Specify duplicate semantics.
- Calculate output shape.
- Account for temporary storage.
- Separate plan creation.
- Choose a release-specific contract.

## Mechanism and vocabulary

Library algorithms expose more than an operation name. Sorting needs comparator and stability semantics; reductions need identity and dtype rules; matrix operations need layout and leading dimensions; FFTs need normalization and transform conventions. Some APIs create reusable plans or request temporary storage. Plan lifetime, workspace ownership and stream association affect both correctness and performance.

Choose a small release-pinned library family instead of installing every package. Compare an educational reference and a prepared library result on tiny fixtures, including empty or rejected cases and duplicate keys. Reuse plans only when their shape/dtype contract permits. Report plan creation separately from repeated execution. Python accessibility does not eliminate CUDA resource and compatibility requirements.



### Key terms

- **Stable sort:** A sort that keeps equal keys in their original relative order.
- **Comparator:** The rule that orders two keys and must define a consistent ordering.
- **Reusable plan:** A library object, such as an FFT plan, prepared for one shape and dtype and reused only within that contract.
- **Temporary storage:** Workspace memory a library algorithm requests, whose ownership and stream association affect correctness.

## Worked examples

### Worked example 1

A stable sort of [(2, A),(1, B),(2, C)] by key retains A before C among equal keys. An unstable sort may legally change that relative order.

### Worked example 2

A matrix multiply output shape follows contracted dimensions: a 2 by 3 matrix times 3 by 4 gives 2 by 4. A plan prepared for a different dtype or shape cannot be reused blindly.

## How to run the CPU model

Edit the copy; the [reference](../references/cuda-107_cpu.py) adds assertions.

```sh
python courses/cuda/python/lessons/cuda-107_cpu.py
```

```python
records = [(2, "A"), (1, "B"), (2, "C")]
ordered = sorted(records, key=lambda row: row[0])
assert ordered == [(1, "B"), (2, "A"), (2, "C")]
a, b = (2, 3), (3, 4)
assert a[1] == b[0]
print("CPU library contracts:", ordered, "matrix output", (a[0], b[1]))
```

**Expected observation:** Stable duplicate order and matrix output shape (2,4).

**Variable trace.** Before running the model, predict these final values; then compare:

| Variable | Final value |
|---|---|
| `records` | `[(2, 'A'), (1, 'B'), (2, 'C')]` |
| `ordered` | `[(1, 'B'), (2, 'A'), (2, 'C')]` |
| `a` | `(2, 3)` |
| `b` | `(3, 4)` |

## Practice and transfer

Record each attempt in the [worksheet](../lessons/cuda-107.md) before opening hints.

### Exercise 1: Trace stable sorting

**Trap to avoid:** Assuming every GPU sort is stable lets downstream code rely on an order an unstable sort may legally change, which then varies between runs or releases.

### Exercise 2: Specify duplicate semantics

**Trap to avoid:** Leaving the rule unstated passes tests on small inputs where an unstable algorithm happens to preserve order, then fails on larger inputs that use a different internal path.

### Exercise 3: Calculate output shape

**Trap to avoid:** Taking the output as 3 by 3 or 2 by 3 confuses contracted and kept dimensions, and allocating the wrong output buffer causes a library error or an out-of-bounds write.

### Exercise 4: Account for temporary storage

**Trap to avoid:** Budgeting only inputs and outputs leads to out-of-memory errors that appear only on large arrays.

### Exercise 5: Separate plan creation

**Trap to avoid:** Reusing a plan prepared for a different shape or dtype gives wrong results or errors, so caching must be keyed by both.

### Exercise 6: Choose a release-specific contract

**Trap to avoid:** Relying on the latest online docs while running an older release can promise features or guarantees the installed version does not have.

## Progressive hints

Hint *k* belongs to exercise *k*; open one at a time.

1. Sort the records by key and keep the original order among records whose keys are equal.
2. Ask whether the library documents a guaranteed order among duplicates, and what you may assume if it does not.
3. Drop the contracted inner dimension and keep the two outer dimensions.
4. Add the workspace the library requests to the inputs and outputs that are live at the same time.
5. Time creating the plan separately from running it repeatedly.
6. Read the documentation for the exact installed release rather than the newest online version.

## Common mistakes and self-check

A common mistake is assuming every sort is stable. An unstable sort may legally put record C before A when both have key 2, which breaks code that relies on input order. Another is reusing a plan built for a different shape or dtype, or forgetting the workspace it allocates. Fix both by stating duplicate semantics in the contract, testing duplicates and empty inputs on tiny fixtures and keeping plan creation, workspace and stream association explicit in the ledger.

**Misconception:** A library sum or FFT returns the same answer as NumPy as long as the inputs match. **Correction:** Library conventions differ. A reduction may accumulate in a different dtype or order, so a float32 sum can differ in its last digits, and an integer sum may overflow its type. Some FFT libraries leave both directions unnormalized, so a forward then inverse transform returns values n times larger than the input, while NumPy scales the inverse by 1/n by default. Read each function's dtype, identity and normalization rules and compare on tiny fixtures with stated tolerances.

**Evidence limit:** The reference traces a stable sort and a `(2, 4)` output shape in Python. It calls no CUDA library, so plan lifetime, workspace size and release-specific behavior require the prepared library package.

1. What does an FFT contract need besides the input array?
2. Why does a plan have a shape and dtype contract?
3. Why choose a small release-pinned library family?

Answers: [self-check answers](../solutions/cuda-107_solutions.md#self-check-answers).

## Primary references

- [PyTorch CUDA semantics](https://docs.pytorch.org/docs/2.9/notes/cuda.html)
- [TensorFlow GPU guide](https://www.tensorflow.org/guide/gpu)

Full lists: [documentation and sources](../../STUDY-GUIDE.md#documentation-and-sources).

## Ask an AI tutor about this lesson

```text
Use the checked-in $guide-ds60sqlpy-learning skill for cuda-107: Python-accessible CUDA library algorithms.
Read courses/cuda/python/guides/cuda-107.md and courses/cuda/python/lessons/cuda-107.md.
Start with my current attempt and the two worked examples, and ask which backend actually ran.
Give one progressive hint at a time. Keep the separate solution closed and do not mark
progress unless I request it. Treat synthetic timings and CPU models as model evidence,
not as GPU or cluster measurements.
```
