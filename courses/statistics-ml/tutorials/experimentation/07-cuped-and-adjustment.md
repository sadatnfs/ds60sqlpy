# Use baseline information without changing the causal question

Tutorial ID: `statistics-exp-007`. Prerequisites: `statistics-exp-006`, `statistics-011`, `statistics-014`. Complete example: [experiment_07.py](examples/experiment_07.py).

## Key terms

- **CUPED:** A variance reduction that subtracts \(\theta\) times the centered pretreatment covariate from the outcome, with \(\theta=\operatorname{Cov}(X,Y)/\operatorname{Var}(X)\).
- **Prognostic covariate:** A pretreatment variable that predicts the outcome; the stronger the prediction, the larger the precision gain from adjustment.
- **Treatment-covariate interaction:** A regression term multiplying treatment by the centered covariate, so baseline slopes can differ by arm while the treatment coefficient remains the average contrast.
- **HC2 covariance:** A heteroskedasticity-robust variance estimate that divides each squared residual by one minus its leverage instead of assuming a common residual variance.

## Remove predictable noise

Users differ greatly before the page experiment. A pretreatment activity measurement can explain outcome variation that random assignment did not cause. Adjustment can make the treatment comparison more precise while preserving its assignment target under the appropriate design and estimation conditions.

For a scalar baseline \(X\), define \(Y^*=Y-\theta(X-\mu_X)\). With a fixed coefficient and correct centering,

\[
\operatorname{Var}(Y^*)=\operatorname{Var}(Y)+\theta^2\operatorname{Var}(X)
-2\theta\operatorname{Cov}(X,Y).
\]

Differentiation gives \(\theta=\operatorname{Cov}(X,Y)/\operatorname{Var}(X)\), assuming positive covariate variance. The optimized variance is \(\operatorname{Var}(Y)(1-\rho^2)\). This identity describes outcome variance. To infer a treatment effect, one must also specify how coefficients are estimated and how the adjusted contrast's uncertainty is calculated.

## Trace a realized contrast

Suppose raw treatment-control value differs by 1.8 and treatment users have baseline mean .1 higher. If a coefficient of four is fixed using independent historical evidence, adjustment subtracts \(4(.1)=.4\), producing 1.4. The realized estimate changes because randomization balanced baseline only in expectation. This does not automatically mean the estimand changed.

The complete fixture has baseline imbalance about .0201. The code checks the exact fixed-coefficient relationship between the raw difference and the residualized difference. Centering on a common mean cancels in an arm contrast; centering each arm separately would erase this imbalance correction and leave the raw difference unchanged.

## Estimate the coefficient and its uncertainty

The second calculation fits an interacted regression

\[
Y_i=\beta_0+\tau A_i+\beta_X(X_i-\bar X)
+\beta_{AX}A_i(X_i-\bar X)+\epsilon_i.
\]

At the common covariate center, the treatment coefficient represents the fitted average contrast. Interactions allow baseline slopes to differ. The program uses HC2 covariance rather than treating the fitted coefficient as known or assuming common residual variance. This is an asymptotic robust analysis, not an exact guarantee for every randomized design or tiny sample.

For this fixture, the raw effect is about 1.584 with SE .623. The adjusted effect is about 1.504 with HC2 SE .158, giving an approximate interval [1.194,1.813]. The synthetic target is 1.6. The example demonstrates a large precision gain from a strongly prognostic baseline, with a real two-arm comparison and an explicit variance procedure. One interval containing the oracle does not establish a coverage rate.

## Missing history and harmful adjustment

New users may have no preperiod record. Dropping them changes the population. Filling missing history with zero without an indicator equates unavailable history with observed zero activity. A defensible design can center/impute from pretreatment information, include missing-history indicators and interactions, and report subgroup support. Flexible nuisance functions may require cross-fitting and a variance method matched to that estimator.

Post-treatment visits are different: the interface may change them. Adjusting for visits can remove part of the policy effect or induce selection bias. A predictive covariate is not automatically an admissible causal covariate.

**Answered discussion: Must adjusted estimates always be closer to the true effect?** No. Precision is a repeated-procedure property. A well-designed adjustment can still move an individual estimate away from the truth. Compare its sampling behavior under plausible scenarios and report the method chosen before seeing which answer looks better.

## Worked example: estimate theta and the variance it removes

This block computes the CUPED coefficient from pooled data and applies it with a common center. Append it to [experiment_07.py](examples/experiment_07.py).

```python prelude=examples/experiment_07.py
users, _, _, _ = experiment_fixture()
x, y, a = users.baseline, users.value, users.assigned
theta = np.cov(x, y, ddof=1)[0, 1] / x.var(ddof=1)
rho2 = np.corrcoef(x, y)[0, 1] ** 2
y_star = y - theta * (x - x.mean())
est, se, _ = welch_summary(y_star[a == 1], y_star[a == 0])
print(f"theta={theta:.3f} rho^2={rho2:.3f} variance kept={1 - rho2:.3f}")
print(f"CUPED estimate={est:.3f} se={se:.3f}")
```

```text
theta=3.980 rho^2=0.913 variance kept=0.087
CUPED estimate=1.504 se=0.159
```

The estimated slope, 3.980, is close to the generating coefficient of four, and baseline explains about 91% of outcome variance. Keeping 8.7% of the variance should shrink the SE by about \(\sqrt{0.087}\approx0.30\); indeed 0.159 is about a quarter of the raw 0.623. The match is approximate because the pooled \(\rho^2\) mixes both arms, including their mean shift, while the SE depends on within-arm variances. The adjusted estimate equals the interacted-regression estimate of 1.504 to three decimals because the slopes barely differ by arm. Estimating theta from the same outcomes adds a small amount of uncertainty that this Welch SE ignores; the HC2 regression in the main example accounts for it.

## Worked example: adjusting for a post-treatment variable

Suppose an analyst adds an engagement score measured after assignment. Here engagement rises with the treatment effect itself, which is the defining feature of a mediator.

```python
users, _, _, effect = experiment_fixture()
rng = np.random.default_rng(707)
engagement = users.baseline + users.assigned * effect + rng.normal(0, 0.5, len(users))
a = users.assigned.to_numpy()
x = users.baseline - users.baseline.mean()
for label, cols in [("baseline", [a, x]), ("post-treatment", [a, x, engagement])]:
    fit = sm.OLS(users.value, sm.add_constant(np.column_stack(cols))).fit(cov_type="HC2")
    print(f"adjust for {label:14s}: treatment coef={fit.params.iloc[1]:.3f}")
```

```text
adjust for baseline      : treatment coef=1.504
adjust for post-treatment: treatment coef=0.621
```

Adding engagement cuts the treatment coefficient from 1.504 to 0.621. Nothing about the redesign changed; the regression now asks what treatment does holding engagement fixed, and engagement is one of the paths through which the redesign works. The coefficient on engagement absorbs most of the effect. A diagnostic is to regress each candidate covariate on assignment: a pretreatment variable should show no systematic arm difference, while engagement here differs by about 1.6 by construction.

## When CUPED gains little

If baseline and outcome correlate weakly, \(1-\rho^2\) stays near one and the adjustment mostly adds estimation noise. New users without history, a changed metric definition between periods, or a seasonal shift can all break the correlation that made the preperiod useful.

Continue to [monitoring](08-monitoring-and-multiplicity.md). Primary source: [original CUPED paper](https://ai.stanford.edu/~ronnyk/2013-02CUPEDImprovingSensitivityOfControlledExperiments.pdf).
