# Partial pooling, prediction and a decision loss

Tutorial ID: `statistics-science-002`. Prerequisites: `statistics-018`, `statistics-012`, `statistics-learning-002`. Complete program: [science_02.py](examples/science_02.py). This unit uses only the default scientific packages.

## Key terms

- **Partial pooling:** Estimating each group mean as a precision-weighted compromise between its own sample mean and a shared prior center, so small groups shrink more.
- **Data weight:** The share \(n_j\tau^2/(\sigma^2+n_j\tau^2)\) given to a group's sample mean in its posterior mean.
- **Posterior predictive distribution:** The distribution of a new outcome after integrating over posterior uncertainty in the group mean, so its variance adds observation noise to posterior variance.
- **Prior predictive check:** Simulating complete datasets from the prior and likelihood before seeing data to judge whether the implied outcomes are plausible.
- **Asymmetric loss:** A cost that penalizes shortfall and excess differently; with costs four and one, the optimal action is the .8 quantile of the predictive distribution.

## Separate uncertainty about means from future outcomes

Three groups have observed means -1,.2,1.4 and sample sizes 2,10,30. Assume individual outcome variance four and a normal prior for each group mean with population center zero and variance one. Those variances and the center are treated as known in this first case. A later hierarchical model estimates them and must propagate the additional uncertainty.

Multiplying the normal likelihood and prior, then completing the square, gives

\[
v_j=\left(\frac1{\tau^2}+\frac{n_j}{\sigma^2}\right)^{-1},\qquad
m_j=v_j\left(\frac{\mu_0}{\tau^2}+\frac{n_j\bar y_j}{\sigma^2}\right).
\]

Equivalently, the data weight is \(w_j=n_j\tau^2/(\sigma^2+n_j\tau^2)\). The posterior mean is \(w_j\bar y_j+(1-w_j)\mu_0\). Larger groups supply more information and shrink less toward the prior center.

## Work the pooling calculation

The weights are approximately .333,.714,.882. Posterior means become -.333,.143,1.235, while posterior SDs are .816,.535,.343. These are different from unpooled sample means, and the shrinkage is intentional. It is justified by a shared prior model, not by an assertion that every group is identical.

For a new outcome in an existing group, integrate over uncertainty in its mean and add observation noise. Predictive variance is \(v_j+\sigma^2\). The resulting predictive SDs are about 2.160,2.070,2.029, much larger than uncertainty about the means. The program draws group means from their exact posteriors, then observations conditionally, and checks the empirical predictive variance against that analytic result.

## Change a substantive assumption

Replace prior variance one by .25, representing stronger belief that groups resemble the population center. The posterior means shrink more, especially for the two-observation group. Report this sensitivity rather than interpreting one prior as neutral. If observed groups were selected for extreme performance, the likelihood/selection model also matters; changing prior scale alone may not address selection.

Prior predictive checks ask what complete datasets the prior and likelihood imply before seeing the data. Posterior predictive checks ask which observed features are reproduced after conditioning. Neither is a substitute for convergence diagnostics when posterior draws come from MCMC. Here direct normal draws avoid MCMC error but still carry finite Monte Carlo uncertainty.

## Connect prediction to an action

Suppose understaffing costs four units per missing unit and overstaffing costs one. For action a and future workload Y, loss is \(4\max(Y-a,0)+\max(a-Y,0)\). The optimal action under a continuous predictive distribution is its .8 quantile, not the posterior mean of the group parameter. The example evaluates expected loss at action two by averaging over posterior predictive draws.

A parameter credible interval and an operational loss answer different questions. A narrowly estimated mean can coexist with wide future outcome uncertainty and expensive tails. Refit or revise the model when its predictive behavior misses important features, rather than treating narrow parameter uncertainty as proof of usefulness.

**Answered discussion: Can pooling hide a real unusual group?** Yes, especially with a badly chosen shared distribution. Compare no pooling, partial pooling and prior scales; inspect group residuals and predictive tails. Let the model express credible heterogeneity rather than forcing every group toward the same convenient answer.

