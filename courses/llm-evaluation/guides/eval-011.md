# eval-011: Judge calibration and presentation bias

## Starting point and outcome

Intermediate; approximately 120 minutes. Direct prerequisites: `eval-003`, `eval-004`, `eval-010`.

Audit a judge using identity-aware order swaps and held-out probability calibration while keeping agreement distinct from correctness.

## Classroom execution

Choose **LLM evaluation and alignment** in `/classroom`, open `eval-011`, and use its `python-core` profile. A Run starts a fresh Python process. Both worked programs below include their own setup and can be copied in full. Save your draft first. The examples use small authored fixtures and explicit numerical checks. Process success establishes those checks, not population validity, safety certification or natural-language competence. Code and notes persist; temporary program files do not. No network call or model download is needed.

## Evaluate the evaluator

A model judge can help scale annotation, but its outputs remain measurements with error. A benchmark result depends on the judge model, rubric, prompt, candidate presentation, reference material and aggregation rule. A judge that repeats the same decision reliably can still prefer longer text, familiar style or the first displayed answer. Repeatability alone is not validity.

In a paired comparison, distinguish candidate identity from display position. If candidate A is shown on the left, a left win favors A; if A is shown on the right, that same left win favors B. Failing to invert the outcome after swapping positions produces an incorrect identity-level score. Counterbalancing makes position effects observable, although it does not automatically remove every interaction between position and answer quality.

Research on model judges motivates audits of order, verbosity and related presentation effects. The examples here do not call a judge model. They use deliberately authored judge decisions so the accounting and failure modes can be checked independently of a particular model's behavior.

## Worked case A: an always-left judge

The same pair is displayed in both orientations. An always-left judge gives candidate A a win in one orientation and a loss in the other, averaging one half. Its identity-level decisions are inconsistent under the swap even though its position behavior is perfectly consistent. A quality-sensitive authored judge that prefers A in both orientations has identity consistency one.

```python
import numpy as np


def identity_wins(left_wins, a_on_left):
    if len(left_wins) != len(a_on_left) or not left_wins:
        raise ValueError("Paired orientations required")
    if any(type(side) is not bool for side in a_on_left) or any(
        win not in (0, 0.5, 1) for win in left_wins
    ):
        raise ValueError("Known comparison labels and Boolean orientation required")
    return np.array(
        [float(win if left else 1 - win) for win, left in zip(left_wins, a_on_left, strict=True)]
    )


def calibration(probabilities, labels, edges=(0.0, 0.5, 1.0)):
    p = np.asarray(probabilities, float)
    y = np.asarray(labels, float)
    if (
        p.shape != y.shape
        or not p.size
        or np.any((p < 0) | (p > 1))
        or not np.isfinite(p).all()
        or np.any((y != 0) & (y != 1))
    ):
        raise ValueError("Invalid calibration records")
    edges = np.asarray(edges, float)
    if (
        edges.ndim != 1
        or len(edges) < 2
        or not np.isfinite(edges).all()
        or edges[0] != 0
        or edges[-1] != 1
        or np.any(np.diff(edges) <= 0)
    ):
        raise ValueError("Increasing probability bin edges required")
    bin_id = np.clip(np.searchsorted(edges, p, side="right") - 1, 0, len(edges) - 2)
    ece = 0.0
    for index in range(len(edges) - 1):
        take = bin_id == index
        if take.any():
            ece += take.mean() * abs(p[take].mean() - y[take].mean())
    return float(np.mean((p - y) ** 2)), float(ece)


def worked_a():
    biased = identity_wins([1, 1], [True, False])
    quality = identity_wins([1, 0], [True, False])
    assert biased.tolist() == [1.0, 0.0] and biased.mean() == 0.5
    assert quality.tolist() == [1.0, 1.0]
    print(
        "Always-left identity scores:", biased.tolist(), "consistent preference:", quality.tolist()
    )


worked_a()
```

## Worked case B: calibration does not imply discrimination

For probabilistic judgments \(p_i\) and binary reference labels \(y_i\), the Brier score is

\[
\operatorname{BS}=\frac{1}{n}\sum_i(p_i-y_i)^2.
\]

A binned calibration error compares mean probability and observed frequency within bins, weighting each absolute gap by its bin size. This helper places an internal boundary in the higher bin, with probability 1 included in the last bin. Its value depends on bin boundaries and finite sample noise; it is not a complete proper scoring rule. A constant 0.5 predictor on balanced labels can have zero binned calibration error while having no useful discrimination. The code contrasts that case with more informative probabilities.

