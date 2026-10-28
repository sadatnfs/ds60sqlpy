# eval-003: Annotation rubrics and construct validity

## Starting point and outcome

Beginner; approximately 120 minutes. Direct prerequisites: `eval-002`.

Turn an intended capability into auditable labels, distinguish disagreement from missing evidence, and preserve adjudication history.

## Classroom execution

Choose **LLM evaluation and alignment** in `/classroom`, open `eval-003`, and use its `python-core` profile. A Run starts a fresh Python process. Both worked programs below include their own setup and can be copied in full. Save your draft first. The examples use small authored fixtures and explicit numerical checks. Process success establishes those checks, not population validity, safety certification or natural-language competence. Code and notes persist; temporary program files do not. No network call or model download is needed.

## Operationalize the claim

A rubric connects an intended capability to observations. For the Research Support Desk, an answer may be syntactically valid, numerically correct, supported by its cited source, appropriately scoped and usable by its recipient. These are separate properties. A fluent answer with the wrong denominator can satisfy a style criterion while failing the actual task.

Begin with the use case and the decisions that labels will support. Specify an eligible response, an applicable criterion, the allowed evidence and the unit at which the label is assigned. A citation-support label may belong to a claim, while task completion belongs to an answer. Averaging claim scores gives long answers more weight unless the aggregation rule explicitly addresses that choice.

**Construct validity** asks whether the operational measure represents the intended concept. Reliable annotators can agree perfectly on a poor proxy. For example, a rule that awards a point whenever an answer contains a citation marker is reproducible but does not measure whether the cited passage supports the claim. Conversely, a nuanced factuality rubric may be meaningful yet initially yield poor agreement because its instructions are incomplete.

Use anchored categories with examples and counterexamples. A numerical-answer rubric can distinguish a wrong value, a correct value with an unstated unit, and a fully correct value/unit/denominator. Ordinal levels carry an ordering, but equal distances between adjacent levels are not automatic. A score of two is not necessarily twice the quality of one. Keep labels and aggregation policy separately versioned.

## Worked case A: critical conditions remain separate

The first example evaluates two authored answers. Both have useful surface form, but one fails an access-control condition. A weighted average can still favor that answer if the other dimensions are strong. The release gate therefore combines a minimum quality score with an explicit critical-condition check. The chosen numbers are illustrative policy constants, not universal thresholds for assistants.

The rubric function distinguishes an inapplicable criterion from a failed criterion. Dividing by the full rubric length when some dimensions do not apply penalizes a system for questions it was not asked to answer. Dropping difficult applicable criteria has the opposite problem. Eligibility should be fixed without using the desired outcome.

```python
def rubric_score(criteria):
    applicable = [value for value in criteria.values() if value is not None]
    if not applicable:
        raise ValueError("No applicable rubric dimensions")
    if any(type(v) is not int or v not in (0, 1, 2) for v in applicable):
        raise ValueError("Invalid rubric label")
    return sum(applicable) / (2 * len(applicable))


def admit(criteria, access_ok):
    return rubric_score(criteria) >= 0.75 and access_ok is True


def adjudicate(records, item, label, reason):
    if type(label) is not int or label not in (0, 1, 2):
        raise ValueError("Invalid adjudication label")
    originals = [r for r in records if r["item"] == item]
    if len(originals) < 2 or not reason.strip():
        raise ValueError("Adjudication needs originals and reason")
    if len({r["rubric"] for r in originals}) != 1:
        raise ValueError("Mixed rubric versions")
    return records + [
        {
            "item": item,
            "annotator": "adjudicator",
            "label": label,
            "rubric": originals[0]["rubric"],
            "parents": [r["annotator"] for r in originals],
            "reason": reason,
        }
    ]


def worked_a():
    criteria = {"correctness": 2, "evidence": 2, "style": 2, "format": None}
    assert rubric_score(criteria) == 1
    assert admit(criteria, True) and not admit(criteria, False)
    weaker = {"correctness": 1, "evidence": 1, "style": 2, "format": None}
    assert rubric_score(weaker) == 2 / 3
    print(
        "Applicable score:",
        rubric_score(criteria),
        "restricted answer admitted:",
        admit(criteria, False),
    )


worked_a()
```

## Worked case B: adjudication does not erase evidence

Two reviewers assign different labels. An adjudicator can resolve a production label for downstream scoring, but the original annotations remain useful for assessing ambiguity, training annotators and estimating uncertainty. The code appends an adjudication record linked to the originals instead of overwriting the first reviewer.

