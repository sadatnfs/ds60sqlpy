# eval-001: Evaluation contracts, populations and estimands

## Starting point and outcome

Beginner; approximately 120 minutes. Direct prerequisites: `python-08`, `llm-001`.

Define which population, unit, loss and decision an evaluation estimates, and demonstrate why a different denominator can reverse its conclusion.

## Classroom execution

Choose **LLM evaluation and alignment** in `/classroom`, open `eval-001`, and use its `python-core` profile. A Run starts a fresh Python process. Both worked programs below include their own setup and can be copied in full. Save your draft first. The examples use small authored fixtures and explicit numerical checks. Process success establishes those checks, not population validity, safety certification or natural-language competence. Code and notes persist; temporary program files do not. No network call or model download is needed.

## Define the quantity before collecting scores

An evaluation is an argument about a decision. The Research Support Desk answers questions about metrics, evidence and operational procedures. Before comparing assistants, specify the intended population: all future requests, an equal mixture of task families, or requests admitted by an access policy. These populations can have different averages even when they use the same rows. A benchmark is a sample with a construction process, not the population itself.

An **estimand** is the quantity the analysis seeks to learn. A **metric** is a rule applied to observations to estimate or describe it. The **unit** is what counts as an independent opportunity or randomized entity. A request row can be an observation while a user, document or question family is the dependence unit. A metric definition must include the denominator and how refusals, timeouts, missing labels and duplicate variants are treated. Dropping failures after inspecting outcomes changes the question.

For loss \(L\), system \(s\), input \(X\), outcome \(Y\) and target distribution \(P\), the risk is

\[
R_s(P)=\mathbb{E}_{(X,Y)\sim P}[L(s(X),Y)].
\]

Here \(\mathbb{E}\) denotes expectation: the population-weighted average of the loss under the stated distribution. A sample mean estimates that quantity only under an appropriate sampling or modeling argument.

A paired improvement can be defined as \(\Delta=\mathbb{E}[L_A-L_B]\), so positive values favor B. If using correctness instead, define \(\Delta=\mathbb{E}[C_B-C_A]\). Do not reuse the word improvement while silently reversing this sign convention. The programs use correctness differences with explicit identifiers.

## Worked case A: family balance changes the question

Three metrics questions improve by one point each; one policy question worsens by one. The request-weighted difference is 0.5. Equal weighting of the two family means gives zero. Neither calculation is arithmetically wrong. The first describes the observed request mix; the second treats the two families as equally important. A product decision needs a declared target mix and enough independently sampled families to support its uncertainty analysis.

Duplicating the metrics examples should change the request average if those copies are treated as additional requests. It should not change an equal-family average when the family means themselves stay unchanged. This is an invariant of the estimator, not evidence that duplication creates new information. The assertion below makes the distinction inspectable.

```python
import numpy as np


def family_difference(rows, weighting="request"):
    ids = [r[0] for r in rows]
    if not rows or len(ids) != len(set(ids)):
        raise ValueError("Requests must be nonempty and uniquely paired.")
    differences = np.array([r[3] - r[2] for r in rows], dtype=float)
    if weighting == "request":
        return float(differences.mean())
    if weighting != "family":
        raise ValueError("Unknown weighting")
    families = sorted({r[1] for r in rows})
    return float(np.mean([np.mean([r[3] - r[2] for r in rows if r[1] == f]) for f in families]))


def decision(gates):
    required = {"quality", "label_coverage", "access_policy"}
    return "go" if set(gates) == required and all(v is True for v in gates.values()) else "no-go"


def worked_a():
    rows = [
        ("m1", "metrics", 0, 1),
        ("m2", "metrics", 0, 1),
        ("m3", "metrics", 0, 1),
        ("p1", "policy", 1, 0),
    ]
    assert family_difference(rows) == 0.5
    assert family_difference(rows, "family") == 0
    extended = rows + [(f"m{i}", "metrics", 0, 1) for i in range(4, 10)]
    assert family_difference(extended, "family") == 0
    print(
        "Request difference:",
        family_difference(rows),
        "family difference:",
        family_difference(rows, "family"),
    )


worked_a()
```

## Worked case B: unknown labels and critical failures

