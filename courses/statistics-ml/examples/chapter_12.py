import numpy as np

def leverage_and_residuals():
    x=np.array([0.,1.,2.,3.,20.])
    design=np.column_stack([np.ones(5),x])
    hat=design@np.linalg.pinv(design)
    leverage=np.diag(hat)
    assert np.isclose(leverage.sum(),2) and leverage[-1]>.9
    print("Leverage:",leverage,"sum equals rank:",leverage.sum())

def partial_pooling():
    grand_mean,tau2,sigma2=5.,1.,4.
    n=np.array([1.,4.,100.]);group_mean=np.array([9.,9.,9.])
    weight=tau2/(tau2+sigma2/n)
    pooled=weight*group_mean+(1-weight)*grand_mean
    assert np.all(np.diff(weight)>0) and np.all((pooled>5)&(pooled<9))
    assert np.isclose(tau2/(tau2+sigma2),.2)
    print("Pooling weights:",weight,"group predictions:",pooled,"ICC:",.2)

def within_estimation():
    x=np.array([[0.,1.,2.],[10.,11.,12.]])
    intercept=np.array([100.,-100.])[:,None]
    y=intercept+2*x
    xc=x-x.mean(axis=1,keepdims=True)
    yc=y-y.mean(axis=1,keepdims=True)
    within=np.sum(xc*yc)/np.sum(xc*xc)
    pooled=np.polyfit(x.ravel(),y.ravel(),1)[0]
    assert np.isclose(within,2) and pooled<0
    print("Within-unit slope:",within,"naive pooled slope:",pooled)

def main():
    leverage_and_residuals();partial_pooling();within_estimation()

if __name__ == "__main__":
    main()
