# llm-007: worked solutions

Open this reference after an attempt or an explicit reveal request. Preserve
your own version beside it. The [learner guide](../guides/llm-007.md) contains
the public fixture and its independent Expected/Verify contracts. These six
sections correspond to the same six learner actions, rather than six answer
steps for one task. A different implementation is acceptable when it preserves
the stated input policy, observations and evidence boundary.

The [executable reference](llm-007_solution.py) exposes a `verify()` helper for
authors and later comparison. It uses only local literals and the declared
Python/NumPy environment. An assertion failure should retain its actual input
and smallest failing observation. A passing reference is evidence about these
fixed cases; use a changed fixture and a closed-reference explanation before
recommending progression. The reading worksheet remains a reading exercise,
regardless of the optional arithmetic checker.

## Exercise 1: Trace the first candidate counts

The two words contain pairs a/b, b/EOW, a/c and c/EOW, each once. Integer-tuple lexical ordering chooses a/b because its left token a is smaller than b or c and its right token b is smaller than c. Reversing the order of training words must not change this choice. Record the table before replacement so the decision is auditable; a saved tokenizer hash alone would not explain why that rule was chosen.

**Expected:** Four pairs each have count one, and the selected pair is ((97,),(98,)).

**Verify:** Inspect the explicit pair-count table and assert the chosen rule under the declared lexical tie policy.

## Exercise 2: Construct a one-step trainer

The trainer counts adjacent current tokens, selects the declared maximum/tie candidate and merges its nonoverlapping occurrences. With budget one, the only rule is ((97,),(98,)). Encoding ab then gives token (97,98) followed by (256,). Decoding flattens the bytes, removes the final marker and uses strict UTF-8. The ordered merge list is the learned state. A vocabulary set without that order is insufficient to reproduce the same encoding procedure.

**Expected:** The ordered rule list contains only a+b; encoded ab is [(97,98),(256,)].

**Verify:** Assert the exact rule tuple, encoded tokens and decoded ab round trip.

## Exercise 3: Diagnose overlapping replacement

For aaaa, a left-to-right scan matches positions zero/one, consumes both, then matches two/three. The result is two aa tokens and one end marker. Reusing position one in another pair would count the same source byte twice and break a round-trip check. Some implementations might produce different intermediate data structures, but they must reconstruct exactly four a bytes and respect the declared nonoverlapping replacement policy.

**Expected:** The result is two (97,97) tokens followed by the end marker, not overlapping triple coverage.

**Verify:** Assert the output token list and reconstruct exactly four original a bytes.

## Exercise 4: Freeze validation encoding

The saved a+b rule does not match ad, so encoding returns the two separate base byte tokens and the marker. Serialize the same ordered rule list before and after and compare its hash. No fit call belongs in encoding. A new byte is supported by the fixed byte base, so there is no need to leak validation into merge selection. This fixture distinguishes an honest fallback from a tokenizer that silently retrains on every incoming document.

**Expected:** Tokens [(97,),(100,),(256,)] and an unchanged merge hash.

**Verify:** Assert the complete token sequence and hash equality; no fit call may occur in the encoding path.

## Exercise 5: Handle a bounded or absent fit

A zero merge budget deliberately retains the base representation and produces an empty learned rule list. It is valid and still round-trips text. An empty training collection has no declared fitting evidence and raises ValueError; a negative budget is invalid and also raises. Keep the valid zero-budget case distinct from absent data. The loop also stops when no adjacent pairs remain, so it never invents filler merges merely to reach a requested count.

**Expected:** Zero limit returns no rules; empty training and negative limit raise ValueError.

**Verify:** Capture both exceptions and assert zero-limit byte encoding still round-trips ab.

## Exercise 6: Transfer to UTF-8 text

The UTF-8 representation of é is the two-byte sequence 195,169. With no matching a+b pair, those bytes remain separate tokens plus the marker. Strict decoding reconstructs the original single code point. Token count, byte count and code-point count differ under this representation. This is a reversible toy encoding, not an embedding vocabulary-ID assignment; the following unit requires a separate fixed mapping from whatever tokens are chosen to legal table rows.

**Expected:** Base byte IDs 195 and 169 plus the end marker; decoding returns one code point é.

**Verify:** Assert token byte contents and strict decoded equality without changing the learned rules.

## Inspectable reference functions

The core functions below make the input and reduction policies explicit. The
separate executable file adds all six exercise checks. Do not replace a failed
assertion with a flattering default value or remove the invalid-input case.

```python
from __future__ import annotations
from collections import Counter
import hashlib
import json

END = (256,)


def byte_tokens(word):
    if not isinstance(word, str):
        raise TypeError("training words must be text")
    return [(value,) for value in word.encode("utf-8")] + [END]


def merge_pair(tokens, pair):
    output = []
    index = 0
    while index < len(tokens):
        if index + 1 < len(tokens) and (tokens[index], tokens[index + 1]) == pair:
            output.append(tokens[index] + tokens[index + 1])
            index += 2
        else:
            output.append(tokens[index])
            index += 1
    return output


def fit_bpe(words, limit):
    words = list(words)
    if not words or type(limit) is not int or limit < 0:
        raise ValueError("nonempty training collection and nonnegative integer limit required")
    corpus = [byte_tokens(word) for word in words]
    rules = []
    for _ in range(limit):
        counts = Counter(pair for word in corpus for pair in zip(word, word[1:]))
        if not counts:
            break
        maximum = max(counts.values())
        pair = min(pair for pair, count in counts.items() if count == maximum)
        rules.append(pair)
        corpus = [merge_pair(word, pair) for word in corpus]
    return rules


def encode_word(word, rules):
    tokens = byte_tokens(word)
    for pair in rules:
        tokens = merge_pair(tokens, pair)
    return tokens


def decode_tokens(tokens):
    values = [value for token in tokens for value in token]
    if not values or values[-1] != 256 or 256 in values[:-1]:
        raise ValueError("exactly one final end marker required")
    return bytes(values[:-1]).decode("utf-8")


def merge_hash(rules):
    return hashlib.sha256(json.dumps(rules, separators=(",", ":")).encode()).hexdigest()
```

## Retrieval and alternatives

Without the reference, explain why a merge list must be ordered and why a left-to-right scan cannot reuse one byte in two overlapping matches. Then propose a fresh tied training fixture and state its deterministic first choice.

After revealing this file, choose another fixture before treating the answer
as independent retrieval evidence. Explain why the rejected case is invalid,
not merely which exception class appeared. Alternative notation, array layout
or a direct calculation is welcome when its domain meaning and denominator
remain explicit. Keep implementation correctness separate from broad claims
about unseen model quality, reliability or safety.
