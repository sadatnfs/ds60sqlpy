# 17. Causal Estimation, Heterogeneous Effects, and Policy Learning

Book: **Statistics and Machine Learning for Data Scientists End To End**. Chapter ID: `statistics-017`. Tutorial mode; all examples and interview answers are fully worked.

## The decision and the mental model

Once a causal effect is identified, estimation still requires care. Outcome regression estimates what would happen under each intervention; propensity weighting reconstructs a comparison population through assignment probabilities. Both depend on measured confounding, consistency and overlap. A sophisticated estimator cannot compensate for an unidentified target.

### Derive the augmented inverse-probability estimator

Write e(X)=P(A=1|X) and m_a(X)=E[Y|A=a,X]. For each observation, form phi=m1(X)-m0(X)+A*(Y-m1(X))/e(X)-(1-A)*(Y-m0(X))/(1-e(X)). Average phi to estimate the ATE. If the outcome models are correct, the residual terms have conditional mean zero. If the propensity model is correct, inverse-weighted residuals correct errors in the outcome predictions. This explains the double-robust consistency property, under the remaining identification and regularity assumptions.

Double robustness does not mean that two poor models cancel automatically, or that ordinary confidence intervals work at any sample size. With flexible nuisance estimates, asymptotic inference often requires product-rate conditions and cross-fitting. Fit nuisance models on other folds, calculate scores on held-out rows, then combine. Cross-fitting reduces overfitting bias but cannot create overlap or observe hidden confounders.

### Heterogeneity and decisions

A conditional average effect is estimated from comparisons of groups, not both potential outcomes of each person. Uplift ranking should be evaluated on independent randomized or properly adjusted data. A policy that treats whenever estimated benefit exceeds cost must be assessed for utility, uncertainty, capacity and harms. Treatment response prediction and treatment-effect prediction are different learning tasks.

## Methods, mechanisms, and limits

### stat-17-01

**Outcome regression**

Fit E[Y|A,X], predict each unit under both treatment values, and average their difference over the target population. Extrapolation into sparse treatment-covariate combinations can dominate the result despite good overall predictive fit.

### stat-17-02

**G-computation**

The g-formula averages modeled outcome distributions over intervention-defined covariate histories. In longitudinal settings, simulate time-varying variables in causal order. Ordinary adjustment for a treatment-affected confounder can target the wrong quantity.

### stat-17-03

**Propensity scores**

The propensity score is treatment probability conditional on pretreatment covariates. It is a balancing score under the relevant model, not a measure of outcome risk. Assess overlap and balance rather than classification accuracy alone.

### stat-17-04

**Propensity score matching**

Match units with comparable assignment scores and define the resulting target population. Calipers and discarded units alter the estimand. Matching does not remove unmeasured confounding, and matched-set dependence affects uncertainty.

### stat-17-05

**Inverse-probability treatment weighting**

Weight treated by \(\frac{1}{e}\) and controls by \(\frac{1}{1-e}\) for an ATE target. Stabilization or normalization changes finite-sample behavior. Extreme scores indicate weak support and high variance.

### stat-17-06

**Overlap weighting**

Weight treated by 1-e and controls by e, emphasizing covariate regions with treatment equipoise. This improves stability but targets an overlap population, not automatically the full-population ATE.

### stat-17-07

**Entropy balancing**

Choose weights satisfying prespecified covariate moment constraints, often minimizing relative entropy from base weights. Exact balance on chosen moments does not imply balance on all relevant nonlinear features or hidden confounders.

### stat-17-08

**Covariate balance diagnostics**

Compare weighted or matched covariate distributions using standardized differences, tails and overlap. Significance tests confound balance with sample size. Good measured balance supports the adjustment procedure but does not prove causal exchangeability.

### stat-17-09

**Augmented inverse-probability weighting**

Combine outcome contrasts with propensity-weighted residual corrections. The score has the double-robust property under identification assumptions. Use appropriate covariance and cross-fitting when nuisance learners are adaptive.

### stat-17-10

**Doubly robust estimation**

Consistency can survive misspecification of one nuisance component if the other is correct and remaining conditions hold. This is not robustness to unmeasured confounding, no overlap or both models being wrong.

