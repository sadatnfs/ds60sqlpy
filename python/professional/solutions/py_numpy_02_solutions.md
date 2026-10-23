# python-numpy-02: Explained reference solutions

These answers implement the contracts in [Axes, Broadcasting, and Batched Linear Algebra](../companion-guides/py_numpy_02.md). Compare after an attempt. The [executable reference](py_numpy_02_solution.py) contains the complete implementations and assertions. Each answer explains the mechanism, not just the final value.

## Exercises and reasoning

### Exercise 1: Reduce the observation axis

Return a new floating matrix whose columns have zero means. Require a finite two-dimensional array with at least one row. Test two rows and three columns so row/column mistakes cannot pass accidentally.

**Expected:** [[1,10,100],[3,14,108]] becomes[[-1,-2,-4],[1,2,4]]. The source is unchanged; shape(0,3) and a vector raise ValueError.

```python
def column_center(values: np.ndarray) -> np.ndarray:
    x=np.asarray(values,dtype=float)
    if x.ndim!=2 or x.shape[0]==0 or not np.isfinite(x).all():
        raise ValueError("Expected a finite matrix with observations")
    return x-x.mean(axis=0,keepdims=True)
```

Each output column subtracts the average across observations, so axis zero is reduced. Keeping the dimension documents that the result has one row of feature means. Conversion makes fractional means representable. The nonsquare fixture prevents a row-centered result from having a misleadingly compatible interpretation, and the empty-observation rejection prevents an undefined mean from quietly producing NaNs.

```python
x=np.array([[1,10,100],[3,14,108]])
assert np.allclose(column_center(x),[[-1,-2,-4],[1,2,4]])
assert x[0,0]==1
expect_value_error(lambda:column_center(np.empty((0,3))))
expect_value_error(lambda:column_center(np.array([1,2])))
```

### Exercise 2: Broadcast one factor per row

Multiply each matrix row by its corresponding finite factor without mutating either input. Require factors to be a one-dimensional vector whose length equals the number of rows. Permit an empty row batch.

**Expected:** [[1,2,3],[4,5,6]] with [10,100] gives [[10,20,30],[400,500,600]]. Three factors raise ValueError; shape(0,3) with an empty vector returns (0,3).

```python
def scale_rows(values: np.ndarray, factors: np.ndarray) -> np.ndarray:
    x=np.asarray(values,dtype=float);f=np.asarray(factors,dtype=float)
    if x.ndim!=2 or f.ndim!=1 or len(f)!=x.shape[0] or not np.isfinite(x).all() or not np.isfinite(f).all():
        raise ValueError("Expected one finite factor per row")
    return x*f[:,None]
```

The new axis changes factors from shape(n,) to(n,1), so the factor is repeated across columns of its own row. Without it, a vector is matched to the last dimension and means column factors. The length check is deliberately stronger than asking whether NumPy can broadcast the inputs, because a numerically valid broadcast could violate the function's row-level meaning.

```python
x=np.array([[1,2,3],[4,5,6]])
assert np.allclose(scale_rows(x,np.array([10,100])),[[10,20,30],[400,500,600]])
assert scale_rows(np.empty((0,3)),np.array([])).shape==(0,3)
expect_value_error(lambda:scale_rows(x,np.array([1,2,3])))
```

### Exercise 3: Create all pairs with a declared contraction

Return squared Euclidean distances between rows of two finite matrices with equal feature counts. Support empty row sets. Reject mismatched feature dimensions. Use the tiny broadcasted difference, not Python nested loops.

**Expected:** [[0,0],[3,4]] against [[0,0]] yields [[0],[25]]. Empty left shape(0,2) returns shape(0,1); two versus three features raises ValueError.

```python
def pairwise_squared(left: np.ndarray, right: np.ndarray) -> np.ndarray:
    a=np.asarray(left,dtype=float);b=np.asarray(right,dtype=float)
    if a.ndim!=2 or b.ndim!=2 or a.shape[1]!=b.shape[1] or not np.isfinite(a).all() or not np.isfinite(b).all():
        raise ValueError("Expected finite matrices with equal feature dimensions")
    difference=a[:,None,:]-b[None,:,:]
    return np.sum(difference*difference,axis=-1)
```

The temporary has an axis for left rows, an axis for right rows and an axis for features. Squaring and summing only the feature axis preserves the pair table. The explicit feature-count check prevents unrelated coordinate spaces from being compared. For large row counts this temporary can be expensive; the exercise teaches shape correctness, while a later optimization should use blocking and numerical checks rather than assume broadcasting is always cheap.

```python
a=np.array([[0,0],[3,4]]);b=np.array([[0,0]])
assert np.allclose(pairwise_squared(a,b),[[0],[25]])
assert pairwise_squared(np.empty((0,2)),b).shape==(0,1)
expect_value_error(lambda:pairwise_squared(a,np.ones((1,3))))
```

### Exercise 4: Contract observations using valid weights

Return weighted column means for a finite matrix using one nonnegative finite weight per row. Require positive total weight. Reject negative weights, zero total or wrong length, rather than dividing and returning NaNs.

**Expected:** [[1,10],[3,30]] with [1,3] gives [2.5,25]. Weights[0,0],[-1,2] and [1] raise ValueError; weights scaled by ten give the same means.

