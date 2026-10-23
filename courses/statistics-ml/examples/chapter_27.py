import numpy as np

def reconciliation():
    base=np.array([100.,40.,50.])
    constraint=np.array([[1.,-1.,-1.]])
    corrected=base-constraint.T@np.linalg.solve(constraint@constraint.T,constraint@base)
    assert np.isclose(corrected[0],corrected[1]+corrected[2])
    assert np.allclose(corrected,[290/3,130/3,160/3])
    print("Base total minus children:",(constraint@base)[0],"reconciled:",corrected)

def losses():
    train=np.array([10.,12.,14.,16.]);actual=np.array([18.,20.]);prediction=np.array([16.,22.])
    error=actual-prediction
    scale=np.mean(np.abs(np.diff(train)))
    mase=np.mean(np.abs(error))/scale
    q=.9;pinball=np.maximum(q*error,(q-1)*error)
    assert mase==1. and np.allclose(pinball,[1.8,.2])
    print("MASE:",mase,"0.9 pinball losses:",pinball)

def intervals_and_origins():
    actual=np.array([10.,15.,20.]);lo=np.array([8.,12.,18.]);hi=np.array([12.,14.,22.])
    covered=(lo<=actual)&(actual<=hi)
    assert covered.tolist()==[True,False,True]
    assert np.isclose(covered.mean(),2/3)
    assert np.isclose(np.mean(hi-lo),10/3)
    origins=[3,4,5]
    pairs=[(np.arange(origin+1),origin+1) for origin in origins]
    assert all(train.max()<target for train,target in pairs)
    print("Coverage and mean width:",covered.mean(),np.mean(hi-lo),"origins:",origins)

def main():
    reconciliation();losses();intervals_and_origins()

if __name__ == "__main__":
    main()
