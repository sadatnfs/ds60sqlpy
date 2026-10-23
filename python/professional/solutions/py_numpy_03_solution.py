"""Reference implementation and exact boundary checks for python-numpy-03."""

import numpy as np

def gather_positions(values: np.ndarray, positions: np.ndarray) -> np.ndarray:
    p=np.asarray(positions)
    if values.ndim!=1 or p.ndim!=1 or not np.issubdtype(p.dtype,np.integer) or np.any(p < -len(values)) or np.any(p >= len(values)):
        raise ValueError("Expected in-range one-dimensional integer positions")
    return values[p]

def sum_by_code(values: np.ndarray, codes: np.ndarray, bins: int) -> np.ndarray:
    v=np.asarray(values,dtype=float);c=np.asarray(codes)
    if isinstance(bins,bool) or not isinstance(bins,(int,np.integer)) or bins<0 or v.ndim!=1 or c.ndim!=1 or len(v)!=len(c) or not np.isfinite(v).all() or not np.issubdtype(c.dtype,np.integer) or np.any(c<0) or np.any(c>=bins):
        raise ValueError("Expected finite values and valid category codes")
    result=np.zeros(bins,dtype=float)
    np.add.at(result,c,v)
    return result

def select_rows(values: np.ndarray, mask: np.ndarray) -> np.ndarray:
    m=np.asarray(mask)
    if values.ndim!=2 or m.ndim!=1 or m.dtype!=np.bool_ or len(m)!=values.shape[0]:
        raise ValueError("Expected one Boolean value per row")
    return values[m]

def cartesian_submatrix(values: np.ndarray, rows: np.ndarray, columns: np.ndarray) -> np.ndarray:
    r=np.asarray(rows);c=np.asarray(columns)
    if values.ndim!=2 or r.ndim!=1 or c.ndim!=1 or not np.issubdtype(r.dtype,np.integer) or not np.issubdtype(c.dtype,np.integer) or np.any(r<0) or np.any(c<0) or np.any(r>=values.shape[0]) or np.any(c>=values.shape[1]):
        raise ValueError("Expected valid nonnegative row and column positions")
    return values[np.ix_(r,c)]

def stable_top_indices(scores: np.ndarray, k: int) -> np.ndarray:
    s=np.asarray(scores,dtype=float)
    if s.ndim!=1 or not np.isfinite(s).all() or isinstance(k,bool) or not isinstance(k,(int,np.integer)) or not 0<=k<=len(s):
        raise ValueError("Expected finite scores and a valid integer k")
    return np.argsort(-s,kind="stable")[:k]

def inverse_permutation(order: np.ndarray) -> np.ndarray:
    p=np.asarray(order)
    if p.ndim!=1 or not np.issubdtype(p.dtype,np.integer) or not np.array_equal(np.sort(p),np.arange(len(p))):
        raise ValueError("Expected a permutation of every original position")
    return np.argsort(p)

def expect_value_error(call):
    try:
        call()
    except ValueError:
        return
    raise AssertionError("Expected ValueError")

def main():
    # Exercise 1: Gather with explicit index rules
    a=np.array([10,20,30]);r=gather_positions(a,np.array([2,-1,0]))
    assert r.tolist()==[30,30,10] and not np.shares_memory(a,r)
    assert gather_positions(a,np.array([],dtype=int)).shape==(0,)
    expect_value_error(lambda:gather_positions(a,np.array([3])))
    expect_value_error(lambda:gather_positions(a,np.array([1.])))
    expect_value_error(lambda:gather_positions(a,np.array([True])))
    # Exercise 2: Accumulate repeated category codes
    assert sum_by_code(np.array([1,2,5]),np.array([0,0,2]),3).tolist()==[3,0,5]
    assert sum_by_code(np.array([]),np.array([],dtype=int),0).shape==(0,)
    expect_value_error(lambda:sum_by_code(np.array([1]),np.array([3]),3))
    expect_value_error(lambda:sum_by_code(np.array([1]),np.array([0]),True))
    # Exercise 3: Validate a row mask
    a=np.array([[1,2],[3,4],[5,6]])
    r=select_rows(a,np.array([True,False,True]))
    assert r.tolist()==[[1,2],[5,6]] and not np.shares_memory(a,r)
    assert select_rows(a,np.zeros(3,dtype=bool)).shape==(0,2)
    expect_value_error(lambda:select_rows(a,np.array([1,0,1])))
    expect_value_error(lambda:select_rows(a,np.ones((3,2),dtype=bool)))
    # Exercise 4: Select every row-column combination
    a=np.arange(12).reshape(3,4)
    assert cartesian_submatrix(a,np.array([2,0]),np.array([3,1])).tolist()==[[11,9],[3,1]]
    assert cartesian_submatrix(a,np.array([],dtype=int),np.array([3,1])).shape==(0,2)
    expect_value_error(lambda:cartesian_submatrix(a,np.array([3]),np.array([0])))
    # Exercise 5: Make top-k ties deterministic
    s=np.array([5.,9.,9.,1.])
    assert stable_top_indices(s,3).tolist()==[1,2,0] and s.tolist()==[5,9,9,1]
    assert stable_top_indices(s,0).size==0
    expect_value_error(lambda:stable_top_indices(s,5))
    expect_value_error(lambda:stable_top_indices(np.array([np.nan]),1))
    # Exercise 6: Restore original observation order
    p=np.array([2,0,1]);inverse=inverse_permutation(p);a=np.array([10,20,30])
    assert inverse.tolist()==[1,2,0] and np.array_equal(a[p][inverse],a)
    assert inverse_permutation(np.array([],dtype=int)).size==0
    expect_value_error(lambda:inverse_permutation(np.array([0,0])))
    expect_value_error(lambda:inverse_permutation(np.array([0.,1.])))
    print("python-numpy-03: all six normal and boundary contracts passed")

if __name__ == "__main__":
    main()
