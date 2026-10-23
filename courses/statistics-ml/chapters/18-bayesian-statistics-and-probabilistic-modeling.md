# 18. Bayesian Statistics and Probabilistic Modeling

Book: **Statistics and Machine Learning for Data Scientists End To End**. Chapter ID: `statistics-018`. Tutorial mode; all examples and interview answers are fully worked.

## The decision and the mental model

Bayesian inference combines a model for observations with a probability distribution over unknown quantities. Bayes' rule gives posterior proportional to likelihood times prior. The result is conditional on those choices; a narrow posterior can be confidently wrong when the model omits a systematic error or its prior excludes plausible behavior.

### A complete beta-binomial update

Let p be a success probability, p~Beta(alpha,beta), and observe s successes in n independent trials. Multiplication of p^(alpha-1)*(1-p)^(beta-1) by p^s*(1-p)^(n-s) gives Beta(alpha+s,beta+n-s). The posterior mean is a weighted average of the prior mean and sample proportion, with total prior concentration alpha+beta acting as prior information in this model. For Beta(2,2) and eight successes out of ten, the posterior is Beta(10,4) with mean 10/14. The next outcome is still binary, so its uncertainty is much larger than uncertainty in the posterior mean alone.

### Computation and diagnostics

Conjugacy gives an exact reference against which numerical algorithms can be checked. MCMC constructs dependent draws with the desired stationary distribution. A symmetric Metropolis proposal accepts with min(1,posterior(new)/posterior(old)); rejected proposals must retain the current state in the chain. Warmup helps the algorithm adapt or reach useful regions, but discarding a fixed prefix does not prove convergence. Multiple chains, rank-normalized split R-hat, bulk/tail effective sample size and sampler-specific diagnostics interrogate different failures.

Bayesian workflow also checks the model itself: simulate data from the prior, fit, then simulate posterior predictive data and compare quantities relevant to the decision. A satisfactory sampler proves neither a plausible likelihood nor adequate predictive performance.

## Methods, mechanisms, and limits

### stat-18-01

**Prior distributions**

A prior assigns probability to parameter values before the current likelihood. It is scale-dependent and can encode regularization or substantive knowledge. Assess consequences on observable outcomes, not just parameter density plots.

### stat-18-02

**Likelihoods**

A likelihood evaluates the observed data as a function of model parameters. It can be multiplied by constants independent of those parameters for posterior calculation, but marginal likelihood comparisons need proper normalization.

### stat-18-03

**Posterior distributions**

The posterior conditions prior uncertainty on observed evidence through the likelihood. It is a probability distribution given the model, not an unconditional guarantee of scientific truth or frequentist coverage.

### stat-18-04

**Conjugate models**

Conjugate prior-likelihood pairs preserve a convenient posterior family. They support transparent calculations and algorithm checks. Convenience should not force a scientifically implausible likelihood or prior.

### stat-18-05

**Weakly informative priors**

Use realistic scales to regularize extreme estimates while allowing plausible values. A very wide normal prior can imply absurd outcome predictions, so weak informativeness should be judged on the observational scale.

### stat-18-06

**Prior elicitation**

Translate expert statements about probabilities, quantiles or plausible effects into distributional constraints. Elicit uncertainty and dependence, not just a best guess. Check whether implied events match the expert's intended meaning.

### stat-18-07

**Prior predictive checks**

Draw parameters from the prior and then simulate observations. Impossible values or extreme frequencies expose prior-likelihood incompatibility before fitting. This is a model-design check, not a test against observed posterior fit.

### stat-18-08

**Posterior predictive distributions**

Integrate future-outcome distributions over posterior parameter uncertainty. Both parameter uncertainty and irreducible observation variability enter. Plugging in a posterior mean generally omits one source of uncertainty.

### stat-18-09

**Posterior predictive checks**

Compare replicated data with observed summaries such as tails, zeros or subgroup patterns. A model can fit the mean while missing extremes. Choose discrepancies tied to the decision rather than a single universal pass score.

### stat-18-10

**Hierarchical Bayesian models**

Let group parameters arise from a shared distribution, producing partial pooling. Hyperpriors govern pooling and between-group variation. Sparse groups can be strongly prior-sensitive even when the overall dataset is large.

### stat-18-11

**Empirical Bayes**

Estimate prior hyperparameters from observed groups before computing shrinkage. This can be computationally convenient but plug-in analysis may understate hyperparameter uncertainty relative to a full hierarchical model.

