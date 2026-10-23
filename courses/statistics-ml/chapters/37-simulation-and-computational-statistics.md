# 37. Simulation and Computational Statistics

Book: **Statistics and Machine Learning for Data Scientists End To End**. Chapter ID: `statistics-037`. Tutorial mode; all examples and interview answers are fully worked.

## The decision and the mental model

Simulation approximates consequences of a model by generating artificial observations or trajectories. It is especially useful when a quantity is mathematically defined but difficult to integrate or solve directly. The artificial output is evidence about the implemented model, not automatically about the real system. Separate uncertainty in simulation parameters, randomness within the simulated system and numerical Monte Carlo error.

### An average is an estimator with its own error

To estimate \(\mu=\mathbb{E}[f(X)]\), draw X_1,...,X_n from the target distribution and average f(X_i). With independent draws and finite variance \({\sigma_{f}}^{2}\), the Monte Carlo standard error is approximately \(\frac{s_f}{\sqrt{n}}\). Halving this numerical error generally needs four times as many independent draws. More simulation can reduce Monte Carlo error while leaving a badly chosen input distribution or model structure unchanged.

A fixed seed makes a demonstration repeatable, but it is not a statistical guarantee. Keep independent streams or a deliberate common-random-number design when comparing alternatives. If a simulation uses autocorrelated MCMC output, the independent-draw standard error is inappropriate and must account for dependence. Rare events can produce zero observed occurrences in a small run without having zero probability.

### Change the computation without changing the target

Variance reduction uses mathematical structure to obtain a more precise estimator per unit of work. A control variate subtracts a centered quantity with known expectation. Importance sampling changes the sampling distribution and restores the target through likelihood ratios. Antithetic sampling pairs negatively related draws. Each method needs its own validity and support conditions; a lower observed variance is not enough if the estimator became biased for an unintended target.

For a control variate g with known mean m_g, estimate E[f] by the mean of f(X)-beta*(g(X)-m_g). The expectation remains E[f] for fixed beta. The variance-minimizing coefficient is \(\frac{\operatorname{Cov}(f,g)}{\operatorname{Var}(g)}\), when these quantities exist. Estimating beta from the same finite sample introduces details worth handling deliberately in formal uncertainty analysis. The example uses the analytically known coefficient for a simple uniform distribution.

### Simulate the decision process, not only a histogram

A queue simulation must represent arrivals, service completion, resource availability and the observation window. An agent-based model adds heterogeneous entities and interaction rules. A system-dynamics model tracks aggregate stocks and flows. The right representation depends on which mechanism affects the decision. Calibration to one aggregate statistic can leave multiple incompatible mechanisms, so validate outputs and intermediate behavior against independent observations.

### Information and optimization

Simulation can compare policies, quantify sensitivity and estimate the value of additional information. Use the same scenario distribution for alternatives and preserve the timing of what a decision-maker knows. A perfect-information policy sees the uncertain state before acting; an ordinary policy does not. The difference in achievable expected value bounds what it is worth paying to learn that state, under the model. When searching many policies on noisy simulations, retain independent evaluation runs to avoid selecting a lucky winner.

## Methods, mechanisms, and limits

### stat-37-01

**Monte Carlo simulation**

Monte Carlo simulation estimates expectations, probabilities or other quantities through repeated random draws under a specified model. The target, sampling distribution and estimator should be written explicitly. Independent draws with finite variance support familiar standard-error calculations, but heavy tails or dependence can break them. Increasing the draw count improves numerical precision only for the model being simulated, not its substantive correctness.

### stat-37-02

**Monte Carlo error analysis**

Monte Carlo error is the numerical uncertainty from using finitely many simulation draws. For independent finite-variance outputs, standard error scales as one over the square root of sample size. Report it separately from uncertainty in model parameters or real-world variation. A narrow Monte Carlo interval around a misspecified model's expectation can create false confidence if those other uncertainty sources are omitted.

### stat-37-03

**Importance sampling**

Importance sampling draws from proposal q instead of target p and weights outputs by p(x)/q(x). The proposal must have support wherever the target integrand contributes. A poor proposal can create extreme weights and infinite or enormous variance. Inspect weight concentration and effective sample-size diagnostics, while recognizing that one reassuring diagnostic cannot prove the absence of unseen tail contributions.

### stat-37-04

**Rejection sampling**

Rejection sampling accepts a proposal draw with probability p(x)/(M*q(x)) when M bounds that ratio. Accepted draws follow the target under the stated conditions. A valid envelope is essential; underestimating M changes the distribution. Efficiency deteriorates when the proposal poorly matches the target, particularly in high dimensions, so record acceptance rate and justify the bound.

### stat-37-05

**Sequential Monte Carlo**

Sequential Monte Carlo propagates weighted particles through a sequence of distributions, reweighting as new information arrives and resampling when needed. Weight degeneracy means a few particles dominate; resampling combats it but can reduce diversity. Proposal choice, resampling schedule and rejuvenation steps affect accuracy. Track effective sample size and repeated-run stability rather than treating a large nominal particle count as sufficient.

