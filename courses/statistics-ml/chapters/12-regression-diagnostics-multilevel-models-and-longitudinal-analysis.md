# 12. Regression Diagnostics, Multilevel Models, and Longitudinal Analysis

Book: **Statistics and Machine Learning for Data Scientists End To End**. Chapter ID: `statistics-012`. Tutorial mode; all examples and interview answers are fully worked.

## The decision and the mental model

Repeated measurements create two kinds of variation: differences between entities and changes within an entity. A customer with high baseline engagement may remain high every week. Treating those weeks as independent customers makes uncertainty too optimistic and can confuse a between-customer association with a within-customer effect.

A random-intercept model writes y_ij=X_ij beta+b_j+epsilon_ij, with group variance tau^2 and residual variance sigma^2. Two observations in the same group share b_j, creating covariance tau^2 and intraclass correlation tau^2/(tau^2+sigma^2). Partial pooling shrinks a noisy group mean toward the population mean by weight tau^2/(tau^2+sigma^2/n_j). Small groups shrink more because their means contain less information.

Fixed-effects panel estimation instead removes each unit's mean, identifying coefficients from within-unit changes. Time-invariant predictors disappear under this transformation. Random effects can estimate such associations but ordinarily assumes the random effect is suitably independent of included predictors. Neither method automatically handles treatment-confounder feedback, endogenous timing or short-panel lagged outcomes.

## Methods, mechanisms, and limits

### stat-12-01

**Residual analysis**

Plot residuals against fitted values, predictors, time and groups. Structure reveals errors not visible in one aggregate loss. Normal-looking residuals do not establish exogeneity or causal identification.

### stat-12-02

**Leverage**

Leverage is the diagonal of the projection matrix and depends on predictors, not outcome residual size. A high-leverage point can strongly determine a fit while having a deceptively small residual.

### stat-12-03

**Cook’s distance**

Cook's distance combines residual size and leverage to assess fitted-model change on deletion. Investigate influential records rather than automatically deleting them. A rare legitimate operating regime may be scientifically central.

### stat-12-04

**Multicollinearity diagnostics**

Near-linear predictor dependencies inflate coefficient uncertainty and instability. Predictions inside the observed design may remain accurate. Distinguish numerical scaling problems from insufficient independent variation for interpreting separate effects.

### stat-12-05

**Variance inflation factors**

VIF is 1/(1-R_j^2) from regressing a predictor on the others. It diagnoses linear redundancy conditional on the design. Universal cutoff rules ignore sample size, scientific contrasts and prediction objectives.

### stat-12-06

**Heteroskedasticity diagnostics**

Inspect residual spread and use tests such as Breusch-Pagan with care about mean misspecification. Robust standard errors address uncertainty under heteroskedasticity; variance modeling may also improve prediction intervals.

### stat-12-07

**Autocorrelation diagnostics**

Check lagged residual relationships after fitting. Unmodeled autocorrelation reduces effective information and can indicate missing dynamics. The relevant time ordering must reflect actual observation intervals rather than arbitrary row order.

### stat-12-08

**Model specification tests**

Specification diagnostics test selected implications, such as omitted nonlinear structure. A rejection does not identify the unique correction, while nonrejection does not validate every model assumption.

### stat-12-09

**Linear mixed-effects models**

Combine fixed population coefficients with modeled group-level deviations. Fit covariance components by likelihood or restricted likelihood, then inspect singular fits and residual patterns. Random-effects distributions are substantive modeling assumptions.

### stat-12-10

**Generalized linear mixed models**

Apply a link and non-Gaussian response with group random effects. Conditional subject-specific coefficients differ from marginal population-average effects, particularly with nonlinear links. Integrating random effects is part of prediction.

### stat-12-11

**Random intercept models**

Give each group its own deviation from a common baseline. This induces within-group correlation and shrinkage. It cannot represent groups whose predictor slopes genuinely differ.

### stat-12-12

**Random slope models**

Allow selected predictor coefficients to vary by group, potentially correlated with intercepts. Each group needs enough within-group variation. Sparse groups can make covariance estimates singular or highly prior-sensitive.

### stat-12-13

**Partial pooling**

Combine local evidence with a common distribution. Small or noisy groups shrink more than well-measured groups. Pooling assumes relevant common structure; forcing unrelated groups together can erase real heterogeneity.

### stat-12-14

**Intraclass correlation**

ICC measures the fraction of variance attributable to shared group variation in a simple random-intercept model. It depends on scale and model. Non-Gaussian outcomes need care about latent versus observed-scale ICC.

### stat-12-15

**Cross-classified models**

Represent intersecting memberships, such as students assessed by multiple teachers across schools. Treating one membership as nested in another misstates correlation when the actual structure crosses.

### stat-12-16

**Nested models**

Represent levels contained within higher levels, such as measurements within patients within hospitals. Distinguish hierarchical nesting from the separate use of nested models in likelihood comparisons.

