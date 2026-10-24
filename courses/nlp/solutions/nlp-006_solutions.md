# nlp-006: Explanatory solutions

The executable reference checks the declared fixtures. It is separate from the learner scaffold and does not certify general task quality.

## Exercise 1: Construct the event vocabulary

The denominator counts possible next-token events, so including BOS would incorrectly allocate mass to a token the model never intends to predict. EOS must be included because ending a sentence is a modeled event. UNK reserves probability for out-of-vocabulary input under the declared mapping policy.

**Expected:** Seven prediction targets, five observed words plus EOS/UNK.

## Exercise 2: Derive smoothed rows

Each row has its own denominator. BOS has three observations, we has two, like has three and tea has two. Adding alpha once per vocabulary target adds seven to each row denominator. Using the grand corpus count would fail normalization and no longer estimate the stated conditional distribution.

**Expected:** \([0.3,\frac{1}{3},0.3,\frac{1}{3}]\).

## Exercise 3: Implement log scoring

The log representation avoids multiplying many tiny values. The inverse geometric average probability is computed per prediction event. A correct numeric answer needs the boundary convention as well as the formula; reporting only a perplexity without its token unit makes comparisons ambiguous.

**Expected:** Joint probability .01, four events and perplexity \(\sqrt{10}\).

## Exercise 4: Prove normalization

The additive numerator sums to the observed row total plus \(\alpha\cdot V\), exactly matching the denominator. This invariant catches vocabulary and denominator errors. It also verifies the declared unseen-context behavior rather than relying on one plausible sentence score.

**Expected:** Each row sums to one within numerical tolerance.

## Exercise 5: Keep evaluation immutable

Evaluation should measure a frozen model. Learning vocabulary or transitions from the probe changes the system under test and can make perplexity artificially favorable. The state snapshot makes this boundary observable on the small fixture.

**Expected:** Finite score; cocoa absent from vocabulary; counts and vocabulary unchanged.

## Exercise 6: Explain empty and incomparable scores

The model assigns EOS probability one-tenth after BOS because no empty sentence was observed and smoothing allocates one count-equivalent. This is a deliberate convention. A different tokenizer or omission of EOS changes the event space and denominator, so lower perplexity alone does not establish a better model across those changes.

**Expected:** One EOS prediction with perplexity 10; a written comparison lists tokenization, corpus and boundary conventions.

## Transfer and limits

A language model assigns probabilities to sequences of language units. An n-gram model approximates the next-token distribution using a limited history. A bigram model uses only the immediately preceding token, making its assumptions and counts easy to inspect. It is a useful baseline and a foundation for understanding the next-token objective used by much larger models.

This lesson trains on three authored sentences: we like tea, we like coffee, and they like tea. The vocabulary contains five observed words plus an end-of-sequence token and an unknown token, for seven possible predictions. A beginning-of-sequence marker provides context but is never predicted. These choices determine the probability denominator and the perplexity calculation, so they are part of the model rather than formatting details.

The implementation learns real conditional count distributions with additive smoothing. It does not contain neural embeddings or attention. A finite probability for an unseen sentence means the smoothing policy assigns it mass, not that the model understands or verifies its meaning.

## Mechanism review and counterexample

Counter stores next-token counts for one context, and the model keeps a dictionary from contexts to those counters. probability uses get rather than mutating defaultdict lookup during evaluation, so scoring cannot silently add contexts or vocabulary items. The reference snapshots the model before an unknown-word probe and checks that it remains unchanged afterward.

Log probabilities turn the product into a sum, avoiding underflow on longer sequences. Exponentiating the negative average log value produces perplexity only after the correct event count is known. Empty raw input still predicts EOS from BOS under this model, so it contains one prediction event and has perplexity ten. This differs from an API that defines an empty sequence as no scored events; either convention must be explicit.

A bigram can capture local preferences but loses longer context. We do not assert that a low perplexity sentence is factual, grammatical or useful. Evaluate a changed domain, repeated templates and unknown-token rate separately. If every unfamiliar word maps to one UNK, a model can hide important vocabulary distinctions behind a finite but uninformative score.
