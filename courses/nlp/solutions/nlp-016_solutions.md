# nlp-016: Explanatory solutions

The executable reference checks the declared fixtures. It is separate from the learner scaffold and does not certify general task quality.

## Exercise 1: Build teacher-forced inputs

The shift ensures each prediction conditions only on previous target tokens. EOS remains a prediction event, making stopping part of the learned sequence contract. Reject raw reserved markers so the helper cannot accidentally create duplicated or ambiguous boundary tokens.

**Expected:** [BOS,repair] versus[repair,EOS]; empty becomes[BOS] versus[EOS].

## Exercise 2: Trace cross-attention dimensions

The score matrix has one target row and two source columns. Stable softmax normalizes over source positions. Multiplying by values produces the stated two-dimensional output. This exact fixture detects wrong-axis normalization and confusing key/value roles.

**Expected:** Weights sum to one; output[10p,20(1-p)] with \(p=\operatorname{sigmoid}\!\left(\frac1{\sqrt2}\right)\).

## Exercise 3: Mask source padding

The masked source must contribute zero weight even if its value is large or relevant-looking. An all-invalid source cannot supply a meaningful normalized context and is rejected rather than producing NaNs or an invented average.

**Expected:** Output exactly[10,0]; an all-invalid source raises.

## Exercise 4: Expose greedy search failure

The locally best first token has a weaker continuation. Retaining the alternative lets beam search find the larger joint probability. The result depends on the fixed score and stopping conventions and does not imply that wider beams always improve task quality.

**Expected:** Greedy tea,EOS probability.3; beam coffee,EOS probability.4.

## Exercise 5: Preserve extractive provenance

The baseline returns source text rather than generating a new claim. Its abstention marks no lexical support under its scoring rule, not proof that the corpus contains no semantic answer. Evaluate coverage and semantic relevance separately before using it as a real summarizer.

**Expected:** Return index0 and the unchanged unavailable sentence; refund returns None.

## Exercise 6: Explain generation error propagation

At inference the model conditions on its own prefix, so later distributions can differ from those seen under correct training prefixes. A high-likelihood continuation can still be unsupported by the source. Acceptance therefore needs generated task evaluation, not only training loss or attention visualization.

**Expected:** A concrete account separates teacher-forced loss, autoregressive rollout, search score and factual support.

## Transfer and limits

Sequence-to-sequence learning predicts an output sequence conditioned on an input sequence. Translation, summarization and structured generation fit this pattern, but each has a different success contract. A translation should preserve meaning, a summary should preserve important claims and qualifications, and extraction should respect a schema and source evidence. Fluent output alone cannot establish any of those properties.

An encoder represents the source, and a decoder predicts target tokens conditional on the source and prior target tokens. Cross-attention lets each decoder position consult source representations. During teacher-forced training, the decoder receives the correct earlier target tokens. During generation it receives its own earlier predictions, creating a mismatch when those predictions are wrong.

This offline chapter implements exact cross-attention arithmetic, target shifting and bounded greedy/beam search over an authored probability table. It also provides an honestly labeled extractive summary baseline. It does not train a pretrained encoder-decoder or claim that a keyword-selected sentence is a generative summarizer.

## Mechanism review and counterexample

Extractive summarization selects source spans or sentences. Abstractive summarization generates new wording and can combine information across passages, which adds flexibility and risk of unsupported claims. The reference baseline selects a source sentence by query-word overlap and returns its original index and text. It abstains when there is no overlap.

Selecting a sentence exactly avoids inventing new words but does not guarantee a good summary. It may omit a qualification in another sentence, choose an outdated statement or overemphasize repeated query terms. A generated summary can additionally reverse negation or imply causality absent from the source. Evaluate coverage, factual support and usefulness with representative documents and multiple valid references where appropriate.

Preserve source identity, offsets and the selection/generation configuration. A later assistant should be able to show why a sentence or claim was included. Cross-attention weights are internal model computations, not a substitute for an external citation-support check.
