# python-numpy-03: Explained reference solutions

These answers implement the contracts in [Gather, Scatter, Masks, and Deterministic Selection](../companion-guides/py_numpy_03.md). Compare after an attempt. The [executable reference](py_numpy_03_solution.py) contains the complete implementations and assertions. Each answer explains the mechanism, not just the final value.

## Exercises and reasoning

### Exercise 1: Gather with explicit index rules

Gather a one-dimensional source using a one-dimensional integer index array. Allow negative positions in the normal NumPy range and preserve duplicates/order. Reject Boolean, floating or out-of-range indices with ValueError. Return an independent result.

**Expected:** [10,20,30] with [2,-1,0] yields [30,30,10]. Empty integer positions return shape(0,). Position 3, float1.0 or a Boolean index array raises ValueError.

```python
def gather_positions(values: np.ndarray, positions: np.ndarray) -> np.ndarray:
    p=np.asarray(positions)
    if values.ndim!=1 or p.ndim!=1 or not np.issubdtype(p.dtype,np.integer) or np.any(p < -len(values)) or np.any(p >= len(values)):
        raise ValueError("Expected in-range one-dimensional integer positions")
    return values[p]
```

The dtype check distinguishes positional indices from Boolean masks, which have a different meaning despite often containing zero/one-like values. Negative positions are validated against the actual source length rather than normalized without bounds. Advanced indexing creates the gathered output in the index-array order, retaining duplicate requests. An empty integer request is valid even for an empty source because no position is accessed.

```python
a=np.array([10,20,30]);r=gather_positions(a,np.array([2,-1,0]))
assert r.tolist()==[30,30,10] and not np.shares_memory(a,r)
assert gather_positions(a,np.array([],dtype=int)).shape==(0,)
expect_value_error(lambda:gather_positions(a,np.array([3])))
expect_value_error(lambda:gather_positions(a,np.array([1.])))
expect_value_error(lambda:gather_positions(a,np.array([True])))
```

### Exercise 2: Accumulate repeated category codes

Sum finite one-dimensional values into bins using one nonnegative integer code per value. Reject unequal lengths, invalid codes or negative/noninteger bin counts. Zero bins are allowed only with empty inputs. Preserve every repeated-code contribution.

**Expected:** Values[1,2,5] and codes[0,0,2] with 3 bins produce[3,0,5]. Empty inputs and zero bins produce shape(0,); code 3 for 3 bins raises ValueError.

```python
def sum_by_code(values: np.ndarray, codes: np.ndarray, bins: int) -> np.ndarray:
    v=np.asarray(values,dtype=float);c=np.asarray(codes)
    if isinstance(bins,bool) or not isinstance(bins,(int,np.integer)) or bins<0 or v.ndim!=1 or c.ndim!=1 or len(v)!=len(c) or not np.isfinite(v).all() or not np.issubdtype(c.dtype,np.integer) or np.any(c<0) or np.any(c>=bins):
        raise ValueError("Expected finite values and valid category codes")
    result=np.zeros(bins,dtype=float)
    np.add.at(result,c,v)
    return result
```

The category vector names destinations, and multiple observations can legitimately share a destination. add.at implements the required accumulation rather than a buffered overwrite-like update. Starting from zeros also defines absent categories as known zero totals in this synthetic complete-input contract. Missing observations would require a separate count or missingness policy instead of assuming their absence means zero.

```python
assert sum_by_code(np.array([1,2,5]),np.array([0,0,2]),3).tolist()==[3,0,5]
assert sum_by_code(np.array([]),np.array([],dtype=int),0).shape==(0,)
expect_value_error(lambda:sum_by_code(np.array([1]),np.array([3]),3))
expect_value_error(lambda:sum_by_code(np.array([1]),np.array([0]),True))
```

### Exercise 3: Validate a row mask

Filter a matrix using an exactly matching one-dimensional Boolean row mask. Preserve selected order and return independent storage. Reject integer flags, a cell-shaped mask or wrong row count with ValueError.

**Expected:** [[1,2],[3,4],[5,6]] with [True, False, True] gives [[1,2],[5,6]]. All false gives shape(0,2); an integer[1,0,1] mask is rejected.

```python
def select_rows(values: np.ndarray, mask: np.ndarray) -> np.ndarray:
    m=np.asarray(mask)
    if values.ndim!=2 or m.ndim!=1 or m.dtype!=np.bool_ or len(m)!=values.shape[0]:
        raise ValueError("Expected one Boolean value per row")
    return values[m]
```

Requiring Boolean dtype prevents an integer array from being interpreted as positional advanced indexing. Requiring one dimension prevents a cell mask from flattening selected entries and losing the row grain. The all-false case preserves the feature count in an empty matrix, which is essential for downstream schema consistency. The gathered result is detached, so a caller can transform it without modifying the original table.

```python
a=np.array([[1,2],[3,4],[5,6]])
r=select_rows(a,np.array([True,False,True]))
assert r.tolist()==[[1,2],[5,6]] and not np.shares_memory(a,r)
assert select_rows(a,np.zeros(3,dtype=bool)).shape==(0,2)
expect_value_error(lambda:select_rows(a,np.array([1,0,1])))
expect_value_error(lambda:select_rows(a,np.ones((3,2),dtype=bool)))
```