An audit ledger needs stable item and annotator IDs, a rubric version, a timestamp or order, the evidence consulted and an adjudication reason. The toy records omit real people and real timestamps intentionally. Their purpose is to show version and lineage checks, not to impersonate an actual human annotation study.

```python
def rubric_score(criteria):
    applicable = [value for value in criteria.values() if value is not None]
    if not applicable:
        raise ValueError("No applicable rubric dimensions")
    if any(type(v) is not int or v not in (0, 1, 2) for v in applicable):
        raise ValueError("Invalid rubric label")
    return sum(applicable) / (2 * len(applicable))


def admit(criteria, access_ok):
    return rubric_score(criteria) >= 0.75 and access_ok is True


def adjudicate(records, item, label, reason):
    if type(label) is not int or label not in (0, 1, 2):
        raise ValueError("Invalid adjudication label")
    originals = [r for r in records if r["item"] == item]
    if len(originals) < 2 or not reason.strip():
        raise ValueError("Adjudication needs originals and reason")
    if len({r["rubric"] for r in originals}) != 1:
        raise ValueError("Mixed rubric versions")
    return records + [
        {
            "item": item,
            "annotator": "adjudicator",
            "label": label,
            "rubric": originals[0]["rubric"],
            "parents": [r["annotator"] for r in originals],
            "reason": reason,
        }
    ]


def worked_b():
    labels = [
        {"item": "q1", "annotator": "a", "label": 1, "rubric": "v1"},
        {"item": "q1", "annotator": "b", "label": 2, "rubric": "v1"},
    ]
    resolved = adjudicate(labels, "q1", 1, "Unit absent from numerical answer")
    assert len(labels) == 2 and len(resolved) == 3
    assert resolved[-1]["parents"] == ["a", "b"] and resolved[1]["label"] == 2
    print("Original labels retained:", [r["label"] for r in labels])


worked_b()
```

## Design a labeling study

Train annotators on a development set, revise ambiguous rules there, and then freeze the rubric before assessing the held-out evaluation set. Blind candidate identity when feasible. Randomize display order for paired judgments and retain that order for analysis. Include repeated and calibration items deliberately, while distinguishing them from new independent observations.

Estimate the resources needed for double labeling and adjudication rather than pretending that every row has equal certainty. A sample of difficult cases selected for adjudication is valuable for improving a rubric, but its disagreement rate is not automatically the population disagreement rate. Sampling weights and selection criteria matter.

## Diagnose a rubric failure

If agreement rises while task usefulness falls, inspect whether the rubric became easier to satisfy rather than more valid. If a model optimizes the visible rubric, test counterexamples that keep the proxy high while damaging the intended outcome. Preserve failures with their original inputs and evidence. A single composite score is insufficient to explain whether a system became more correct, merely longer, or better at producing required formatting.


## Six investigations

### 1. Separate a missing dimension

Score one level 2 criterion and one inapplicable criterion.

**Expected:** Score 1.0 with one applicable dimension.

**Hint:** Keep the denominator explicit.

### 2. Add a critical failure

Give a response all level 2 quality labels but a failed access gate.

**Expected:** The response is not admitted.

**Hint:** Quality and required constraints use separate logic.

### 3. Reject malformed labels

Supply Boolean True as an ordinal rubric level.

**Expected:** The validator rejects it.

**Hint:** Python bool is an int subclass unless checked deliberately.

### 4. Retain reviewer disagreement

Adjudicate labels 1 and 2 to final label 1.

**Expected:** Both original labels remain in the ledger.

**Hint:** Append a linked resolution.

### 5. Change the rubric version

Combine labels from v1 and v2 without a crosswalk.

**Expected:** Adjudication rejects the mixed versions.

**Hint:** A label value only has meaning under its rubric.

### 6. Construct a proxy counterexample

Write a citation-looking response whose cited passage is irrelevant.

**Expected:** Formatting succeeds while evidence support fails.

**Hint:** Separate the marker from the claim-passage relation.

## Primary references

- [Model Cards for Model Reporting](https://arxiv.org/abs/1810.03993)
- [HELM multi-metric evaluation](https://arxiv.org/abs/2211.09110)

## Study companion

Use the repository learning-companion skill with this lesson ID and your own source/output. Ask for clarification of the estimand, probability distribution, data split or gradient before a hint. Keep claims about the authored fixture separate from claims requiring real population or model evidence.
