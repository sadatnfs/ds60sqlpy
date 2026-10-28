# Axes, Broadcasting, and Batched Linear Algebra

**Stable ID:** `python-numpy-02`

**Estimated time:** 150 minutes; split the reading and implementation across sessions when useful.

## Level and prerequisites

Intermediate. Direct catalog prerequisites: `python-numpy-01`. This lesson deepens the named mechanism after the introductory track; it does not require a cloud account or download data.

## Learning objectives

By the end, explain the mechanism in your own words, implement each bounded contract, and use a counterexample to distinguish a correct result from a plausible mistake. The six exercises progress from inspection to transformation, edge handling and transfer.

## How to run this lesson

**Primary browser route:** run `./classroom` from the repository root and
choose **Python** on `/classroom`. Open this lesson in the shared workspace,
read its capability notice, and use its supported coding or reading workflow.
The [classroom guide](../../../docs/classroom-experience.md) explains saved work, runtimes and switching subjects.

**Optional contributor route:** use the prepared environment in
[CONTRIBUTING](../../../CONTRIBUTING.md) on Linux, macOS or Windows through
WSL 2. The commands below assume its packages are already installed. They are
not prerequisites for opening this lesson in the Docker classroom. Local
`.learning/` files and CLI progress belong to this checkout; they do not read or
update the Docker classroom's named learning volume.

Open the [learner script](../lessons/py_numpy_02.py) in the prepared repository environment. In the Docker classroom, edit the saved learner pad; drafts, notes and results persist in the classroom learning volume. An ignored `.learning/` copy is a separate optional contributor workspace. Run from the repository root. The provided worked examples execute immediately; task functions intentionally raise `NotImplementedError` until you implement them. A successful example is not evidence that the six tasks are finished.

Prepared POSIX/WSL contributor terminal:

```sh
uv run --no-sync python python/professional/lessons/py_numpy_02.py
```

Dependencies: NumPy. All fixtures are tiny and local. The terminal prints the worked results and stops without editing your files. Keep [explanatory solutions](../solutions/py_numpy_02_solutions.md) and [runnable reference](../solutions/py_numpy_02_solution.py) closed until an attempt or an explicit worked comparison.

## Vocabulary and mental model

- **Axis:** A numbered dimension of an array; reducing an axis combines the positions along that dimension.

- **Broadcasting:** A rule matching dimensions from the right, allowing equal sizes or a size of one without explicitly repeating the smaller input.

- **Contraction:** An operation that multiplies values and sums over a shared dimension, as in a dot product.

- **Batch dimension:** A leading dimension indexing independent examples or matrices while trailing dimensions describe each example.

Shape is part of a function's meaning. An array with shape(n, d) can represent n observations and d features, but NumPy does not know those names. Reducing axis zero averages observations and returns one value per feature. Reducing axis one averages features and returns one value per observation. Both computations can run successfully while one answers the wrong question.

Broadcasting compares dimensions from the right. A matrix(n, d) plus a vector(d,) applies one offset per feature. A vector(n,) does not mean one value per row unless its shape is made(n,1). When n happens to equal d, the wrong operation may run and silently act on columns. Tests should use unequal sizes so a shape mistake cannot hide in a square example.

`keepdims=True` retains reduced dimensions with size one. A row mean then has shape(n,1), preserving the axis role needed for subtraction. It is clearer than deleting an axis and later guessing how to restore it. Inserting `None` or using `np.newaxis` adds a size-one dimension without duplicating all values; the resulting arithmetic may still allocate a much larger result.

Pairwise distances illustrate both power and cost. If a has shape(n, d) and b has shape(m, d), then a[:, None,:]-b[None,:,:] has shape(n, m, d). Summing squared differences over the last axis yields (n, m) distances. This is readable for tiny fixtures but uses memory proportional to n*m*d. A formula or blocked implementation can reduce temporary storage for large inputs, with different numerical tradeoffs.

Matrix multiplication contracts the last dimension of the left array with the next-to-last dimension of the right. For an input batch(b, n, d) and weights(d, k), the result is(b, n, k). `einsum` names axes explicitly, making a contraction such as 'bnd, dk->bnk' visible. It is a notation for a mathematical operation, not a guarantee of speed. Compare the result with a hand-derived small case before optimizing.

The exercises make shape validation explicit, preserve inputs, reject undefined denominators and test nonsquare examples. Empty outer batches can remain valid, while a mean over an empty feature axis is usually undefined. Decide these cases before relying on a library warning or accidental broadcasting behavior.

## Worked examples and syntax anatomy

### Example 1

```python
x = np.array([[1.0, 3.0, 5.0], [2.0, 4.0, 9.0]])
centered = x - x.mean(axis=1, keepdims=True)
assert centered.shape == (2, 3) and np.allclose(centered.mean(axis=1), 0)
print("Row centered:", centered.tolist())
```

axis=1 combines the three feature positions inside each row. keepdims retains a two-by-one mean so subtraction repeats each row's own mean across its three columns. The zero row means are a mathematical invariant, not merely an expected printout.

