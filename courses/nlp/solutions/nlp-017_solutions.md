# nlp-017: Explanatory solutions

The executable reference checks the declared fixtures. It is separate from the learner scaffold and does not certify general task quality.

## Exercise 1: Implement clipped precision

Only one occurrence of the can be credited because the reference contains one. The remaining repetitions contribute to the denominator without extra matches. This prevents a simple repetition exploit but does not make overlap a semantic metric.

**Expected:** Precision .25, not1.

## Exercise 2: Derive the brevity penalty

The geometric mean is one because every candidate n-gram appears in the reference. The brevity penalty reduces the result for omitted content. This example isolates length handling from n-gram matching and documents the exact teaching convention.

**Expected:** Both precisions1; BP and score \(\exp(-0.5)\).

## Exercise 3: Implement longest common subsequence

A subsequence can skip not while preserving the other words in order. The resulting high score is mathematically correct under the metric. It demonstrates a limitation of the metric rather than a coding defect to be fixed by changing expected values.

**Expected:** LCS3, precision1, recall.75, \(F_{1}=\frac{6}{7}\).

## Exercise 4: Document semantic failure

The answer changes not ready into ready, reversing the source. A useful evaluator must detect or escalate this error independently of overlap. A handcrafted negation check on this one sentence is not a general entailment model, so its scope must remain explicit.

**Expected:** The candidate contradicts readiness; a high overlap score is retained alongside the failure label.

## Exercise 5: Aggregate at the right unit

Equal-family averaging prevents the family with more variants from receiving more weight merely because it was expanded. Row-level weighting can be appropriate for a different target population, but the choice must be stated. Confidence intervals should preserve the same dependence unit.

**Expected:** Family rates[.5,0] and equal-family mean.25; explain why row mean1/3 answers a different weighting question.

## Exercise 6: Specify an evaluation packet

The packet makes both scores and judgments reproducible. It should include unsupported and contradictory examples, preserve disagreements and keep final acceptance families out of prompt tuning. A high average cannot override a critical failure category without an explicit decision rule.

**Expected:** Record includes task/source/version/output/atomic support labels/metric config/rater or judge identity and an abstention case.

## Transfer and limits

Generated language often has many acceptable answers, so evaluation cannot rely on one exact string. Translation can use synonyms, a summary can select different useful details, and a domain assistant may correctly abstain when evidence is missing. A metric must be chosen for the task and must not receive a stronger interpretation than its calculation supports.

This lesson implements transparent overlap calculations and an exact longest-common-subsequence dynamic program. The BLEU function is explicitly a single-reference, unsmoothed, sentence-level teaching variant with a chosen maximum n-gram order. It is not advertised as a drop-in implementation of a corpus benchmark. The examples expose why high overlap can coexist with a serious factual contradiction.

Separate surface similarity, semantic similarity, source support and user usefulness. A learned semantic metric can recognize paraphrases better than exact overlap, but it is itself a model with training data and failure modes. A model judge adds a rubric and another inference process, not an automatic ground-truth oracle.

## Mechanism review and counterexample

Suppose a source says a service is not ready and a repair is scheduled. A generated summary says the service is ready after repair. It shares many words, sounds coherent and could receive a favorable generic fluency score. A task-specific review identifies an unsupported completion claim and a reversed readiness state.

The evaluation packet should retain the source snapshot, generated text, atomic claims, support judgments and scoring rationale. A correction should target the failure mechanism, such as evidence interpretation or instruction following, and be retested on new related cases. Improving the overlap score alone is not a repair for the unsupported claim.