## Worked example: choosing the staffing action

The guide states that the expected-loss minimizer is the 0.8 predictive quantile. Using the same posterior as `examples/science_02.py`, this snippet computes that quantile for each group and compares expected loss at three candidate actions.

```python
import numpy as np
from scipy import stats

means, sizes = np.array([-1.0, 0.2, 1.4]), np.array([2, 10, 30])
v = 1 / (1 / 1.0 + sizes / 4.0)
m = v * sizes * means / 4.0
sd = np.sqrt(v + 4.0)
best = m + sd * stats.norm.ppf(0.8)
rng = np.random.default_rng(1802)
y = rng.normal(m, sd, size=(20000, 3))


def loss(action):
    return np.mean(4 * np.maximum(y - action, 0) + np.maximum(action - y, 0), axis=0)


print("0.8 quantile actions:", np.round(best, 3))
print("loss at action m_j:  ", np.round(loss(m), 3))
print("loss at action 2:    ", np.round(loss(2.0), 3))
print("loss at quantile:    ", np.round(loss(best), 3))
```

```text
0.8 quantile actions: [1.485 1.885 2.943]
loss at action m_j:   [4.332 4.053 4.015]
loss at action 2:     [3.11  2.889 3.157]
loss at quantile:     [3.031 2.881 2.822]
```

The quantile actions are 1.485, 1.885 and 2.943, each well above the posterior means because shortage costs four times surplus. Staffing at the posterior mean costs about 4.0 to 4.3 units per period. The fixed action 2 costs 3.110, 2.889 and 3.157; the quantile action costs 3.031, 2.881 and 2.822. For the middle group the quantile 1.885 is close to 2, so the two losses nearly tie, while for the 30-observation group the gap is about 0.33 units per period. The mean is the right summary for a squared-error question and the wrong one for this asymmetric decision.

## Worked example: three prior scales

The amount of pooling is controlled by \(\tau^2\). Tightening and loosening it shows how much of each posterior mean comes from the prior rather than the data.

```python
import numpy as np

means, sizes = np.array([-1.0, 0.2, 1.4]), np.array([2, 10, 30])
for tau2 in (0.25, 1.0, 100.0):
    w = sizes * tau2 / (4.0 + sizes * tau2)
    print(f"tau^2={tau2:6.2f} weights {np.round(w, 3)} posterior means {np.round(w * means, 3)}")
```

```text
tau^2=  0.25 weights [0.111 0.385 0.652] posterior means [-0.111  0.077  0.913]
tau^2=  1.00 weights [0.333 0.714 0.882] posterior means [-0.333  0.143  1.235]
tau^2=100.00 weights [0.98  0.996 0.999] posterior means [-0.98   0.199  1.398]
```

With \(\tau^2=0.25\), even the 30-observation group keeps only 0.652 of its own mean, and its posterior mean falls from 1.4 to 0.913. At the guide value of one, the weights are 0.333, 0.714 and 0.882. At 100 the prior barely matters and the posterior means sit near the raw means, -0.98, 0.199 and 1.398. The two-observation group moves the most across the three rows, from -0.111 to -0.98, which is exactly where a reader should look when asking whether the prior scale was defensible.

## Assumptions behind this conjugate shortcut

The calculation treats \(\sigma^2\) and \(\tau^2\) as known. In practice both are estimated, and their uncertainty widens predictive intervals, most of all for small groups; the PyMC tutorial handles that case. Normal outcomes are assumed too: skewed workloads put more mass in the upper tail, raising the optimal quantile action beyond what the normal model suggests.

Continue to the explicitly prepared [PyMC diagnostic workflow](09-pymc-hierarchy-and-diagnostics.md). Reference: [Bayesian Data Analysis resources](https://sites.stat.columbia.edu/gelman/book/).