### Example 2

```python
a = np.array([[0.0, 0.0], [3.0, 4.0]])
b = np.array([[0.0, 4.0], [3.0, 0.0], [0.0, 0.0]])
difference = a[:, None, :] - b[None, :, :]
distance = np.sqrt(np.sum(difference**2, axis=-1))
assert distance.shape == (2, 3)
assert np.allclose(distance, [[4, 3, 0], [3, 4, 5]])
print("Pairwise distances:", distance.tolist())
```

The inserted singleton axes form every a-row/b-row pair. The final axis still represents coordinate differences and is the only axis summed. The resulting two-by-three table preserves the identities of both sets of points; accidentally summing axis zero would answer a different question.

## Exercises

1. **Reduce the observation axis.** Return a new floating matrix whose columns have zero means. Require a finite two-dimensional array with at least one row. Test two rows and three columns so row/column mistakes cannot pass accidentally.

**Expected:** [[1,10,100],[3,14,108]] becomes[[-1,-2,-4],[1,2,4]]. The source is unchanged; shape(0,3) and a vector raise ValueError.

2. **Broadcast one factor per row.** Multiply each matrix row by its corresponding finite factor without mutating either input. Require factors to be a one-dimensional vector whose length equals the number of rows. Permit an empty row batch.

**Expected:** [[1,2,3],[4,5,6]] with [10,100] gives [[10,20,30],[400,500,600]]. Three factors raise ValueError; shape(0,3) with an empty vector returns (0,3).

3. **Create all pairs with a declared contraction.** Return squared Euclidean distances between rows of two finite matrices with equal feature counts. Support empty row sets. Reject mismatched feature dimensions or unrepresentable squared distances with ValueError. Use the tiny broadcasted difference, not Python nested loops.

**Expected:** [[0,0],[3,4]] against [[0,0]] yields [[0],[25]]. Empty left shape(0,2) returns shape(0,1); two versus three features raises ValueError.

4. **Contract observations using valid weights.** Return weighted column means for a finite matrix using one nonnegative finite weight per row. Require positive total weight. Reject negative weights, zero total or wrong length, rather than dividing and returning NaNs.

**Expected:** [[1,10],[3,30]] with [1,3] gives [2.5,25]. Weights[0,0],[-1,2] and [1] raise ValueError; weights scaled by ten give the same means.

5. **Preserve leading batch axes.** Apply a finite two-dimensional weight matrix(d, k) to values with at least two dimensions and final dimension d. Return all leading dimensions followed by k. Reject an incompatible final dimension.

**Expected:** A(2,3,4) input times a(4,2) weight matrix returns (2,3,2), matching an explicit per-batch matrix multiply. A(3,4) input also works; weights(3,2) are rejected.

6. **Normalize while preserving zero vectors.** Return a new finite matrix whose nonzero rows have Euclidean norm one and zero rows remain zero. Reject nonfinite or nonmatrix inputs. Avoid evaluating a zero division and then hiding its warning.

**Expected:** [[3,4],[0,0],[-2,0]] becomes[[.6,.8],[0,0],[-1,0]]. All results are finite, source stays unchanged and infinity raises ValueError.

## Common mistakes and diagnosis

A broadcasting error names incompatible dimensions, but a successful broadcast can still be wrong. Write the semantic axis names and use nonsquare fixtures before changing shapes. If normalization produces NaN only for zero rows, inspect whether division happened before masking. If a pairwise operation exhausts memory, calculate the temporary shape(n, m, d) and estimate its bytes before increasing hardware. If einsum gives an unexpected axis order, read the labels to the right of the arrow as the exact output order and compare one small result with an explicit loop.

## Self-check and retrieval

Without copying code, explain which input property each function assumes, which observable result proves the normal case, and which counterexample would expose an incorrect implementation. Trace one boundary input by hand before running it. Keep the input and expected output beside your saved result so a reviewer can reproduce the evidence.

## Next steps

Use these mechanisms in the next deepening lesson or return to the original prerequisite examples and explain precisely which new failure cases you can now diagnose. Review the [professional track](../README.md) for related modules.

## Primary sources and official APIs

- [NumPy broadcasting rules](https://numpy.org/doc/stable/user/basics.broadcasting.html).

- [NumPy einsum API](https://numpy.org/doc/stable/reference/generated/numpy.einsum.html).

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning to coach me through python-numpy-02: Axes, Broadcasting, and Batched Linear Algebra.
Read python/professional/companion-guides/py_numpy_02.md and python/professional/lessons/py_numpy_02.py. Direct prerequisites: python-numpy-01.
Explain the vocabulary and mechanism at a beginner-friendly pace, then ask me to predict a concrete result before my attempt. Give one hint at a time, review my numerical or exception evidence, and ask retrieval questions in my own words. Do not read solutions/ until I request it or have made an honest attempt. Use only the prepared local Python environment and tiny offline inputs; preserve my saved work.
Done when all six contracts and their boundary cases have inspected evidence and I can explain why a tempting incorrect implementation fails.
```
