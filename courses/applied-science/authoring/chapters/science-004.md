## Different adoption times create different comparisons

A two-period difference-in-differences calculation compares the change in a treated group with the change in an untreated group. With staggered adoption, a unit can be untreated at one time and treated later. A regression that mechanically uses all other units as controls can therefore compare a newly treated group with a group whose treatment effect is already evolving.

Let \(G_i\) be the first treatment period and let \(Y_{it}\) be the observed outcome. For cohort \(g\) at time \(t\ge g\), a group-time contrast uses the last pretreatment baseline \(g-1\) and an eligible comparison group:

\[
\widehat{\operatorname{ATT}}(g,t)
=\overline{Y_t-Y_{g-1}}_{G=g}
-\overline{Y_t-Y_{g-1}}_{G>t}.
\]

The displayed expression is the simple unconditional comparison used by our fixture. Identification requires a suitable parallel-trends assumption, no anticipation, well-defined treatment and overlap. Conditional approaches may require additional outcome or propensity modeling. The formula is not a claim that every staggered design is identified by unconditional averaging.

## Worked case 1: recover cohort-specific dynamic effects

The six synthetic units belong to an early cohort adopting at time two, a later cohort adopting at time four, and a never-treated group. Untreated outcomes combine a unit intercept with a common linear time trend. Treatment effects begin at two and grow by two per exposed period. These mechanisms deliberately satisfy the simple identifying assumptions.

At time four, the early cohort's effect is six and the later cohort's effect is two. The function selects controls with \(G>t\), so neither cohort uses an already treated unit as an untreated comparison. The code recovers both effects exactly. It also verifies that the early cohort's first-period effect is two, checking the event-time indexing.

An event-time summary averages different cohort-time cells at a common number of periods since adoption. The available cohorts may differ at longer horizons. A plotted curve can therefore change because treatment effects evolve, because the composition of represented cohorts changes, or both. Report the aggregation weights and the support behind each horizon. Do not connect unsupported horizons with a smooth curve that implies evidence.

## Worked case 2: an already-treated control erases the effect

For the newly treated cohort at time four, the observed outcome change is three: one unit of background trend and two units of treatment effect. The early cohort also changes by three because its existing treatment effect grows by another two. Subtracting the early cohort's change produces zero, even though the new cohort's treatment effect is two.

This is a direct numerical demonstration of a contaminated comparison. It does not prove that every two-way fixed-effect estimate is biased in the same direction. The mixture of comparisons and weights depends on adoption timing, treatment-effect heterogeneity and specification. The lesson is to inspect which units act as controls for each contrast and what causal quantity their differences can identify.

The function refuses a comparison with no eligible controls, no target cohort or a time before adoption. A common implementation error is to substitute all other units when eligible controls vanish. That produces an answer by changing the comparison, not by recovering missing support.

## Diagnostics that support a design

Pretreatment outcomes can reveal incompatible trends, coding errors or anticipation. A nonsignificant pretrend test does not prove parallel trends: it may have low power, and the post-treatment counterfactual remains unobserved. Examine effect sizes and uncertainty, substantively relevant violations, timing definitions and selection into the analysis population.

Treatment can change covariates, survival in the sample or observation intensity. Conditioning on those post-treatment variables may undermine the intended contrast. Record whether the panel is balanced, why units enter or leave, and whether calendar effects differ across cohorts. Inference usually needs to respect the assignment level and serial dependence, often through clustered resampling or a design-specific procedure rather than treating every row as independent.

## Answered scientific discussion

**Can we average the two recovered effects into four?** Only after specifying weights and the target. An equal-cohort average, an equal-unit average and an event-time average can differ in a real unbalanced panel. The numerical average is easy; the scientific interpretation requires the weighting rule.

**What does this program establish?** It shows that eligible-control group-time contrasts recover known effects under the constructed mechanism, and that one clearly invalid comparison fails. An external policy study still needs an argument for identification, appropriate uncertainty and a transparent aggregation strategy.
