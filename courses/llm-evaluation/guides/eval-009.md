# eval-009: Claim support, citations and evidence provenance

## Starting point and outcome

Intermediate; approximately 120 minutes. Direct prerequisites: `eval-008`, `eval-003`.

Separate claim truth, citation support, evidence coverage and source availability using an auditable claim-document relation.

## Classroom execution

Choose **LLM evaluation and alignment** in `/classroom`, open `eval-009`, and use its `python-core` profile. A Run starts a fresh Python process. Both worked programs below include their own setup and can be copied in full. Save your draft first. The examples use small authored fixtures and explicit numerical checks. Process success establishes those checks, not population validity, safety certification or natural-language competence. Code and notes persist; temporary program files do not. No network call or model download is needed.

## A citation marker is not an entailment judgment

An answer may cite a real document while making an unsupported claim. It may also faithfully repeat a false or outdated statement from that document. Evaluation therefore needs several distinct questions: is the answer correct for the task, does each citation support its associated claim, are important claims supported, and was the source available and authorized when the answer was produced?

The Research Support Desk's evidence ledger identifies a claim, a document version and a support label. A claim may need multiple passages jointly, and a passage may support only one part of a compound claim. Splitting an answer into atomic claims is itself an annotation procedure requiring a rubric. The code uses authored atomic claims and authored support labels so that no model is secretly serving as an unquestioned judge.

Define link precision as supported citation links divided by evaluated citation links, and claim coverage as claims with at least one supported link divided by eligible claims. These quantities have different denominators. A response that cites one claim correctly and leaves nine uncited can have perfect link precision with poor coverage. A response with many irrelevant links can have good coverage but low precision.

## Worked case A: reconstruct the support relation

Three claims have three citation links. Two links are supported, and one claim remains uncited. Link precision and claim coverage are both two thirds in this fixture, but that numerical equality is accidental. Adding an unsupported extra citation changes precision without changing which claims are covered.

```python
def citation_metrics(claims, links, support):
    if not claims or len(set(claims)) != len(claims):
        raise ValueError("Distinct eligible claims required")
    if len(set(links)) != len(links) or any(
        c not in claims or (c, d) not in support for c, d in links
    ):
        raise ValueError("Unjudged or duplicate link")
    if any(type(support[pair]) is not bool for pair in links):
        raise ValueError("Support judgment must be known Boolean")
    valid = [(c, d) for c, d in links if support[c, d] is True]
    return {
        "link_precision": len(valid) / len(links) if links else None,
        "claim_coverage": len({c for c, d in valid}) / len(claims),
    }


def eligible_evidence(document, cutoff, allowed):
    return document["id"] in allowed and document["published"] <= cutoff


def worked_a():
    claims = ["c1", "c2", "c3"]
    links = [("c1", "d1"), ("c2", "d2"), ("c2", "d1")]
    support = {("c1", "d1"): True, ("c2", "d2"): True, ("c2", "d1"): False}
    result = citation_metrics(claims, links, support)
    assert result == {"link_precision": 2 / 3, "claim_coverage": 2 / 3}
    assert citation_metrics(claims, links[:1], support) == {
        "link_precision": 1.0,
        "claim_coverage": 1 / 3,
    }
    print("Citation metrics:", result)


worked_a()
```

## Worked case B: evidence timing and truth are separate

A document published after the answer's decision cutoff was not available to that historical system. The source gate rejects it even if its content is now correct. A cited but restricted document fails authorization independently. These checks happen before treating the document as eligible evidence.

The example also allows a support label to be true while the claim's truth label is false. This represents faithful repetition of an incorrect source. Such a case needs source-quality or contradiction analysis; it cannot be diagnosed by counting citation markers or support labels alone.

```python
def citation_metrics(claims, links, support):
    if not claims or len(set(claims)) != len(claims):
        raise ValueError("Distinct eligible claims required")
    if len(set(links)) != len(links) or any(
        c not in claims or (c, d) not in support for c, d in links
    ):
        raise ValueError("Unjudged or duplicate link")
    if any(type(support[pair]) is not bool for pair in links):
        raise ValueError("Support judgment must be known Boolean")
    valid = [(c, d) for c, d in links if support[c, d] is True]
    return {
        "link_precision": len(valid) / len(links) if links else None,
        "claim_coverage": len({c for c, d in valid}) / len(claims),
    }


def eligible_evidence(document, cutoff, allowed):
    return document["id"] in allowed and document["published"] <= cutoff


def worked_b():
    document = {"id": "d1-v2", "published": 12}
    assert not eligible_evidence(document, 10, {"d1-v2"})
    assert eligible_evidence(document, 12, {"d1-v2"})
    assert not eligible_evidence(document, 12, set())
    support = True
    truth = False
    assert support and not truth
    print("Faithful repetition can still be false:", support, truth)


worked_b()
```

## What a judge can and cannot establish

A human or model judge may assist with support assessment, but its errors require their own evaluation. Keep claim segmentation, support scoring and final correctness scoring as separate versions. Use blinded, calibrated examples, disagreement analysis and sensitivity checks. A larger judge model is not a proof oracle, and repeated agreement with itself is not independent validation.

When multiple documents disagree, define the authority and time policy explicitly. Current documentation may supersede an earlier policy; a corrected table may revise a published metric. A provenance record should retain the content digest or version, passage boundaries and retrieval time. A bare URL can later resolve to different text and cannot reconstruct a historical answer on its own.

## Diagnose citation failures

Start with one claim and inspect its exact supporting passage. Check whether the passage states the relevant value, unit, time range and population. A passage about annual revenue does not support a claim about monthly profit merely because both mention the same company. A cited denominator may also differ from the denominator in the question.

Count missing or unjudged support relations separately from negative labels. The helper refuses links for which the fixture has no support judgment. This is deliberately strict: replacing unknown with false or true would silently change the metric's meaning. A real study can use a sampling design for citation assessment, but must then account for that sampling in its estimates.

The offline programs test evidence identity and arithmetic only. They do not read arbitrary websites, run an entailment model or certify the truth of real documents. A deployment packet should preserve the authorized corpus snapshot, claim ledger, support judgments, unresolved contradictions and critical failures alongside its aggregate scores.


## Six investigations

### 1. One supported claim

Cite only c1 correctly among three eligible claims.

**Expected:** Precision 1, coverage 1/3.

**Hint:** The link and claim denominators differ.

### 2. No citations

Evaluate an answer with one eligible claim and no links.

**Expected:** Precision is missing; coverage is 0.

**Hint:** Distinguish an empty link denominator from absent claim support.

### 3. Unknown support relation

Add a link with no adjudicated support label.

**Expected:** The helper rejects it.

**Hint:** An unjudged pair is not a negative or positive label.

### 4. Duplicate a citation

Repeat an identical claim-document link.

**Expected:** The helper rejects it.

**Hint:** Count distinct evidence relations.

### 5. Use a newer document

Evaluate a day 10 answer with a day 12 document.

**Expected:** That version is ineligible for the historical reconstruction.

**Hint:** Use availability time as well as content.

### 6. Disentangle truth and support

Construct a claim that accurately quotes an erroneous source.

**Expected:** Support can be true while truth is false.

**Hint:** Audit source authority and the task ground truth separately.

## Primary references

- [Citation evaluation research](https://arxiv.org/abs/2305.14627)
- [Existing provenance and retrieval route](../../../courses/llm-applied/README.md)

## Study companion

Use the repository learning-companion skill with this lesson ID and your own source/output. Ask for clarification of the estimand, probability distribution, data split or gradient before a hint. Keep claims about the authored fixture separate from claims requiring real population or model evidence.
