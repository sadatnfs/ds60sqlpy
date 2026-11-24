# Estimate the effect and decide what its interval supports

Tutorial ID: `statistics-exp-006`. Prerequisites: `statistics-exp-004`, `statistics-exp-005`, `statistics-008`. Complete example: [experiment_06.py](examples/experiment_06.py).

## Key terms

- **Welch interval:** An interval for a difference in means that uses separate arm variances and Welch-Satterthwaite degrees of freedom.
- **Minimum practical benefit:** The smallest effect that matters for the decision, .5 points here, which the lower interval bound must exceed to establish benefit.
- **Ratio contrast:** A comparison of per-arm ratios such as value per visit, whose standard error must preserve the numerator-denominator covariance within each arm.
- **Delta method:** A linearization that converts numerator and denominator variability into an approximate standard error for a ratio.
- **Equivalence test:** Two one-sided tests that show the difference lies inside prespecified margins such as plus or minus .5, rather than accepting a nonsignificant null.

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

## Worked example: equivalence and noninferiority from one estimate

The same Welch machinery answers similarity questions once the margin is set. Run this in [experiment_06.py](examples/experiment_06.py); `alpha=0.10` produces the 90% interval used by two one-sided tests.

```python
users, _, _, _ = experiment_fixture()
t, c = users[users.assigned == 1], users[users.assigned == 0]
est, se, ci90 = welch_summary(t.value, c.value, alpha=0.10)
print("90% interval:", np.round(ci90, 3))
print("equivalent within 0.5:", bool(-0.5 < ci90[0] and ci90[1] < 0.5))
print("noninferior at -0.5:", bool(ci90[0] > -0.5))
```

```text
90% interval: [0.554 2.613]
equivalent within 0.5: False
noninferior at -0.5: True
```

The 90% interval, [0.554, 2.613], sits entirely above the noninferiority margin of -0.5, so the redesign is not worse by more than half a point. It is not equivalent to control, because the upper end exceeds 0.5 by a wide margin: the data suggest a real increase. Notice that the 90% lower bound clears the practical threshold of 0.5 even though the 95% lower bound, 0.356, does not. That is not a loophole. A superiority claim against a margin at one-sided .025 uses the 95% bound; using the 90% bound would be a one-sided .05 test, and that error rate must be chosen before looking.

## Worked example: one extreme user moves everything

Mean differences have no protection against a single extreme record. Add 200 points to the first treated user and rerun the primary analysis.

```python
users, _, _, _ = experiment_fixture()
spiked = users.copy()
first_treated = spiked.index[spiked.assigned == 1][0]
spiked.loc[first_treated, "value"] += 200
for label, rows in [("clean", users), ("one +200 user", spiked)]:
    est, se, ci = welch_summary(
        rows.loc[rows.assigned == 1, "value"], rows.loc[rows.assigned == 0, "value"]
    )
    print(f"{label:14s} estimate={est:6.3f} se={se:.3f} ci={np.round(ci, 3)}")
```

```text
clean          estimate= 1.584 se=0.623 ci=[0.356 2.812]
one +200 user  estimate= 3.250 se=1.780 ci=[-0.269  6.77 ]
```

The estimate roughly doubles, from 1.584 to 3.250, because 200/120 adds about 1.67 to the treatment mean. The SE nearly triples, so the interval now includes zero. A single bot, test account or logging bug can both inflate the point estimate and erase significance. The fix belongs in the prespecified plan: a capping rule chosen from pretreatment data, a bot filter applied identically by arm, or a robust estimand such as a trimmed mean that is reported as a different target. Deciding after seeing the spike is outcome-dependent analysis.

## Checks before reading the primary interval

Confirm the analysis window matches the plan, inspect the largest few user values in each arm, and compare the Welch SE with a user bootstrap on the primary metric as well as the ratio. A large disagreement between the two usually traces back to tails or to a handful of influential users.

Continue to [adjustment](07-cuped-and-adjustment.md). Primary reading: [online controlled experiments](https://assets.cambridge.org/97811087/24265/toc/9781108724265_toc.pdf).
