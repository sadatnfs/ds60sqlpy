# Use baseline information without changing the causal question

Tutorial ID: `statistics-exp-007`. Prerequisites: `statistics-exp-006`, `statistics-011`, `statistics-014`. Complete example: [experiment_07.py](examples/experiment_07.py).

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

Continue to [monitoring](08-monitoring-and-multiplicity.md). Primary source: [original CUPED paper](https://ai.stanford.edu/~ronnyk/2013-02CUPEDImprovingSensitivityOfControlledExperiments.pdf).
