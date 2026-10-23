# python-numpy-01: Explained reference solutions

These answers implement the contracts in [NumPy Memory Ownership, Strides, and Safe Mutation](../companion-guides/py_numpy_01.md). Compare after an attempt. The [executable reference](py_numpy_01_solution.py) contains the complete implementations and assertions. Each answer explains the mechanism, not just the final value.

## Exercises and reasoning

### Exercise 1: Inspect a concrete layout

Implement layout for any NumPy array, returning shape, strides, itemsize and nbytes as a dictionary. Inspect np.arange(12, dtype=np.int64).reshape(3,4), its transpose and an empty float32 array. Do not mutate values.

**Expected:** The original has shape(3,4), strides(32,8), itemsize 8 and nbytes 96; the transpose has strides(8,32); the empty array has nbytes 0.

```python
def layout(values: np.ndarray) -> dict:
    return {"shape": values.shape, "strides": values.strides, "itemsize": values.itemsize, "nbytes": values.nbytes}
```

The properties describe the array view, not necessarily a new allocation. nbytes counts represented element bytes and can differ from the size of a shared underlying buffer. Transposition exchanges axis strides while preserving the number of elements. The empty case verifies that a valid shape can represent no stored elements; inspecting it must not invent a minimum allocation or divide by its length.

```python
a=np.arange(12,dtype=np.int64).reshape(3,4)
assert layout(a)=={"shape":(3,4),"strides":(32,8),"itemsize":8,"nbytes":96}
assert layout(a.T)["strides"]==(8,32)
assert layout(np.array([],dtype=np.float32))["nbytes"]==0
```

### Exercise 2: Return an independent window

Implement a one-dimensional half-open window [start, stop) that returns an independent copy. Require 0<=start<=stop<=len(values); reject a matrix or invalid bounds with ValueError. An empty valid window is allowed.

**Expected:** For [10,20,30,40] and bounds 1,3 return [20,30]. Changing output[0] leaves source[1]=20. Bounds 2,2 return shape(0,); bounds 3,2 raise ValueError.

```python
def copy_window(values: np.ndarray, start: int, stop: int) -> np.ndarray:
    if values.ndim != 1 or not 0 <= start <= stop <= len(values):
        raise ValueError("Expected a valid one-dimensional half-open window")
    return values[start:stop].copy()
```

Validation precedes slicing so Python's forgiving slice normalization does not silently accept a contract violation. The stop boundary is excluded, making adjacent windows nonoverlapping by construction. Calling copy after selecting the window allocates only the selected values. The mutation test is essential: equal initial values do not prove independence, while changing the returned window and inspecting the source directly demonstrates the intended ownership boundary.

```python
a=np.array([10,20,30,40]);b=copy_window(a,1,3)
assert b.tolist()==[20,30] and not np.shares_memory(a,b)
b[0]=-1
assert a[1]==20 and copy_window(a,2,2).shape==(0,)
expect_value_error(lambda:copy_window(a,3,2))
expect_value_error(lambda:copy_window(np.ones((2,2)),0,1))
```

### Exercise 3: Transform without mutating callers

Return a new floating-point matrix with each row mean subtracted. Require a finite two-dimensional numeric input with at least one column. Permit zero rows. Integer inputs must not fail because of in-place float subtraction. Reject an unrepresentable centered result with ValueError.

**Expected:** [[1,3],[10,14]] becomes[[-1,1],[-2,2]]; source stays unchanged and result shares no memory. Shape(0,2) remains(0,2); a zero-column or NaN input raises ValueError.

```python
def row_center_owned(values: np.ndarray) -> np.ndarray:
    array=np.asarray(values,dtype=float)
    if array.ndim != 2 or array.shape[1]==0 or not np.isfinite(array).all():
        raise ValueError("Expected finite rows with at least one column")
    mean=(array/array.shape[1]).sum(axis=1,keepdims=True)
    with np.errstate(over="ignore",invalid="ignore"):
        result=array-mean
    if not np.isfinite(result).all():
        raise ValueError("Centered result exceeds finite floating range")
    return result
```

Conversion to float permits fractional means without an integer casting error. Dividing before summing avoids overflow in a large finite row mean; retaining the reduced axis gives an n-by-one mean that broadcasts across each row. A centered result outside floating range is rejected explicitly. Subtraction creates the result rather than modifying the caller's array, even when the input conversion reused a float buffer. A row with no columns has an undefined mean and is rejected; a matrix with no rows has no row means to compute and preserves its valid column count.

