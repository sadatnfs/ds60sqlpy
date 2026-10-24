# 28. Survival Analysis, Duration Models, and Reliability

Book: **Statistics and Machine Learning for Data Scientists End To End**. Chapter ID: `statistics-028`. Tutorial mode; all examples and interview answers are fully worked.

## The decision and the mental model

Duration data contain a time origin, an event definition and an observation mechanism. A customer still active when a study ends has not necessarily survived forever; the event time is only known to exceed the last observed follow-up. Treating this person as an observed non-event at an arbitrary final time loses information and changes the target. Begin by specifying what starts the clock, what ends it, and who could enter the study.

### Survival and hazard answer different questions

For nonnegative event time T, survival is \(S(t)=\Pr(T>t)\). The hazard h(t) is the instantaneous event rate conditional on survival to t. In a continuous model, \(S(t)=e^{-H(t)}\), where H(t) is the integrated hazard. Hazard is a rate with time units, not a probability, and a hazard ratio is not a ratio of cumulative event probabilities. Translating model output into a decision often requires survival curves or restricted mean time, not only a coefficient.

### Risk sets encode observation correctly

At each event time, count individuals still under observation and event-free immediately before that time. Kaplan-Meier multiplies conditional survival factors \(1-\frac{d_{j}}{n_{j}}\), with d_j events among n_j at risk. Censored individuals contribute to earlier risk sets and leave when follow-up ends; they do not create a survival drop. Delayed entry requires excluding individuals before their actual entry time. Ignoring these rules can create artificial survival advantages.

### Censoring assumptions require substantive reasoning

Standard right-censoring methods assume censoring is independent of the event time, possibly conditional on modeled covariates. If severely ill participants leave follow-up more often, observed survivors are selected. Rich adjustment, inverse-probability methods or sensitivity analyses may be needed. No estimator can recover unseen outcome behavior from a censoring label without assumptions.

### Choose an estimand before a model

A treatment comparison may concern survival probability at one year, restricted mean survival over two years, a cause-specific event rate or cumulative incidence of a particular cause. Competing events change these relationships. A Cox coefficient can summarize a proportional hazard relation, but if effects cross over time a single hazard ratio may obscure the main scientific result. Show curves, risk-set sizes and clinically or operationally meaningful time scales.

The offline examples calculate risk sets and survival steps directly, integrate the survival curve for restricted mean time, and distinguish competing-event incidence from censoring. They explain the bookkeeping that a survival package performs. They do not fit every specialized duration model listed below.

## Methods, mechanisms, and limits

### stat-28-01

**Time-to-event analysis**

Time-to-event analysis models the distribution of elapsed time until a defined event while accounting for incomplete observation. The event can be failure, churn or recovery, but changing its definition changes the target. Specify the clock origin and observation endpoint. Repeated customer records are not automatically independent event times, and retrospective inclusion based on surviving long enough can introduce immortal-time bias.

### stat-28-02

**Survival functions**

The survival function \(S(t)=\Pr(T>t)\) gives the probability of remaining event-free beyond t. It is nonincreasing and begins at one when all event times are positive. A step estimate between observed events does not imply the underlying process changes only at those instants. Report time units and uncertainty, especially in the far tail where few individuals remain at risk.

### stat-28-03

**Hazard functions**

The hazard is an instantaneous conditional event rate among those who have survived to t. In continuous time it equals f(t)/S(t), when defined. A rising hazard does not imply survival rises; survival still falls as risk accumulates. Comparing hazards conditions on different survivor populations over time, which complicates causal interpretation of a hazard ratio even in randomized studies.

### stat-28-04

**Right censoring**

Right censoring records that T exceeds a last observed time C, often representing administrative study end or lost follow-up. The observed record is min(T,C) plus an event indicator. Censored individuals supply event-free time until C. Standard methods require an appropriate independent-censoring assumption; treating all censored times as failures biases survival downward, while deleting them discards useful follow-up.

### stat-28-05

**Left censoring**

Left censoring means an event occurred before a known observation time, but its exact time is unknown. Examples include a biomarker threshold already crossed at first measurement. The likelihood contribution is a probability over an earlier interval rather than an exact event density. It differs from left truncation, where some individuals are absent from the sample entirely until surviving an entry threshold.

