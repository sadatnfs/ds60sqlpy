# 11. Regression and Generalized Linear Models

Book: **Statistics and Machine Learning for Data Scientists End To End**. Chapter ID: `statistics-011`. Tutorial mode; all examples and interview answers are fully worked.

## The decision and the mental model

Regression specifies how an outcome distribution changes with predictors. A linear regression is linear in coefficients, so squared features and spline bases can represent curved relationships while retaining a linear coefficient problem. A generalized linear model separates three choices: an outcome family, a linear predictor eta=X beta, and a link g(mu)=eta. These choices encode support and variance as well as mean behavior.

### Derive ordinary least squares

Let r=y-X beta and minimize r-transpose r. Differentiating gives gradient -2 X-transpose r. Setting it to zero yields the normal equations X-transpose X beta=X-transpose y. With full column rank the solution is unique, but QR or SVD is preferable to explicitly inverting the normal matrix. Under E[epsilon|X]=0, coefficients describe a correctly specified conditional mean. Homoskedasticity is needed for the simplest covariance formula, not for calculating the minimizing coefficients. Normal errors are useful for exact small-sample t inference, not a requirement that predictors or outcomes be normally distributed.

A coefficient measures a conditional contrast holding the other encoded columns fixed. With y=beta0+beta1*x+beta2*z+beta3*x*z, the x slope is beta1+beta3*z. Reporting beta1 as a universal effect ignores the interaction. Prediction outside the observed design region adds extrapolation assumptions that the normal equations cannot check.

### Derive logistic regression

For binary y, set p=sigmoid(eta)=1/(1+exp(-eta)). The negative log likelihood is sum(log(1+exp(eta))-y*eta); `logaddexp` computes this stably. Its gradient is X-transpose(p-y) and Hessian X-transpose W X with W_i=p_i(1-p_i). A coefficient beta_j multiplies conditional odds by exp(beta_j) per unit, not probabilities. If an intercept-only model has p=.2, adding log(2) to its linear predictor changes p to one-third, not .4. Complete separation can make unpenalized coefficients diverge even while classification looks perfect.

### Select a family and a loss

Use a Poisson log-link mean for counts with exposure offsets; inspect overdispersion before relying on Poisson standard errors. Use gamma for strictly positive continuous outcomes with a suitable mean-variance relation; use a two-part or Tweedie model when exact zeros have substantive meaning. Quantile regression minimizes asymmetric absolute loss and answers a different question from mean regression. Penalization addresses prediction stability, not unmeasured confounding. Standardize columns within training folds before comparing penalty strengths, and keep the intercept treatment explicit.

## Methods, mechanisms, and limits

### stat-11-01

**Ordinary least squares**

Minimize squared residuals to estimate a linear conditional mean or best linear projection. Diagnose residual structure and leverage. A good projection coefficient need not equal a causal effect or remain stable under population shift.

### stat-11-02

**Weighted least squares**

Weight squared residuals, often inversely to known conditional error variances. Precision weights differ from sampling weights and policy-importance weights. Incorrect weights can hurt efficiency and change the fitted projection under misspecification.

### stat-11-03

**Generalized least squares**

Use a specified full residual covariance matrix to account for heteroskedasticity and correlation. Whitening transforms the problem to ordinary least squares. Estimating the covariance adds uncertainty and can introduce misspecification.

### stat-11-04

**Polynomial regression**

Add powers of predictors to capture curvature while remaining linear in coefficients. Centering helps numerical behavior. High-degree polynomials can oscillate or extrapolate wildly even when interpolation fits well.

### stat-11-05

**Interaction models**

Include products of predictors so one association varies with another variable. Interpret conditional slopes or contrasts at meaningful covariate values. Main-effect coefficients alone no longer summarize the full relationship.

### stat-11-06

**Spline regression**

Join local polynomial pieces at knots with continuity constraints. Knot placement and regularization control flexibility. Too many effective degrees of freedom overfit; insufficient boundary data make extrapolation unreliable.

### stat-11-07

**Restricted cubic splines**

Natural or restricted cubic splines impose linear behavior in the tails. This improves stability relative to unrestricted cubic extrapolation but does not make beyond-range predictions scientifically validated.

### stat-11-08

**Generalized additive models**

Model the link-scale mean as a sum of smooth predictor functions. Penalized smoothness controls complexity. Additivity excludes interactions unless explicitly modeled, so inspect residual structure for missing joint effects.

### stat-11-09

**Generalized linear models**

Choose a response family, link and linear predictor together. The link constrains means to valid support, while the family supplies a variance relationship. Robust covariance can relax some variance assumptions but not repair a wrong mean.

### stat-11-10

**Logistic regression**

Use a logit link to estimate conditional binary probabilities. Exponentiated coefficients are conditional odds ratios. Check separation, calibration, functional form and class weighting; weighted training probabilities may need interpretation adjustment.

### stat-11-11

**Probit regression**

Use the standard normal CDF as the inverse link. Coefficients act on a latent normal index and are not odds ratios. Report probability contrasts at relevant covariate values for interpretability.

### stat-11-12