Suppose one candidate has two judged successes and one unjudged response. Its observed-label accuracy is 1.0, but only two thirds of eligible responses have labels. Reporting 1.0 without label coverage hides a selection problem. Coding the missing response as a failure changes the estimand too; that may be a conservative operational convention, but it must be named and justified.

A critical access violation remains a separate gate. High average correctness cannot compensate for exposing a restricted document. Keep a decision packet with named metric results, label coverage, critical-error outcomes and unresolved conditions. The code returns an explicit no-go when a required gate fails or remains unknown.

```python
import numpy as np


def family_difference(rows, weighting="request"):
    ids = [r[0] for r in rows]
    if not rows or len(ids) != len(set(ids)):
        raise ValueError("Requests must be nonempty and uniquely paired.")
    differences = np.array([r[3] - r[2] for r in rows], dtype=float)
    if weighting == "request":
        return float(differences.mean())
    if weighting != "family":
        raise ValueError("Unknown weighting")
    families = sorted({r[1] for r in rows})
    return float(np.mean([np.mean([r[3] - r[2] for r in rows if r[1] == f]) for f in families]))


def decision(gates):
    required = {"quality", "label_coverage", "access_policy"}
    return "go" if set(gates) == required and all(v is True for v in gates.values()) else "no-go"


def worked_b():
    labels = [1, 1, None]
    observed = [x for x in labels if x is not None]
    assert np.mean(observed) == 1 and len(observed) / len(labels) == 2 / 3
    gates = {"quality": True, "label_coverage": False, "access_policy": True}
    assert decision(gates) == "no-go"
    gates["label_coverage"] = True
    gates["access_policy"] = None
    assert decision(gates) == "no-go"
    print("Observed accuracy:", np.mean(observed), "label coverage:", len(observed) / len(labels))


worked_b()
```

## Reading the code and diagnosing errors

`family_difference` first pairs systems on the same identifiers, forms differences, then groups them. Means calculated from two independently filtered tables are not paired comparisons. The duplicate-key guard fails before any average is produced. `decision` uses `is True`, so missing evidence cannot become a positive decision by truthiness or by an empty list of failures.

When a result looks unexpectedly favorable, inspect the eligible row count, judged row count, refusal policy and family mix before changing a model. Preserve the original eligibility ledger. Otherwise a later analyst cannot determine whether an improvement came from better answers or from removing difficult requests.

For a real deployment, replace the authored records with a documented sample and a labeling protocol. State the coverage gap, affected users, evaluation period and conditions for revisiting the decision. This lesson establishes arithmetic and contract checks on a synthetic fixture. It does not estimate a real assistant's risk or provide a universal release threshold.


## Six investigations

### 1. Reverse the comparison

Compute B minus A and then A minus B for one success gained by B.

**Expected:** The values are +1 and -1.

**Hint:** Write the sign convention next to the subtraction.

### 2. Change the target mix

Reweight the worked families to 75% metrics and 25% policy.

**Expected:** The weighted improvement is 0.5.

**Hint:** Use family means +1 and -1.

### 3. Duplicate an identifier

Append an existing request with the same ID.

**Expected:** The paired-data validator rejects it.

**Hint:** The number of rows must equal the number of unique IDs.

### 4. Require complete gates

Omit the access-policy result from an otherwise favorable packet.

**Expected:** The result remains no-go.

**Hint:** Check the required field set as well as values.

### 5. Show missing-label coverage

Add a second unjudged row to case B.

**Expected:** Observed accuracy stays 1 while label coverage falls to 0.5.

**Hint:** Keep eligibility and judged denominators separately.

### 6. Define an empty population

Evaluate no eligible requests.

**Expected:** Raise an error instead of returning perfect accuracy.

**Hint:** A zero denominator is not a high score.

## Primary references

- [HELM evaluation framework](https://arxiv.org/abs/2211.09110)
- [Existing task-contract route](../../../courses/llm-applied/guides/llm-applied-001.md)

## Study companion

Use the repository learning-companion skill with this lesson ID and your own source/output. Ask for clarification of the estimand, probability distribution, data split or gradient before a hint. Keep claims about the authored fixture separate from claims requiring real population or model evidence.
