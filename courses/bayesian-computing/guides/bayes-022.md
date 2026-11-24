# bayes-022: Stan marginalized mixtures and label conventions

Tutorial mode. Stage: advanced. Direct prerequisites: `bayes-018`, `bayes-011`.

## A mixture sums over unobserved membership

A finite mixture models each observation through several possible component distributions. If the component indicator is not observed, its likelihood contribution sums the weighted component densities. Stan's Hamiltonian methods require a differentiable continuous target, so discrete latent membership is often marginalized rather than declared as a sampled discrete parameter.

For two normal components with first-component weight w,

\[
p(y_i\mid\theta)=w\,\mathcal N(y_i\mid\mu_1,\sigma^2)
+(1-w)\,\mathcal N(y_i\mid\mu_2,\sigma^2).
\]

The program uses `log_mix` to compute the corresponding log density stably. Averaging component log densities would be a different calculation because the logarithm of a sum is not the sum of logarithms.

## Key terms

- **Finite mixture:** A model in which each observation comes from one of several component distributions with mixing weights.
- **Marginalization:** Summing over the unobserved component label so the target density stays continuous and differentiable.
- **log_mix:** The Stan function that computes the log of a weighted sum of component densities stably from log terms.
- **Responsibility:** The posterior probability that an observation belongs to a component, given one parameter draw.
- **Label switching:** The symmetry that lets component labels permute across draws unless an ordering or anchored prior sets a convention.

## Worked case 1: fit a marginalized two-component model

The tiny data contain one group of values near minus two and another near two. The model orders its two means and uses explicitly stated prior anchors near those two locations. The shared positive scale keeps the example compact. The weight receives a Beta(2,2) prior.

Ordering defines a label convention, while anchored priors add substantive prior information. They should not be conflated. If the scientific model instead uses symmetric exchangeable components, an ordering restriction can establish an interpretable labeling convention, but other prior choices must still match that intended model.

For each observation, the program adds the log of the weighted mixture density. This is the likelihood after integrating out its unobserved component indicator. The computation preserves uncertainty over membership rather than assigning each row permanently to whichever component currently has the larger density.

## Worked case 2: compute responsibilities and replicate observations

A generated responsibility is the posterior component probability conditional on one parameter draw and the observed value:

\[
r_{i1}=\frac{w\,\mathcal N(y_i\mid\mu_1,\sigma^2)}
{w\,\mathcal N(y_i\mid\mu_1,\sigma^2)+(1-w)\,\mathcal N(y_i\mid\mu_2,\sigma^2)}.
\]

The code computes it from log terms and the same mixture normalizer. Averaging responsibilities over posterior draws incorporates parameter uncertainty. A hard label discards that uncertainty and should not be reported as a discovered factual identity without further interpretation.

For replicated data, the program first draws a component according to the sampled mixture weight and then draws from that component. This is different from drawing at a weighted-average mean. A normal centered at that average would erase the multimodal structure the mixture was designed to represent.

## Review identifiability and model criticism

Mixtures can have multiple modes, weakly separated components and difficult geometry. Additional components can improve in-sample density while remaining poorly identified. Component-specific scales can introduce further pathologies and require careful priors and diagnostics. A model that compiles and produces draws has not automatically discovered a meaningful number of populations.

Label switching can make naive component-wise posterior means misleading in a symmetric model. Label-invariant predictions or quantities may still be meaningful, but the reporting convention must be stated. Ordering and informative anchors can change the interpretation and should be retained in the model record.

Predictive checks should examine modes, spread, tails and any features important to the scientific question. A mixture can fit a bimodal histogram while missing dependence, covariate effects or the observation process. For example, two measurement devices with different biases could produce modes without representing two substantive populations.

The short classroom chains are especially limited for multimodal problems. Inspect actual summaries and traces, compare initializations and investigate disagreement. The ordered, anchored synthetic example is intentionally approachable; it is not evidence that two short chains reliably explore arbitrary mixture posteriors.

## Answered scientific discussion

**Why not sample one integer membership per observation directly?** Stan's standard HMC target is continuous. Marginalization integrates those discrete possibilities into a differentiable likelihood when the structure permits it.

