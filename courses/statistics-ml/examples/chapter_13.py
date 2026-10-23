import numpy as np
from itertools import product
from scipy.stats import norm

def factorial_and_alias():
    ab=np.array(list(product([-1.,1.],repeat=2)))
    a,b=ab.T
    design=np.column_stack([np.ones(4),a,b,a*b])
    y=10+2*a+3*b+4*a*b
    beta=np.linalg.solve(design,y)
    assert np.allclose(beta,[10,2,3,4])
    assert np.isclose(y[a==1].mean()-y[a==-1].mean(),4)
    c=a*b
    alias=np.column_stack([np.ones(4),a,b,c,a*b])
    assert np.linalg.matrix_rank(alias)==4 and alias.shape[1]==5
    print("Factorial coefficients:",beta,"C and AB are identical:",np.array_equal(c,a*b))

def blocked_assignment():
    rng=np.random.default_rng(13)
    blocks=np.repeat(np.arange(4),4)
    treatment=np.zeros(16,dtype=int)
    for block in np.unique(blocks):
        rows=np.flatnonzero(blocks==block)
        treatment[rng.choice(rows,2,replace=False)]=1
    assert all(treatment[blocks==b].sum()==2 for b in range(4))
    print("Treated per block:",[int(treatment[blocks==b].sum()) for b in range(4)])

def sample_size():
    sigma,delta=2.,1.
    n=2*sigma**2*(norm.ppf(.975)+norm.ppf(.8))**2/delta**2
    half_effect=2*sigma**2*(norm.ppf(.975)+norm.ppf(.8))**2/(delta/2)**2
    assert np.isclose(half_effect,4*n)
    print("Approximate per-arm n:",int(np.ceil(n)),"half effect:",int(np.ceil(half_effect)))

def main():
    factorial_and_alias();blocked_assignment();sample_size()

if __name__ == "__main__":
    main()
