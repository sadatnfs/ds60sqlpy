# 16. Quasi-Experiments and Causal Study Designs

Book: **Statistics and Machine Learning for Data Scientists End To End**. Chapter ID: `statistics-016`. Tutorial mode; all examples and interview answers are fully worked.

## The decision and the mental model

Quasi-experiments replace deliberate randomization with a specific source of plausibly exogenous variation. The design, not the estimator's name, carries the causal argument. A policy cutoff, a timing difference and a randomized encouragement support different local or population effects and require different falsification checks.

### Difference-in-differences

With treated/control groups and before/after periods, compute (treated_after-treated_before)-(control_after-control_before). The control trend substitutes for the treated group's unobserved untreated trend. Parallel trends concerns that counterfactual evolution, not equal starting levels. Observed parallel pretrends can support plausibility but cannot prove the unobserved postperiod condition. Anticipation, changing composition and concurrent policies can violate it.

### Instrumental variables

Let Z be a randomized encouragement, A treatment uptake and Y outcome. The Wald ratio [E(Y|Z=1)-E(Y|Z=0)]/[E(A|Z=1)-E(A|Z=0)] divides the outcome intention-to-treat effect by the treatment first stage. With independence, exclusion, relevance, monotonicity and well-defined interventions, it identifies a complier average effect. A tiny first stage amplifies noise and makes ordinary normal approximations unreliable. The exclusion restriction is a substantive pathway claim, not a statistical test the instrument can prove.

### Regression discontinuity

Compare outcome limits immediately above and below an assignment cutoff. Smooth counterfactual outcomes near the cutoff support a local effect when other changes do not occur at the same boundary. Narrow bandwidths reduce extrapolation bias but increase variance. Flexible global polynomials can behave badly near boundaries; local fits and bandwidth sensitivity are generally more interpretable.

## Methods, mechanisms, and limits

### stat-16-01

**Natural experiments**

An external event may create as-if random treatment variation. Explain the assignment mechanism and why agents cannot sort strategically into it. Calling an event natural does not establish exchangeability.

### stat-16-02

**Difference-in-differences**

Subtract a comparison group's change from the treated group's change. Define the group-time target and preserve clustering. Parallel untreated trends, no anticipation and stable composition are central identification conditions.

### stat-16-03

**Parallel trends**

Assume untreated outcome trends would match across the comparison groups, perhaps conditional on covariates. Equal levels are unnecessary. Preperiod tests have limited power and cannot certify postperiod counterfactual behavior.

### stat-16-04

**Event-study designs**

Estimate contrasts by time relative to adoption to inspect dynamics and possible anticipation. Simultaneous uncertainty and appropriate controls matter. Event-time coefficients from naive pooled designs can mix heterogeneous effects.

### stat-16-05

**Staggered adoption designs**

Different adoption cohorts contribute different group-time effects. Use not-yet-treated or never-treated controls only when appropriate, then aggregate with explicit weights. Already-treated controls can contaminate comparisons.

### stat-16-06

**Two-way fixed-effects limitations**

A two-way fixed-effects coefficient can combine comparisons with negative or problematic weights when treatment effects differ over cohorts or time. A familiar regression formula is not sufficient justification for the target.

### stat-16-07

**Triple differences**

Subtract a second difference-in-differences contrast across an additional dimension. This can remove a shared bias only under a corresponding triple-difference parallel-trend restriction. Extra differencing does not automatically strengthen validity.

### stat-16-08

**Synthetic control**

Choose untreated donor weights to reproduce treated preperiod behavior. Good prefit and a credible donor pool matter. Interference, postperiod donor shocks and extrapolation beyond the donor span threaten interpretation.

### stat-16-09

**Augmented synthetic control**

Add an outcome-model correction to synthetic-control weighting to reduce bias from imperfect prefit. The correction introduces modeling assumptions and can extrapolate. Inspect both weight behavior and the size of the augmentation.

### stat-16-10

**Synthetic difference-in-differences**

Combine unit and time weighting with a difference-in-differences structure. The method aims to balance preperiod patterns and remove additive effects. Validity depends on the panel structure and comparative untreated dynamics.

### stat-16-11

**Interrupted time series**

Fit preintervention trends and estimate level or slope changes after an interruption. Account for autocorrelation, seasonality and concurrent events. Without a credible counterfactual, a break is not uniquely attributable to the intervention.

### stat-16-12

**Regression discontinuity**

Use a treatment threshold to compare units near its cutoff. The estimand is local, not automatically a population ATE. Sorting, density discontinuities and other policy changes at the cutoff challenge validity.

### stat-16-13

**Sharp regression discontinuity**

Treatment switches deterministically at the running-variable cutoff. A discontinuity in outcome limits identifies a local treatment effect under continuity assumptions. Discrete scores can limit arbitrarily local comparisons.

