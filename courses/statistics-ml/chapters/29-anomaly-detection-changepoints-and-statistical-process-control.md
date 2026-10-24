# 29. Anomaly Detection, Changepoints, and Statistical Process Control

Book: **Statistics and Machine Learning for Data Scientists End To End**. Chapter ID: `statistics-029`. Tutorial mode; all examples and interview answers are fully worked.

## The decision and the mental model

Detection is a decision under an asymmetric information problem. Most unusual observations are not labeled in advance, and the cost of an alert depends on the operator who must investigate it. A detector therefore needs more than a score: it needs a reference population, a definition of abnormality, a threshold, an investigation action and a way to evaluate false alarms and missed events.

### Separate three questions

A point anomaly asks whether one value is unusual relative to a reference distribution. A contextual anomaly asks whether it is unusual given time, location or other conditions. A changepoint asks whether the process generating observations has changed. A single large spike may be a point anomaly without a persistent process shift; a small sustained rise may be a changepoint without any spectacular individual value. Choosing the wrong target can make a technically correct detector operationally unhelpful.

### Scores are not calibrated probabilities

A reconstruction error, isolation depth or local-density ratio ranks observations under a chosen mechanism. It does not automatically equal the probability that an incident is real. Feature scaling, reference-window contamination and changing operational mix alter score distributions. Fit preprocessing on the reference data and test thresholds on representative held-out periods, including known benign changes and missing-data incidents.

For a binary alert, positive predictive value depends on prevalence. With event prevalence pi, sensitivity s and false-positive rate f, \(\mathrm{PPV}=\frac{\pi s}{\pi s+(1-\pi)f}\). A 90 percent sensitive detector with a one percent false-positive rate has PPV about 8.3 percent when real events occur in only one-tenth of one percent of cases. This base-rate calculation explains why seemingly excellent classification metrics can overwhelm a monitoring team.

### Sequential evidence is different from one-shot testing

A CUSUM retains positive evidence of a shift through \(C_t=\max\bigl(0,C_{t-1}+x_t-\mu_0-k\bigr)\). The reference value k discounts fluctuations too small to matter; an alarm occurs when C exceeds a threshold h. An EWMA instead maintains a decaying weighted level. Repeated monitoring changes false-alarm behavior, so choose thresholds using run-length or event-level evaluation rather than interpreting every point as an isolated 5 percent test.

### An operational investigation path

For service latency, first distinguish changed traffic mix, missing instrumentation and genuine slower execution. Model expected latency conditional on load and endpoint before scoring residuals. Assess alerts at the incident level so one long outage does not count as hundreds of independent successes. Report false alerts per operator-day, missed incidents and detection-delay distributions. After a signal, localize contributing dimensions and test a reversible hypothesis. A correlation with an alert is a lead for investigation, not established root cause.

## Methods, mechanisms, and limits

### stat-29-01

**Point anomalies**

A point anomaly is one observation unusually far from a reference distribution. The reference may be global or feature-conditional, and its choice determines which values appear unusual. A legitimate large customer can be a global revenue outlier without being erroneous. Preserve the original value and context, and distinguish a data-quality check with a known valid range from a statistical rarity score.

### stat-29-02

**Contextual anomalies**

A contextual anomaly is unexpected given conditions such as hour, workload or peer group. A temperature of 30 degrees has different meaning in a freezer and an office. Build the conditional baseline using information available at detection time. If context is itself affected by the incident, conditioning too aggressively can hide the signal, so retain both raw and adjusted views.

### stat-29-03

**Collective anomalies**

A collective anomaly is a sequence or group whose joint pattern is unusual although individual elements may look ordinary. Repeated small transfers or an abnormal ordering of events can fit this category. The representation must preserve sequence, duration or relationships. Scoring each row independently loses the mechanism, while overly flexible sequence models can reconstruct the unusual pattern and fail to flag it.

### stat-29-04

**Robust z-scores**

A robust z-score centers at the median and scales by median absolute deviation, often using the normal-consistency factor about 1.4826. It reduces the influence of extreme observations relative to mean/standard-deviation scaling. MAD can be zero for discrete or constant data, requiring a documented fallback. Robustness does not justify a universal threshold across heavy-tailed, seasonal or dependent populations.

### stat-29-05

**Mahalanobis distance**

Mahalanobis distance measures displacement through the inverse covariance: \(d^2=(x-\mu)^{\mathsf T}\Sigma^{-1}(x-\mu)\). It accounts for scale and linear correlation, so a point can be unusual jointly even when each coordinate is ordinary. Covariance estimation is fragile with contamination or many features relative to observations. Use regularization or robust estimates and calibrate scores without assuming Gaussian tails by default.

### stat-29-06

**Local outlier factor**

