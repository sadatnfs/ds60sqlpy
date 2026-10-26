# From Bernoulli likelihood to interval coverage

Tutorial ID: `statistics-learning-002`. Prerequisites: `statistics-learning-001`, `statistics-004`, `statistics-008`. Complete program: [learning_01.py](examples/learning_01.py).

## Separate data, parameter and estimator

Suppose independent trials share an unknown success probability \(p\). The observed sequence is fixed while we compare possible parameter values. For \(s\) successes in \(n\) trials, the likelihood is proportional to \(p^s(1-p)^{n-s}\). It is a function of the parameter, not a probability distribution over parameters. A prior plus likelihood would define a Bayesian posterior instead.

Taking logarithms turns products into sums:

\[
\ell(p)=s\log p+(n-s)\log(1-p),\quad
\ell'(p)=\frac{s}{p}-\frac{n-s}{1-p}.
\]

For an interior solution, setting the score to zero gives \(\widehat p=s/n\). When \(s=0\) or \(s=n\), the maximizer is on the boundary and the interior differentiation argument must be modified. The success count is sufficient for the common probability under this model; the ordering could still matter for diagnosing a violated independence assumption.

## Curvature connects the model to precision

Expected negative second derivative gives Fisher information \(I_n(p)=n/[p(1-p)]\). A regular large-sample approximation suggests variance \(p(1-p)/n\), estimated by plugging in the fitted probability. This is a connection between likelihood curvature and repeated-sample precision under the model, not a universal rule that any steep objective implies a calibrated interval.

With one success in 12 trials, the estimate is .0833. The ordinary Wald interval uses this plug-in SE and can extend below zero. Clipping the endpoint to zero makes the printed interval legal but does not fix its coverage. In particular, zero observed successes produce zero estimated variance and the degenerate Wald interval [0,0].

## Invert a score comparison

The Wilson interval solves the inequality

\[
\frac{(\widehat p-p)^2}{p(1-p)/n}\le z_{.975}^2
\]

for candidate values of \(p\), using the null candidate's variance rather than the estimate's variance. Its center is \((\widehat p+z^2/(2n))/(1+z^2/n)\); its halfwidth follows from the quadratic formula. The program calculates both intervals and shows that Wilson has a positive lower bound for the one-success example.

## Evaluate the procedure, not one interval

At a declared true probability .05, enumerate every possible count from zero through 12. Weight each count's coverage indicator by its exact binomial probability. This calculates the coverage of the complete procedure without Monte Carlo noise. Wilson covers much more often than the Wald interval in this setting. Wilson is still an approximation and can have coverage above or below .95 at other probabilities because counts are discrete.

The example's oracle is available only because the data-generating probability is specified. In real data, inspecting the realized interval cannot reveal whether it contains the unknown truth. Robustness analysis should change meaningful assumptions, such as shared latent probabilities or repeated users, not merely rerun the same calculation with another seed.

**Answered discussion: Does a more sophisticated interval fix selected data?** No. If only successful visits are logged, both likelihood and interval analyze a distorted population. Fix the observation model and estimand before selecting an uncertainty formula.

Continue to [logistic regression](03-logistic-model-to-decision.md). Related chapter: [estimation](../../chapters/08-estimation-and-statistical-inference.md). Reference: [NIST proportion intervals](https://www.itl.nist.gov/div898/handbook/prc/section2/prc241.htm).
