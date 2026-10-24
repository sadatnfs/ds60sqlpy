# llm-004: worked solutions

Open this reference after an attempt or an explicit reveal request. Preserve
your own version beside it. The [learner guide](../guides/llm-004.md) contains
the public fixture and its independent Expected/Verify contracts. These six
sections correspond to the same six learner actions, rather than six answer
steps for one task. A different implementation is acceptable when it preserves
the stated input policy, observations and evidence boundary.

The [executable reference](llm-004_solution.py) exposes a `verify()` helper for
authors and later comparison. It uses only local literals and the declared
Python/NumPy environment. An assertion failure should retain its actual input
and smallest failing observation. A passing reference is evidence about these
fixed cases; use a changed fixture and a closed-reference explanation before
recommending progression. The reading worksheet remains a reading exercise,
regardless of the optional arithmetic checker.

## Exercise 1: Trace training counts

The first document contributes A-to-B and B-to-A. The second contributes A-to-A. In order [A,B,C], these create rows [1,1,0], [1,0,0] and [0,0,0]. Total transitions are three. Concatenating the documents would add a spurious A-to-A boundary transition and change the model. Keep document membership explicit even when the entire fixture fits on one line; a small array can otherwise conceal the same leakage as a large corpus pipeline.

**Expected:** Counts [[1,1,0],[1,0,0],[0,0,0]], totaling three transitions.

**Verify:** Assert the complete matrix and total count three, not a transition count from concatenated documents.

## Exercise 2: Construct a smoothed row

Add one to each of the three candidate counts. A becomes [2,2,1], denominator five; B becomes [2,1,1], denominator four; C becomes [1,1,1], denominator three. The resulting rows match the expected fractions and each sums to one. The vocabulary order is part of the contract because an array of correct probabilities in a different token order would score the wrong targets. Do not normalize over every matrix entry at once.

**Expected:** Rows \(A=[\frac{2}{5},\frac{2}{5},\frac{1}{5}]\), \(B=[\frac{1}{2},\frac{1}{4},\frac{1}{4}]\) and \(C=[\frac{1}{3},\frac{1}{3},\frac{1}{3}]\).

**Verify:** Assert all three arrays with rtol=0, atol=1e-12 and inspect each denominator.

## Exercise 3: Preserve document boundaries

A one-token document has no neighboring-token pair. Two independent one-token documents still have zero transitions. Concatenating them invents one A-to-B pair, whose count is not present in the declared data. Reset at each document boundary or introduce an explicitly modeled boundary token in a different lesson. A low held-out loss cannot retroactively justify a transition that was created by incorrectly joining separate sources.

**Expected:** Separate documents contain zero transitions; concatenation contains one A-to-B transition.

**Verify:** Assert both matrices and retain the wrong-boundary counterexample in your evidence.

## Exercise 4: Handle an unseen context

The reference chooses a uniform distribution over the existing vocabulary for an unknown scoring context Z. Its shape remains three, it sums to one, and the original count matrix is not changed. This is a transparent fallback policy rather than a learned distribution for Z. Another application could reject the unknown context, but it must disclose that alternative. It must not expand the vocabulary or fit new counts while claiming validation was read-only.

**Expected:** The declared fallback returns three equal values \(\frac{1}{3}\) and leaves vocabulary/counts unchanged.

**Verify:** Compare the before/after count matrix and assert output shape (3,) and row sum one.

## Exercise 5: Reject malformed training data

An empty vocabulary has no candidate distribution, duplicate entries create ambiguous indices, and an unknown training token violates the fixed training alphabet. Raise ValueError for all three. Silently extending the table changes both dimensions and smoothing denominators, which would make earlier predictions incomparable. After the failed calls, fit the valid fixture again and compare its exact counts to ensure validation did not retain mutable state or corrupt a shared mapping.

**Expected:** Each case raises ValueError instead of silently extending or merging the vocabulary.

**Verify:** Capture the three named failures and rerun the original fixture successfully afterward.

## Exercise 6: Keep validation read-only

Context C has no observed transitions, so add-one smoothing yields A probability \(\frac{1}{3}\) and negative log score ln(3). Scoring that lookup must not increment C-to-A or otherwise consume validation as training. Copy and compare the matrix before and after to expose mutation. This is held-out arithmetic for a public classroom fixture, not evidence of general language ability. A meaningful broader comparison needs a frozen source-family split and a declared target denominator.

**Expected:** Probability \(\frac{1}{3}\) and negative log score \(\log(3)\); no training count changes.

**Verify:** Copy the count matrix before scoring, assert byte-equal values afterward and compare the held-out score with \(\log(3)\).

## Inspectable reference functions

The core functions below make the input and reduction policies explicit. The
separate executable file adds all six exercise checks. Do not replace a failed
assertion with a flattering default value or remove the invalid-input case.

```python
from __future__ import annotations
import math
import numpy as np


def fit_bigram(sequences, vocabulary):
    vocabulary = tuple(vocabulary)
    if not vocabulary or len(set(vocabulary)) != len(vocabulary):
        raise ValueError("unique nonempty vocabulary required")
    indices = {token: index for index, token in enumerate(vocabulary)}
    counts = np.zeros((len(vocabulary), len(vocabulary)), dtype=np.int64)
    for sequence in sequences:
        sequence = list(sequence)
        if any(token not in indices for token in sequence):
            raise ValueError("unknown training token")
        for left, right in zip(sequence, sequence[1:]):
            counts[indices[left], indices[right]] += 1
    return counts


def next_probabilities(counts, context, vocabulary):
    vocabulary = tuple(vocabulary)
    counts = np.asarray(counts)
    if not vocabulary or counts.shape != (len(vocabulary), len(vocabulary)):
        raise ValueError("vocabulary/count shape mismatch")
    if (counts < 0).any():
        raise ValueError("nonnegative counts required")
    row = counts[vocabulary.index(context)] if context in vocabulary else np.zeros(len(vocabulary))
    mass = np.asarray(row, dtype=np.float64) + 1
    return mass / mass.sum()
```

## Retrieval and alternatives

Without the table, count transitions in the two documents [C,A] and [A]. State which boundary pair must not appear, then derive the smoothed C row under vocabulary [A,B,C].

After revealing this file, choose another fixture before treating the answer
as independent retrieval evidence. Explain why the rejected case is invalid,
not merely which exception class appeared. Alternative notation, array layout
or a direct calculation is welcome when its domain meaning and denominator
remain explicit. Keep implementation correctness separate from broad claims
about unseen model quality, reliability or safety.