**Multinomial logistic regression**

Compare each unordered class against a reference through log odds, producing probabilities that sum to one. Reference-class changes alter coefficients but not predictions. Basic multinomial logit imposes restrictive substitution structure.

### stat-11-13

**Ordinal regression**

Model ordered categories, often through cumulative probabilities and proportional odds. Test whether shared slopes across thresholds are plausible. Treating ordinal labels as equally spaced numbers imposes a different, often unjustified assumption.

### stat-11-14

**Poisson regression**

Set log(mu)=X beta+log(exposure) for event counts. Exponentiated coefficients are rate ratios given predictors. Positive exposure is required; unexplained overdispersion affects uncertainty and predictive tails.

### stat-11-15

**Negative binomial regression**

Add a dispersion parameter so count variance can exceed the mean. This suits heterogeneous rates but does not automatically model excess structural zeros or temporal dependence. Compare residual and predictive count distributions.

### stat-11-16

**Quasi-likelihood models**

Specify a mean and variance function without a complete likelihood. Quasi-score equations can estimate effects with a dispersion adjustment. Likelihood-based model comparisons cannot be transferred mechanically without an actual likelihood.

### stat-11-17

**Zero-inflated models**

Model structural-zero probability separately from a count process that may also emit zero. The two components require distinct interpretation and can be difficult to identify. Diagnose both zero frequency and positive-count tails.

### stat-11-18

**Hurdle models**

Fit zero versus positive occurrence, then a zero-truncated positive outcome model. Every observed zero belongs to the hurdle component. This distinguishes participation from intensity when the substantive process supports that split.

### stat-11-19

**Gamma regression**

Use a gamma response for strictly positive skewed outcomes, often with log link and variance proportional to mean squared. Zeros need another mechanism, and inverse-link choices can create undesirable domain behavior.

### stat-11-20

**Tweedie models**

For power between one and two, a compound Poisson-gamma Tweedie model combines exact zero mass with continuous positive outcomes. Exposure and dispersion matter; not every zero-heavy quantity fits this generating process.

### stat-11-21

**Beta regression**

Model an outcome strictly inside (0,1), often with separate mean and precision parameters. Boundary observations violate the basic beta support. Measurement rounding or zero/one inflation needs an explicit extension.

### stat-11-22

**Fractional response models**

Model conditional fractions with a link keeping the mean in [0,1], potentially using Bernoulli quasi-likelihood. Values zero and one can be allowed without pretending the fractional observations are individual binary trials.

### stat-11-23

**Quantile regression**

Minimize pinball loss for a chosen conditional quantile. Coefficients describe that quantile, not an average effect. Fitting quantiles separately can produce crossing estimates unless constrained or reconciled.

### stat-11-24

**Expectile regression**

Minimize asymmetrically weighted squared residuals. Expectiles use residual magnitudes differently from quantiles and are not generally quantiles at the same nominal level. They remain more tail-sensitive than absolute-loss summaries.

### stat-11-25

**Nonlinear least squares**

Specify a nonlinear mean function and minimize squared residuals over its parameters. Multiple local optima and parameter tradeoffs can occur. Inspect starting-value sensitivity, identifiability and residual assumptions.

### stat-11-26

**Robust regression**

Use robust losses or estimators to reduce contamination sensitivity. Distinguish residual outliers from predictor leverage. Robust coefficients do not automatically retain the same target under a misspecified mean function.

### stat-11-27

**Ridge regression**

Add lambda times squared coefficient norm. Shrinkage stabilizes correlated directions but usually retains all coefficients. Scaling and whether the intercept is penalized determine the actual optimization problem.

### stat-11-28

**Lasso regression**

Add an absolute-value coefficient penalty, producing zeros via soft thresholding in simple cases. With correlated features, selected variables can be unstable. Selection does not make ordinary post-fit p-values valid.

### stat-11-29

**Elastic net**

Combine L1 and L2 penalties to balance sparsity and stability among correlated predictors. Tune both strength and mixing using nested or appropriately separated validation, not the final test set.

### stat-11-30

**Group lasso**

Penalize norms of predefined coefficient groups so entire groups enter or leave together. Group definition and size scaling matter. Overlapping groups need a dedicated formulation, not ordinary independent group penalties.

### stat-11-31

**Firth regression**

Use a bias-reducing likelihood adjustment, commonly Jeffreys-information based, to mitigate small-sample bias and separation. It differs from arbitrary ridge shrinkage and does not guarantee a meaningful model under omitted structure.

### stat-11-32

**Generalized additive location, scale, and shape models**

Allow location, scale and shape parameters to depend on predictors, extending beyond mean-only models. This can represent changing skew or dispersion but increases identifiability, fitting and diagnostic demands.

## Worked Python demonstrations

Complete offline program: [chapter_11.py](../examples/chapter_11.py). It uses tiny fixtures, no downloads, and assertions that check the expected observations. Run from the repository root:

```text
python courses/statistics-ml/examples/chapter_11.py
```

### Solve and inspect the OLS geometry

