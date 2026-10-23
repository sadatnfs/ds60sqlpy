import numpy as np

def aipw_and_balance():
    x=np.repeat([0.,1.],4)
    a=np.tile([0.,0.,1.,1.],2)
    y=2*x+3*a+np.tile([-1.,1.,-1.,1.],2)
    e=np.full(8,.5)
    wrong_m0=np.zeros(8);wrong_m1=np.ones(8)
    score=wrong_m1-wrong_m0+a*(y-wrong_m1)/e-(1-a)*(y-wrong_m0)/(1-e)
    assert np.isclose(score.mean(),3.)
    assert np.isclose(np.average(x[a==1],weights=1/e[a==1]),np.average(x[a==0],weights=1/(1-e[a==0])))
    print("AIPW with deliberately wrong outcome models:",score.mean())

def cross_fitted_nuisance():
    x=np.arange(12,dtype=float)
    y=1+2*x
    prediction=np.empty_like(y)
    folds=np.arange(len(y))%3
    for fold in range(3):
        train=folds!=fold;test=~train
        assert not set(np.flatnonzero(train)) & set(np.flatnonzero(test))
        beta=np.polyfit(x[train],y[train],1)
        prediction[test]=np.polyval(beta,x[test])
    assert np.allclose(prediction,y)
    print("Cross-fitted nuisance prediction maximum error:",np.max(np.abs(prediction-y)))

def policy_value():
    effect=np.array([-.5,.5,2.,4.]);cost=1.
    policy=effect>cost
    value=np.mean(policy*(effect-cost))
    assert policy.tolist()==[False,False,True,True] and value==1.
    assert value>np.mean(effect-cost)
    print("Treat:",policy,"incremental net value per eligible unit:",value)

def main():
    aipw_and_balance();cross_fitted_nuisance();policy_value()

if __name__ == "__main__":
    main()