### Exercise 4: Select every row-column combination

Return a Cartesian submatrix from nonnegative integer row and column arrays. Preserve duplicates and index-array order in both axes. Reject out-of-range, Boolean or noninteger indices. An empty selection on either axis must preserve the other output dimension.

**Expected:** np.arange(12).reshape(3,4), rows[2,0], columns[3,1] gives [[11,9],[3,1]]. Empty rows with two columns returns shape(0,2), not a flat vector.

```python
def cartesian_submatrix(values: np.ndarray, rows: np.ndarray, columns: np.ndarray) -> np.ndarray:
    r=np.asarray(rows);c=np.asarray(columns)
    if values.ndim!=2 or r.ndim!=1 or c.ndim!=1 or not np.issubdtype(r.dtype,np.integer) or not np.issubdtype(c.dtype,np.integer) or np.any(r<0) or np.any(c<0) or np.any(r>=values.shape[0]) or np.any(c>=values.shape[1]):
        raise ValueError("Expected valid nonnegative row and column positions")
    return values[np.ix_(r,c)]
```

ix_ constructs index arrays with complementary singleton dimensions, so broadcasting produces every pair. Direct values[rows, columns] instead pairs corresponding positions and would return only two values for the normal fixture. Preserving output axes makes the result usable as a smaller matrix, including empty selections. Duplicate requests intentionally repeat rows or columns and must not be removed with unique unless the contract changes.

```python
a=np.arange(12).reshape(3,4)
assert cartesian_submatrix(a,np.array([2,0]),np.array([3,1])).tolist()==[[11,9],[3,1]]
assert cartesian_submatrix(a,np.array([],dtype=int),np.array([3,1])).shape==(0,2)
expect_value_error(lambda:cartesian_submatrix(a,np.array([3]),np.array([0])))
```

### Exercise 5: Make top-k ties deterministic

Return indices of the k largest finite one-dimensional scores in descending score order, breaking ties by original position. Require an integer k between zero and the number of scores, rejecting Boolean k. Do not mutate scores.

**Expected:** [5,9,9,1] with k=3 returns [1,2,0]. k=0 returns an empty integer array; k=5 or a NaN score raises ValueError.

```python
def stable_top_indices(scores: np.ndarray, k: int) -> np.ndarray:
    s=np.asarray(scores,dtype=float)
    if s.ndim!=1 or not np.isfinite(s).all() or isinstance(k,bool) or not isinstance(k,(int,np.integer)) or not 0<=k<=len(s):
        raise ValueError("Expected finite scores and a valid integer k")
    return np.argsort(-s,kind="stable")[:k]
```

Negating finite floating scores converts descending ranking into ascending sorting. Stable sorting retains input position among equal keys, making the boundary tie policy explicit. A full sort is intentionally used before introducing partial selection optimization. Returning indices preserves access to associated records and avoids confusing a score value with a unique record identity.

```python
s=np.array([5.,9.,9.,1.])
assert stable_top_indices(s,3).tolist()==[1,2,0] and s.tolist()==[5,9,9,1]
assert stable_top_indices(s,0).size==0
expect_value_error(lambda:stable_top_indices(s,5))
expect_value_error(lambda:stable_top_indices(np.array([np.nan]),1))
```

### Exercise 6: Restore original observation order

Return the inverse of a one-dimensional integer permutation of 0 through n-1. Reject duplicates, missing positions, negative values and noninteger dtype. Support the empty permutation. Demonstrate recovery of records after reordering.

**Expected:** Order[2,0,1] has inverse[1,2,0], and original[order][inverse] equals original. Order[0,0] is invalid; an empty integer array returns empty.

```python
def inverse_permutation(order: np.ndarray) -> np.ndarray:
    p=np.asarray(order)
    if p.ndim!=1 or not np.issubdtype(p.dtype,np.integer) or not np.array_equal(np.sort(p),np.arange(len(p))):
        raise ValueError("Expected a permutation of every original position")
    return np.argsort(p)
```

A true permutation has exactly one occurrence of every original position, which is verified by comparing its sorted values with arange(n). argsort then maps each original position back to the place where it appears in the reordered array. The round-trip identity is the independent correctness criterion. A selection with duplicates cannot be inverted because information was repeated or discarded, so it must be rejected rather than guessed.

```python
p=np.array([2,0,1]);inverse=inverse_permutation(p);a=np.array([10,20,30])
assert inverse.tolist()==[1,2,0] and np.array_equal(a[p][inverse],a)
assert inverse_permutation(np.array([],dtype=int)).size==0
expect_value_error(lambda:inverse_permutation(np.array([0,0])))
expect_value_error(lambda:inverse_permutation(np.array([0.,1.])))
```

## Verification and interpretation

Run `python python/professional/solutions/py_numpy_03_solution.py` from the repository root with the prepared interpreter. The code checks normal inputs and explicit edge cases before printing its success line. Assertions are the evidence; the printed sentence alone is not. The helper `expect_value_error` requires an actual `ValueError` and fails if a function silently accepts an invalid input. Inspect each function's mutation and ordering behavior as part of its contract.
