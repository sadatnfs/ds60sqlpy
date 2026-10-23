"""python-numpy-01: NumPy Memory Ownership, Strides, and Safe Mutation.

Run the worked examples, then implement the six contracts below.
Official implementations remain in solutions/.
"""

import numpy as np

def layout(values: np.ndarray) -> dict:
    """Implement layout for any NumPy array, returning shape, strides, itemsize and nbytes as a dictionary. Inspect np.arange(12, dtype=np.int64).reshape(3,4), its transpose and an empty float32 array. Do not mutate values."""
    raise NotImplementedError("Implement layout")

def copy_window(values: np.ndarray, start: int, stop: int) -> np.ndarray:
    """Implement a one-dimensional half-open window [start, stop) that returns an independent copy. Require 0<=start<=stop<=len(values); reject a matrix or invalid bounds with ValueError. An empty valid window is allowed."""
    raise NotImplementedError("Implement copy_window")

def row_center_owned(values: np.ndarray) -> np.ndarray:
    """Return a new floating-point matrix with each row mean subtracted. Require a finite two-dimensional numeric input with at least one column. Permit zero rows. Integer inputs must not fail because of in-place float subtraction."""
    raise NotImplementedError("Implement row_center_owned")

def read_only_view(values: np.ndarray) -> np.ndarray:
    """Return a view that shares numeric storage but rejects assignment through that view. Do not change the source writeable flag. Demonstrate that changing the source remains visible in the view."""
    raise NotImplementedError("Implement read_only_view")

def stride_select(values: np.ndarray, step: int) -> np.ndarray:
    """Return every step-th value from a one-dimensional array as a view. Require a positive integer step and reject bool, zero, negative or noninteger steps. Preserve empty inputs."""
    raise NotImplementedError("Implement stride_select")

def snapshot_arrays(values: dict[str, np.ndarray]) -> dict[str, np.ndarray]:
    """Copy each array in a mapping so future numeric mutations of source arrays do not affect the snapshot. Preserve keys and allow an empty mapping. Reject object-dtype arrays with ValueError because copying their buffer would not deep-copy nested Python objects."""
    raise NotImplementedError("Implement snapshot_arrays")

def worked_examples():
    a=np.arange(6,dtype=np.int64)
    view=a[::2]
    view[1]=99
    assert a.tolist()==[0,1,99,3,4,5]
    assert np.shares_memory(a,view)
    print("Shared slice:",a.tolist(),view.strides)

    a=np.arange(6,dtype=np.int64).reshape(2,3)
    copy=a[:,1:].copy()
    copy[0,0]=-1
    assert a[0,1]==1 and not np.shares_memory(a,copy)
    assert a.T.strides==(8,24)
    print("Original preserved:",a.tolist(),"transpose strides:",a.T.strides)

if __name__ == "__main__":
    worked_examples()
    print("Worked examples passed. Complete the six task functions and their boundary checks.")

# Exercise 1: Inspect a concrete layout
# Prompt: Implement layout for any NumPy array, returning shape, strides, itemsize and nbytes as a dictionary. Inspect np.arange(12, dtype=np.int64).reshape(3,4), its transpose and an empty float32 array. Do not mutate values.
# Expected: The original has shape(3,4), strides(32,8), itemsize 8 and nbytes 96; the transpose has strides(8,32); the empty array has nbytes 0.

# Exercise 2: Return an independent window
# Prompt: Implement a one-dimensional half-open window [start, stop) that returns an independent copy. Require 0<=start<=stop<=len(values); reject a matrix or invalid bounds with ValueError. An empty valid window is allowed.
# Expected: For [10,20,30,40] and bounds 1,3 return [20,30]. Changing output[0] leaves source[1]=20. Bounds 2,2 return shape(0,); bounds 3,2 raise ValueError.

# Exercise 3: Transform without mutating callers
# Prompt: Return a new floating-point matrix with each row mean subtracted. Require a finite two-dimensional numeric input with at least one column. Permit zero rows. Integer inputs must not fail because of in-place float subtraction.
# Expected: [[1,3],[10,14]] becomes[[-1,1],[-2,2]]; source stays unchanged and result shares no memory. Shape(0,2) remains(0,2); a zero-column or NaN input raises ValueError.

# Exercise 4: Distinguish access restriction from a snapshot
# Prompt: Return a view that shares numeric storage but rejects assignment through that view. Do not change the source writeable flag. Demonstrate that changing the source remains visible in the view.
# Expected: Assigning view[0]=9 raises ValueError; source[0]=7 succeeds and then view[0] equals 7. Source flags.writeable remainsTrue.

# Exercise 5: Select a strided view deliberately
# Prompt: Return every step-th value from a one-dimensional array as a view. Require a positive integer step and reject bool, zero, negative or noninteger steps. Preserve empty inputs.
# Expected: For np.arange(7) with step 3 return [0,3,6]; a mutation of result[1] changes source[3]. Step 0 andTrue raise ValueError; an empty source returns shape(0,).

# Exercise 6: Transfer ownership across a cache boundary
# Prompt: Copy each array in a mapping so future numeric mutations of source arrays do not affect the snapshot. Preserve keys and allow an empty mapping. Reject object-dtype arrays with ValueError because copying their buffer would not deep-copy nested Python objects.
# Expected: Two keys pointing to one source array produce two independent snapshot arrays. Mutating one snapshot leaves the other and source unchanged. Empty input returns{}; dtype=object is rejected.