### stat-17-11

**Targeted maximum likelihood estimation**

Update an initial outcome estimate along a targeted fluctuation that solves an estimand-related score equation. TMLE preserves relevant outcome constraints and supports influence-function inference when regularity and nuisance conditions are satisfied.

### stat-17-12

**Double/debiased machine learning**

Use orthogonal scores that are locally insensitive to nuisance-estimation errors, usually with cross-fitting. The theory requires suitable convergence rates and identification; fitting two arbitrary models is not by itself double machine learning.

### stat-17-13

**Cross-fitting**

Train nuisance functions outside the fold where their scores are evaluated. Keep all rows from a dependent unit together. The full procedure still needs an independent comparison or appropriate inference for the final target.

### stat-17-14

**Marginal structural models**

Use longitudinal treatment and censoring weights to estimate a marginal intervention model under sequential exchangeability and positivity. Products of many weights can become unstable, exposing limited support for sustained regimes.

### stat-17-15

**Structural nested models**

Model how treatment at each time changes potential outcomes after accounting for later treatment rules. These models address time-varying causal effects using assumptions different from a standard outcome regression on observed histories.

### stat-17-16

**G-estimation**

Estimate structural nested parameters by making treatment innovations independent of suitably adjusted counterfactual outcomes under the assignment assumptions. Valid moment restrictions and timing are central; the method does not remove hidden confounding automatically.

### stat-17-17

**Mediation analysis**

Define a mediator intervention and target direct or indirect effects explicitly. Treatment-induced mediator-outcome confounding complicates identification. A product of two regression coefficients is causal only under restrictive conditions.

### stat-17-18

**Direct and indirect effects**

Natural effects involve cross-world counterfactual relationships, while interventional effects use alternative mediator distributions. The chosen definition determines assumptions and interpretation. A total effect need not split uniquely without that choice.

### stat-17-19

**Causal forests**

Use trees designed for treatment-effect heterogeneity with honest splitting or other bias controls. Ordinary prediction forests on outcomes do not automatically estimate causal heterogeneity. Overlap, confounding adjustment and valid uncertainty remain necessary.

### stat-17-20

**S-learners**

Fit one response model containing treatment and covariates, then subtract counterfactual predictions. Strong regularization can suppress treatment interactions and hide heterogeneity, particularly when the treatment signal is weak.

### stat-17-21

**T-learners**

Fit separate response models in each arm, then subtract their predictions. Unequal group sizes create unequal nuisance precision. Sparse groups can yield unstable differences even if the larger arm fits well.

### stat-17-22

**X-learners**

Impute treatment effects using arm-specific outcome models and combine effect models with appropriate weights. It can exploit imbalance, but performance depends on nuisance quality and the heterogeneity structure.

### stat-17-23

**R-learners**

Residualize Y by E[Y|X] and A by e(X), then fit effects through their residual relationship. The R-loss separates baseline prediction from heterogeneity, while small treatment residuals reveal weak overlap.

### stat-17-24

**Uplift modeling**

Learn incremental response to an action rather than baseline response propensity. Specify treatment cost and eligibility. A high-response segment can have low uplift if its members would respond without treatment.

### stat-17-25

**Qini and uplift curves**

Rank by predicted effects and compare cumulative treatment-control outcomes on independent data. Allocation imbalance and observational confounding require adjustment. Curve area depends on conventions and should be paired with policy-value interpretation.

### stat-17-26

**Policy learning**

Optimize an intervention rule within a feasible policy class using estimated effects or robust value scores. Restrict complexity and evaluate out of sample to avoid learning policies that exploit estimation noise.

### stat-17-27

**Off-policy evaluation**

Estimate a new policy's value from data generated by a logging policy. Known or credible propensities, support and correct time order are essential. Rare actions create high-variance importance weights.

### stat-17-28

**Sensitivity to unmeasured confounding**

Vary the strength or structure of hidden common causes and identify decision tipping points. Sensitivity parameters need domain meaning. A single robustness number does not validate exchangeability.

### stat-17-29

**Causal discovery**

Infer candidate graphs from conditional independences, functional restrictions or interventions. Markov equivalence often leaves directions unresolved. Hidden variables, selection and faithfulness violations limit what observational discovery can establish.

