import numpy as np
from scipy import stats

def robust_location():
    clean = np.array([9.,10.,10.,11.,10.])
    contaminated = np.append(clean, 1000.)
    median = np.median(contaminated)
    trimmed = stats.trim_mean(contaminated, proportiontocut=1/6)
    assert median == 10 and trimmed == 10.25
    assert contaminated.mean() > 100
    residual = np.array([0., 1., 100.])
    huber_score = np.clip(residual, -1.5, 1.5)
    assert huber_score[-1] == 1.5
    print("Mean/median/trimmed:", contaminated.mean(), median, trimmed, "Huber scores:", huber_score)

def imputation_uncertainty():
    estimates = np.array([2., 2.5, 3.])
    within_variance = np.array([.04, .04, .04])
    m = len(estimates)
    between = estimates.var(ddof=1)
    total = within_variance.mean() + (1+1/m)*between
    assert np.isclose(total, .04+1/3) and total > within_variance.mean()
    observed_mean, missing_fraction = 2., .3
    deltas = np.array([-2., 0., 2.])
    sensitivity = observed_mean + missing_fraction*deltas
    assert np.allclose(sensitivity, [1.4,2.,2.6])
    print("Pooled estimate/SE:", estimates.mean(), np.sqrt(total), "MNAR scenarios:", sensitivity)

def main():
    robust_location()
    imputation_uncertainty()

if __name__ == "__main__":
    main()