### stat-18-12

**Bayesian shrinkage**

Combine noisy local estimates with common structure through the prior. Shrinkage magnitude should reflect relative uncertainty. Inappropriate common structure can erase genuine group differences and should be checked predictively.

### stat-18-13

**Credible intervals**

A credible interval contains a specified posterior probability under the chosen model. Equal-tail and highest-density intervals can differ for skewed or multimodal posteriors. Do not equate it automatically with frequentist coverage.

### stat-18-14

**Bayesian decision analysis**

Average action losses over the posterior and choose the smallest expected loss. Posterior probability thresholds follow consequence ratios. Robust decisions may require sensitivity to prior and likelihood alternatives.

### stat-18-15

**Bayes factors**

Compare integrated likelihoods under proper model priors. Bayes factors can change strongly with prior scale because they average fit over parameter space. A good posterior within each model does not eliminate this sensitivity.

### stat-18-16

**Bayesian model averaging**

Average predictions or estimands across models using posterior model weights. This propagates uncertainty among included models only. If all models share a structural error, averaging does not remove it.

### stat-18-17

**Markov chain Monte Carlo**

Construct a Markov chain targeting the posterior and retain its dependence in uncertainty assessment. More iterations help only if the chain explores relevant regions. Disconnected modes may remain invisible to one chain.

### stat-18-18

**Metropolis–Hastings**

Propose a move and correct using the target-density ratio and proposal asymmetry. Symmetric proposals simplify the ratio. Store repeated states after rejection; keeping accepted moves alone changes the sampled distribution.

### stat-18-19

**Gibbs sampling**

Sample each variable or block from its full conditional distribution. Strong posterior correlation can make coordinate updates mix slowly. Conjugate conditionals simplify sampling but do not guarantee efficient exploration.

### stat-18-20

**Hamiltonian Monte Carlo**

Augment parameters with momentum and use gradients to simulate trajectories, then correct discretization error. HMC benefits smooth continuous posteriors but can struggle with funnels, poor scaling and discontinuities.

### stat-18-21

**No-U-Turn sampling**

NUTS adapts HMC trajectory length to avoid redundant retracing. Warmup also tunes step size and metric. Divergences indicate potentially biased exploration and need model or geometry investigation, not merely more draws.

### stat-18-22

**Variational inference**

Optimize a tractable approximation to the posterior. Restricted families can miss correlations or modes and understate uncertainty. Fast optimization convergence says little about approximation adequacy without diagnostic comparisons.

### stat-18-23

**Laplace approximation**

Expand log posterior near a mode to second order and use inverse curvature as Gaussian covariance. Skewness, boundaries and multiple modes undermine this local approximation even if the optimizer finds a good mode.

### stat-18-24

**Approximate Bayesian computation**

Simulate data at proposed parameters and retain or weight proposals whose summaries resemble observations. ABC depends on summary informativeness and tolerance. Smaller tolerance reduces approximation bias but may be computationally expensive.

### stat-18-25

**Simulation-based inference**

Use simulator-generated pairs to learn likelihood, likelihood-ratio or posterior approximations. Coverage depends on simulator validity and training support. Validate with held-out simulations and examine misspecification against real observations.

### stat-18-26

**MCMC diagnostics**

Check multiple chains, effective sample sizes, Monte Carlo errors and sampler-specific failures. R-hat near one is necessary evidence in common workflows but not a proof all modes were explored.

### stat-18-27

**Simulation-based calibration**

Repeatedly draw parameters and data from the model, fit, and assess posterior-rank calibration. SBC checks the inference pipeline under the simulated model. It does not validate that model against the world.

### stat-18-28

**Bayesian nonparametrics**

Use priors over flexible objects whose effective complexity can increase with data. Nonparametric does not mean assumption-free or parameter-free; the prior still constrains smoothness, clustering or tail behavior.

### stat-18-29

**Dirichlet process models**

A Dirichlet process is a random probability measure with concentration and base distribution. Its draws are discrete; mixture constructions can yield continuous observations. Inferred cluster counts can be sensitive to the model and prior.

### stat-18-30

**Gaussian processes**

Specify a joint Gaussian law for function values through a mean and kernel. Conditioning gives predictions and uncertainty. Kernel choice encodes smoothness and structure, while standard exact fitting has cubic training cost in sample size.