<!-- detailed-case-studies:start -->

## Extended case studies and scientific reasoning

### Case study: trace an AIPW score by hand

For one treated observation with outcome eight, estimated treatment probability .5, predicted treated outcome six and predicted control outcome three, the score is \(6-3+\frac{8-6}{0.5}=7\). For one control observation with outcome four and the same nuisance predictions, the score is \(6-3-\frac{4-3}{0.5}=1\). Their average is four. The outcome model contributes a baseline contrast three, and observed residuals adjust that contrast using assignment probabilities.

Each score is not an individual treatment effect. It can lie outside the outcome range and can be noisy because inverse probabilities amplify residuals. Averaging many appropriately sampled scores estimates the population target under assumptions. Treating a large score as proof that one person benefits greatly would confuse an estimating-equation contribution with a personal causal quantity.

With true propensity e and estimated propensity e_hat, let \(\delta_{a}=m_{\mathrm{hat\_a}}-m_{a}\) be outcome-model error. Conditional bias in the AIPW score can be written as (e_hat-e)*[delta_1/e_hat+delta_0/(1-e_hat)]. This product structure explains double robustness: either correct nuisance component makes this expression zero. It also explains failure when both errors are substantial, especially near propensity boundaries.

Cross-fitting helps control the relationship between learned nuisance errors and evaluation noise. It does not make arbitrary slow or inconsistent learners satisfy the asymptotic conditions. In a practical report, include overlap, effective weight behavior, nuisance diagnostics, score tails and sensitivity to modeling choices. A standard error computed from the score's sample variability is meaningful only when the assumptions supporting that approximation hold.

### Case study: overlap changes the population you can answer for

A treatment is almost universal among high-risk units and rare among low-risk units. An ATE estimator weights the unusual high-risk controls and low-risk treated units heavily. Those few records can dominate the comparison. Trimming them may stabilize the calculation but discards the very observations used to represent unsupported counterfactuals.

Overlap weighting targets units whose treatment probabilities are nearer equipoise. That can be a sensible decision population, particularly when the real choice is uncertain only for such units. But its effect need not equal the full-population ATE. State the new target population explicitly and quantify which units lost influence. A more stable number is not automatically a better estimate of the original question.

Matching has a similar target issue. Calipers, replacement and unmatched exclusions alter which treated or control units are represented. Balance diagnostics should inspect meaningful distributions and nonlinear terms, not just average propensity scores. Since the propensity is one-dimensional, similar scores do not guarantee every finite-sample covariate is balanced without checking.

### Case study: time-varying confounding affected by prior treatment

A system receives preventive maintenance each week. Current wear predicts both next week's maintenance and failure, but previous maintenance also reduces wear. Adjusting for current wear in an ordinary regression may block part of previous treatment's effect while trying to control confounding for current treatment.

Marginal structural models use sequential treatment probabilities to construct a weighted comparison of treatment histories under specified regimes. The identifying assumption is sequential exchangeability given the observed history, together with sequential positivity and consistency. Long treatment histories can make products of inverse probabilities extremely variable, revealing that some sustained regimes have little support.

The g-formula takes another route: model how wear and outcomes evolve under each history, simulate the proposed regime and average. Structural nested models and g-estimation target causal contrasts through different modeling restrictions. These methods answer related longitudinal questions but do not eliminate the need to observe the confounding history or define feasible treatment strategies.

### Case study: evaluating a learned policy without rewarding overfitting

A flexible effect model assigns the highest estimated benefit to a small segment. Selecting that segment using noisy effects creates a winner's-curse problem. Evaluating the same segment on the same data can produce an impressive uplift curve even when the true effect is constant.

Use separate policy-learning and evaluation observations, ideally randomized with logged probabilities. Evaluate net value against treating none, treating all where feasible, and a simple targeting rule. Include treatment cost and any capacity constraint. If the policy changes who receives labels or who remains observable, future training data become policy-dependent and need feedback-loop management.

Off-policy evaluation requires that the historical policy sometimes chose every action the new policy would choose in relevant contexts. A deterministic logger can leave no support for alternate actions. Importance weighting cannot estimate an unobserved action's value from zero-probability logs. Model-based extrapolation may still be considered, but its assumptions must be visible and uncertainty should reflect that evidence gap.

