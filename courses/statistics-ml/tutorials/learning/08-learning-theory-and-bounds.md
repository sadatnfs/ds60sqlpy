# Generalization guarantees have a population and a hypothesis class

Tutorial ID: `statistics-learning-008`. Prerequisites: `statistics-learning-002`, `statistics-learning-007`, `statistics-019`. Complete program: [learning_08.py](examples/learning_08.py).

## Key terms

- **Estimation error:** The excess risk from choosing a hypothesis with a finite sample, distinct from approximation error caused by the model family and optimization error from an inexact solver.
- **Union bound:** Bounding the probability that any of several events occurs by the sum of their probabilities, which makes Hoeffding's guarantee hold uniformly over a finite class.
- **VC dimension:** The largest number of points a class can shatter, that is, label in every possible way; thresholds on a line have VC dimension one.
- **Rademacher complexity:** A measure of how strongly a function class can correlate with random signs on a sample.
- **PAC-Bayes bound:** A risk bound for a randomized predictor drawn from a posterior over hypotheses, penalized by its KL divergence from a prior fixed before the data.

## Separate three errors

Approximation error comes from restricting the model family. Estimation error comes from choosing a model using a finite sample. Optimization error comes from not finding the desired empirical objective minimum. A flexible model can reduce approximation error while increasing estimation difficulty; a converged optimizer addresses only the last part. Distribution shift is another issue because the risk target itself may change.

Let \(R(h)=\mathbb E[\ell(h(X),Y)]\) be deployment risk and \(\widehat R_n(h)\) its average over independent identically distributed training observations. Assume loss lies in [0,1] and a finite hypothesis set \(\mathcal H\) of size \(M\) is fixed independently of those observations. Hoeffding plus a union bound gives

\[
\Pr\left(\sup_{h\in\mathcal H}|\widehat R_n(h)-R(h)|>\epsilon\right)
\le 2M e^{-2n\epsilon^2}.
\]

Solving at failure probability \(\delta\) yields \(\epsilon=\sqrt{\log(2M/\delta)/(2n)}\). Uniformity matters because the selected hypothesis depends on the data. For empirical risk minimization, adding and subtracting empirical risks gives excess risk at most \(2\epsilon\) relative to the best member of the fixed class on that event.

## Work a risk oracle

Generate \(X\) uniformly on [0,1] and \(Y\mid X=x\) as Bernoulli \(.2+.6x\). A threshold predicts one when \(x\ge t\). Integrating its two error regions gives

\[
R(t)=\int_0^t(.2+.6x)\,dx+\int_t^1(.8-.6x)\,dx
=.5-.6t+.6t^2.
\]

The best threshold is .5 with risk .35. The program fixes 41 thresholds before sampling 1,000 rows, selects empirical risk's minimum, and reports the actual risk from the integral. It checks the bound on this particular realization. The theorem's repeated-sample guarantee comes from its assumptions and proof, not from one successful numerical assertion.

## Beyond a finite list

Thresholds on a line can shatter one point but not every labeling of two ordered points, so their VC dimension is one. VC theory controls an infinite class using its possible label patterns rather than literally counting infinitely many functions. Rademacher complexity measures how strongly a class can correlate with random signs on a sample. These tools explain why capacity is a property of a function class and sample geometry, not just a count of fitted parameters.

Algorithmic stability asks how predictions or losses change when a training observation is replaced. Strongly regularized procedures can be stable under specified conditions. Stability bounds require their actual boundedness, convexity or other theorem assumptions; changing a seed and observing similar scores is only a diagnostic.

## A PAC-Bayes continuation

A fixed uniform prior over the 41 rules and a data-dependent Gibbs posterior define a randomized predictor. A standard bounded-loss PAC-Bayes inequality bounds binary KL between its empirical and true risk by

\[
\frac{\operatorname{KL}(Q\Vert P)+\log(2\sqrt n/\delta)}{n}.
\]

