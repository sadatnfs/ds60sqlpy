# nlp-004: Explanatory solutions

This is a character-based word BPE demonstration over a declared ASCII alphabet. It is not a drop-in tokenizer for an existing model. The executable reference covers five computational exercises; the final compatibility contract remains an explanation task.

## Exercise 1: Segmentation is a policy

Whitespace splitting produces two items because it recognizes only whitespace boundaries. It leaves the final period attached. The first regex separates punctuation from word-character runs, splitting the straight apostrophe out of the contraction. The second adds a repeated apostrophe-plus-word group to retain that particular contraction form.

The `pay` match begins at index 6 and ends at 9 in the unchanged input. Each match's slice reproduces its token, making the offset claim inspectable. These examples do not determine which segmentation is linguistically ideal. A real annotation or pretrained-model contract may require a different policy. The reference asserts exact outputs to make the implemented behavior reproducible, not to declare one list universally correct.

**Expected:** the three distinct token lists in the guide and the exact `[6,9)` span for `pay`.

## Exercise 2: Weight counts by observed frequency

Both training word types contain the adjacent pairs `l,o` and `o,w`. The word `low` occurs three times and `lower` once, so each pair contributes 3+1=4 weighted occurrences. Only `low` has `w` adjacent to the terminal marker, giving that pair count 3.

If each dictionary key were counted once, the first two pair counts would be 2 and the terminal pair count 1. That would treat a type inventory as though it were the token-frequency corpus. The code explicitly multiplies each adjacency by the stored frequency so its statistic corresponds to the stated training data. Positive integer count validation rejects zero, negative and Boolean frequencies rather than quietly changing their meaning.

**Expected:** counts 4, 4 and 3 for the specified pairs.

## Exercise 3: Resolve overlapping candidate positions

In three consecutive `a` symbols, the two candidate pairs overlap at the middle symbol. The left-to-right replacement consumes positions 0 and 1 together, advances by two, and then retains position 2. The terminal marker remains at the end. This yields `aa,a,</w>`, which decodes back to `aaa`.

The example shows why a pair occurrence count does not always equal the number of independent replacements in a single pass. The algorithm's consumption rule determines what actually happens. Reusing the middle symbol in two output merges would duplicate information. The reconstruction check detects that error on a fixture small enough to trace by hand.

**Expected:** exactly `('aa','a','</w>')`, with a correct three-letter reconstruction.

## Exercise 4: Make training choices reproducible

The initial frequency tie is resolved lexicographically, selecting `l,o`. After applying that merge to every word, the counts are rebuilt on the new sequences. The next chosen pair is `lo,w`. Rebuilding is necessary because the symbols and adjacencies are no longer the same as at initialization.

Reversing dictionary insertion order is a meaningful negative control for accidental dependence on input iteration order. With the explicit key `(-frequency, pair)`, the selected merges remain unchanged. This establishes determinism for the declared algorithm and fixture. It does not establish compatibility with another BPE implementation that uses different tie handling, normalization, pre-tokenization or special symbols.

**Expected:** the two recorded merge pairs and the same final state under both insertion orders.

## Exercise 5: Separate training from encoding

Encoding applies the frozen merge sequence to a new supported word. `lower` uses the learned `low` symbol. `row` remains separate characters because no learned rule directly merges `o,w` in that context. This illustrates why applying the ranked merge list is not equivalent to inventing an arbitrary longest-substring encoder.

The character `s` was absent from the tiny training alphabet, so `slow` raises an explicit error. A production tokenizer may offer an unknown symbol or byte fallback, but this reference deliberately implements neither. The merge tuple is inspected before and after encoding to verify that inference did not learn a new rule from the test input. Supported words round-trip to the original modeled lowercase ASCII input.

**Expected:** the exact token tuples for `lower` and `row`, valid round trips, unchanged merges and an unknown-symbol failure for `slow`.

## Exercise 6: Describe a tokenizer as part of a model artifact

A useful compatibility record identifies the tokenizer algorithm and implementation version, normalization order, pre-tokenization rules, vocabulary and token-ID mapping, merge order, special tokens and chat template. It should also name the representation to which any offsets refer. A file hash can identify exact bytes, while the human-readable fields explain what those bytes are intended to mean.

A changed vocabulary can assign a different meaning to an embedding row. A changed chat template can insert different training or inference markers. A changed tokenization can alter sequence length and the denominator of token-level loss. Therefore a round trip alone is not enough to justify exchanging tokenizer files between models. It checks a reconstruction property, not semantic quality, embedding compatibility or comparable perplexity units.

**Expected:** an explicit compatibility record and at least one explanation of a change that forces a new validation step.

## Transfer after comparison

Add a frequent word to the training corpus, retrain the tiny model and inspect which merge changes first. Keep the original model frozen for comparison. Report both merge lists and token lengths on a fixed supported probe set. Explain why lower token counts are evidence about compression under this corpus, not automatically evidence of better downstream language understanding.
