# Estimate the effect and decide what its interval supports

Tutorial ID: `statistics-exp-006`. Prerequisites: `statistics-exp-004`, `statistics-exp-005`, `statistics-008`. Complete example: [experiment_06.py](examples/experiment_06.py).

## Freeze the question and analysis time

Assume assignment, measurement and outcome maturity have passed their defined checks. Analyze the prespecified seven-day value outcome after the fixed enrollment and follow-up window. One row represents one independently assigned user. A confidence interval describes sampling uncertainty under its statistical assumptions; it does not repair an eligibility or instrumentation defect.

For independent arm means, estimate \(\widehat\tau=\bar Y_T-\bar Y_C\) and

\[
\widehat{\operatorname{SE}}(\widehat\tau)
=\sqrt{\frac{s_T^2}{n_T}+\frac{s_C^2}{n_C}}.
\]

The example uses the Welch-Satterthwaite degrees of freedom from [chapter 09](../../chapters/09-hypothesis-tests-and-group-comparisons.md), avoiding an unmotivated pooled-variance assumption. A t critical value is an approximation for these nonnormal outcomes, not a universal exact result.

## Work the primary result

The treatment-control estimate is about 1.584 points per user, SE .623, with 95% interval [0.356, 2.812]. Zero is excluded, but a minimum practical benefit of .5 is not excluded on the low side. The result supports a positive difference under the model; it remains inconclusive against the stricter business threshold. Report those as separate statements rather than converting statistical significance into a launch command.

Had the interval been [-.2, 2.8], it would include both harm and meaningful benefit. Saying no effect would overstate the evidence. Conversely, a tiny but precise effect can be statistically clear and operationally unhelpful.

## Work a ratio contrast

Compute total value divided by total visits separately in each arm. Their difference is about .123 points per visit. The user-level delta-method SE is about .359, much larger than the effect. This ratio result does not contradict the primary value-per-user result; visits supply a different denominator and the ratio is noisier.

For independent arms, add the two ratio variance estimates. Within each arm, preserve numerator-denominator covariance through the influence contribution from unit 02. The example also resamples complete user rows within each arm 600 times, recomputing both ratios. Its bootstrap SE is about .361, close to the delta SE for this fixture. Agreement between two approximations on one dataset does not prove either one's coverage under rare denominators or severe tails.

## Similarity requires its own target

Equivalence does not mean accepting a nonsignificant null. If differences within plus or minus .5 are acceptable, two one-sided tests at .05 correspond to an appropriate 90% interval inside those margins. An interval [-.1,.1] satisfies this rule; [-2,2] does not, although both contain zero. Noninferiority excludes deterioration beyond one margin and answers a different question.

**Answered discussion: Why not stop once this interval excludes zero?** That creates an outcome-dependent stopping rule. The reported interval would then belong to a different procedure from the fixed-horizon one used to justify it. Use the monitoring design in unit 08, or preserve the fixed horizon and treat interim displays according to the prespecified plan.

Continue to [adjustment](07-cuped-and-adjustment.md). Primary reading: [online controlled experiments](https://assets.cambridge.org/97811087/24265/toc/9781108724265_toc.pdf).
