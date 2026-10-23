"""Reference implementation and exact boundary checks for python-numpy-02."""

import numpy as np

def column_center(values: np.ndarray) -> np.ndarray:
    x=np.asarray(values,dtype=float)
    if x.ndim!=2 or x.shape[0]==0 or not np.isfinite(x).all():
        raise ValueError("Expected a finite matrix with observations")
    return x-x.mean(axis=0,keepdims=True)

def scale_rows(values: np.ndarray, factors: np.ndarray) -> np.ndarray:
    x=np.asarray(values,dtype=float);f=np.asarray(factors,dtype=float)
    if x.ndim!=2 or f.ndim!=1 or len(f)!=x.shape[0] or not np.isfinite(x).all() or not np.isfinite(f).all():
        raise ValueError("Expected one finite factor per row")
    return x*f[:,None]

def pairwise_squared(left: np.ndarray, right: np.ndarray) -> np.ndarray:
    a=np.asarray(left,dtype=float);b=np.asarray(right,dtype=float)
    if a.ndim!=2 or b.ndim!=2 or a.shape[1]!=b.shape[1] or not np.isfinite(a).all() or not np.isfinite(b).all():
        raise ValueError("Expected finite matrices with equal feature dimensions")
    difference=a[:,None,:]-b[None,:,:]
    return np.sum(difference*difference,axis=-1)

def weighted_columns(values: np.ndarray, weights: np.ndarray) -> np.ndarray:
    x=np.asarray(values,dtype=float);w=np.asarray(weights,dtype=float)
    if x.ndim!=2 or w.ndim!=1 or len(w)!=x.shape[0] or not np.isfinite(x).all() or not np.isfinite(w).all() or np.any(w<0) or w.sum()<=0:
        raise ValueError("Expected finite nonnegative weights with positive sum")
    return np.einsum("n,nd->d",w,x)/w.sum()

def batched_projection(values: np.ndarray, weights: np.ndarray) -> np.ndarray:
    x=np.asarray(values,dtype=float);w=np.asarray(weights,dtype=float)
    if x.ndim<2 or w.ndim!=2 or x.shape[-1]!=w.shape[0] or not np.isfinite(x).all() or not np.isfinite(w).all():
        raise ValueError("Expected a compatible final feature dimension")
    return np.einsum("...d,dk->...k",x,w)

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

def expect_value_error(call):
    try:
        call()
    except ValueError:
        return
    raise AssertionError("Expected ValueError")

def main():
    # Exercise 1: Reduce the observation axis
    x=np.array([[1,10,100],[3,14,108]])
    assert np.allclose(column_center(x),[[-1,-2,-4],[1,2,4]])
    assert x[0,0]==1
    expect_value_error(lambda:column_center(np.empty((0,3))))
    expect_value_error(lambda:column_center(np.array([1,2])))
    # Exercise 2: Broadcast one factor per row
    x=np.array([[1,2,3],[4,5,6]])
    assert np.allclose(scale_rows(x,np.array([10,100])),[[10,20,30],[400,500,600]])
    assert scale_rows(np.empty((0,3)),np.array([])).shape==(0,3)
    expect_value_error(lambda:scale_rows(x,np.array([1,2,3])))
    # Exercise 3: Create all pairs with a declared contraction
    a=np.array([[0,0],[3,4]]);b=np.array([[0,0]])
    assert np.allclose(pairwise_squared(a,b),[[0],[25]])
    assert pairwise_squared(np.empty((0,2)),b).shape==(0,1)
    expect_value_error(lambda:pairwise_squared(a,np.ones((1,3))))
    # Exercise 4: Contract observations using valid weights
    x=np.array([[1,10],[3,30]])
    assert np.allclose(weighted_columns(x,np.array([1,3])),[2.5,25])
    assert np.allclose(weighted_columns(x,np.array([10,30])),[2.5,25])
    expect_value_error(lambda:weighted_columns(x,np.array([0,0])))
    expect_value_error(lambda:weighted_columns(x,np.array([-1,2])))
    expect_value_error(lambda:weighted_columns(x,np.array([1])))
    # Exercise 5: Preserve leading batch axes
    x=np.arange(24).reshape(2,3,4);w=np.arange(8).reshape(4,2)
    r=batched_projection(x,w)
    assert r.shape==(2,3,2) and np.allclose(r,np.stack([x[0]@w,x[1]@w]))
    assert batched_projection(x[0],w).shape==(3,2)
    expect_value_error(lambda:batched_projection(x,np.ones((3,2))))
    # Exercise 6: Normalize while preserving zero vectors
    x=np.array([[3.,4.],[0.,0.],[-2.,0.]])
    r=unit_rows(x)
    assert np.allclose(r,[[.6,.8],[0,0],[-1,0]]) and np.isfinite(r).all()
    assert np.array_equal(x,[[3,4],[0,0],[-2,0]])
    assert np.allclose(unit_rows(np.array([[1e308,1e308]])),[[2**-.5,2**-.5]])
    expect_value_error(lambda:unit_rows(np.array([[np.inf]])))
    print("python-numpy-02: all six normal and boundary contracts passed")

if __name__ == "__main__":
    main()