### stat-16-14

**Fuzzy regression discontinuity**

Treatment probability jumps at the threshold but does not switch perfectly. Divide the outcome discontinuity by the uptake discontinuity under local IV assumptions. Weak uptake jumps create unstable estimates.

### stat-16-15

**Regression kink designs**

Use a slope change in a treatment-assignment rule rather than a level jump. Identification requires smooth counterfactual derivatives and restrictions on other slope changes. Derivative estimation is especially sensitive to bandwidth and noise.

### stat-16-16

**Instrumental variables**

An instrument changes treatment while affecting outcome only through allowed treatment pathways and remaining appropriately independent of confounders. Relevance alone is insufficient; a powerful predictor can be an invalid instrument.

### stat-16-17

**Two-stage least squares**

Project treatment onto instruments and exogenous controls, then regress outcome on projected treatment and controls. Correct IV covariance accounts for generated regressors; ordinary second-stage OLS standard errors are not appropriate.

### stat-16-18

**Local average treatment effects**

LATE targets compliers whose treatment changes with the instrument, under monotonicity and other IV assumptions. Different instruments can identify different complier populations and therefore legitimately different effects.

### stat-16-19

**Weak instrument diagnostics**

Assess first-stage strength with diagnostics appropriate to the instrument count, error structure and identification setting. A universal F>10 rule is not a proof. Weak-IV-robust intervals can be very wide or unbounded.

### stat-16-20

**Exclusion restrictions**

The instrument must have no disallowed direct or alternative pathway to outcome. An encouragement that also changes motivation, information or access may violate exclusion. Overidentification tests cannot validate all instruments together.

### stat-16-21

**Encouragement designs**

Randomize an offer or encouragement when actual uptake cannot be forced. ITT is identified by assignment; converting it to an uptake effect requires IV assumptions and a clearly described complier target.

### stat-16-22

**Placebo and falsification tests**

Test outcomes, times or thresholds where no effect should occur and examine covariate continuity or pretrends. Failure challenges the design; success leaves untested assumptions and should not be oversold as proof.

<!-- detailed-case-studies:start -->

## Extended case studies and scientific reasoning

### Case study: a policy change with a concurrent shock

A city adopts a transport policy and travel time falls from 40 to 30 minutes. A comparison city falls from 35 to 30. The before-after treated change is minus ten, while DiD is minus five. The comparison trend attributes half the reduction to changes that would have happened anyway. That attribution is the design assumption, not a fact produced by subtraction.

If the treated city also opens a major rail line at the same time, the remaining five-minute reduction may mix both interventions. Adding more historical periods helps describe pretrends but cannot isolate perfectly simultaneous shocks without additional variation or assumptions. Placebo dates and unaffected outcomes can challenge the story, while a second comparison region may reveal that the original control followed an unusual path.

For an event study, plot effects with uncertainty by event time and use a consistent reference. Preperiod coefficients can detect some anticipation or differential trends, but selecting the study because its pretrend p-values exceed .05 can itself create selection problems. Report the pattern, power to detect consequential violations, and sensitivity of the postperiod conclusion to plausible trend departures.

### Case study: staggered treatment creates changing controls

Suppose one group adopts in January and another in July. Before July, the later group may be an untreated comparison for the early group. After July, a standard two-way fixed-effects regression can also compare changes in the newly treated group with the already treated group. If the early group's treatment effect grows over time, its continued improvement is not an untreated counterfactual trend.

A single coefficient can therefore mix valid-looking early comparisons with contaminated later ones, sometimes through negative weights. This is not merely a standard-error problem. Cohort-time effects make the target explicit, with comparison groups chosen according to the identification assumptions. Aggregation can weight cohorts by population, calendar time or exposure duration, each answering a different question.

Choose the policy question before selecting an aggregate. A rollout forecast may care about effects by time since adoption, while an annual budget decision may care about calendar-time totals. Heterogeneity that is inconvenient for one summary can be the central information needed for the decision.

### Case study: a synthetic control with excellent prefit but weak evidence

Two untreated donor units have preperiod outcomes ten and fourteen, while the treated unit has twelve. Equal weights match the preperiod exactly. After intervention, donor outcomes become twelve and eighteen, giving a synthetic counterfactual fifteen. If treated outcome is nineteen, the estimated effect is four.

With only one preperiod, exact matching is easy and proves little. Many weight combinations or models may fit a short history. Longer preperiods, relevant predictors, donor plausibility and placebo comparisons help assess whether the synthetic combination reproduces the treated unit's untreated dynamics. Spillovers from the treatment into donor units invalidate their role as untreated references.

