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

def main():
    mean_and_prediction()
    bootstrap_and_delta()

if __name__ == "__main__":
    main()
