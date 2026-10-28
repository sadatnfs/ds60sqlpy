## Evaluate the evaluator

A model judge can help scale annotation, but its outputs remain measurements with error. A benchmark result depends on the judge model, rubric, prompt, candidate presentation, reference material and aggregation rule. A judge that repeats the same decision reliably can still prefer longer text, familiar style or the first displayed answer. Repeatability alone is not validity.

In a paired comparison, distinguish candidate identity from display position. If candidate A is shown on the left, a left win favors A; if A is shown on the right, that same left win favors B. Failing to invert the outcome after swapping positions produces an incorrect identity-level score. Counterbalancing makes position effects observable, although it does not automatically remove every interaction between position and answer quality.

Research on model judges motivates audits of order, verbosity and related presentation effects. The examples here do not call a judge model. They use deliberately authored judge decisions so the accounting and failure modes can be checked independently of a particular model's behavior.

## Worked case A: an always-left judge

The same pair is displayed in both orientations. An always-left judge gives candidate A a win in one orientation and a loss in the other, averaging one half. Its identity-level decisions are inconsistent under the swap even though its position behavior is perfectly consistent. A quality-sensitive authored judge that prefers A in both orientations has identity consistency one.

{{WORKED_A}}

## Worked case B: calibration does not imply discrimination

For probabilistic judgments \(p_i\) and binary reference labels \(y_i\), the Brier score is

\[
\operatorname{BS}=\frac{1}{n}\sum_i(p_i-y_i)^2.
\]

A binned calibration error compares mean probability and observed frequency within bins, weighting each absolute gap by its bin size. This helper places an internal boundary in the higher bin, with probability 1 included in the last bin. Its value depends on bin boundaries and finite sample noise; it is not a complete proper scoring rule. A constant 0.5 predictor on balanced labels can have zero binned calibration error while having no useful discrimination. The code contrasts that case with more informative probabilities.

{{WORKED_B}}

## Build a calibration protocol

Use adjudicated labels or another justified reference set to assess the judge. Fit any calibration mapping on development data, freeze it, and evaluate it on separate items. With repeated variants, split by the relevant family before fitting the mapping. Otherwise a well-calibrated development curve can hide overfitting to familiar prompts.

Report probability quality, label accuracy, abstentions and disagreement with humans separately. Confidence intervals must respect paired or clustered observations. When human labels are themselves uncertain, describe their protocol and examine sensitivity to disputed items. A judge should not be promoted to ground truth merely because its name or parameter count suggests authority.

## Counterexamples and diagnosis

Swap order while preserving exact answer text. Then change length without adding information, or change formatting while retaining the same factual claims. These interventions test particular invariances; they do not establish universal fairness. Preserve the original outputs and every intervention so a reviewer can reproduce the comparison.

If a judge changes its answer after a swap, inspect whether the rubric permits a tie, whether a truncation boundary changed, and whether references were attached to positions rather than identities. If a probability score looks good, inspect the reliability table and a discrimination metric as well. The constant predictor is a useful sanity check because it exposes why a single calibration number cannot summarize judge quality.

This unit establishes metric arithmetic and presentation bookkeeping on constructed decisions. Real model-judge validation requires representative items, a fixed rubric, independent reference evidence and a documented operating context. An evaluator can support a scientific decision only to the extent that those conditions have been examined.