The constructed residual vector is orthogonal to the intercept and slope columns, so the fitted coefficients are exactly 1 and 2 despite nonzero residuals. The assertion tests the normal equations, rather than only checking that a library returned an object. Residual spread would still matter for confidence and prediction intervals.

### Fit logistic regression from its objective

The example explicitly computes stable negative log likelihood and its gradient. BFGS must converge and leave a small gradient norm. The fitted objective must improve over probability 0.5 for every row. A separate odds calculation converts baseline probability .2 to one-third after doubling odds, exposing a common interpretation error.

### Counts require an exposure denominator

An intercept-only Poisson rate model with offsets yields total count divided by total exposure: 20/10=2. It predicts means 2,4,6,8 for exposures 1,2,3,4. Without the offset, differences in observation time would be confused with rate differences.

### See shrinkage algebra numerically

For centered one-feature data, ridge gives beta=sum(x*y)/(sum(x^2)+lambda). Here numerator is 30, squared-feature sum is 10 and lambda is 10, so the slope halves from 3 to 1.5. This is intentional bias, and whether it improves future prediction requires validation.

### Complete executable example

```python
import numpy as np
from scipy.special import expit
from scipy.optimize import minimize
from sklearn.linear_model import Ridge
import statsmodels.api as sm

def ordinary_least_squares():
    x=np.arange(6,dtype=float)
    design=np.column_stack([np.ones(6),x])
    y=1+2*x+np.array([1.,-1.,0.,0.,-1.,1.])
    beta=np.linalg.lstsq(design,y,rcond=None)[0]
    assert np.allclose(beta,[1,2])
    assert np.allclose(design.T@(y-design@beta),0)
    print("OLS intercept/slope:",beta)

def logistic_likelihood():
    x=np.column_stack([np.ones(8),np.arange(8)-3.5])
    y=np.array([0.,0.,1.,0.,1.,0.,1.,1.])
    objective=lambda b: np.sum(np.logaddexp(0,x@b)-y*(x@b))
    gradient=lambda b: x.T@(expit(x@b)-y)
    fit=minimize(objective,np.zeros(2),jac=gradient,method="BFGS")
    assert fit.success and np.linalg.norm(gradient(fit.x))<1e-4
    assert objective(fit.x)<objective(np.zeros(2))
    doubled_odds_probability=expit(np.log(.2/.8)+np.log(2))
    assert np.isclose(doubled_odds_probability,1/3)
    print("Logistic coefficients:",fit.x,"twice odds probability:",doubled_odds_probability)

def counts_with_exposure():
    exposure=np.array([1.,2.,3.,4.])
    counts=np.array([2.,5.,5.,8.])
    fit=sm.GLM(counts,np.ones((4,1)),family=sm.families.Poisson(),offset=np.log(exposure)).fit()
    estimated_rate=np.exp(fit.params[0])
    assert np.isclose(estimated_rate,counts.sum()/exposure.sum())
    assert np.allclose(fit.predict(offset=np.log(exposure)),2*exposure)
    print("Exposure-adjusted Poisson rate:",estimated_rate)

def shrinkage():
    x=np.array([[-2.],[-1.],[0.],[1.],[2.]])
    y=3*x[:,0]
    ridge=Ridge(alpha=10,fit_intercept=False).fit(x,y)
    assert np.isclose(ridge.coef_[0],1.5)
    print("Unpenalized slope 3; ridge slope:",ridge.coef_[0])

def main():
    ordinary_least_squares();logistic_likelihood();counts_with_exposure();shrinkage()

if __name__ == "__main__":
    main()
```

## Data science interview discussions

**Interview: What are the assumptions of linear regression?** Separate calculation, interpretation and inference. OLS always minimizes its objective when solved correctly. An unbiased coefficient interpretation needs a suitable conditional mean and exogeneity. Classical standard errors add variance and dependence assumptions; exact t inference adds normal-error assumptions. Causality requires identification beyond these algebraic conditions.

**Interview: How do you interpret a logistic coefficient of log(2)?** It doubles conditional odds per encoded unit, holding the remaining design fixed. The probability change depends on baseline probability and interactions. It is not a doubling of risk and is not inherently causal.

**Interview: Why might lasso select one of two equally useful features?** Correlated columns offer similar loss reduction, and the L1 geometry can choose sparse alternatives. The selected identity can change with small perturbations. Elastic net or stability analysis may better represent the shared predictive signal.

**Interview: Choose Poisson, negative binomial or a hurdle model.** Begin with count exposure and the generating process. Use Poisson for the basic mean-variance relation, negative binomial for extra rate heterogeneity, and a hurdle when occurrence and positive intensity are substantively separate. Validate zeros, tails and held-out predictive behavior.

## Primary sources and official APIs

- [scikit-learn linear model formulations and regularization](https://scikit-learn.org/stable/modules/linear_model.html).

- [statsmodels generalized linear models](https://www.statsmodels.org/stable/glm.html).

## Reading connections

[Previous chapter](10-multiple-testing-sequential-inference-and-selective-inference.md) | [Book contents](../README.md) | [Next chapter](12-regression-diagnostics-multilevel-models-and-longitudinal-analysis.md)
