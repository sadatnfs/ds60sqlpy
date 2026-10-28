# eval-015: Monitoring, delayed labels and online experiments

## Starting point and outcome

Advanced; approximately 120 minutes. Direct prerequisites: `eval-007`, `eval-012`, `eval-014`.

Monitor mature cohorts and service behavior without confusing delayed outcomes or changing traffic with model improvement.

## Classroom execution

Choose **LLM evaluation and alignment** in `/classroom`, open `eval-015`, and use its `python-core` profile. A Run starts a fresh Python process. Both worked programs below include their own setup and can be copied in full. Save your draft first. The examples use small authored fixtures and explicit numerical checks. Process success establishes those checks, not population validity, safety certification or natural-language competence. Code and notes persist; temporary program files do not. No network call or model download is needed.

## Monitoring observes a changing process

A deployed assistant receives a changing mix of requests, permissions, documents and user behavior. Its model may stay fixed while its inputs or evaluation labels change. Monitoring should therefore retain the system version, event time, label-availability time, eligibility rules and denominator for every reported metric.

Fast labels can be selected labels. Easy successful requests may receive immediate confirmation, while difficult failures are investigated later. Reporting correctness only among currently labeled items can make early performance look favorable even when the full cohort will not be. A mature-cohort rule can compare outcomes after a common follow-up window, but its assumptions must match the actual label process.

Distribution shift and quality degradation are also distinct. An input histogram can change without altering conditional task performance. Quality can deteriorate with an unchanged coarse histogram if the model or an unmonitored feature changes. Use drift measures as diagnostic signals alongside outcome, coverage, latency and critical-error measurements.

## Worked case A: the same cohort changes as labels arrive

Two requests occur on day 1. The success label arrives on day 2; the failure label arrives on day 10. At day 2 the observed-label accuracy is one with half the cohort labeled. At day 10 it is one half with complete label coverage. No model changed between these reports. Comparing the two numbers without maturity information would create a false story about performance decay.

```python
import numpy as np


def observed_cohort(rows, as_of):
    eligible = [r for r in rows if r["event"] <= as_of]
    observed = [r for r in eligible if r["label_available"] <= as_of]
    return {
        "eligible": len(eligible),
        "labeled": len(observed),
        "label_coverage": len(observed) / len(eligible) if eligible else None,
        "accuracy": float(np.mean([r["correct"] for r in observed])) if observed else None,
    }


def js_divergence(p, q):
    p = np.asarray(p, float)
    q = np.asarray(q, float)
    if (
        p.shape != q.shape
        or p.ndim != 1
        or not p.size
        or not np.isfinite(p).all()
        or not np.isfinite(q).all()
        or np.any(p < 0)
        or np.any(q < 0)
        or not np.isclose(p.sum(), 1)
        or not np.isclose(q.sum(), 1)
    ):
        raise ValueError("Probability vectors required")
    m = (p + q) / 2

    def term(x):
        positive = x > 0
        return float(np.sum(x[positive] * np.log(x[positive] / m[positive])))

    return (term(p) + term(q)) / 2


def worked_a():
    rows = [
        {"event": 1, "label_available": 2, "correct": 1},
        {"event": 1, "label_available": 10, "correct": 0},
    ]
    early = observed_cohort(rows, 2)
    mature = observed_cohort(rows, 10)
    assert early["accuracy"] == 1 and early["label_coverage"] == 0.5
    assert mature["accuracy"] == 0.5 and mature["label_coverage"] == 1
    print("Early:", early, "mature:", mature)


worked_a()
```

## Worked case B: drift is a bounded diagnostic

The Jensen-Shannon divergence compares two categorical distributions through their midpoint \(M=(P+Q)/2\):

\[
\operatorname{JS}(P,Q)=\tfrac12 D_{KL}(P\Vert M)+\tfrac12 D_{KL}(Q\Vert M).
\]

With natural logarithms it lies between zero and \(\log 2\). The helper treats zero-probability terms as zero contributions, validates the probability vectors and reports a finite diagnostic for a changed traffic mix. A large value does not directly measure answer correctness or identify the cause of a change. SciPy `jensenshannon` returns the square root of this divergence, which is a distance; square that return value to compare with this helper. SciPy also normalizes its inputs, while this teaching helper deliberately rejects an invalid probability vector.

