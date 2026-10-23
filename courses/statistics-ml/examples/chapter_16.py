import numpy as np

def difference_in_differences():
    treated=np.array([10.,15.]);control=np.array([7.,9.])
    did=np.diff(treated)[0]-np.diff(control)[0]
    assert did==3
    counterfactual=treated[0]+np.diff(control)[0]
    assert counterfactual==12
    print("Untreated treated-group counterfactual:",counterfactual,"DiD effect:",did)

def instrumental_variables():
    uptake=np.array([.2,.6]);outcome=np.array([4.,5.2])
    first_stage=uptake[1]-uptake[0]
    effect=(outcome[1]-outcome[0])/first_stage
    assert np.isclose(effect,3.)
    assert np.isclose((outcome[1]-outcome[0])/.04,30.)
    print("ITT:",outcome[1]-outcome[0],"first stage:",first_stage,"Wald effect:",effect)

def local_discontinuity():
    x=np.array([-3.,-2.,-1.,1.,2.,3.])
    treated=(x>0).astype(float)
    y=5+.5*x+2*treated
    design=np.column_stack([np.ones(len(x)),x,treated])
    beta=np.linalg.lstsq(design,y,rcond=None)[0]
    assert np.allclose(beta,[5,.5,2])
    print("RD illustrative intercept/slope/jump:",beta)

def main():
    difference_in_differences();instrumental_variables();local_discontinuity()

if __name__ == "__main__":
    main()
