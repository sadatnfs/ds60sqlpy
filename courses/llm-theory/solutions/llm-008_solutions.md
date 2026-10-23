# llm-008: worked solutions

Open this reference after an attempt or an explicit reveal request. Preserve
your own version beside it. The [learner guide](../guides/llm-008.md) contains
the public fixture and its independent Expected/Verify contracts. These six
sections correspond to the same six learner actions, rather than six answer
steps for one task. A different implementation is acceptable when it preserves
the stated input policy, observations and evidence boundary.

The [executable reference](llm-008_solution.py) exposes a `verify()` helper for
authors and later comparison. It uses only local literals and the declared
Python/NumPy environment. An assertion failure should retain its actual input
and smallest failing observation. A passing reference is evidence about these
fixed cases; use a changed fixture and a closed-reference explanation before
recommending progression. The reading worksheet remains a reading exercise,
regardless of the optional arithmetic checker.

## Exercise 1: Trace row selection

ID two selects [2,2], zero selects [1,0], and the repeated two selects [2,2] again. Stack those selections in token order to obtain the expected (3,2) matrix. The vocabulary length four is used to validate the IDs and is contracted away by selection; it is not a result dimension. This fixed lookup demonstrates index ing only. No optimization or semantic-quality claim is supported by the supplied feature values.

**Expected:** Output [[2,2],[1,0],[2,2]], shape (3,2).

**Verify:** Assert the entire matrix and explain why vocabulary size four is not an output axis here.

## Exercise 2: Construct a lookup guard

A one-hot matrix for [2,0,2] has shape (3,4), with one indicator per selected vocabulary row. Multiplying by the (4,2) table gives the same (3,2) feature matrix as direct lookup. The equality makes the roles of the vocabulary and feature axes explicit. Direct index ing is the canonical small interface because forming dense one-hot arrays is unnecessary for large vocabularies. The two computations should agree exactly on these integer-valued float64 fixtures.

**Expected:** np.eye(4)[ids] @ table matches the lookup exactly.

**Verify:** Assert both matrices and inspect the one-hot shape (3,4) before multiplication.

## Exercise 3: Reject invalid IDs

Reject -1 even though NumPy would select the final row. Reject 4 because the valid row range is zero through three. Reject 1.5 as a noninteger instead of rounding it to another token. A domain guard is deliberately narrower than NumPy's general index ing behavior. Validate before selection and retain the actual named exception. The valid fixture should still work afterward, demonstrating that rejected requests did not mutate the table or tokenizer mapping.

**Expected:** Negative/out-of-range IDs raise ValueError; noninteger IDs raise TypeError.

**Verify:** Capture each exception independently and confirm the original valid lookup still works.

## Exercise 4: Handle an empty token list

This lookup contract accepts an empty token list and returns an empty matrix with feature width two. That is a defined selection result, not proof that every later model accepts empty context. The attention pilot explicitly rejects a sequence with no keys, while a reader might still preserve empty notes. Different boundaries can choose different emptiness policies. Preserve shape (0,2) so the feature schema is not lost merely because this batch contains no tokens.

**Expected:** The lookup returns shape (0,2), while the later attention contract rejects an empty sequence.

**Verify:** Assert both dimensions of the empty output rather than calling its size-zero result a successful attention run.

## Exercise 5: Preserve table ownership

Advanced integer index ing creates independent output storage here. Mutating the first selected row therefore leaves the original table unchanged. It also must not modify the third selected row merely because both originated from vocabulary ID two. Save and compare the table and repeated row explicitly. Another implementation might intentionally share storage, but that would be a different mutation contract and should not be silently substituted for this learner helper.

**Expected:** The table remains unchanged and output[2] remains [2,2].

**Verify:** Assert a saved table copy still matches exactly and the repeated result row was not aliased to the modified row.

## Exercise 6: Transfer across a vocabulary permutation

The row permutation [2,0,3,1] moves old row two to new position zero and old row zero to new position one. Thus old IDs [2,0,2] become [0,1,0]. Their selected features remain identical when both transformations are applied. Keeping the old IDs after changing row order would produce a plausible-shaped but different representation. Store the tokenizer and table configuration/hash together; a matching matrix shape alone cannot establish that their vocabulary identities agree.

**Expected:** Remapped IDs are [0,1,0], and the result equals the original lookup.

**Verify:** Assert the unchanged feature matrix and explain why storing a tokenizer hash/version with the table prevents a silent row-order mismatch.

## Inspectable reference functions

The core functions below make the input and reduction policies explicit. The
separate executable file adds all six exercise checks. Do not replace a failed
assertion with a flattering default value or remove the invalid-input case.

```python
from __future__ import annotations
import numpy as np


def lookup(table, ids):
    table = np.asarray(table, dtype=np.float64)
    ids = np.asarray(ids)
    if table.ndim != 2 or not all(table.shape) or not np.isfinite(table).all():
        raise ValueError("finite nonempty embedding table required")
    if ids.ndim != 1:
        raise ValueError("token IDs must be a vector")
    if ids.size == 0:
        return np.empty((0, table.shape[1]), dtype=np.float64)
    if not np.issubdtype(ids.dtype, np.integer) or ids.dtype == np.bool_:
        raise TypeError("integer token IDs required")
    if (ids < 0).any() or (ids >= len(table)).any():
        raise ValueError("token ID outside vocabulary")
    return table[ids].copy()
```

## Retrieval and alternatives

Without the table in view, state the three shape roles: vocabulary, tokens and features. Then invent a three-row table and show how a table-row permutation requires a matching ID permutation to preserve the selected features.

After revealing this file, choose another fixture before treating the answer
as independent retrieval evidence. Explain why the rejected case is invalid,
not merely which exception class appeared. Alternative notation, array layout
or a direct calculation is welcome when its domain meaning and denominator
remain explicit. Keep implementation correctness separate from broad claims
about unseen model quality, reliability or safety.