### stat-28-06

**Interval censoring**

Interval censoring identifies an event only between two inspections, such as a failure discovered during a monthly visit. The contribution is \(\Pr(L<T\le R)\), determined by both interval endpoints. Replacing every event with the midpoint can distort uncertainty and time patterns when intervals are wide or variable. Use a method designed for interval observation and describe the inspection process.

### stat-28-07

**Left truncation**

Left truncation, or delayed entry, includes an individual only after they survive to an entry time. Risk sets must exclude that individual before entry. Treating everyone as observed from time zero grants guaranteed survival time that was required for inclusion. The sampling mechanism also needs assumptions about entry relative to event time; delayed-entry bookkeeping alone cannot cure selection on unmeasured prognosis.

### stat-28-08

**Kaplan–Meier estimation**

Kaplan-Meier estimates survival by multiplying \(1-\frac{d_{j}}{n_{j}}\) at each event time. Censoring changes later denominators without creating an event drop. Ties require a clear convention for events and censoring at the same recorded time. Its tail is unstable when few remain under observation, so accompany curves with numbers at risk and avoid interpreting an unreached median as an infinite lifetime.

### stat-28-09

**Nelson–Aalen estimation**

Nelson-Aalen estimates cumulative hazard as the sum \(\frac{d_{j}}{n_{j}}\) across event times. Exponentiating its negative gives a survival estimate related to, but not identical to, Kaplan-Meier in finite samples. It is useful for inspecting accumulated event intensity and model diagnostics. Large jumps near the tail can reflect small risk sets rather than a well-estimated sudden biological change.

### stat-28-10

**Log-rank tests**

The log-rank test compares observed and expected events between groups across risk sets. It is particularly sensitive to certain consistent hazard differences and can have poor power for crossing effects. A p-value does not quantify the magnitude or timing of a difference. Pair it with survival curves or a prespecified effect estimand, and account for stratification or clustered observations when relevant.

### stat-28-11

**Cox proportional hazards models**

The Cox model specifies \(h(t\mid x)=h_0(t)\exp(x^{\mathsf T}\beta)\), leaving the baseline hazard unspecified. Partial likelihood compares covariates within event-time risk sets to estimate beta. Proportional hazards means a covariate hazard ratio is constant over time. A coefficient is a log hazard ratio, not a direct survival-probability change or an accelerated-time factor.

### stat-28-12

**Proportional-hazards diagnostics**

Proportional-hazards diagnostics examine whether covariate effects vary with time, using residual patterns, plots or formal tests such as scaled Schoenfeld residual checks. Multiple testing and sparse late follow-up affect interpretation. If proportionality fails, consider time-varying effects, stratification or a different estimand rather than hiding the issue behind one averaged coefficient. Also inspect functional form and influential observations.

### stat-28-13

**Accelerated failure-time models**

An accelerated failure-time model specifies \(\log T=x^{\mathsf T}\beta+\varepsilon\), so \(\exp(\beta)\) describes multiplicative time scaling under the chosen model. A factor above one generally lengthens survival time for a positive coefficient. The error distribution determines the survival family and extrapolation. AFT and proportional-hazard interpretations coincide only for particular families, so do not translate coefficients indiscriminately.

### stat-28-14

**Parametric survival models**

Parametric survival models specify a full event-time distribution, such as exponential, Weibull or lognormal. This supports smooth curves and extrapolation beyond observed follow-up, but that extrapolation is strongly assumption-dependent. Compare hazard shapes, residuals and substantive mechanisms, not only information criteria. A distribution that fits central follow-up can still imply implausible long-term behavior.

### stat-28-15

**Time-varying covariates**

Time-varying covariates allow an individual's measured predictors to change during follow-up. Represent intervals with covariate values known at each interval start, avoiding future measurements. Treatment changes influenced by evolving prognosis can create time-dependent confounding, so a standard extended Cox model is not automatically causal. Distinguish external calendar covariates from internal processes tied to the event.

### stat-28-16

**Time-varying effects**