Local outlier factor compares an observation's local reachability density with neighboring densities. It can reveal points sparse relative to their neighborhood even when global density varies. Neighbor count and scaling define locality. The scikit-learn distinction between outlier detection on fitting data and novelty detection on unseen data matters; enabling novelty does not make fit-sample scoring semantics interchangeable.

### stat-29-07

**Isolation forests**

Isolation forests recursively partition feature space and identify observations isolated by relatively short paths. They avoid explicit density estimation and scale to many observations, but feature representation and irrelevant dimensions still matter. The contamination parameter sets a threshold convention, not a discovered truth about incident prevalence. Examine performance on realistic anomalies rather than only synthetic points placed far outside the data cloud.

### stat-29-08

**One-class support vector machines**

A one-class SVM learns a boundary around training observations in a kernel feature space. The nu and kernel-scale choices influence boundary flexibility and allowed training violations. It works best with a meaningful mostly normal training sample and careful scaling. A contaminated reference set or high-dimensional kernel mismatch can yield an attractive boundary with poor novelty detection.

### stat-29-09

**Reconstruction-based anomaly detection**

Reconstruction detectors train a low-dimensional or constrained model and score how poorly an input is reconstructed. PCA and autoencoders encode different representations. A powerful model can reconstruct anomalies too, while benign distribution shift can cause high error. Inspect which features contribute to error and validate the training-reference assumption instead of treating reconstruction loss as an incident probability.

### stat-29-10

**Density-based anomaly detection**

Density-based detection flags low estimated probability or density under a reference model. Low density can reflect legitimate minority groups, boundary effects or a poor high-dimensional model. Continuous density is coordinate-dependent, so a numerical threshold changes under transformations. Choose a representation tied to the decision and assess whether rare but acceptable cases consume the alert budget.

### stat-29-11

**Extreme-value anomaly thresholds**

Extreme-value thresholding models the tail beyond a high threshold, often with a generalized Pareto approximation. The threshold balances approximation validity against the number of exceedances available for estimation. Dependence may require declustering, and regime shifts can invalidate a historical tail fit. Report tail uncertainty and extrapolation distance rather than presenting a rare-event cutoff as exact.

### stat-29-12

**Offline changepoint detection**

Offline changepoint detection uses a complete historical sequence to segment it into regimes. A cost function measures within-segment fit and a penalty controls additional breaks. Minimum segment length and the assumed change type affect the result. Retrospective detection can use observations after a break, so its estimated location and accuracy are not equivalent to real-time detection delay.

### stat-29-13

**Online changepoint detection**

Online changepoint detection updates evidence as each observation arrives and decides when to signal a change. It trades false alarms against detection speed. Algorithms may use cumulative likelihood ratios, Bayesian run-length distributions or other sequential summaries. Evaluate from the true change time to the alarm under representative shift sizes, and specify reset behavior after an alarm.

### stat-29-14

**CUSUM charts**

A CUSUM accumulates evidence for a sustained shift while resetting negative accumulated evidence to zero in a one-sided version. The reference value k determines sensitivity to shift size, and h controls alarm frequency. Standard calibration assumes a suitable in-control model. Serial dependence, heavy tails or changing variance can alter run lengths substantially, so simulation or historical replay should match operational conditions.

### stat-29-15

**EWMA charts**

An EWMA chart tracks \(z_t=\lambda x_t+(1-\lambda)z_{t-1}\), giving exponentially decaying weight to older observations. Smaller lambda emphasizes sustained small shifts but responds more slowly. Control limits depend on the in-control variance and initialization, with early-time variance differing from its long-run value. It is a monitoring procedure, not merely a smoothed plot with arbitrary horizontal lines.

### stat-29-16

**Shewhart charts**

A Shewhart chart compares individual observations or subgroup summaries with limits estimated from an in-control process. It is effective for relatively large abrupt changes. Rational subgrouping determines which variation estimates short-term common-cause noise. Repeated runs rules affect false-alarm probability and should be specified in advance. Specification limits describe acceptable output, while control limits describe process behavior.

### stat-29-17

**Multivariate control charts**

Multivariate control charts monitor joint behavior, such as Hotelling T-squared for a correlated vector or multivariate EWMA for small shifts. A global signal can occur without any single univariate chart crossing its threshold. Covariance estimation and dimensionality are central. After signaling, contribution diagnostics guide investigation but do not uniquely identify the causal source of the joint change.

### stat-29-18

**Process capability analysis**

Process capability compares a stable process distribution with engineering specification limits. Indices such as Cp describe spread relative to the allowed range, while Cpk additionally reflects centering under standard assumptions. A process that is not in statistical control does not support a stable capability statement. Non-normality, autocorrelation and measurement error require methods appropriate to those conditions.

