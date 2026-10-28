## A pairwise objective encodes a comparison

Pairwise ranking learns that one item should score above another for a given context. A pair should therefore have a defensible interpretation. A positive historical interaction and an unobserved item do not automatically form a known preference pair. Exposure, observation windows and sampling policy determine what the training comparison means.

For a linear score \(s(x)=\mathbf w^{\mathsf T}x\), let \(d=x^+-x^-\) be a positive-minus-negative feature difference. A regularized pairwise logistic objective is

\[
\mathcal L(\mathbf w)=\frac{1}{n}\sum_i\log\{1+\exp(-d_i^{\mathsf T}\mathbf w)\}
+\frac{\lambda}{2}\|\mathbf w\|^2.
\]

The implementation uses `logaddexp` for the loss and the logistic function for its gradient. Computing a naive exponential at a very large margin can overflow even when the mathematical loss is finite. Numerical stability is part of a correct implementation, but it does not validate the sampled comparisons.

## Worked case 1: learn and independently check the gradient

Three synthetic pair differences have known positive directions. Starting from zero weights gives equal scores and a loss near the logarithm of two. Gradient descent lowers the objective and makes every training margin positive. The code verifies both properties.

An independent central finite-difference calculation checks each gradient component at the fitted weight vector. This compares the analytic derivative with the actual implemented scalar objective. It would catch a reversed pair sign, omitted regularization term or incorrect averaging factor. The step size is small enough for this smooth, moderate-scale fixture; a finite-difference check itself can fail numerically at unsuitable scales or nondifferentiable points.

The learned weights are not probabilities of user preference unless a suitable probabilistic interpretation and calibration procedure are established. They produce scores under a particular training objective. A lower training loss also does not establish better ranking on new users, items or time periods.

## Worked case 2: a future positive is not a known negative

The second fixture contains four exposures and two positive events, each with an availability time. At cutoff five, only the first positive is known. The sampler requires a three-unit attribution window plus a declared two-unit maximum reporting delay before treating an exposed item as a candidate negative. It therefore admits only i3. At cutoff nine, i3 and i4 are eligible, while the delayed positive for i2 has arrived and excludes that item. Merely subtracting currently known positives from the catalog would incorrectly label immature exposures as negatives.

This example separates two uncertainties: whether an item was exposed and whether its response window has matured. A defensible negative-sampling scheme might sample from displayed-but-unclicked items after an explicit attribution window, or it might treat unobserved items as noisy negatives under a stated learning objective. Those are different assumptions, not interchangeable labels.

Changing the negative-sampling distribution changes which comparisons dominate learning. Popular-item negatives, hard negatives and uniformly sampled items can lead to different objectives and different evaluation behavior. A harder training task is not automatically a more valid one. Keep the sampling mechanism reproducible and evaluate against the intended serving candidate set.

## Design evaluation around queries and time

Ranking metrics are usually defined per query or user context. Resampling individual item rows can break those groups and produce overly optimistic uncertainty. Preserve the query unit when comparing models, and account for repeated users or correlated sessions when those structures matter.

Split before feature construction, candidate mining and hyperparameter choice. A model can leak test information through vocabulary, item statistics, hard-negative mining or an index built from future interactions, even when its final fitting function sees only training labels. Record the entire procedure being evaluated.

A system may need constraints on diversity, eligibility, repetition or provider exposure. Adding those constraints after optimizing a pairwise model changes the delivered ranking. Evaluate the resulting combined policy, not only the unconstrained scorer. Business utility, safety and calibration should be reviewed alongside relevance metrics.

## Answered scientific discussion

**Does a positive margin for every training pair prove the recommendation is good?** It proves that the supplied comparisons are ordered in-sample. Those comparisons may be biased, sparse or unrepresentative, and their features may not be available at serving time.

**Why compare a gradient with finite differences when an autodiff library is available?** A finite-difference check can validate the intended objective and reduction against an independent calculation. Autodiff faithfully differentiates the program supplied to it, including an incorrectly signed or incorrectly weighted objective.