Time-varying effects let a predictor coefficient depend on follow-up time, relaxing proportional hazards. Interactions with time or flexible coefficient functions can describe early benefit and later attenuation. Complexity needs enough events across time, and interpretation should use curves or time-specific contrasts. A changing covariate value and a changing effect of that covariate are separate model features.

### stat-28-17

**Frailty models**

Frailty models introduce latent multiplicative heterogeneity in hazard, often shared within families, sites or repeated units. Mixing individuals with different risks can create changing marginal hazards even when conditional hazards are simple. Distributional assumptions for frailty affect inference. A fitted random effect accounts for modeled dependence but does not prove all relevant unmeasured heterogeneity has been identified.

### stat-28-18

**Competing risks**

Competing risks occur when one event prevents the event of interest from occurring in the studied state, such as death before device revision. The probability of a particular event depends on all competing event processes. Censoring competing events can be appropriate for estimating a cause-specific hazard under its interpretation, but not for directly estimating that cause's real-world cumulative incidence.

### stat-28-19

**Cause-specific hazard models**

A cause-specific hazard models the instantaneous rate of one event among individuals still free of all events. Other causes remove individuals from that risk set. This is useful for etiologic or transition-rate questions, but cumulative incidence requires combining all cause-specific hazards with overall event-free survival. A reduced cause-specific hazard can coexist with a different incidence pattern if competing risks change.

### stat-28-20

**Cumulative incidence functions**

The cumulative incidence function F_k(t) gives \(\Pr(T\le t,\mathrm{cause}=k)\). It accumulates overall event-free survival just before each time multiplied by the cause-specific hazard increment. Unlike one-minus-Kaplan-Meier after censoring competitors, it respects the fact that other causes prevent future target events. The CIFs across causes sum to total event probability, providing a useful accounting check.

### stat-28-21

**Fine–Gray models**

Fine-Gray regression models a subdistribution hazard related to the cumulative incidence of a target cause. Its modified risk set retains certain individuals after competing events through weighting, so the coefficient has a different meaning from a cause-specific hazard ratio. It can be useful for incidence prediction, but interpreting it as a direct biological instantaneous rate is misleading.

### stat-28-22

**Recurrent-event models**

Recurrent-event models analyze repeated events per individual, such as repairs or hospital admissions. Total-time, gap-time and event-order formulations answer different questions. Dependence among events and terminal events must be handled explicitly. Simply treating each episode as an independent person can understate uncertainty and ignore how previous events change subsequent risk or exposure time.

### stat-28-23

**Multistate models**

Multistate models represent transitions among states such as healthy, ill and dead. Transition-specific hazards determine state-occupation probabilities under specified assumptions, often Markov or semi-Markov. The time scale may reset at state entry or remain on a global clock. Distinguish an estimated transition rate from a probability of occupying a state at a later horizon.

### stat-28-24

**Joint longitudinal–survival models**

Joint longitudinal-survival models connect a repeated biomarker process with an event process, often through shared random effects or latent current value. They can address informative dropout caused by the event and update risk predictions as measurements arrive. Results depend on both submodels and the association structure. The biomarker-error model is consequential because plugging noisy observed values directly into a hazard can bias relationships.

### stat-28-25

**Restricted mean survival time**

Restricted mean survival time is the area under S(t) from zero to a prespecified horizon tau. It measures expected event-free time accumulated within that window and remains interpretable when hazards are nonproportional. Choose tau with adequate follow-up support. Comparing RMST differences avoids extrapolating an unobserved tail, but censoring and causal assumptions still apply.

### stat-28-26

**Reliability engineering**

Reliability engineering translates event-time models into failure probabilities, repair policies and system availability. A series system fails when any required component fails; a parallel redundant system has a different structure. Dependence among components can invalidate simple products of survival probabilities. Separate time-to-first-failure reliability from availability in a repairable system, which depends on both failure and repair processes.

### stat-28-27

**Accelerated life testing**