The displayed version uses iid observations, a sample-independent prior, bounded loss and the usual finite-class measurable setting, with \(n\ge8\) for the stated exponential-moment bound. Pinsker's inequality produces the looser risk upper bound used in the program. The posterior-weighted true risk is available through the oracle. This result concerns a random draw from \(Q\), not automatically its majority vote or the single best model. A prior selected using the same outcomes needs a different valid construction.

**Answered discussion: Does a small bound certify production?** Only for the stated distribution, loss and procedure. Unbounded losses, dependent users, reused evaluation data or shift break the simple argument. A numerically loose bound can still clarify which assumptions matter without replacing empirical validation.

## Worked example: how the uniform radius scales

The radius \(\sqrt{\log(2M/\delta)/(2n)}\) depends on the sample size directly and on the class size only through a logarithm. Tabulating it for a few combinations makes both rates concrete.

```python
import numpy as np

delta = 0.05
for n in (100, 1000, 10000):
    radii = [np.sqrt(np.log(2 * m / delta) / (2 * n)) for m in (1, 41, 10**6)]
    print(f"n={n:5d} radius for M=1, 41, 1e6: {np.round(radii, 3).tolist()}")
```

```text
n=  100 radius for M=1, 41, 1e6: [0.136, 0.192, 0.296]
n= 1000 radius for M=1, 41, 1e6: [0.043, 0.061, 0.094]
n=10000 radius for M=1, 41, 1e6: [0.014, 0.019, 0.03]
```

Moving from one fixed rule to 41 thresholds at \(n=1000\) widens the radius from 0.043 to 0.061, and even a million rules only reach 0.094. Multiplying the sample by ten divides each radius by about 3.16, the square root of ten. This is why a modest finite grid costs little, while the sample size dominates. The table also exposes the limit of the argument: with \(M=10^6\) and \(n=100\), the guarantee of 0.296 on a loss bounded by one is nearly useless.

## Worked example: empirical and true risk along the grid

Rebuild the 1,000-row sample from `examples/learning_08.py` and compare empirical risk with the integral risk at evenly spaced thresholds and at the selected one.

```python
import numpy as np

rng = np.random.default_rng(1908)
thresholds = np.linspace(0, 1, 41)
x = rng.uniform(size=1000)
y = rng.binomial(1, 0.2 + 0.6 * x)
empirical = ((x[:, None] >= thresholds) != y[:, None]).mean(axis=0)
risk = 0.5 - 0.6 * thresholds + 0.6 * thresholds**2
for i in (0, 10, 20, 30, 40, int(np.argmin(empirical))):
    print(f"t={thresholds[i]:.3f} empirical={empirical[i]:.3f} true={risk[i]:.3f}")
print("largest gap over all 41:", np.abs(empirical - risk).max().round(3))
```

```text
t=0.000 empirical=0.509 true=0.500
t=0.250 empirical=0.403 true=0.387
t=0.500 empirical=0.355 true=0.350
t=0.750 empirical=0.371 true=0.388
t=1.000 empirical=0.491 true=0.500
t=0.575 empirical=0.349 true=0.353
largest gap over all 41: 0.021
```

The selected threshold is 0.575, with empirical risk 0.349 and true risk 0.353, while the oracle threshold 0.5 has true risk 0.350. Selection cost only 0.003 of excess risk. The largest empirical-versus-true gap across all 41 rules is 0.021, well inside the uniform radius of 0.061. Note that the selected rule's empirical risk sits below its true risk: choosing the minimum favors rules whose sample happened to look good, which is the optimism the uniform bound accounts for.

## Assumptions to check before quoting a bound

The hypothesis set must be fixed before the data are seen; adding thresholds after viewing errors changes \(M\) after the fact. Observations must be independent draws from the deployment distribution. The loss must be bounded, which squared error on unbounded outcomes is not. If any of these fails, the radius is a heuristic rather than a guarantee.

References: [Understanding Machine Learning](https://www.cs.huji.ac.il/~shais/UnderstandingMachineLearning/understanding-machine-learning-theory-algorithms.pdf), [Maurer's tightened PAC-Bayes bound](https://arxiv.org/abs/cs/0411099). Continue to the [scientific cases](../science/README.md).
