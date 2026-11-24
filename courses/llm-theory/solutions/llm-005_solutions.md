# llm-005: worked solutions

Use this cross entropy, perplexity and denominator traps reference after your own attempt. The [learner guide](../guides/llm-005.md) keeps the fixture and Expected/Verify contracts for *Trace a perplexity* to *Challenge a tokenizer ranking*, six separate actions; any implementation is acceptable if *Reject an absent or invalid score* still fails on that input.

`verify()` in the [executable reference](llm-005_solution.py) uses the Python standard library and literals only; on failure, keep the *Reject an absent or invalid score* input. A pass says nothing beyond these cross entropy, perplexity and denominator traps fixtures, so next explain cross entropy here from memory on a changed fixture. The reading worksheet remains a reading exercise, regardless of the optional arithmetic checker.

## Exercise 1: Trace a perplexity

The two negative log terms are ln(2) and ln(4), so total NLL is 3*ln(2). Divide by the two active targets to obtain 1.5*ln(2), then exponentiate for perplexity \({2}^{1.5}\). Each field has a different interpretation. Keeping the count next to the result makes later padding and batching errors visible. The perplexity is not a count of correct predictions or a probability that the observed text is factually true.

**Expected:** Total \(3\cdot \log(2)\), count 2, mean \(1.5\cdot \log(2)\), perplexity \({2}^{1.5}\).

**Verify:** Assert all four fields with explicit tolerances rather than comparing one unlabeled number.

## Exercise 2: Construct a masked score

The ignored third slot contributes neither a negative log term nor a target count. The complete score therefore matches the original two-target result. Selecting by a boolean mask before reduction is the canonical reference behavior. Merely appending zero loss and averaging all three entries would lower the objective without improving any prediction. Preserve a test where adding ignored padding leaves the active count and every reported normalized value unchanged.

**Expected:** The padded fixture retains active count 2 and exactly the original mean/perplexity.

**Verify:** Compare the complete returned metrics and the active count against the unpadded result.

## Exercise 3: Compare document weighting

Document A has total ln(2) over one target; B has total 6*ln(2) over three. Combining all targets gives 7*ln(2)/4. Averaging the two document means gives (ln(2)+2*ln(2))/2, or 3*ln(2)/2. The discrepancy is weighting, not floating-point error. Declare whether documents or targets are the primary units before comparing systems. The later corpus split should also preserve source families rather than pretending repeated paraphrases are independent evidence.

**Expected:** Token-weighted mean is \(\frac{7\cdot \log(2)}{4}\), while equal-document mean is \(\frac{3\cdot \log(2)}{2}\).

**Verify:** Record both the four-target denominator and two-document denominator in a labeled table.

## Exercise 4: Handle zero probability

A zero-probability active target is impossible under the supplied distribution, so mean NLL and perplexity are infinite. If the zero slot is explicitly ignored, only the probability 0.5 remains, giving ln(2) and perplexity 2. This distinction relies on the mask policy, not on silently clipping probabilities. Ignoring an inconvenient real target after seeing its score would be selection bias; only predeclared padding or exclusion rules justify its removal.

**Expected:** Active zero gives infinite mean and perplexity; ignoring it leaves mean \(\log(2)\) and perplexity 2.

**Verify:** Use math.isinf for the first case and assert active count 1 in the second.

## Exercise 5: Reject an absent or invalid score

An all-false mask and an empty sequence have no defined empirical mean. A value above one is not a probability. Reject those with ValueError and reject an integer mask with TypeError under the explicit boolean convention. Do not use a default zero score to hide absence or a malformed request. Repeat the normal two-target fixture after the failures to demonstrate the reference is not mutating input lists or retaining accidental state between calls.

**Expected:** The first three raise ValueError; integer mask raises TypeError.

**Verify:** Capture each exception independently and confirm the original two-target result still passes.

## Exercise 6: Challenge a tokenizer ranking

A assigns probability 0.25 to its one token, so mean NLL is ln(4) and perplexity 4. B assigns 0.5 to each of three character targets, yielding perplexity 2 but complete-string probability \({0.5}^{3}=0.125\). The smaller B perplexity did not mean it assigned more probability to the same complete string. Neither alone proves answer quality. A compatible comparison must state representation and unit, or use an independently justified common scoring basis rather than sorting raw token perplexities.

**Expected:** A perplexity 4 with string probability 0.25; B perplexity 2 with string probability 0.125.

**Verify:** Assert both scores and explain why the smaller raw perplexity cannot directly rank these incompatible token units.

## Inspectable reference functions

*Two target probabilities* validates and reduces its input in the functions below; the executable file covers all six cross entropy, perplexity and denominator traps exercises. Keep the *Reject an absent or invalid score* assertion and its invalid-input case; never replace them with a default.

```python
from __future__ import annotations
import math


def score_targets(probabilities, mask=None):
    probabilities = list(probabilities)
    if not probabilities:
        raise ValueError("nonempty probability sequence required")
    if any(not math.isfinite(float(p)) or float(p) < 0 or float(p) > 1 for p in probabilities):
        raise ValueError("finite probabilities in [0,1] required")
    if mask is None:
        mask = [True] * len(probabilities)
    mask = list(mask)
    if any(type(value) is not bool for value in mask):
        raise TypeError("mask must be boolean")
    if len(mask) != len(probabilities) or not any(mask):
        raise ValueError("same-length mask with active targets required")
    active = [float(p) for p, include in zip(probabilities, mask) if include]
    total = math.inf if 0 in active else math.fsum(-math.log(p) for p in active)
    mean = total / len(active)
    try:
        perplexity = math.exp(mean)
    except OverflowError:
        perplexity = math.inf
    return {
        "total_nll": total,
        "active_targets": len(active),
        "mean_nll": mean,
        "perplexity": perplexity,
    }
```

## Retrieval and alternatives

Without formulas in view, derive the mean loss and perplexity for probabilities [1, 0.5]. Then explain why adding an ignored padding target should change neither the loss nor the active-target count.

Next, pick a fixture unlike *Two target probabilities* to test independent recall, and explain why *Reject an absent or invalid score* rejects its case rather than naming the exception. Any notation works if cross entropy here and its denominator stay explicit; these cross entropy, perplexity and denominator traps checks say nothing about unseen model quality or safety.
