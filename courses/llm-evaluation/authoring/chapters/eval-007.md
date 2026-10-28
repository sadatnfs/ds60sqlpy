## A collection of tests is one decision procedure

An evaluation often compares several models, prompts, datasets and metrics. It may also be inspected repeatedly while labels arrive. A per-test threshold does not describe the error behavior of the whole procedure. The relevant family should follow the claims and decisions being made, not whichever grouping produces the smallest adjustment.

For events \(E_j\) representing false rejections, the union bound gives

\[
P\left(\bigcup_{j=1}^{m}E_j\right)\leq\sum_{j=1}^{m}P(E_j).
\]

If each fixed analysis uses a valid p-value under its null and thresholds \(\alpha_j\) have a prespecified sum at most \(\alpha\), this controls the probability of at least one false rejection in that family. Independence is not required for the bound. Validity of the individual tests is still required: adjustment does not repair data leakage, a wrong sampling unit or a post-hoc hypothesis invented from the final labels.

A threshold-crossing event is also different from a decision to deploy. An improvement too small to matter can be statistically detectable, while an uncertain critical-risk condition may still block a release. Retain effect sizes, practical margins, uncertainty and operational gates separately.

## Worked case A: three opportunities for a false alarm

For three independent continuous uniform p-values under their nulls, testing each at 0.05 gives a family error probability of \(1-0.95^3\), approximately 0.143. Equal Bonferroni allocation uses 0.05 divided by three and has a probability below 0.05 in this independent illustration. Real repeated looks at accumulating data are correlated; the independent calculation is an explanatory contrast, not their exact operating characteristic.

The decision function below uses the declared number of hypotheses even if one p-value is missing. Reducing the family size after excluding an inconvenient result would change the procedure. Missing assessments remain explicit and cannot be interpreted as passed conditions.

{{WORKED_A}}

## Worked case B: spending across declared looks

The second case allocates 0.01,0.015 and 0.025 to three fixed monitoring times. Their sum is 0.05. A p-value of 0.02 at the first look does not cross its allocated threshold, even though it is below 0.05. The same p-value can cross the third threshold under this declared rule. This is a conservative spending example, not an implementation of an always-valid confidence sequence.

{{WORKED_B}}

## What optional stopping changes

A fixed-sample p-value evaluated only at a prespecified sample size has a different interpretation from the smallest p-value seen across arbitrary stopping times. You may use a valid group-sequential design, a confidence sequence, an e-process or another method whose assumptions match continuous monitoring. The choice must be made and explained before its favorable result is used. Repeatedly applying an ordinary test until it passes is not such a method.

Do not mix a rule calibrated for cumulative data with a sequence of independently selected subsets without reviewing its assumptions. Similarly, observing early outcomes can affect later enrollment, exposure or annotation. That feedback can change the population and invalidate an analysis that assumed a fixed, unaffected sampling process.

## Diagnosis and transfer

Start a release notebook by listing all candidate models, primary and secondary metrics, error-control goals, look times and practical thresholds. Classify exploratory findings honestly and reserve independent data for confirmation. A useful discovery can motivate a later study without being relabeled as a prespecified success.

The programs enforce bounded probabilities and explicit budgets. They demonstrate arithmetic and decision logic on authored p-values; they do not manufacture a valid p-value for an LLM benchmark. The paired and clustered methods from the previous unit still need the appropriate null and dependence assumptions. Preserve the entire monitoring history so a reviewer can reconstruct why the decision was made.