```python
import numpy as np


def observed_cohort(rows, as_of):
    eligible = [r for r in rows if r["event"] <= as_of]
    observed = [r for r in eligible if r["label_available"] <= as_of]
    return {
        "eligible": len(eligible),
        "labeled": len(observed),
        "label_coverage": len(observed) / len(eligible) if eligible else None,
        "accuracy": float(np.mean([r["correct"] for r in observed])) if observed else None,
    }


def js_divergence(p, q):
    p = np.asarray(p, float)
    q = np.asarray(q, float)
    if (
        p.shape != q.shape
        or p.ndim != 1
        or not p.size
        or not np.isfinite(p).all()
        or not np.isfinite(q).all()
        or np.any(p < 0)
        or np.any(q < 0)
        or not np.isclose(p.sum(), 1)
        or not np.isclose(q.sum(), 1)
    ):
        raise ValueError("Probability vectors required")
    m = (p + q) / 2

    def term(x):
        positive = x > 0
        return float(np.sum(x[positive] * np.log(x[positive] / m[positive])))

    return (term(p) + term(q)) / 2


def worked_b():
    value = js_divergence([0.8, 0.2], [0.2, 0.8])
    assert np.isclose(value, 0.8 * np.log(1.6) + 0.2 * np.log(0.4))
    assert 0 < value < np.log(2)
    assert np.isclose(js_divergence([1, 0], [0, 1]), np.log(2))
    print("Traffic JS divergence:", value)


worked_b()
```

## Online experiments need stable assignment

If comparing a new policy online, define the randomization unit and keep assignment stable for that unit. Requests from the same user can share history and affect one another. Randomizing every request may expose a user to both policies and violate a no-interference assumption. Conversely, user-level assignment requires user-level or cluster-aware analysis, even when many request rows are observed.

Version the entire treatment: model, prompt, retrieval policy, tools and fallback behavior. Record assignment and actual exposure separately. Failures before a response is returned remain part of an intention-to-treat analysis when that is the declared estimand. Analyze delayed labels with the planned maturity policy rather than peeking at whichever outcomes arrived first.

## Guardrails and incident decisions

Monitor latency and timeout rates as well as semantic quality. A correct answer returned after an operational deadline can have low utility. Keep critical policy failures separate from averages and define a rollback path that restores a known configuration with its artifacts. Alert thresholds should be calibrated to the monitoring procedure and the consequences of false alarms and missed incidents.

When a signal changes, inspect cohort composition, label coverage, missingness, infrastructure events and configuration history before attributing it to the model. A drift alert is a reason to investigate. It is not, by itself, a causal estimate of a model effect or a mandate to retrain.

The programs demonstrate delayed-label accounting and exact categorical divergence on synthetic data. They do not run a live monitoring service. An operational deployment needs reliable instrumentation, ownership, privacy review and a validated decision process, with the same explicit distinction between observed data and the claim it can support.


## Six investigations

### 1. Report immature labels

Evaluate the two requests at day 2.

**Expected:** Accuracy 1 with label coverage 0.5.

**Hint:** Use the same eligible cohort in both denominators.

### 2. Wait for the cohort

Evaluate the same requests at day 10.

**Expected:** Accuracy 0.5 and label coverage 1.

**Hint:** No model change is required for the apparent decline.

### 3. Identical distributions

Compare a histogram to itself.

**Expected:** JS divergence 0.

**Hint:** Every log ratio is 1 before taking the logarithm.

### 4. Disjoint support

Compare[1,0] with[0,1] using natural logarithms.

**Expected:** JS divergence is log 2.

**Hint:** Both are compared to their midpoint.

### 5. Choose assignment units

Requests from one user share conversational history.

**Expected:** Consider user-level assignment and cluster-aware analysis.

**Hint:** Interference can occur across request rows.

### 6. Investigate an alert

A drift score rises while mature-cohort quality is stable.

**Expected:** Investigate composition and coverage before concluding model degradation.

**Hint:** A diagnostic is not a causal attribution.

## Primary references

- [Existing online experimentation route](../../../courses/statistics-ml/tutorials/experimentation/README.md)
- [scipy Jensen-Shannon distance definition](https://docs.scipy.org/doc/scipy/reference/generated/scipy.spatial.distance.jensenshannon.html)

## Study companion

Use the repository learning-companion skill with this lesson ID and your own source/output. Ask for clarification of the estimand, probability distribution, data split or gradient before a hint. Keep claims about the authored fixture separate from claims requiring real population or model evidence.
