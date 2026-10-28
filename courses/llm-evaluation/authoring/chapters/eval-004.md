## Agreement has several denominators

Two annotators can disagree because an item is ambiguous, because their instructions differ, because one makes mistakes, or because the target concept itself is underspecified. The agreement table organizes those possibilities but cannot decide among them. Begin with a cross-tabulation, not one summary coefficient.

For two categorical annotators, observed agreement \(p_o\) is the fraction of paired labels that match. Cohen's kappa uses the agreement \(p_e\) implied by the two empirical marginal label frequencies:

\[
\kappa=\frac{p_o-p_e}{1-p_e},\qquad
p_e=\sum_c p_{A,c}p_{B,c}.
\]

The correction defines a reference model. It does not mean that people literally guess independently according to their observed marginals. A large kappa is evidence about agreement under that convention, not proof that the labels represent the intended scientific construct.

If both reviewers assign the same category to every item, observed agreement is one and the denominator is zero. Kappa is undefined in that degenerate table. Returning one would conceal the absence of variation; returning zero would invent disagreement. The program raises an explicit error and reports the raw agreement separately.

## Worked case A: calculate the complete table

For labels `[1,1,0,0]` and `[1,0,0,0]`, observed agreement is three quarters. The first annotator's positive frequency is one half and the second's is one quarter, so expected agreement is one half. Kappa is therefore one half. The result follows from the table rather than an arbitrary threshold label such as good or bad.

The second comparison retains a 90% raw agreement while changing marginal prevalence. Kappa changes because its reference agreement changes. When comparing studies, inspect the sample composition, category prevalence and annotation protocol before interpreting a difference in coefficients as better annotator training.

{{WORKED_A}}

## Worked case B: distance matters for ordinal labels

A level 0 versus level 2 disagreement may be more serious than level 1 versus level 2. An ordinal disagreement measure can assign squared distance normalized by the square of the maximum category gap. This example computes the observed weighted disagreement only. It does not silently call that quantity weighted kappa, which would additionally need its own marginal-based expected disagreement.

{{WORKED_B}}

## From coefficients to a useful study

Report the paired count, missing-label policy, confusion matrix, marginal proportions and uncertainty. If prompts share families, bootstrap families when that is the sampling unit. Resampling individual labels as if repeated variants were independent can make the interval too narrow. With very few families, a numerical bootstrap interval is weak evidence regardless of how many resamples are requested.

For more than two reviewers or varying missingness, other reliability coefficients use different coincidence or variance models. Krippendorff's alpha can accommodate incomplete annotation designs with a declared distance function; an intraclass correlation may fit continuous measurements under an appropriate random-effects model. These names are not interchangeable, and this unit does not implement those estimators. Read their assumptions before selecting one.

## Diagnose validity separately

Imagine both reviewers label every answer containing a citation marker as supported. Their agreement could be perfect while both are wrong about actual entailment. Validate the rubric using calibrated evidence and counterexamples. Conversely, adjudication can create one final label while leaving genuine uncertainty about ambiguous items. Retain the original labels and reasons so downstream analyses can examine sensitivity to disputed cases.

When the cost of an error is asymmetric, review the kinds of disagreements rather than only their frequency. A missed unsupported claim and a harmless formatting disagreement may need different follow-up even if they count equally in kappa. The reference programs establish arithmetic, category validation and a degeneracy policy on authored labels, not a universal standard for human reliability.