<!-- detailed-case-studies:end -->

## Worked Python demonstrations

Complete offline program: [chapter_17.py](../examples/chapter_17.py). It uses tiny fixtures, no downloads, and assertions that check the expected observations. Run from the repository root:

```text
python courses/statistics-ml/examples/chapter_17.py
```

### See the residual correction work

The toy population has effect three and exact treatment balance within each covariate stratum. Deliberately wrong outcome predictions suggest effect one, but the correct propensity-weighted residual terms restore three. Exact recovery is a property of this constructed fixture, not a guarantee that either estimated nuisance model is correct in real data.

### Keep prediction and score rows separate

Each of three folds receives predictions from a line fitted on the other folds. The exact linear fixture is predicted correctly, and an explicit index assertion proves disjointness. This illustrates the cross-fitting boundary; causal inference would additionally require the full score and its assumptions.

### Convert effects into a policy

With action cost one, only effects two and four produce positive net value. Treating those two of four eligible people yields net value one per eligible person, outperforming treating everyone in this known-effect fixture. Estimated effects require separate policy evaluation and uncertainty.

### Complete executable example

```python
import numpy as np

def aipw_and_balance():
    x=np.repeat([0.,1.],4)
    a=np.tile([0.,0.,1.,1.],2)
    y=2*x+3*a+np.tile([-1.,1.,-1.,1.],2)
    e=np.full(8,.5)
    wrong_m0=np.zeros(8);wrong_m1=np.ones(8)
    score=wrong_m1-wrong_m0+a*(y-wrong_m1)/e-(1-a)*(y-wrong_m0)/(1-e)
    assert np.isclose(score.mean(),3.)
    assert np.isclose(np.average(x[a==1],weights=1/e[a==1]),np.average(x[a==0],weights=1/(1-e[a==0])))
    print("AIPW with deliberately wrong outcome models:",score.mean())

def cross_fitted_nuisance():
    x=np.arange(12,dtype=float)
    y=1+2*x
    prediction=np.empty_like(y)
    folds=np.arange(len(y))%3
    for fold in range(3):
        train=folds!=fold;test=~train
        assert not set(np.flatnonzero(train)) & set(np.flatnonzero(test))
        beta=np.polyfit(x[train],y[train],1)
        prediction[test]=np.polyval(beta,x[test])
    assert np.allclose(prediction,y)
    print("Cross-fitted nuisance prediction maximum error:",np.max(np.abs(prediction-y)))

def policy_value():
    effect=np.array([-.5,.5,2.,4.]);cost=1.
    policy=effect>cost
    value=np.mean(policy*(effect-cost))
    assert policy.tolist()==[False,False,True,True] and value==1.
    assert value>np.mean(effect-cost)
    print("Treat:",policy,"incremental net value per eligible unit:",value)

def main():
    aipw_and_balance();cross_fitted_nuisance();policy_value()

if __name__ == "__main__":
    main()
```

## Data science interview discussions

**Interview: What exactly is doubly robust?** The estimating equation can remain consistent when either the outcome nuisance model or the propensity nuisance model is correct, assuming identification and regularity. Both wrong, hidden confounding, insufficient overlap or inappropriate dependence can still invalidate the result.

**Interview: Why cross-fit rather than fit nuisance models on all rows?** Evaluating residual scores on the same rows used for flexible fitting can couple estimation errors to observed noise. Cross-fitting separates these roles and supports orthogonal-score theory. It does not replace genuine external validation for policy decisions.

**Interview: Why not target the highest predicted responders?** They may respond without treatment. Targeting should consider incremental benefit minus cost and constraints, then verify policy value on independent evidence.

## Primary sources and official APIs

- [Chernozhukov et al., Double/Debiased Machine Learning](https://arxiv.org/abs/1608.00060).

- [Hernán and Robins, longitudinal causal methods](https://miguelhernan.org/whatifbook).

## Reading connections

[Previous chapter](16-quasi-experiments-and-causal-study-designs.md) | [Book contents](../README.md) | [Next chapter](18-bayesian-statistics-and-probabilistic-modeling.md)