### stat-12-17

**Generalized estimating equations**

GEE estimates a marginal mean using a working correlation and sandwich covariance. Robustness concerns the correlation specification under adequate independent clusters, not a wrong mean or informative missingness.

### stat-12-18

**Repeated-measures models**

Model within-unit covariance across repeated conditions or times. Sphericity, compound symmetry and unstructured covariance impose different restrictions. The correct choice depends on design, sample information and target contrasts.

### stat-12-19

**Growth curve models**

Represent individual trajectories with time functions and possibly random intercepts or slopes. Center time meaningfully to interpret baseline effects. Attrition tied to unobserved trajectories can bias estimated growth.

### stat-12-20

**Panel fixed-effects models**

Subtract unit means or include unit indicators to remove time-invariant unit factors. Identification comes from within-unit variation. Time-varying confounding, measurement error and endogenous treatment remain possible.

### stat-12-21

**Panel random-effects models**

Model unit-specific variation while retaining between-unit information. Standard consistency assumptions relate those effects to predictors. A correlated-random-effects or Mundlak formulation can explicitly include unit predictor means.

### stat-12-22

**Dynamic panel models**

A lagged outcome correlates with transformed errors in short fixed-effects panels, creating Nickell-type bias. Instrument-based estimators need valid moment conditions and control of instrument proliferation, not just additional lags.

### stat-12-23

**Hausman tests**

Compare two estimators consistent under a null but differently robust under alternatives. A significant difference challenges the joint assumptions, not uniquely one cause. Covariance estimation and finite samples affect interpretation.

### stat-12-24

**Multilevel regression and poststratification**

Fit hierarchical outcome models over demographic or geographic cells, then average predictions using population cell counts. MRP depends on model adequacy and accurate target composition, especially for sparsely sampled or empty cells.

<!-- detailed-case-studies:start -->

## Extended case studies and scientific reasoning

### Case study: repeated customer measurements

Assume a customer contributes four weekly outcomes. A useful decomposition is y_ij=mu+b_j+epsilon_ij, with Var(b_j)=9 and Var(epsilon_ij)=1. A single measurement has variance ten, and two weeks from the same customer have covariance nine. The intraclass correlation is .9. The customer's four-week mean has variance 9+1/4=9.25, not 10/4=2.5. Repeating observations reduces transient noise but barely reduces uncertainty from which customers were sampled.

For m equal observations per group, the familiar design-effect expression 1+(m-1)*ICC follows by expanding the variance of their sum and including all pairwise covariances. Here it is 3.7. A thousand weekly rows from 250 highly stable customers can provide much less independent information than a thousand distinct customers. The approximation concerns a particular mean under a simple correlation structure; unequal group sizes and covariate adjustment require fuller analysis.

The model also defines what prediction means. For an existing customer with observed history, a random-intercept estimate can adapt to that customer's baseline. For a new customer, that baseline is unknown and must be integrated over its population distribution. Evaluating new-customer predictions while allowing the model to use that customer's other weeks leaks the very information deployment lacks. Grouped validation distinguishes those questions.

### Case study: pooling a small region responsibly

A national rate is .10. A small region has one event in two observations, giving raw rate .50. A large region has 500 events in 1,000 observations, also giving .50. Treating both estimates as equally precise creates unstable rankings and incentives. A hierarchical model combines local likelihood information with a distribution of regional rates, generally shrinking the small region more.

The prior or random-effects distribution should reflect relevant comparability. If the small region uses a different measurement rule or serves a different population, shrinkage toward the national mean can conceal a structural difference. Include plausible predictors, check posterior or fitted predictive distributions, and inspect whether the group variance is near a boundary. A singular mixed-model fit can indicate insufficient data for the proposed random-slope covariance, not merely an optimizer inconvenience.

Report both the target and uncertainty. A shrunk region estimate is a model-based estimate for that region, not a raw observed rate. If the purpose is to allocate investigation, posterior exceedance probability or expected loss may be more appropriate than sorting point estimates. For public comparison, explain how group sizes and pooling affect the result so small regions are not mistaken for having proven exceptional performance.

### Case study: fixed effects remove some confounding, not every problem

Consider a panel of stores with stable location quality. High-quality stores may both spend more on advertising and sell more. A pooled sales-advertising coefficient combines between-store quality differences with within-store spending changes. Store fixed effects remove time-invariant quality by demeaning within each store. Calendar effects can remove shocks common to all stores.

But a manager may increase advertising after observing an unrecorded local demand opportunity. That time-varying confounder survives store and calendar demeaning. Lagged sales may be jointly determined with current errors, and a short panel containing a lagged dependent variable introduces additional estimation bias. Fixed effects are a precise transformation of variation, not a universal causal label.

