import numpy as np
from scipy import stats

def mean_and_prediction():
    x = np.array([8.,9.,10.,11.,12.])
    n, mean, sd = len(x), x.mean(), x.std(ddof=1)
    critical = stats.t.ppf(.975, n-1)
    mean_halfwidth = critical*sd/np.sqrt(n)
    prediction_halfwidth = critical*sd*np.sqrt(1+1/n)
    assert prediction_halfwidth > mean_halfwidth
    assert np.isclose(mean_halfwidth, 1.9632431615)
    print("Mean:", mean, "mean CI halfwidth:", mean_halfwidth, "prediction halfwidth:", prediction_halfwidth)

def bootstrap_and_delta():
    rng = np.random.default_rng(8)
    x = np.array([1.,2.,3.,4.,5.])
    means = rng.choice(x, size=(4000,len(x)), replace=True).mean(axis=1)
    expected_bootstrap_se = x.std(ddof=0)/np.sqrt(len(x))
    assert abs(means.std(ddof=1)-expected_bootstrap_se) < .04
    theta, variance = 4., .25
    log_se = np.sqrt(variance)/theta
    assert log_se == .125
    print("Bootstrap SE:", means.std(ddof=1), "delta log SE:", log_se)

def repeated_sample_coverage():
    rng=np.random.default_rng(808)
    samples=rng.normal(loc=3.,scale=2.,size=(5000,20))
    means=samples.mean(axis=1)
    halfwidth=stats.norm.ppf(.975)*2/np.sqrt(20)
    coverage=np.mean(np.abs(means-3)<=halfwidth)
    monte_carlo_se=np.sqrt(.95*.05/len(means))
    assert abs(coverage-.95)<4*monte_carlo_se
    assert halfwidth<stats.norm.ppf(.975)*2
    print("Repeated-sample coverage:",coverage,"Monte Carlo SE near target:",monte_carlo_se)

def main():
    repeated_sample_coverage()
    mean_and_prediction()
    bootstrap_and_delta()

if __name__ == "__main__":
    main()