## Worked Python demonstrations

Complete offline program: [chapter_18.py](../examples/chapter_18.py). It uses tiny fixtures, no downloads, and assertions that check the expected observations. Run from the repository root:

```text
python courses/statistics-ml/examples/chapter_18.py
```

### An exact posterior gives a calibration target

The prior contributes two successes and two failures in beta-binomial algebra, producing Beta(10,4). Its mean is about .714, below the observed .8 because of prior shrinkage. The interval quantifies uncertainty about p; a future binary draw has larger variance because it also includes trial noise.

### Rejections are part of a Markov chain

The Metropolis chain targets a standard normal density using a symmetric random-walk proposal. The test checks approximate mean and variance with loose simulation tolerances and verifies repeated states occur. This is a transparent sampler demonstration, not a substitute for modern multichain diagnostics in a complex posterior.

### A kernel makes an uncertainty assumption

Gaussian conditioning uses a squared-exponential covariance plus observation noise. The latent variance at x=3 exceeds that at .5 because it is farther from observed inputs. That behavior follows from the selected kernel and training support; it does not guarantee calibrated uncertainty under a different generating process.

### Complete executable example

```python
import numpy as np
from scipy import stats

def conjugacy_and_prediction():
    prior_a,prior_b=2.,2.;successes,trials=8,10
    a,b=prior_a+successes,prior_b+trials-successes
    mean=a/(a+b);interval=stats.beta.ppf([.025,.975],a,b)
    assert np.isclose(mean,5/7) and interval[0]<mean<interval[1]
    future_variance=mean*(1-mean)
    parameter_variance=stats.beta.var(a,b)
    assert future_variance>parameter_variance
    print("Posterior mean/interval:",mean,interval,"next binary variance:",future_variance)

def metropolis_reference():
    rng=np.random.default_rng(18);current=0.;chain=[];accepted=0
    for _ in range(12000):
        proposal=current+rng.normal(scale=1.)
        log_ratio=-.5*proposal**2+.5*current**2
        if np.log(rng.random())<min(0.,log_ratio):
            current=proposal;accepted+=1
        chain.append(current)
    draws=np.array(chain[2000:])
    assert abs(draws.mean())<.12 and abs(draws.var()-1)<.18
    assert len(set(chain))<len(chain)
    print("MH normal mean/variance/acceptance:",draws.mean(),draws.var(),accepted/len(chain))

def gaussian_process_conditioning():
    train=np.array([0.,1.]);test=np.array([.5,3.]);y=np.array([0.,1.])
    kernel=lambda a,b: np.exp(-.5*(a[:,None]-b[None,:])**2)
    k=kernel(train,train)+.01*np.eye(2)
    cross=kernel(test,train)
    mean=cross@np.linalg.solve(k,y)
    variance=np.diag(kernel(test,test)-cross@np.linalg.solve(k,cross.T))
    assert np.all(variance>=0) and variance[1]>variance[0]
    print("GP means:",mean,"latent variances:",variance)

def main():
    conjugacy_and_prediction();metropolis_reference();gaussian_process_conditioning()

if __name__ == "__main__":
    main()
```

## Data science interview discussions

**Interview: Why can a weak prior have a strong effect?** Weakness is relative to the likelihood information and parameter scale. Sparse data, separation or weak identification can leave substantial posterior sensitivity. Examine prior predictive implications and alternative defensible scales.

**Interview: R-hat is satisfactory. Is the analysis valid?** It supports mixing consistency across the sampled chains, but cannot rule out missed common modes, inadequate effective sample size, computational pathologies or model misspecification. Check sampler diagnostics and predictive fit separately.

**Interview: When prefer variational inference over MCMC?** When computational needs justify approximation and its errors can be assessed for the intended decision. Compare uncertainty and predictions on smaller exact or MCMC references; a faster point estimate alone does not validate posterior tails.

## Primary sources and official APIs

- [Stan posterior analysis and diagnostics](https://mc-stan.org/docs/reference-manual/analysis.html).

- [Stan prior and posterior predictive checks](https://mc-stan.org/docs/stan-users-guide/posterior-predictive-checks.html).

## Reading connections

[Previous chapter](17-causal-estimation-heterogeneous-effects-and-policy-learning.md) | [Book contents](../README.md) | [Next chapter](19-statistical-learning-and-classical-supervised-models.md)
