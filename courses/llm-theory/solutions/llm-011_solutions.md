# llm-011: explanatory solutions

Compare these answers only after an attempt or an explicit solution reveal. They use the same literal inputs as the guide, so a discrepancy can be localized to a specific step. The executable companion runs the assertions; the explanation states why those assertions test the subject. Passing a reference function is rehearsal, and should be followed by a new input chosen without looking at the answer.

## Mechanism review

Multiple attention heads divide a representation into separate feature subspaces. Splitting and joining are layout transformations; they must preserve every value before any learning is considered. A width-four representation divided into two heads gives head width two. Each head can use a different attention distribution, after which the outputs are concatenated and projected. Residual additions require the original width. A feed-forward block transforms each token independently, usually expanding its feature width and then projecting back. Tokenwise operations preserve a causal prefix only if no other operation mixes future positions. Layout correctness and information-boundary correctness are separate checks.

**Head:** A separate feature subspace used by an attention computation.

**Residual connection:** Addition of a same-shaped branch to its input.

**Feed-forward block:** A shared tokenwise feature transformation.

## Reading the implementation

reshape changes the interpretation of contiguous dimensions, while transpose moves the head axis beside the batch axis. Rejoining needs the inverse transpose before reshape. A residual x+branch requires equal shapes. An elementwise activation followed by a matrix product operates independently on token rows; reductions across time do not. Use small integer-valued arrays to inspect layout before introducing random projection matrices.

## Exercise 1: Split and rejoin

The question is: Reshape two width4 rows into2 heads of width2, then invert the layout change.

The axes here are heads,time,features after transposition. A reshape alone cannot exchange semantic axes, which is why the inverse transpose matters.

```python
x=np.arange(8).reshape(2,4); heads=x.reshape(2,2,2).transpose(1,0,2)
restored=heads.transpose(1,0,2).reshape(2,4)
np.testing.assert_array_equal(restored,x); assert heads.shape==(2,2,2)
```

**Expected:** exact round trip and head width2.

**Verify:** Compare the computed values or written argument with exact round trip and head width2.

## Exercise 2: Calculate a residual

The question is: Apply a branch2*x and add the original input.

Residual addition does not concatenate features. Concatenation would double the width and change every following projection contract.

```python
branch=2*x; residual=x+branch
np.testing.assert_array_equal(residual,3*x); assert residual.shape==x.shape
```

**Expected:** result3*x with unchanged shape.

**Verify:** Compare the computed values or written argument with result3*x with unchanged shape.

## Exercise 3: Use a tokenwise nonlinear block

The question is: Apply max(x-2,0) independently and project with identity.

The shared computation treats token rows independently while applying the same feature rule. Changing another row cannot affect the first row.

```python
feed=np.maximum(x-2,0)@np.eye(4)
np.testing.assert_array_equal(feed[0],[0,0,0,1])
```

**Expected:** first row[0,0,0,1].

**Verify:** Compare the computed values or written argument with first row[0,0,0,1].

## Exercise 4: Test a prefix

The question is: Recompute the feed-forward branch on only the first row and compare with the full result.

This check is simple because the branch is tokenwise. The attention part of a full decoder still needs a separate causal mask test.

```python
np.testing.assert_array_equal(np.maximum(x[:1]-2,0)@np.eye(4),feed[:1])
```

**Expected:** first-row output unchanged.

**Verify:** Compare the computed values or written argument with first-row output unchanged.

## Exercise 5: Reject an indivisible width

The question is: Check width5 with2 heads before reshaping.

A head layout requires an integer number of features per head. Silently dropping a feature or padding it without a policy would change the model representation.

```python
width,head_count=5,2
assert width%head_count!=0
```

**Expected:** divisibility check fails.

**Verify:** Compare the computed values or written argument with divisibility check fails.

## Exercise 6: Detect a wrong rejoin

The question is: Flatten the transposed heads without first reversing the transpose.

The element count still matches, so a shape-only test would pass. Exact value placement catches the semantic axis error.

```python
wrong=heads.reshape(2,4)
assert not np.array_equal(wrong,x)
```

**Expected:** wrong result differs from the original rows.

**Verify:** Compare the computed values or written argument with wrong result differs from the original rows.

## Review after comparison

Repeat one case with a changed fixture and explain the difference before running it. Keep the original failure case as well as the repaired result. Record a missing framework separately from a failing assertion. No solution downloads data, calls an online model, deploys a service or changes a database.
