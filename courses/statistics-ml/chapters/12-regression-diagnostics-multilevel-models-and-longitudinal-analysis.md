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
