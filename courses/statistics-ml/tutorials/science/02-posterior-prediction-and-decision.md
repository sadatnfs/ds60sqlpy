# Partial pooling, prediction and a decision loss

Tutorial ID: `statistics-science-002`. Prerequisites: `statistics-018`, `statistics-012`, `statistics-learning-002`. Complete program: [science_02.py](examples/science_02.py). This unit uses only the default scientific packages.

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

Continue to the explicitly prepared [PyMC diagnostic workflow](09-pymc-hierarchy-and-diagnostics.md). Reference: [Bayesian Data Analysis resources](https://sites.stat.columbia.edu/gelman/book/).
