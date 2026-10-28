## Define the target before the estimator

A scientific result needs an intervention, outcome, population and time horizon. An **estimand** is the mathematical quantity that those choices identify. An **estimator** is the rule used to calculate a number from observed data. A software package can implement an estimator correctly while estimating the wrong quantity for a decision. This tutorial starts with a small population whose mechanisms are completely known, so the distinction can be checked independently of an algorithm.

Let \(A\) denote a binary intervention, \(X\) a pretreatment stratum and \(Y^a\) the outcome under intervention \(a\). Define \(m_a(x)=\mathbb{E}[Y^a\mid X=x]\). The stratum-specific effect is \(m_1(x)-m_0(x)\). For a chosen target distribution \(p_T(x)\), its average is

\[
\tau_T=\sum_x p_T(x)\{m_1(x)-m_0(x)\}.
\]

The target weights describe people or units in the target population, not treatment propensities or numerical convenience. To identify this expression from an observational sample, consistency, conditional exchangeability and treatment positivity are needed. Transport from a separate study additionally requires suitable conditional outcome or effect comparability and overlap between study and target covariates. The finite synthetic table below supplies the potential-outcome means directly; it demonstrates standardization arithmetic, not evidence that those assumptions hold in a real study.

## Worked case 1: one mechanism, two populations

The untreated means are one and five in two strata. Treated means are three and six. The effects are therefore two and one. A study population containing 80% of the first stratum has effect \(.8(2)+.2(1)=1.8\). A target population containing only 20% of the first stratum has effect \(.2(2)+.8(1)=1.2\). Nothing about the intervention's stratum-specific behavior changed. The population composition changed.

The `standardize` function requires matching vector shapes, nonnegative weights and a total of one. These validations are scientific contracts: silently normalizing arbitrary counts could conceal that the intended target was never supplied. The assertion that adding the same constant to both potential-outcome means leaves the effect unchanged checks the contrast itself. It would fail for a ratio estimand, reminding us that additive and multiplicative targets are distinct.

When reporting a transported effect, retain the target population definition and weights. A later demographic change can alter the population average even if all conditional effects remain stable. An effect estimate without that information is difficult to reuse responsibly. Choosing weights after seeing which population produces the most favorable result changes the question and should be disclosed.

## Worked case 2: a crude comparison reverses the conclusion

Now suppose observed treated units are 90% in the low-baseline stratum, while controls are 90% in the high-baseline stratum. Their crude outcome means differ negatively, even though the treatment effect is positive in both strata. The program constructs this comparison separately from the target effect and asserts that their signs differ. This is a controlled example of confounding by composition, often described through Simpson's paradox.

The remedy is not an automatic rule to adjust for every available column. Adjustment must use an appropriate set of pretreatment variables. Conditioning on a collider or a treatment-induced mediator can create a different bias or change the estimand. A causal graph and the timing of measurements help justify which variables belong in the analysis. Flexible prediction does not itself settle that choice.

## Diagnose assumptions and data requirements

Start a real analysis with a table describing the observation unit, eligibility, treatment versions, follow-up horizon and missing-data process. Ask whether the target distribution is measured, whether all important target strata appear in the study, and whether the intervention means the same thing in both places. A model can return predictions for an absent stratum, but those are extrapolations rather than empirical comparisons.

The example contains no sampling error because it supplies a complete finite mechanism. Real standardization also estimates conditional means and possibly target weights. Its uncertainty calculation should account for those estimation steps and for clustering or repeated units. Reporting a narrow interval from the crude sample while using a transported point estimate would combine incompatible procedures.

## Answered scientific discussion

**Does a larger study automatically transport better?** No. More observations can improve precision inside its support while leaving a target subgroup completely unrepresented. A transparent sensitivity analysis for effect modification may be more useful than another decimal place in an extrapolated estimate.

**What should an analyst deliver?** Supply both the conditional effects and the target-weighted result, define the intervention and horizon, describe identification assumptions, and show how the conclusion changes under relevant target populations. The complete program provides independently inspectable arithmetic for those distinctions. Its positive causal effects are built into the fixture; observational evidence would have to justify them.