### stat-29-19

**Alert threshold calibration**

Alert threshold calibration converts a score into an operational rule using target false-alert rates, investigation capacity and incident costs. Choose thresholds on data separate from model fitting and final evaluation. Count alerts at the unit actually acted upon, such as deduplicated incidents. Retuning after seeing test incidents can inflate apparent performance and should be recorded as development.

### stat-29-20

**Detection delay analysis**

Detection delay measures elapsed time or observations from a genuine change to an alarm. It is meaningful only alongside the false-alarm constraint and missed-detection policy. Compare distributions over repeated scenarios, not one favorable incident. A detector that never alarms has no observed delay but is not excellent; censored or missed detections must remain in the evaluation accounting.

### stat-29-21

**Root-cause localization**

Root-cause localization uses the alert to identify plausible contributing components, features or temporal changes. Decomposition, traces and controlled checks can narrow the hypothesis set. The largest anomaly score contribution need not be the underlying cause, because downstream symptoms can dominate. Preserve an evidence chain from observation through hypothesis to a reversible test and confirmed recovery.

## Worked Python demonstrations

Complete offline program: [chapter_29.py](../examples/chapter_29.py). It uses tiny fixtures, no downloads, and assertions that check the expected observations. Run from the repository root:

```text
python courses/statistics-ml/examples/chapter_29.py
```

### Use a robust reference without forgetting its limits

The reference [9,10,10,11,12] has median ten and MAD one. A value thirty has a normal-consistency-scaled score above thirteen. The calculation is deterministic, but the tiny reference does not establish a universal alarm threshold. A constant reference would have MAD zero and needs a separate policy.

### Accumulate a small persistent shift

After three zeros, observations become one. With \(k=0.25\) the CUSUM adds 0.75 each shifted period, reaching 2.25 at index five and crossing threshold two. One shifted observation is not enough; three consistent observations trigger the signal. The example shows the mechanism, not a calibrated production average run length.

### Explain an apparently disappointing alert stream

At prevalence 0.001, sensitivity 0.9 and false-positive rate 0.01, only about 8.3 percent of alerts are real events. For 100,000 opportunities this corresponds to about 90 true alerts and 999 false alerts in expectation. Reducing false positives can matter more operationally than a small sensitivity improvement.

### Complete executable example

```python
import numpy as np

def robust_score():
    reference=np.array([9.,10.,10.,11.,12.])
    median=np.median(reference);mad=np.median(np.abs(reference-median))
    score=(30-median)/(1.4826*mad)
    assert median==10 and mad==1 and score>13
    print("Median, MAD, score for 30:",median,mad,score)

def cumulative_shift():
    x=np.array([0.,0.,0.,1.,1.,1.,1.]);state=0.;trace=[]
    for value in x:
        state=max(0.,state+value-.25);trace.append(state)
    alarms=np.flatnonzero(np.array(trace)>2.)
    assert trace==[0.,0.,0.,.75,1.5,2.25,3.]
    assert alarms[0]==5
    print("CUSUM trace:",trace,"first alarm index:",alarms[0])

def alert_precision():
    prevalence=.001;sensitivity=.9;false_positive=.01
    ppv=prevalence*sensitivity/(prevalence*sensitivity+(1-prevalence)*false_positive)
    assert np.isclose(ppv,.0009/.01089) and ppv<.1
    print("Alert precision at rare prevalence:",ppv)

def main():
    robust_score();cumulative_shift();alert_precision()

if __name__ == "__main__":
    main()
```

## Data science interview discussions

**Interview: Should an anomaly score be presented as a probability?** Only after a separate justified calibration against representative labels and a defined event. Isolation depth or reconstruction error alone has no such probabilistic interpretation. Explain the scoring mechanism and threshold policy instead.

**Interview: How do you compare two monitoring systems?** Replay the same incidents and normal periods, enforce the same alert-budget accounting, and compare false alerts, missed incidents and delay. Include operator actions and deduplication so hundreds of correlated alerts do not count as independent successes.

**Interview: Does the highest contributing feature identify root cause?** It identifies a statistical contribution under the score. A downstream symptom may contribute most. Use timing, dependencies and a reversible test to distinguish a cause from a correlated effect.

## Primary sources and official APIs

- [scikit-learn outlier and novelty detection](https://scikit-learn.org/stable/modules/outlier_detection.html)

- [NIST engineering statistics handbook: control charts](https://www.itl.nist.gov/div898/handbook/pmc/section3/pmc3.htm)

## Reading connections

[Previous chapter](28-survival-analysis-duration-models-and-reliability.md) | [Book contents](../README.md) | [Next chapter](30-spatial-and-spatiotemporal-statistics.md)
