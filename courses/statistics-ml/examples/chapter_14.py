import numpy as np
from scipy import stats

def allocation_integrity():
    result=stats.chisquare([600,400],f_exp=[500,500])
    assert result.pvalue<1e-8
    print("SRM statistic/p:",result.statistic,result.pvalue)

def cuped():
    x=np.array([-2.,-1.,0.,1.,2.])
    noise=np.array([1.,-2.,2.,-2.,1.])
    y=10+3*x+noise
    theta=np.cov(x,y,ddof=1)[0,1]/np.var(x,ddof=1)
    adjusted=y-theta*(x-x.mean())
    assert np.isclose(theta,3) and np.isclose(adjusted.mean(),y.mean())
    rho=np.corrcoef(x,y)[0,1]
    assert np.isclose(adjusted.var(ddof=1),y.var(ddof=1)*(1-rho**2))
    print("CUPED theta:",theta,"variance before/after:",y.var(ddof=1),adjusted.var(ddof=1))

def ratio_metric():
    revenue=np.array([1.,9.,4.,8.]);visits=np.array([1.,3.,2.,4.])
    ratio=revenue.sum()/visits.sum()
    influence=(revenue-ratio*visits)/visits.mean()
    se=influence.std(ddof=1)/np.sqrt(len(visits))
    assert np.isclose(ratio,2.2) and np.isclose(np.mean(revenue/visits),2.)
    assert abs(influence.mean())<1e-12 and se>0
    print("Ratio of totals:",ratio,"mean user ratio:",np.mean(revenue/visits),"delta SE:",se)

def main():
    allocation_integrity();cuped();ratio_metric()

if __name__ == "__main__":
    main()