Augmentation can correct imperfect prefit using an outcome model, but a large correction signals that the result relies more heavily on extrapolation. Report donor weights, effective donor support, prefit quality, postperiod shocks and sensitivity to leaving donors out. A polished counterfactual line should not conceal that only a few units carry the estimate.

### Case study: strong relevance is not a valid instrument

A randomized email encourages use of a planning tool. It increases uptake and improves project completion. The email also contains practical planning advice. The advice supplies a direct path from encouragement to outcome, violating the exclusion restriction for tool usage. Randomizing the email identifies the effect of the email policy, but does not automatically identify the effect of tool use.

If the email affects uptake by only one percentage point, the Wald ratio divides by .01 and magnifies both noise and any small exclusion violation. Weak-instrument diagnostics identify limited first-stage information, but a strong first stage would not remove the direct advice pathway. Separate relevance, independence, exclusion and monotonicity in the argument.

Report the reduced-form outcome effect and first stage alongside any IV estimate. Describe who the compliers plausibly are and why the result may differ under another encouragement or population. Avoid calling a local effect the universal treatment effect merely because its units resemble an ATE.

<!-- detailed-case-studies:end -->

## Worked Python demonstrations

Complete offline program: [chapter_16.py](../examples/chapter_16.py). It uses tiny fixtures, no downloads, and assertions that check the expected observations. Run from the repository root:

```text
python courses/statistics-ml/examples/chapter_16.py
```

### Construct the missing trend

The treated group's outcome rises five while the control rises two. Assuming the control change is the valid untreated counterfactual gives an effect of three and a counterfactual treated after-value of 12. The arithmetic cannot test parallel trends because this fixture has only one preperiod.

### Divide by the first stage carefully

Encouragement raises uptake by .4 and outcome by 1.2, yielding a Wald estimate three. Holding the outcome change fixed while shrinking the first stage to .04 gives 30, illustrating denominator instability rather than a credible alternate causal conclusion.

### Recover a local jump in a known generating model

A six-point deterministic fixture contains a linear trend and a jump of two. Regression recovers the jump exactly. Real RD analysis needs bandwidth choice, uncertainty, sorting checks, support near the cutoff and a continuity argument; this calculation demonstrates the estimator's geometry only.

### Complete executable example

```python
import numpy as np

def difference_in_differences():
    treated=np.array([10.,15.]);control=np.array([7.,9.])
    did=np.diff(treated)[0]-np.diff(control)[0]
    assert did==3
    counterfactual=treated[0]+np.diff(control)[0]
    assert counterfactual==12
    print("Untreated treated-group counterfactual:",counterfactual,"DiD effect:",did)

def instrumental_variables():
    uptake=np.array([.2,.6]);outcome=np.array([4.,5.2])
    first_stage=uptake[1]-uptake[0]
    effect=(outcome[1]-outcome[0])/first_stage
    assert np.isclose(effect,3.)
    assert np.isclose((outcome[1]-outcome[0])/.04,30.)
    print("ITT:",outcome[1]-outcome[0],"first stage:",first_stage,"Wald effect:",effect)

def local_discontinuity():
    x=np.array([-3.,-2.,-1.,1.,2.,3.])
    treated=(x>0).astype(float)
    y=5+.5*x+2*treated
    design=np.column_stack([np.ones(len(x)),x,treated])
    beta=np.linalg.lstsq(design,y,rcond=None)[0]
    assert np.allclose(beta,[5,.5,2])
    print("RD illustrative intercept/slope/jump:",beta)

def main():
    difference_in_differences();instrumental_variables();local_discontinuity()

if __name__ == "__main__":
    main()
```

## Data science interview discussions

**Interview: Are nonsignificant pretrends enough for DiD?** No. A small preperiod can miss substantial violations, and postperiod shocks can differ even after parallel historical trends. Combine institutional reasoning, graphical diagnostics, alternative comparisons and sensitivity analysis.

**Interview: What does an IV estimate mean when only some people comply?** Under the standard assumptions it is a local average effect for compliers, whose uptake changes with the instrument. It is not automatically the effect for always-takers, never-takers or everyone eligible.

**Interview: Why avoid treating a staggered rollout as one simple fixed-effects coefficient?** Heterogeneous effects and already-treated comparison groups can make the coefficient a misleading weighted mixture. Estimate coherent cohort-time effects and state how they are aggregated.

## Primary sources and official APIs

- [Callaway and Sant Anna, Difference-in-Differences with Multiple Time Periods](https://arxiv.org/abs/1803.09015).

- [Lee and Lemieux, Regression Discontinuity Designs in Economics](https://www.nber.org/papers/w14723).

## Reading connections

[Previous chapter](15-causal-inference-foundations.md) | [Book contents](../README.md) | [Next chapter](17-causal-estimation-heterogeneous-effects-and-policy-learning.md)