```python
def weighted_columns(values: np.ndarray, weights: np.ndarray) -> np.ndarray:
    x=np.asarray(values,dtype=float);w=np.asarray(weights,dtype=float)
    if x.ndim!=2 or w.ndim!=1 or len(w)!=x.shape[0] or not np.isfinite(x).all() or not np.isfinite(w).all() or np.any(w<0) or w.sum()<=0:
        raise ValueError("Expected finite nonnegative weights with positive sum")
    return np.einsum("n,nd->d",w,x)/w.sum()
```

The repeated n label in the einsum input is summed and the remaining d label names the output feature axis. Division by total weight normalizes a weighted sum into a mean. Scaling all weights equally must not change the result, giving an independent invariant. The nonnegative contract makes these weights interpretable as averaging weights; allowing signed weights would define a different operation with different denominator behavior.

```python
x=np.array([[1,10],[3,30]])
assert np.allclose(weighted_columns(x,np.array([1,3])),[2.5,25])
assert np.allclose(weighted_columns(x,np.array([10,30])),[2.5,25])
expect_value_error(lambda:weighted_columns(x,np.array([0,0])))
expect_value_error(lambda:weighted_columns(x,np.array([-1,2])))
expect_value_error(lambda:weighted_columns(x,np.array([1])))
```

### Exercise 5: Preserve leading batch axes

Apply a finite two-dimensional weight matrix(d, k) to values with at least two dimensions and final dimension d. Return all leading dimensions followed by k. Reject an incompatible final dimension.

**Expected:** A(2,3,4) input times a(4,2) weight matrix returns (2,3,2), matching an explicit per-batch matrix multiply. A(3,4) input also works; weights(3,2) are rejected.

```python
def batched_projection(values: np.ndarray, weights: np.ndarray) -> np.ndarray:
    x=np.asarray(values,dtype=float);w=np.asarray(weights,dtype=float)
    if x.ndim<2 or w.ndim!=2 or x.shape[-1]!=w.shape[0] or not np.isfinite(x).all() or not np.isfinite(w).all():
        raise ValueError("Expected a compatible final feature dimension")
    return np.einsum("...d,dk->...k",x,w)
```

The ellipsis preserves every leading axis instead of hardcoding one batch dimension. Only the feature dimension d contracts with the weight matrix, and k becomes the last output dimension. Comparing with explicit per-batch multiplication validates the contraction independently of its compact notation. A reshape that flattens batches can produce equal numbers but lose entity boundaries, so shape is checked alongside values.

```python
x=np.arange(24).reshape(2,3,4);w=np.arange(8).reshape(4,2)
r=batched_projection(x,w)
assert r.shape==(2,3,2) and np.allclose(r,np.stack([x[0]@w,x[1]@w]))
assert batched_projection(x[0],w).shape==(3,2)
expect_value_error(lambda:batched_projection(x,np.ones((3,2))))
```

### Exercise 6: Normalize while preserving zero vectors

Return a new finite matrix whose nonzero rows have Euclidean norm one and zero rows remain zero. Reject nonfinite or nonmatrix inputs. Avoid evaluating a zero division and then hiding its warning.

**Expected:** [[3,4],[0,0],[-2,0]] becomes[[.6,.8],[0,0],[-1,0]]. All results are finite, source stays unchanged and infinity raises ValueError.

```python
def unit_rows(values: np.ndarray) -> np.ndarray:
    x=np.asarray(values,dtype=float)
    if x.ndim!=2 or not np.isfinite(x).all():
        raise ValueError("Expected a finite matrix")
    scale=np.max(np.abs(x),axis=1,keepdims=True,initial=0)
    scaled=np.zeros_like(x)
    np.divide(x,scale,out=scaled,where=scale!=0)
    norm=np.linalg.norm(scaled,axis=1,keepdims=True)
    result=np.zeros_like(x)
    np.divide(scaled,norm,out=result,where=norm!=0)
    return result
```

Scaling each row by its largest absolute value first prevents squared-norm overflow for very large finite coordinates. The norm then reduces bounded features while retaining a one-column axis. A zero-initialized output gives zero rows their declared result, and where prevents invalid division. This differs from np.where(condition, x/norm,0), which evaluates x/norm before selection and may emit invalid values. Normalization changes scale but does not create meaningful direction for a zero vector.

```python
x=np.array([[3.,4.],[0.,0.],[-2.,0.]])
r=unit_rows(x)
assert np.allclose(r,[[.6,.8],[0,0],[-1,0]]) and np.isfinite(r).all()
assert np.array_equal(x,[[3,4],[0,0],[-2,0]])
assert np.allclose(unit_rows(np.array([[1e308,1e308]])),[[2**-.5,2**-.5]])
expect_value_error(lambda:unit_rows(np.array([[np.inf]])))
```

## Verification and interpretation

Run `python python/professional/solutions/py_numpy_02_solution.py` from the repository root with the prepared interpreter. The code checks normal inputs and explicit edge cases before printing its success line. Assertions are the evidence; the printed sentence alone is not. The helper `expect_value_error` requires an actual `ValueError` and fails if a function silently accepts an invalid input. Inspect each function's mutation and ordering behavior as part of its contract.