### stat-37-06

**Particle filtering**

Particle filtering applies sequential Monte Carlo to dynamic hidden states. Particles are propagated through the transition model and weighted by observation likelihood. It handles nonlinear or non-Gaussian settings beyond a basic Kalman filter but can struggle with informative observations or high-dimensional state. The model and proposal determine whether particles reach plausible regions before weights collapse.

### stat-37-07

**Quasi-Monte Carlo**

Quasi-Monte Carlo replaces independent random points with low-discrepancy designs that cover integration space more evenly. Smooth integrands and effective low dimension can yield substantial gains, but discontinuities and poor variable ordering can reduce them. Deterministic designs do not supply an ordinary independent-sample standard error. Randomized scrambles allow replicated uncertainty assessment under a different design.

### stat-37-08

**Control variates**

Control variates subtract a correlated quantity whose expectation is known, preserving the target while reducing variance. A strong positive correlation permits a large reduction with an appropriate coefficient. The known expectation must actually be correct; substituting an estimated external value adds uncertainty. Multiple controls can help, but unstable coefficient estimation or weak correlations can undermine the expected benefit.

### stat-37-09

**Antithetic variates**

Antithetic variates pair draws so their transformed outputs are negatively correlated, such as U and 1-U for suitable monotone functions. The average can have lower variance than independent draws of the same count. Negative correlation of inputs does not guarantee negative correlation of every nonlinear output. Assess the covariance under the actual integrand rather than assuming antithetic pairing always helps.

### stat-37-10

**Stratified Monte Carlo**

Stratified Monte Carlo partitions the sampling space into regions and combines within-region estimates using known probabilities. Allocating more draws to high-variance or high-impact strata can improve precision. Every contributing stratum needs coverage and correct weights. Using equal averages across unequal-probability strata changes the target, so record the allocation and aggregation rule.

### stat-37-11

**Rare-event simulation**

Rare-event simulation targets probabilities too small for ordinary simulation to observe often. Importance sampling, splitting or specialized conditional methods can focus effort on relevant trajectories. The estimator must correct for the changed sampling design. Zero observed failures in a naive run is not a zero-risk estimate with no uncertainty, and extrapolating rare-event behavior requires careful model validation.

### stat-37-12

**Discrete-event simulation**

Discrete-event simulation advances the clock from one state-changing event to the next, such as an arrival or service completion. An event queue preserves chronological order and resource rules. Tie handling, warm-up periods and termination conditions can materially change results. Validate conservation identities such as arrivals equaling departures plus remaining customers before interpreting waiting-time statistics.

### stat-37-13

**Agent-based simulation**

Agent-based simulation models individual entities with attributes, behavioral rules and interactions. Aggregate patterns emerge from those local assumptions. Different rule sets can reproduce similar aggregate data, creating identification challenges. Validate micro-level behavior where possible and perform sensitivity analysis. A visually plausible animation is not evidence that the represented mechanism is correct or that policy extrapolations are reliable.

### stat-37-14

**System dynamics**

System dynamics represents aggregate stocks, flows and feedback loops, often through differential or difference equations. Delays and nonlinear feedback can generate oscillation or instability. Units must balance: a stock changes by a rate integrated over time. Calibration and sensitivity analysis should separate feedback assumptions from numerical-step artifacts, especially when a coarse time step changes stability.

### stat-37-15

**Digital twins**

A digital twin is a maintained computational representation linked to a real system for analysis or decisions. Its usefulness depends on synchronization, measurement quality, model scope and validation, not on the label. Distinguish a static simulator from a continuously updated operational representation. Document which interventions the twin can support credibly and where extrapolation or stale inputs make its advice unreliable.

### stat-37-16

**Simulation metamodels**

A simulation metamodel approximates expensive simulator outputs with a cheaper statistical or machine-learning surrogate. Design points must cover the relevant decision space, and predictive uncertainty should reflect sparse regions. Optimizing the surrogate can exploit its errors, so verify proposed optima with the original simulator. Surrogate accuracy on average may be inadequate near a binding constraint or rare-event boundary.

### stat-37-17

**Global sensitivity analysis**

Global sensitivity analysis measures output changes across joint uncertainty in inputs, rather than one small local derivative at a fixed point. Screening, variance-based and distributional methods answer different questions. Dependence among inputs changes interpretation and experimental design. A parameter can have small average influence yet control an important tail event, so match the sensitivity target to the decision.

### stat-37-18

**Sobol indices**

Sobol indices decompose output variance into contributions from inputs and their interactions under a specified joint distribution, commonly independent inputs. A first-order index measures variation explained by one input alone; a total index includes its interactions. The indices depend on input ranges and distributions. They are not universal intrinsic importance scores, and dependent-input settings need modified definitions or methods.

### stat-37-19

**Value of information analysis**

