# A causal estimate needs identification, overlap and uncertainty

Tutorial ID: `statistics-science-001`. Prerequisites: `statistics-015`, `statistics-017`, `statistics-learning-007`. Complete program: [science_01.py](examples/science_01.py).

## Specify a world before choosing an estimator

Two pretreatment covariates affect treatment and outcome. The synthetic propensity is \(e(X)=\sigma(.6X_1)\); untreated mean is \(m_0(X)=X_1^2+X_2\); treatment effect is \(1+.5X_1\). Since \(X_1\) is symmetric around zero, the population ATE is one. Assignment is conditionally randomized given X and both treatment probabilities are positive, so conditional exchangeability, consistency and positivity identify the effect in this deliberately known world.

A real analyst cannot verify those assumptions merely by fitting a good propensity model. Here the generating equations provide an oracle so the estimator can be studied separately from identification. No observational algorithm creates a missing confounder.

## Fit nuisance functions on other rows

Split 1,200 observations into three folds. For each held-out fold, train logistic propensity on the other folds and a separate response forest in each treatment arm. Predict the three nuisance quantities only on held-out rows. This produces an actual cross-fitted causal estimator rather than a disconnected demonstration of generic cross-validation.

For each observation, calculate

\[
\phi_i=\widehat m_1(X_i)-\widehat m_0(X_i)
+\frac{A_i\{Y_i-\widehat m_1(X_i)\}}{\widehat e(X_i)}
-\frac{(1-A_i)\{Y_i-\widehat m_0(X_i)\}}{1-\widehat e(X_i)}.
\]

Average these scores. Under the necessary nuisance-rate and regularity conditions, their sample SD divided by \(\sqrt n\) estimates the asymptotic SE. Cross-fitting reduces same-sample overfitting dependence; it does not guarantee those conditions for arbitrary learners.

The example gives an ATE near 1.001, score SE .071 and approximate interval [.861,1.141]. Estimated propensities range roughly .195 to .803. That overlap is favorable in this fixture. Report the distribution of scores and weights in a harder case; clipping extreme probabilities stabilizes arithmetic but can introduce bias and does not repair absent support.

## Explain double robustness algebraically

Let \(\delta_a=\widehat m_a-m_a\). Conditional bias in the score equals

\[
(\widehat e-e)\left\{\frac{\delta_1}{\widehat e}
+\frac{\delta_0}{1-\widehat e}\right\}.
\]

The complete program checks four known-function cases: both correct, only propensity correct, only outcome correct, and both wrong. The first three have zero conditional bias by construction. The deliberately misspecified fourth has average bias about -.423. This proves a bounded algebraic property of the constructed functions, not that either fitted nuisance learner is correct in real data.

## Turn hidden-confounding concern into a decision sensitivity

Suppose a practical benefit must exceed .5 and a domain argument permits positive residual bias B. Shift the estimate and both interval endpoints downward by B. At B=.25 the lower endpoint is about .611; at B=.5 it is about .361, no longer establishing the threshold. The code reports point sensitivity at B=0,.25,.5,1. This is a transparent additive bias scenario, not an identified estimate of hidden confounding. A domain model must justify plausible B values.

**Answered discussion: Is a causal forest automatically better?** A more flexible effect model can change estimation, but identification and support remain. Compare the actual target, nuisance errors, uncertainty and independent policy value before promoting a model name into causal evidence.

Continue to [longitudinal regimes](08-longitudinal-regimes-and-target-trials.md). Primary reference: [Causal Inference: What If](https://miguelhernan.org/whatifbook).