**Does a responsibility of .99 establish a real category?** It is a probability conditional on the mixture model and, before averaging, on one parameter draw. Its scientific meaning depends on whether the components represent defensible mechanisms. A high conditional number cannot establish that interpretation on its own.

## Worked example: log_mix stability and label-swap invariance

```python
import numpy as np
from scipy.special import logsumexp
from scipy import stats

np.set_printoptions(suppress=True)


def log_mix(w, mu1, mu2, y):
    return logsumexp(
        [np.log(w) + stats.norm.logpdf(y, mu1, 1), np.log1p(-w) + stats.norm.logpdf(y, mu2, 1)],
        axis=0,
    )


y = np.array([-1.0, 0.2, 3.9, 60.0])
with np.errstate(divide="ignore"):
    naive = np.log(0.3 * stats.norm.pdf(y, 0, 1) + 0.7 * stats.norm.pdf(y, 4, 1))
print("naive log density:", naive.round(3))
print("log_mix          :", log_mix(0.3, 0.0, 4.0, y).round(3))
a = log_mix(0.3, 0.0, 4.0, y[:3]).sum()
b = log_mix(0.7, 4.0, 0.0, y[:3]).sum()
print(f"total log likelihood {a:.4f}; with labels swapped {b:.4f}")
```

Observed output:

```text
naive log density: [-2.623 -2.141 -1.28    -inf]
log_mix          : [   -2.623    -2.141    -1.28  -1569.276]
total log likelihood -6.0445; with labels swapped -6.0445
```

For ordinary observations the two lines agree: \(-2.623\), \(-2.141\) and \(-1.280\). At 60 the direct formula exponentiates densities near \(e^{-1568}\), both components underflow to zero, and the log of their sum is \(-\infty\). One such point would make the whole log likelihood \(-\infty\) and stop a sampler. log_mix computes the same quantity as a log-sum-exp of the weighted component log densities and returns the finite value \(-1569.276\), which correctly says that the point is almost impossible under this mixture without saying it is impossible. The last line shows the label problem. Swapping the component means and replacing the weight 0.3 by 0.7 gives an identical log likelihood, \(-6.0445\), so the posterior has two mirror-image modes. If half the chains land in each mode, pooled draws would give means near 2 for both components. Declaring the means as an ordered vector in Stan removes one mirror image without changing any fitted density.

## Complete reproducible program

The prepared Stan pad compiles `main.stan` and samples two chains with 100 warmup and 100 retained draws each. Its tiny data are declared in `transformed data`; this pad has no separate JSON editor. The linked project explains standard data-block workflows. These teaching-sized chains can fail the convergence screen from `bayes-006` (R-hat below 1.01, at least 100 bulk and tail effective draws per chain, no divergences); read the printed diagnostics against it before interpreting any estimate. Runtime: `stan-cpu`.

```stan
transformed data {
  int N = 10;
  vector[N] y = [-2.5, -2, -1.8, -1.7, -2.1, 1.5, 1.8, 2.2, 2.4, 2]';
}
parameters {
  ordered[2] mu;
  real<lower=0> sigma;
  real<lower=0, upper=1> mixture_weight;
}
model {
  mu[1] ~ normal(-2, 1);
  mu[2] ~ normal(2, 1);
  sigma ~ normal(0, 1);
  mixture_weight ~ beta(2, 2);
  for (n in 1 : N) {
    target += log_mix(mixture_weight, normal_lpdf(y[n] | mu[1], sigma),
                      normal_lpdf(y[n] | mu[2], sigma));
  }
}
generated quantities {
  vector[N] log_lik;
  vector[N] responsibility_first;
  vector[N] y_rep;
  for (n in 1 : N) {
    real first = normal_lpdf(y[n] | mu[1], sigma);
    real second = normal_lpdf(y[n] | mu[2], sigma);
    log_lik[n] = log_mix(mixture_weight, first, second);
    responsibility_first[n] = exp(log(mixture_weight) + first - log_lik[n]);
    if (bernoulli_rng(mixture_weight))
      y_rep[n] = normal_rng(mu[1], sigma);
    else
      y_rep[n] = normal_rng(mu[2], sigma);
  }
}
```

## Primary references

- [Stan marginalized finite mixtures](https://mc-stan.org/docs/stan-users-guide/finite-mixtures.html)
