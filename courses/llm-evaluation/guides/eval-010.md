# eval-010: Abstention, coverage and decision costs

## Starting point and outcome

Intermediate; approximately 120 minutes. Direct prerequisites: `eval-005`, `eval-009`.

Choose and evaluate an abstention policy with explicit costs, coverage and held-out evidence instead of reporting only conditional accuracy.

## Classroom execution

Choose **LLM evaluation and alignment** in `/classroom`, open `eval-010`, and use its `python-core` profile. A Run starts a fresh Python process. Both worked programs below include their own setup and can be copied in full. Save your draft first. The examples use small authored fixtures and explicit numerical checks. Process success establishes those checks, not population validity, safety certification or natural-language competence. Code and notes persist; temporary program files do not. No network call or model download is needed.

## A selective system changes which questions it answers

An assistant can answer, abstain or route a request to a reviewer. These actions have different costs and change the observed output population. An answer-only accuracy of 100% can be achieved by answering one easy item and refusing everything else. Its usefulness depends on coverage, refusal costs and which users are left without help.

For an answer indicator \(A_i(t)\) under threshold \(t\), coverage is \(\mathbb{E}[A_i(t)]\) and selective risk is \(\mathbb{E}[L_i\mid A_i(t)=1]\). The latter is undefined when nothing is answered. Keep that condition explicit. A risk-coverage curve shows several policies, but choosing the best-looking point and reporting its same-data performance introduces selection bias.

If a score is a calibrated probability of correctness \(p\), a simple two-action cost rule compares expected answer cost \(c_w(1-p)\) to abstention cost \(c_a\). With zero cost for a correct answer, answering is preferred when \(p\geq1-c_a/c_w\). Different loss structures, reviewer capacity or consequential subgroups require a different rule. A confidence-like number is not automatically a calibrated probability.

## Worked case A: an empirical policy choice

The development fixture has scores 0.9,0.8,0.4,0.2 and correctness 1,0,1,0. An incorrect answer costs 5 and an abstention costs 0.4. Among four prespecified thresholds,0.85 has the lowest observed development cost: it answers the first request and abstains on the remaining three. Its coverage is one quarter and its conditional accuracy is one.

That empirical threshold differs from the probability-based cutoff 0.92 because the fixture's scores were not supplied as calibrated probabilities and the development set is tiny. The program does not equate a tuned threshold with a Bayes-optimal policy.

```python
import numpy as np


def policy_metrics(scores, correct, threshold, wrong_cost=5.0, abstain_cost=0.4):
    p = np.asarray(scores, float)
    y = np.asarray(correct, float)
    if (
        p.shape != y.shape
        or not p.size
        or not np.isfinite(p).all()
        or np.any((p < 0) | (p > 1))
        or np.any((y != 0) & (y != 1))
        or not 0 <= threshold <= 1
    ):
        raise ValueError("Invalid selective evaluation")
    if not np.isfinite([wrong_cost, abstain_cost]).all() or wrong_cost < 0 or abstain_cost < 0:
        raise ValueError("Finite nonnegative costs required")
    answered = p >= threshold
    return {
        "coverage": float(answered.mean()),
        "accuracy": float(y[answered].mean()) if answered.any() else None,
        "cost": float(np.mean(np.where(answered, wrong_cost * (1 - y), abstain_cost))),
    }


def choose_threshold(scores, correct, thresholds):
    return min(thresholds, key=lambda t: (policy_metrics(scores, correct, t)["cost"], t))


def worked_a():
    scores = [0.9, 0.8, 0.4, 0.2]
    correct = [1, 0, 1, 0]
    threshold = choose_threshold(scores, correct, [0, 0.75, 0.85, 0.95])
    result = policy_metrics(scores, correct, threshold)
    assert threshold == 0.85 and result["coverage"] == 0.25 and result["accuracy"] == 1
    assert np.isclose(result["cost"], 0.3)
    assert np.isclose(1 - 0.4 / 5, 0.92)
    print("Development policy:", threshold, result)


worked_a()
```

## Worked case B: frozen thresholds can fail on new data

A held-out fixture assigns high scores to two incorrect answers and low scores to two correct ones. Applying the frozen 0.85 threshold gives poor selective performance. Retuning on these labels would invalidate their role as final assessment. The adverse case demonstrates a calibration or distribution-shift problem that conditional accuracy on the development set concealed.