```python
import numpy as np


def identity_wins(left_wins, a_on_left):
    if len(left_wins) != len(a_on_left) or not left_wins:
        raise ValueError("Paired orientations required")
    if any(type(side) is not bool for side in a_on_left) or any(
        win not in (0, 0.5, 1) for win in left_wins
    ):
        raise ValueError("Known comparison labels and Boolean orientation required")
    return np.array(
        [float(win if left else 1 - win) for win, left in zip(left_wins, a_on_left, strict=True)]
    )


def calibration(probabilities, labels, edges=(0.0, 0.5, 1.0)):
    p = np.asarray(probabilities, float)
    y = np.asarray(labels, float)
    if (
        p.shape != y.shape
        or not p.size
        or np.any((p < 0) | (p > 1))
        or not np.isfinite(p).all()
        or np.any((y != 0) & (y != 1))
    ):
        raise ValueError("Invalid calibration records")
    edges = np.asarray(edges, float)
    if (
        edges.ndim != 1
        or len(edges) < 2
        or not np.isfinite(edges).all()
        or edges[0] != 0
        or edges[-1] != 1
        or np.any(np.diff(edges) <= 0)
    ):
        raise ValueError("Increasing probability bin edges required")
    bin_id = np.clip(np.searchsorted(edges, p, side="right") - 1, 0, len(edges) - 2)
    ece = 0.0
    for index in range(len(edges) - 1):
        take = bin_id == index
        if take.any():
            ece += take.mean() * abs(p[take].mean() - y[take].mean())
    return float(np.mean((p - y) ** 2)), float(ece)


def worked_b():
    brier, ece = calibration([0.9, 0.8, 0.2, 0.1], [1, 1, 0, 0])
    assert np.isclose(brier, 0.025) and np.isclose(ece, 0.15)
    constant = calibration([0.5] * 4, [1, 1, 0, 0])
    assert constant == (0.25, 0.0)
    print("Informative scores:", brier, ece, "constant calibration:", constant)


worked_b()
```

## Build a calibration protocol

Use adjudicated labels or another justified reference set to assess the judge. Fit any calibration mapping on development data, freeze it, and evaluate it on separate items. With repeated variants, split by the relevant family before fitting the mapping. Otherwise a well-calibrated development curve can hide overfitting to familiar prompts.

Report probability quality, label accuracy, abstentions and disagreement with humans separately. Confidence intervals must respect paired or clustered observations. When human labels are themselves uncertain, describe their protocol and examine sensitivity to disputed items. A judge should not be promoted to ground truth merely because its name or parameter count suggests authority.

## Counterexamples and diagnosis

Swap order while preserving exact answer text. Then change length without adding information, or change formatting while retaining the same factual claims. These interventions test particular invariances; they do not establish universal fairness. Preserve the original outputs and every intervention so a reviewer can reproduce the comparison.

If a judge changes its answer after a swap, inspect whether the rubric permits a tie, whether a truncation boundary changed, and whether references were attached to positions rather than identities. If a probability score looks good, inspect the reliability table and a discrimination metric as well. The constant predictor is a useful sanity check because it exposes why a single calibration number cannot summarize judge quality.

This unit establishes metric arithmetic and presentation bookkeeping on constructed decisions. Real model-judge validation requires representative items, a fixed rubric, independent reference evidence and a documented operating context. An evaluator can support a scientific decision only to the extent that those conditions have been examined.


## Six investigations

### 1. Invert the swapped result

Candidate A is on the right and the left answer wins.

**Expected:** The identity score for A is 0.

**Hint:** Map position back to candidate identity.

### 2. Check perfect probabilities

Score probabilities 1,0 against labels 1,0.

**Expected:** Brier and the stated ECE are 0.

**Hint:** Use the actual labels, not a thresholded probability.

### 3. Check maximally wrong probabilities

Score 0,1 against 1,0.

**Expected:** Both reported scores are 1.

**Hint:** Each squared error is 1.

### 4. Use a constant judge

Give probability 0.5 to balanced labels.

**Expected:** ECE 0 and Brier 0.25 under these bins.

**Hint:** Calibration and discrimination answer different questions.

### 5. Test verbosity invariance

Duplicate an answer paragraph without adding a claim.

**Expected:** Record whether identity preference changes.

**Hint:** Hold candidate meaning and the comparison partner fixed.

### 6. Freeze a recalibration mapping

Fit a mapping on development labels, then evaluate it on new families.

**Expected:** Final labels do not influence the fitted mapping.

**Hint:** Treat recalibration as model selection.

## Primary references

- [Model-judge presentation bias study](https://arxiv.org/abs/2306.05685)
- [scikit-learn probability calibration](https://scikit-learn.org/stable/modules/calibration.html)

## Study companion

Use the repository learning-companion skill with this lesson ID and your own source/output. Ask for clarification of the estimand, probability distribution, data split or gradient before a hint. Keep claims about the authored fixture separate from claims requiring real population or model evidence.

## Interactive figure variant

Select **Interactive Plotly** in the lesson variant control. Its complete program uses the same authored inputs to draw the corresponding risk, calibration or policy curve. The captured figure retains a description and exact data table, and its JSON can be downloaded. Hovering a point does not create new statistical evidence. The default numerical reference remains separately saved.