Value-of-information analysis compares expected decision value with and without additional observations. Perfect information supplies an upper bound under the model, while sample information accounts for an imperfect proposed study. The decision is reoptimized after information arrives, so this is different from reducing prediction error alone. Study cost, delay and model uncertainty affect whether acquiring information is worthwhile.

### stat-37-20

**Simulation optimization**

Simulation optimization searches decisions using noisy simulation estimates of performance. Common random numbers can improve comparisons when designed appropriately, and repeated evaluation distinguishes robust improvements from noise. Searching many candidates creates selection bias toward lucky estimates. Reserve independent final simulation runs, report uncertainty and check constraints under the same information timing used in deployment.

## Worked Python demonstrations

Complete offline program: [chapter_37.py](../examples/chapter_37.py). It uses tiny fixtures, no downloads, and assertions that check the expected observations. Run from the repository root:

```text
python courses/statistics-ml/examples/chapter_37.py
```

### Reduce numerical error without changing the integral

For U uniform on [0,1], E[\({U}^{2}\)]=1/3 and E[U]=1/2. Subtracting \(U-\frac{1}{2}\) with coefficient one preserves the target and strongly reduces variance because U and \({U}^{2}\) are correlated. A fixed seed makes the demonstration reproducible, while the printed standard errors describe independent Monte Carlo variation. Pairing U with 1-U gives exactly one-half for their average in the separate linear antithetic example.

### Check a queue through conservation

Three arrivals at 0,0.5,1.5 each need one unit of service on one server. Departures are 1,2,3 and waiting times before service are 0,0.5,0.5. At time 2.5, three have arrived and two have departed, leaving one in the system. This identity catches event-order and state-update mistakes before estimating more complicated queue statistics.

### Put a value on knowing the state

Two decisions have payoffs [8,-2] and [2,4] across equally likely states. Without knowing the state, both average three, so the best current value is three. Perfect information selects eight in the first state and four in the second, averaging six. EVPI is three, an upper bound on the value of information under this payoff model before acquisition costs.

### Complete executable example

```python
import numpy as np

def control_and_antithetic():
    rng=np.random.default_rng(37)
    u=rng.uniform(size=20000)
    raw=u**2;controlled=raw-(u-.5)
    raw_se=raw.std(ddof=1)/np.sqrt(len(u))
    controlled_se=controlled.std(ddof=1)/np.sqrt(len(u))
    assert abs(raw.mean()-1/3)<.01 and abs(controlled.mean()-1/3)<.01
    assert controlled_se<raw_se/3
    antithetic=(u+(1-u))/2
    assert np.allclose(antithetic,.5)
    print("Means and MC standard errors:",raw.mean(),controlled.mean(),raw_se,controlled_se)

def queue_conservation():
    arrivals=np.array([0.,.5,1.5]);service=np.array([1.,1.,1.])
    departure=[];previous=0.
    for arrival,duration in zip(arrivals,service):
        previous=max(arrival,previous)+duration;departure.append(previous)
    waits=np.array(departure)-arrivals-service
    assert np.allclose(departure,[1.,2.,3.]) and np.allclose(waits,[0.,.5,.5])
    observed_time=2.5
    arrived=np.sum(arrivals<=observed_time);left=np.sum(np.array(departure)<=observed_time)
    assert arrived==3 and left==2 and arrived-left==1
    print("Departures:",departure,"queue waits:",waits,"remaining at 2.5:",arrived-left)

def perfect_information():
    payoff=np.array([[8.,-2.],[2.,4.]]) # rows decisions, columns equally probable states
    current=np.max(payoff.mean(axis=1))
    informed=np.mean(np.max(payoff,axis=0))
    evpi=informed-current
    assert current==3. and informed==6. and evpi==3.
    print("Current value, perfect-information value, EVPI:",current,informed,evpi)

def main():
    control_and_antithetic();queue_conservation();perfect_information()

if __name__ == "__main__":
    main()
```

## Data science interview discussions

**Interview: Does a fixed random seed make a simulation result accurate?** It makes the exact pseudorandom sequence reproducible. Accuracy still depends on the estimator, draw count, model and input distribution. Report Monte Carlo error separately from substantive model uncertainty.

**Interview: Why can importance sampling be worse than ordinary Monte Carlo?** A poor proposal can produce highly variable or even non-integrable weights. Matching the region that contributes to the target, ensuring support and inspecting tail behavior are essential. Changing the sampling distribution is not a free precision improvement.

**Interview: Why validate a simulator at intermediate states?** Different incorrect mechanisms can produce the same aggregate average. Conservation checks, event traces and micro-level comparisons reveal errors hidden by final summaries and make policy extrapolation more credible.

## Primary sources and official APIs

- [Art Owen, Monte Carlo Theory, Methods and Examples](https://artowen.su.domains/mc/)

- [SciPy quasi-Monte Carlo documentation](https://docs.scipy.org/doc/scipy/reference/stats.qmc.html)

## Reading connections

[Previous chapter](36-optimization-and-operations-research.md) | [Book contents](../README.md) | [Next chapter](38-product-customer-marketing-and-business-analytics.md)