```python
import numpy as np


def policy_metrics(scores, correct, threshold, wrong_cost=5.0, abstain_cost=0.4):
    p = np.asarray(scores, float)
    y = np.asarray(correct, float)
    if (
        p.shape != y.shape
        or not p.size
        or not np.isfinite(p).all()
        or np.any((p < 0) | (p > 1))
        or np.any((y != 0) & (y != 1))
        or not 0 <= threshold <= 1
    ):
        raise ValueError("Invalid selective evaluation")
    if not np.isfinite([wrong_cost, abstain_cost]).all() or wrong_cost < 0 or abstain_cost < 0:
        raise ValueError("Finite nonnegative costs required")
    answered = p >= threshold
    return {
        "coverage": float(answered.mean()),
        "accuracy": float(y[answered].mean()) if answered.any() else None,
        "cost": float(np.mean(np.where(answered, wrong_cost * (1 - y), abstain_cost))),
    }


def choose_threshold(scores, correct, thresholds):
    return min(thresholds, key=lambda t: (policy_metrics(scores, correct, t)["cost"], t))


def worked_b():
    result = policy_metrics([0.99, 0.97, 0.3, 0.2], [0, 0, 1, 1], 0.85)
    assert result["coverage"] == 0.5 and result["accuracy"] == 0 and np.isclose(result["cost"], 2.7)
    assert policy_metrics([0.2, 0.3], [1, 1], 0.9)["accuracy"] is None
    print("Frozen policy on held-out outcomes:", result)


worked_b()
```

## Capacity and subgroup tradeoffs

A reviewer queue has finite capacity, so abstention cost can depend on load and delay. A selective policy may also concentrate refusals on rare languages, unfamiliar domains or difficult user groups. Report coverage and loss by relevant slices with uncertainty; a favorable overall score can hide an unacceptable allocation of service.

A threshold policy is only as useful as its score. Calibration should be evaluated on appropriate held-out data, and calibration drift monitored after deployment. A score derived from a model's self-reported confidence can be systematically biased. Token likelihood, a learned correctness predictor and a human judgment measure different things and need their own validation.

## Diagnose the complete decision

Print counts for all eligible requests, answered requests, wrong answers and abstentions. Inspect empty-answer cases and missing correctness labels. If abstained items have no labels, the performance of a counterfactual always-answer system is not directly observed. Do not impute those labels from the fact that the system abstained.

The reference checks exact costs and invalid inputs on constructed outcomes. It does not estimate the costs of a real product or prove that a particular threshold transfers. A deployment study should state who bears each cost, how the score was calibrated, how the threshold was selected and what independent data supported the final decision. Preserve a fallback route for conditions outside the evaluated scope.


## Six investigations

### 1. Answer everything

Use threshold 0 on the development fixture.

**Expected:** Coverage 1, accuracy 0.5 and cost 2.5.

**Hint:** Two of four answers are wrong.

### 2. Abstain on everything

Choose a threshold above every score.

**Expected:** Coverage 0, missing conditional accuracy and cost 0.4.

**Hint:** An empty answered set is not perfect accuracy.

### 3. Check equality

Use score 0.5 and threshold 0.5.

**Expected:** The request is answered.

**Hint:** The policy uses >=.

### 4. Derive the probability cutoff

Use wrong-answer cost 5 and abstention cost 0.4.

**Expected:** The calibrated-probability cutoff is 0.92.

**Hint:** Compare 5(1-p) to 0.4.

### 5. Inspect subgroup coverage

Compute the policy separately for routine and rare requests.

**Expected:** Report each eligible count, coverage and cost.

**Hint:** Overall utility can hide service allocation.

### 6. Protect the final set

The held-out case exposes a bad threshold. What follows?

**Expected:** Use it as a diagnosis and collect a new final assessment after changes.

**Hint:** Changing the policy consumes the old holdout.

## Primary references

- [Selective prediction with neural networks](https://arxiv.org/abs/1705.08500)
- [Existing selective-inference chapter](../../../courses/statistics-ml/chapters/10-multiple-testing-sequential-inference-and-selective-inference.md)

## Study companion

Use the repository learning-companion skill with this lesson ID and your own source/output. Ask for clarification of the estimand, probability distribution, data split or gradient before a hint. Keep claims about the authored fixture separate from claims requiring real population or model evidence.

## Interactive figure variant

Select **Interactive Plotly** in the lesson variant control. Its complete program uses the same authored inputs to draw the corresponding risk, calibration or policy curve. The captured figure retains a description and exact data table, and its JSON can be downloaded. Hovering a point does not create new statistical evidence. The default numerical reference remains separately saved.
