# nlp-015: Explanatory solutions

The executable reference checks the declared fixtures. It is separate from the learner scaffold and does not certify general task quality.

## Exercise 1: Implement contextual attention

The token's own vector is unchanged, but its output mixes values from the whole valid sequence. The context difference therefore appears in its output. Because the embeddings are handcrafted, this is an algebraic demonstration of contextualization rather than evidence of pretrained language understanding.

**Expected:** Bank's second output coordinate changes sign with river versus money.

## Exercise 2: Prove padding invariance

Removing padding only after attention is too late if valid queries already attended to it. The large vector makes contamination easy to detect. The reference checks both attention weights and final representations, providing stronger evidence than a shape-only assertion.

**Expected:** Original valid outputs unchanged; padded-key weights zero; padded query output zero.

## Exercise 3: Train the document head

This performs actual parameter updates and verifies the objective numerically. The constructed features make the problem easy, so the result is explicitly a training receipt. It does not replace a held-out natural-language evaluation or demonstrate that the fixed encoder parameters were learned.

**Expected:** Loss decreases from log2 to below.1 and training predictions [0,1,0,1].

## Exercise 4: Mask subword supervision

The ignored sentinel is not a class ID. Filtering it first prevents invalid indexing and makes the loss denominator equal the number of supervised positions. A real tokenizer alignment record must explain why each piece is supervised or ignored.

**Expected:** Loss \(\log(1+\exp(-2))\); changing ignored logits does not alter it.

## Exercise 5: Reject missing supervision

An empty valid set makes mean pooling or average supervised loss undefined. Returning zero could make a broken batch appear to train perfectly. The explicit error distinguishes an absent signal from a genuine low loss.

**Expected:** Both raise clear ValueError instead of returning a meaningless average.

## Exercise 6: Design a real encoder evaluation

A real evaluation needs examples not constructed from the same handcrafted geometry. Hold out related documents, compare the baseline fairly and inspect whether context changes the intended task output. Record model/tokenizer versions and reject a claim of pretrained quality from this toy layer alone.

**Expected:** A written plan separates training fit, lexical baseline, contextual task quality and subgroup/truncation errors.

## Transfer and limits

A contextual encoder produces a different vector for a token depending on the surrounding sequence. This addresses a limitation of fixed word vectors: bank near river and bank near money can be represented differently. The encoder can then supply features to a document classifier or a token-level tagging head. The representation, output head and training objective are separate components.

The reference implements a genuine bidirectional scaled dot-product attention calculation in NumPy, followed by actual gradient training of a tiny logistic classification head. The token embeddings and attention projections are deliberately fixed and handcrafted. This is not pretrained BERT, not a complete transformer stack and not evidence of real word-sense accuracy. Its purpose is to expose context mixing, padding masks, pooling and supervised loss alignment with exact checks.

A real pretrained encoder adds learned token/position embeddings, multiple attention heads, feed-forward blocks, residual connections, normalization and pretraining over a corpus. Fine-tuning can update the encoder and head together or freeze some components. Those choices change cost, capacity and generalization and require task-specific held-out evaluation.

## Mechanism review and counterexample

The four examples contain bank/river and bank/money in both orders. The handcrafted vectors already encode a useful separation, and the attention layer pools it into two-dimensional features. A logistic head begins with zero weights, predicts one-half for every example and has cross-entropy log two. Gradient steps update only the head, reducing the loss and recovering all four training labels.

This is a real optimization loop, but the task is deliberately constructed and has no independent natural-language test set. Report it as a training-mechanism check. Do not claim that lower training loss proves the encoder learned semantic disambiguation or that performance generalizes to bank account, riverbank, multilingual usage or quoted text.

A meaningful encoder comparison would hold out document families, use the exact tokenizer and pooling contract, compare a linear lexical baseline, inspect ambiguous cases and measure entity/document-level outcomes. It would also report truncation and subgroup effects, since long inputs and rare vocabulary can behave differently from short clean examples.
