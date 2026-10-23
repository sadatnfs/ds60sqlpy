import numpy as np

def kaplan_meier():
    time=np.array([1.,2.,3.,4.]);event=np.array([1,0,1,1])
    survival=1.;steps=[]
    for t in np.unique(time[event==1]):
        risk=np.sum(time>=t);failures=np.sum((time==t)&(event==1))
        survival*=1-failures/risk;steps.append((t,int(risk),survival))
    assert np.allclose([s[2] for s in steps],[.75,.375,0.])
    print("Event time, risk count, survival:",steps)
    return steps

def restricted_mean():
    # Survival on [0,1), [1,3), [3,4) is 1, .75, .375.
    area=1*1+.75*2+.375*1
    assert area==2.875
    print("Restricted mean through time 4:",area)

def competing_incidence():
    # Four people: cause A at 1, cause B at 2, remaining two censored at 3.
    s=1.;cif_a=0.;cif_b=0.
    cif_a+=s*(1/4);s*=1-1/4
    cif_b+=s*(1/3);s*=1-1/3
    assert np.allclose([cif_a,cif_b,s],[.25,.25,.5])
    assert np.isclose(cif_a+cif_b+s,1.)
    print("CIF A, CIF B, event-free:",cif_a,cif_b,s)

def main():
    kaplan_meier();restricted_mean();competing_incidence()

if __name__ == "__main__":
    main()