```python
a=np.array([[1,3],[10,14]]);b=row_center_owned(a)
assert np.allclose(b,[[-1,1],[-2,2]]) and a.tolist()==[[1,3],[10,14]]
assert not np.shares_memory(a,b) and row_center_owned(np.empty((0,2))).shape==(0,2)
assert np.allclose(row_center_owned(np.array([[1e308,1e308]])),[[0,0]])
expect_value_error(lambda:row_center_owned(np.array([[1.7e308,-1.7e308,-1.7e308]])))
expect_value_error(lambda:row_center_owned(np.empty((2,0))))
expect_value_error(lambda:row_center_owned(np.array([[np.nan]])))
```

### Exercise 4: Distinguish access restriction from a snapshot

Return a view that shares numeric storage but rejects assignment through that view. Do not change the source writeable flag. Demonstrate that changing the source remains visible in the view.

**Expected:** Assigning view[0]=9 raises ValueError; source[0]=7 succeeds and then view[0] equals 7. Source flags.writeable remainsTrue.

```python
def read_only_view(values: np.ndarray) -> np.ndarray:
    result=values.view()
    result.flags.writeable=False
    return result
```

The writeable flag belongs to the array view. Setting it on a newly created view prevents mutation through that handle while leaving the source contract unchanged. Because both refer to the same buffer, a writable alias can still alter the observed values. This is an access convenience, not an immutable snapshot or a security boundary against code that holds other references.

```python
a=np.array([1,2]);b=read_only_view(a)
assert np.shares_memory(a,b) and a.flags.writeable
expect_value_error(lambda:b.__setitem__(0,9))
a[0]=7
assert b[0]==7
```

### Exercise 5: Select a strided view deliberately

Return every step-th value from a one-dimensional array as a view. Require a positive integer step and reject bool, zero, negative or noninteger steps. Preserve empty inputs.

**Expected:** For np.arange(7) with step 3 return [0,3,6]; a mutation of result[1] changes source[3]. Step 0 andTrue raise ValueError; an empty source returns shape(0,).

```python
def stride_select(values: np.ndarray, step: int) -> np.ndarray:
    if values.ndim != 1 or isinstance(step,bool) or not isinstance(step,(int,np.integer)) or step <= 0:
        raise ValueError("Expected one-dimensional data and a positive integer step")
    return values[::step]
```

Basic slicing expresses the step through strides and can reuse storage. The function deliberately promises this aliasing behavior, unlike copy_window. Boolean values are excluded even though Python bool is a subclass of int, because True as a stride hides a likely caller error. The empty output has no elements to mutate, so a false shares_memory result on an empty slice does not contradict the selection semantics.

```python
a=np.arange(7);b=stride_select(a,3)
assert b.tolist()==[0,3,6]
b[1]=99
assert a[3]==99 and stride_select(np.array([]),2).shape==(0,)
expect_value_error(lambda:stride_select(a,0))
expect_value_error(lambda:stride_select(a,True))
```

### Exercise 6: Transfer ownership across a cache boundary

Copy each array in a mapping so future numeric mutations of source arrays do not affect the snapshot. Preserve keys and allow an empty mapping. Reject object-dtype arrays with ValueError because copying their buffer would not deep-copy nested Python objects.

**Expected:** Two keys pointing to one source array produce two independent snapshot arrays. Mutating one snapshot leaves the other and source unchanged. Empty input returns{}; dtype=object is rejected.

```python
def snapshot_arrays(values: dict[str, np.ndarray]) -> dict[str, np.ndarray]:
    if any(array.dtype.hasobject for array in values.values()):
        raise ValueError("Object arrays need an explicit deep-copy policy")
    return {key:array.copy() for key,array in values.items()}
```

The mapping itself and each numeric buffer receive new ownership. Copying entries independently intentionally does not preserve the source alias graph: two keys that shared an input buffer become independent outputs. That is a clear snapshot contract, but it costs additional memory. Object arrays are rejected because a shallow array copy would duplicate references to mutable Python objects and violate the intuitive promise that the snapshot is detached.

```python
a=np.array([1,2]);snap=snapshot_arrays({"a":a,"b":a})
snap["a"][0]=9
assert a[0]==1 and snap["b"][0]==1
assert not np.shares_memory(snap["a"],snap["b"]) and snapshot_arrays({})=={}
expect_value_error(lambda:snapshot_arrays({"x":np.array([{}],dtype=object)}))
```

## Verification and interpretation

Run `python python/professional/solutions/py_numpy_01_solution.py` from the repository root with the prepared interpreter. The code checks normal inputs and explicit edge cases before printing its success line. Assertions are the evidence; the printed sentence alone is not. The helper `expect_value_error` requires an actual `ValueError` and fails if a function silently accepts an invalid input. Inspect each function's mutation and ordering behavior as part of its contract.