If the scientific question concerns a time-invariant store characteristic, a within-store estimator cannot identify its coefficient because demeaning removes it. Random effects or between-store models can retain that variation but need assumptions about relationships between unobserved store effects and predictors. A Hausman comparison can reveal disagreement between estimators under their assumptions; it cannot explain all possible reasons for disagreement.

### Diagnostic reasoning in a review

When residuals show increasing spread, ask whether variance changes or the mean curve is wrong. When residuals correlate over time, ask whether a missing trend, seasonality, group effect or serial process explains the pattern. When one record is influential, verify its provenance and scientific relevance before deleting it. A legitimate extreme operating condition may be precisely the case the model must support.

Use the simplest covariance structure that captures the decision-relevant dependence with available information. An unstructured repeated-measures covariance grows quickly in parameter count, while compound symmetry assumes equal pairwise correlation. Random slopes allow trajectory heterogeneity but require within-group predictor variation. Explain the tradeoff as a claim about the data-generating process and supported precision, not a contest among increasingly complex formulas.

<!-- detailed-case-studies:end -->

## Worked Python demonstrations

Complete offline program: [chapter_12.py](../examples/chapter_12.py). It uses tiny fixtures, no downloads, and assertions that check the expected observations. Run from the repository root:

```text
python courses/statistics-ml/examples/chapter_12.py
```

### A point can determine the line

The observation at x=20 has leverage above .9 because the other predictors lie between zero and three. The leverage values sum to the model rank, two. This checks the projection geometry and explains why residual size alone can fail to flag influential predictor configurations.

### Shrink according to information

Three groups share the observed mean nine but have sample sizes 1,4,100. With population mean five and known variance components, their pooling weights are .2,.5 and about .962. The smallest group moves closest to the shared mean. Variance components are fixed here to isolate the mechanism; fitting them adds uncertainty.

### Separate within and between associations

Both units have a true within-unit slope two, but their baselines differ strongly and inversely with their feature levels. The pooled slope is negative. Demeaning within each unit recovers two, illustrating the source of fixed-effects identification and its inability to estimate time-invariant characteristics.

### Complete executable example

```python
import numpy as np

def leverage_and_residuals():
    x=np.array([0.,1.,2.,3.,20.])
    design=np.column_stack([np.ones(5),x])
    hat=design@np.linalg.pinv(design)
    leverage=np.diag(hat)
    assert np.isclose(leverage.sum(),2) and leverage[-1]>.9
    print("Leverage:",leverage,"sum equals rank:",leverage.sum())

def partial_pooling():
    grand_mean,tau2,sigma2=5.,1.,4.
    n=np.array([1.,4.,100.]);group_mean=np.array([9.,9.,9.])
    weight=tau2/(tau2+sigma2/n)
    pooled=weight*group_mean+(1-weight)*grand_mean
    assert np.all(np.diff(weight)>0) and np.all((pooled>5)&(pooled<9))
    assert np.isclose(tau2/(tau2+sigma2),.2)
    print("Pooling weights:",weight,"group predictions:",pooled,"ICC:",.2)

def within_estimation():
    x=np.array([[0.,1.,2.],[10.,11.,12.]])
    intercept=np.array([100.,-100.])[:,None]
    y=intercept+2*x
    xc=x-x.mean(axis=1,keepdims=True)
    yc=y-y.mean(axis=1,keepdims=True)
    within=np.sum(xc*yc)/np.sum(xc*xc)
    pooled=np.polyfit(x.ravel(),y.ravel(),1)[0]
    assert np.isclose(within,2) and pooled<0
    print("Within-unit slope:",within,"naive pooled slope:",pooled)

def main():
    leverage_and_residuals();partial_pooling();within_estimation()

if __name__ == "__main__":
    main()
```

## Data science interview discussions

**Interview: Does a high VIF make a model useless?** It undermines separate coefficient interpretation and can increase uncertainty, but predictions within the observed covariate region may remain stable. Decide whether the task needs individual effects, contrasts, extrapolation or only prediction.

**Interview: When do random intercepts and cluster-robust standard errors answer different needs?** A random-intercept model changes the probability model and can produce group predictions with pooling. Cluster-robust covariance primarily changes uncertainty for a chosen mean estimator. Neither substitutes automatically for the other.

**Interview: Why can a fixed-effects estimate disagree with a pooled estimate?** They use different variation. Fixed effects isolate within-unit changes; pooled models also use between-unit differences that may be confounded by stable unit characteristics. Agreement is not guaranteed even with correctly executed code.

## Primary sources and official APIs

- [statsmodels linear mixed-effects models](https://www.statsmodels.org/stable/mixed_linear.html).

- [statsmodels generalized estimating equations](https://www.statsmodels.org/stable/gee.html).

## Reading connections

[Previous chapter](11-regression-and-generalized-linear-models.md) | [Book contents](../README.md) | [Next chapter](13-classical-experimental-design.md)
