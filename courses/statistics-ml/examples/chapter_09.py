import numpy as np
from scipy import stats
from itertools import combinations

def paired_and_welch():
    before = np.array([10.,30.,50.,70.,90.,110.])
    changes = np.array([1.,2.,1.,2.,1.,2.])
    after = before+changes
    paired = stats.ttest_rel(after,before)
    independent = stats.ttest_ind(after,before,equal_var=False)
    assert paired.pvalue < .01 and independent.pvalue > .8
    print("Paired p:", paired.pvalue, "unpaired p:", independent.pvalue)

def exact_randomization():
    y = np.array([1.,2.,3.,4.])
    observed = y[2:].mean()-y[:2].mean()
    contrasts=[]
    for treated in combinations(range(4),2):
        mask=np.zeros(4,dtype=bool);mask[list(treated)]=True
        contrasts.append(y[mask].mean()-y[~mask].mean())
    p = np.mean(np.abs(contrasts)>=abs(observed))
    assert np.isclose(p,1/3)
    print("Six valid assignments, exact two-sided p:", p)

def equivalence():
    delta, se, margin = .1, .1, .5
    lower, upper = delta+np.array([-1,1])*stats.norm.ppf(.95)*se
    assert lower > -margin and upper < margin
    print("90% equivalence interval:", lower, upper, "inside +/-", margin)

def main():
    paired_and_welch(); exact_randomization(); equivalence()

if __name__ == "__main__":
    main()
