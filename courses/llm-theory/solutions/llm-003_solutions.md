# llm-003: worked solutions

Open this reference after an attempt or an explicit reveal request. Preserve
your own version beside it. The [learner guide](../guides/llm-003.md) contains
the public fixture and its independent Expected/Verify contracts. These six
sections correspond to the same six learner actions, rather than six answer
steps for one task. A different implementation is acceptable when it preserves
the stated input policy, observations and evidence boundary.

The [executable reference](llm-003_solution.py) exposes a `verify()` helper for
authors and later comparison. It uses only local literals and the declared
Python/NumPy environment. An assertion failure should retain its actual input
and smallest failing observation. A passing reference is evidence about these
fixed cases; use a changed fixture and a closed-reference explanation before
recommending progression. The reading worksheet remains a reading exercise,
regardless of the optional arithmetic checker.

## Exercise 1: Trace the fixed conditionals

The product is \(0.5\cdot 0.25\cdot 0.8=0.1\). Taking the negative natural log yields \(\log(10)\), equivalently the sum of three negative log terms. The scored-target count is three. Each number belongs to its own preceding context in the probability chain. The arithmetic alone cannot check that a model produced the right contextual probability, so retain a prefix/target table as semantic evidence alongside the numeric assertions.

**Expected:** Likelihood 0.1, total NLL \(\log(10)\), and three targets.

**Verify:** Assert the product and log score within 1e-12 and name each preceding context in a short table.

## Exercise 2: Change the conditioning assumption

Reusing 0.5 at every position gives 0.125 and total NLL \(3\cdot \log(2)\). These differ from the supplied conditional table's 0.1 and \(\log(10)\). The probability chain rule does not authorize replacing conditional values with marginals: that substitution changes the assumptions about context and defines a different distribution. It could accidentally match a special dataset, but it is not an identity. Compare the declared contexts rather than declaring either numeric result an implementation bug by itself.

**Expected:** The alternative product is 0.125 and its total NLL is \(3\cdot \log(2)\), different from \(\log(10)\).

**Verify:** Record both products and explain that the changed conditionals define a different model, not an algebraic shortcut.

## Exercise 3: Preserve a long log score

For a thousand values of 0.01, a direct floating product rounds to zero, while adding the negative logs produces the finite total \(1000\cdot \log(100)\). The reference uses math.fsum for the log terms to reduce accumulation error. Store the product and total as separate fields so the underflow is visible instead of hidden. Computing \(-\log(\mathrm{product})\) afterward would either fail at zero or return infinity and would discard useful information already available in the individual factors.

**Expected:** Direct product is 0.0 from underflow; total NLL is finite and equals \(1000\cdot \log(100)\) within 1e-9.

**Verify:** Assert the finite log-space value and keep the underflowed product labeled separately.

## Exercise 4: Handle certain and impossible targets

Every probability in [1,1] is certain under the declared model, so both negative log terms are zero and the total is zero. In [0.5,0], the model assigns no probability to one observed target; its total NLL is positive infinity. This is not the same as underflow from many small positive values. Clipping zero to an epsilon creates a different scoring policy that must be disclosed and justified; it cannot be silently used to obtain a nicer finite result.

**Expected:** The all-one score has NLL 0; a zero-probability target gives product 0 and NLL positive infinity.

**Verify:** Use math.isinf for the impossible-event result and compare it with the finite underflow result from Exercise 3.

## Exercise 5: Reject invalid probabilities

A helper must reject an empty sequence because its mean has no target count. Values below zero or above one are not probabilities, and NaN is not an interpretable finite score. Raise ValueError for each rather than silently clipping, skipping or treating an invalid entry as zero loss. The normal fixture should still produce the same three-target score afterward. This checks both the validation policy and the absence of mutations to a shared probability list.

**Expected:** All four cases raise ValueError with a nonempty/range/finite explanation.

**Verify:** Capture each rejected case separately and then verify the original three-target fixture remains unchanged.

## Exercise 6: Declare an aggregation unit

Document A has total ln(2) over one target. Document B has total 3*ln(4)=6*ln(2) over three targets. Across all four targets, the mean is 7*ln(2)/4. Giving the two document means equal weight gives (ln(2)+2*ln(2))/2=3*ln(2)/2. Both calculations are valid under their different units. State the aggregation before comparing models, and do not switch the policy after seeing which answer supports a preferred conclusion.

**Expected:** Token mean is \(\frac{7\cdot \log(2)}{4}\); equal-document mean is \(\frac{3\cdot \log(2)}{2}\).

**Verify:** Write the four-target denominator and the two-document denominator explicitly and assert both values within 1e-12.

## Inspectable reference functions

The core functions below make the input and reduction policies explicit. The
separate executable file adds all six exercise checks. Do not replace a failed
assertion with a flattering default value or remove the invalid-input case.

```python
from __future__ import annotations
import math


def sequence_score(probabilities):
    probabilities = list(probabilities)
    if not probabilities:
        raise ValueError("nonempty probability sequence required")
    if any(isinstance(p, bool) for p in probabilities):
        raise TypeError("probabilities must be real numbers, not boolean")
    probabilities = [float(p) for p in probabilities]
    if any(not math.isfinite(p) or p < 0 or p > 1 for p in probabilities):
        raise ValueError("finite probabilities in [0,1] required")
    nll = math.inf if 0 in probabilities else math.fsum(-math.log(p) for p in probabilities)
    return {
        "probability": math.prod(probabilities),
        "nll": nll,
        "targets": len(probabilities),
        "mean_nll": nll / len(probabilities),
    }
```

## Retrieval and alternatives

Without opening the helper, derive the log score of probabilities [0.25,1]. Explain why adding conditional log probabilities does not assume independent tokens. Name one way a zero printed likelihood can coexist with finite NLL.

After revealing this file, choose another fixture before treating the answer
as independent retrieval evidence. Explain why the rejected case is invalid,
not merely which exception class appeared. Alternative notation, array layout
or a direct calculation is welcome when its domain meaning and denominator
remain explicit. Keep implementation correctness separate from broad claims
about unseen model quality, reliability or safety.
