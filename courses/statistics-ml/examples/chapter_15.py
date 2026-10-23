import numpy as np

def standardization():
    treated_mean=np.array([2.,10.]);control_mean=np.array([1.,9.])
    target=np.array([.5,.5])
    treated_composition=np.array([.9,.1]);control_composition=np.array([.1,.9])
    naive=treated_mean@treated_composition-control_mean@control_composition
    ate=(treated_mean-control_mean)@target
    assert np.isclose(naive,-5.4) and np.isclose(ate,1.)
    print("Naive difference:",naive,"standardized causal contrast under assumptions:",ate)

def collider_selection():
    a=np.array([0,0,1,1]);u=np.array([0,1,0,1]);y=u.copy()
    assert np.isclose(np.corrcoef(a,y)[0,1],0)
    selected=(a+u)>0
    selected_correlation=np.corrcoef(a[selected],y[selected])[0,1]
    assert selected_correlation < 0
    print("Unconditional correlation: 0; after selection:",selected_correlation)

def effect_targets():
    conditional=np.array([1.,5.])
    population=np.array([.8,.2]);treated=np.array([.2,.8])
    ate=conditional@population;att=conditional@treated
    assert np.isclose(ate,1.8) and np.isclose(att,4.2)
    print("ATE:",ate,"ATT:",att)

def main():
    standardization();collider_selection();effect_targets()

if __name__ == "__main__":
    main()
