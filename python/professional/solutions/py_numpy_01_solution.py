"""Reference implementation and exact boundary checks for python-numpy-01."""

import numpy as np

def layout(values: np.ndarray) -> dict:
    return {"shape": values.shape, "strides": values.strides, "itemsize": values.itemsize, "nbytes": values.nbytes}

def copy_window(values: np.ndarray, start: int, stop: int) -> np.ndarray:
    if values.ndim != 1 or not 0 <= start <= stop <= len(values):
        raise ValueError("Expected a valid one-dimensional half-open window")
    return values[start:stop].copy()

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

def read_only_view(values: np.ndarray) -> np.ndarray:
    result=values.view()
    result.flags.writeable=False
    return result

def stride_select(values: np.ndarray, step: int) -> np.ndarray:
    if values.ndim != 1 or isinstance(step,bool) or not isinstance(step,(int,np.integer)) or step <= 0:
        raise ValueError("Expected one-dimensional data and a positive integer step")
    return values[::step]

def snapshot_arrays(values: dict[str, np.ndarray]) -> dict[str, np.ndarray]:
    if any(array.dtype.hasobject for array in values.values()):
        raise ValueError("Object arrays need an explicit deep-copy policy")
    return {key:array.copy() for key,array in values.items()}

def expect_value_error(call):
    try:
        call()
    except ValueError:
        return
    raise AssertionError("Expected ValueError")

def main():
    # Exercise 1: Inspect a concrete layout
    a=np.arange(12,dtype=np.int64).reshape(3,4)
    assert layout(a)=={"shape":(3,4),"strides":(32,8),"itemsize":8,"nbytes":96}
    assert layout(a.T)["strides"]==(8,32)
    assert layout(np.array([],dtype=np.float32))["nbytes"]==0
    # Exercise 2: Return an independent window
    a=np.array([10,20,30,40]);b=copy_window(a,1,3)
    assert b.tolist()==[20,30] and not np.shares_memory(a,b)
    b[0]=-1
    assert a[1]==20 and copy_window(a,2,2).shape==(0,)
    expect_value_error(lambda:copy_window(a,3,2))
    expect_value_error(lambda:copy_window(np.ones((2,2)),0,1))
    # Exercise 3: Transform without mutating callers
    a=np.array([[1,3],[10,14]]);b=row_center_owned(a)
    assert np.allclose(b,[[-1,1],[-2,2]]) and a.tolist()==[[1,3],[10,14]]
    assert not np.shares_memory(a,b) and row_center_owned(np.empty((0,2))).shape==(0,2)
    assert np.allclose(row_center_owned(np.array([[1e308,1e308]])),[[0,0]])
    expect_value_error(lambda:row_center_owned(np.array([[1.7e308,-1.7e308,-1.7e308]])))
    expect_value_error(lambda:row_center_owned(np.empty((2,0))))
    expect_value_error(lambda:row_center_owned(np.array([[np.nan]])))
    # Exercise 4: Distinguish access restriction from a snapshot
    a=np.array([1,2]);b=read_only_view(a)
    assert np.shares_memory(a,b) and a.flags.writeable
    expect_value_error(lambda:b.__setitem__(0,9))
    a[0]=7
    assert b[0]==7
    # Exercise 5: Select a strided view deliberately
    a=np.arange(7);b=stride_select(a,3)
    assert b.tolist()==[0,3,6]
    b[1]=99
    assert a[3]==99 and stride_select(np.array([]),2).shape==(0,)
    expect_value_error(lambda:stride_select(a,0))
    expect_value_error(lambda:stride_select(a,True))
    # Exercise 6: Transfer ownership across a cache boundary
    a=np.array([1,2]);snap=snapshot_arrays({"a":a,"b":a})
    snap["a"][0]=9
    assert a[0]==1 and snap["b"][0]==1
    assert not np.shares_memory(snap["a"],snap["b"]) and snapshot_arrays({})=={}
    expect_value_error(lambda:snapshot_arrays({"x":np.array([{}],dtype=object)}))
    print("python-numpy-01: all six normal and boundary contracts passed")

if __name__ == "__main__":
    main()