Accelerated life testing observes failures under elevated stress to infer behavior under ordinary use. A stress-life relationship such as an Arrhenius or power model supplies the extrapolation bridge. Higher stress must preserve the relevant failure mechanism; otherwise the experiment estimates the wrong process. Record stress conditions, censoring and model uncertainty, and distinguish interpolation within tested stress from large extrapolation.

## Worked Python demonstrations

Complete offline program: [chapter_28.py](../examples/chapter_28.py). It uses tiny fixtures, no downloads, and assertions that check the expected observations. Run from the repository root:

```text
python courses/statistics-ml/examples/chapter_28.py
```

### Build the risk sets by hand

Four individuals have follow-up times [1,2,3,4] and event flags [1,0,1,1]. At time one, one event among four gives survival \(\frac{3}{4}\). The person censored at time two leaves without a survival drop. At time three, one event among two multiplies survival by one-half, yielding \(\frac{3}{8}\). The final event drops the estimate to zero, based on only one remaining person.

### Integrate meaningful time rather than an unobserved tail

The estimated survival is one for the first time unit, 0.75 for the next two, and 0.375 for the final unit through horizon four. The restricted mean is \(1+1.5+0.375=2.875\) time units. This is a finite-window quantity. It does not estimate an unrestricted lifetime beyond follow-up.

### Account for competing events

With one cause-A event among four and then one cause-B event among the remaining three, each cause has cumulative incidence 0.25 and event-free survival is 0.5. The second increment uses the pre-event survival 0.75 times \(\frac{1}{3}\). The sum-to-one check makes the competing-event accounting explicit.

### Complete executable example

```python
import numpy as np

def kaplan_meier():
    time=np.array([1.,2.,3.,4.]);event=np.array([1,0,1,1])
    survival=1.;steps=[]
    for t in np.unique(time[event==1]):
        risk=np.sum(time>=t);failures=np.sum((time==t)&(event==1))
        survival*=1-failures/risk;steps.append((t,int(risk),survival))
    assert np.allclose([s[2] for s in steps],[.75,.375,0.])
    print("Event time, risk count, survival:",steps)
    return steps

def restricted_mean():
    # Survival on [0,1), [1,3), [3,4) is 1, .75, .375.
    area=1*1+.75*2+.375*1
    assert area==2.875
    print("Restricted mean through time 4:",area)

def competing_incidence():
    # Four people: cause A at 1, cause B at 2, remaining two censored at 3.
    s=1.;cif_a=0.;cif_b=0.
    cif_a+=s*(1/4);s*=1-1/4
    cif_b+=s*(1/3);s*=1-1/3
    assert np.allclose([cif_a,cif_b,s],[.25,.25,.5])
    assert np.isclose(cif_a+cif_b+s,1.)
    print("CIF A, CIF B, event-free:",cif_a,cif_b,s)

def main():
    kaplan_meier();restricted_mean();competing_incidence()

if __name__ == "__main__":
    main()
```

## Data science interview discussions

**Interview: Why not delete censored records?** They contribute known event-free follow-up and risk-set membership before censoring. Deleting them changes denominators and selects a different population. The proper method uses their partial information under a stated censoring assumption.

**Interview: Is a hazard ratio of 0.5 a 50 percent lower probability of failure?** No. It compares instantaneous conditional rates under the model. Cumulative failure probabilities also depend on baseline hazard, follow-up time and competing events. Show the corresponding survival or incidence contrasts for the decision horizon.

**Interview: What does a competing-risk model add?** It distinguishes a target event rate from the probability of observing that event when other events prevent it. Cause-specific hazards and subdistribution hazards answer different questions, and the desired estimand determines which is appropriate.

## Primary sources and official APIs

- [statsmodels survival and duration analysis APIs](https://www.statsmodels.org/stable/duration.html)

- [Kaplan and Meier, Nonparametric Estimation from Incomplete Observations](https://doi.org/10.1080/01621459.1958.10501452)

- [Cox, Regression Models and Life-Tables](https://doi.org/10.1111/j.2517-6161.1972.tb00899.x)

## Reading connections

[Previous chapter](27-advanced-forecasting-and-forecast-evaluation.md) | [Book contents](../README.md) | [Next chapter](29-anomaly-detection-changepoints-and-statistical-process-control.md)
