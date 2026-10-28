# eval-008: Retrieval evaluation and ranking denominators

## Starting point and outcome

Intermediate; approximately 120 minutes. Direct prerequisites: `eval-005`, `eval-006`.

Evaluate retrieval separately from answer quality with explicit relevance grades, duplicate handling and unjudged-document policy.

## Classroom execution

Choose **LLM evaluation and alignment** in `/classroom`, open `eval-008`, and use its `python-core` profile. A Run starts a fresh Python process. Both worked programs below include their own setup and can be copied in full. Save your draft first. The examples use small authored fixtures and explicit numerical checks. Process success establishes those checks, not population validity, safety certification or natural-language competence. Code and notes persist; temporary program files do not. No network call or model download is needed.

## Locate the failure in the pipeline

A retrieval-augmented assistant selects candidate documents, ranks some of them, forms a context and generates an answer. Failure at one stage can be hidden by success at another. A correct answer does not prove that retrieval was adequate, because a model may know the answer independently. A relevant retrieved passage does not prove that the generated answer used it correctly.

Define the candidate corpus and the query population before choosing a ranking metric. A relevance judgment is conditional on a query, a document version and a rubric. It is not a permanent property of a document. An evaluation based on a judgment pool sees only the documents that were judged; relevant documents outside the pool can change recall and ideal rankings.

For a query with a known nonempty relevant set \(G\), recall at \(k\) is the fraction of \(G\) appearing in the first \(k\) distinct results. Reciprocal rank uses the first relevant position. With graded relevance \(r_j\), a common discounted gain is

\[
\operatorname{DCG}@k=\sum_{j=1}^{k}\frac{2^{r_j}-1}{\log_2(j+1)}.
\]

Normalized DCG divides by the ideal DCG obtained by sorting the known relevance grades. The gain convention and discount base are part of the metric definition. These examples use nonnegative integer grades and reject unjudged documents instead of silently assigning them zero relevance. The scikit-learn function discounts the relevance values it receives directly. To reproduce this exponential-gain convention with that API, supply `2**grade - 1` as its relevance values in the same document order. Comparing raw-grade and exponential-gain nDCG without naming the difference changes the metric.

## Worked case A: a strong top ranking

The corpus has three relevant documents with grades 3,2,1 and one irrelevant document. Returning the grade 3 and grade 2 documents first gives recall two thirds at depth two, reciprocal rank one and nDCG one. Perfect nDCG at this cutoff does not imply complete recall, because an ideal top two still omits a third relevant document.

```python
import math


def retrieval_metrics(ranking, relevance, k):
    if type(k) is not int or k < 1 or len(set(ranking)) != len(ranking):
        raise ValueError("Distinct ranking and positive cutoff required")
    if any(d not in relevance for d in ranking):
        raise ValueError("Unjudged document")
    if any(type(v) is not int or v < 0 for v in relevance.values()):
        raise ValueError("Invalid grade")
    positives = {d for d, r in relevance.items() if r > 0}
    if not positives:
        return {"recall": None, "mrr": None, "ndcg": None}
    top = ranking[:k]
    dcg = sum((2 ** relevance[d] - 1) / math.log2(i + 2) for i, d in enumerate(top))
    ideal = sum(
        (2**r - 1) / math.log2(i + 2)
        for i, r in enumerate(sorted(relevance.values(), reverse=True)[:k])
    )
    first = next((i + 1 for i, d in enumerate(top) if relevance[d] > 0), None)
    return {
        "recall": len(positives.intersection(top)) / len(positives),
        "mrr": 0 if first is None else 1 / first,
        "ndcg": dcg / ideal,
    }


def worked_a():
    gold = {"a": 3, "b": 2, "c": 0, "d": 1}
    result = retrieval_metrics(["a", "b", "c"], gold, 2)
    assert result == {"recall": 2 / 3, "mrr": 1.0, "ndcg": 1.0}
    print("Top-two metrics:", result)


worked_a()
```

## Worked case B: weak retrieval can have a nonzero first hit

The second ranking begins with an irrelevant document followed by a grade 1 document. Reciprocal rank is one half, but the discounted gain is small relative to the ideal top two. A single first-hit measure misses this difference in graded utility. Repeating one highly relevant document is rejected, because duplicate entries should not count as additional retrieved evidence.

```python
import math


def retrieval_metrics(ranking, relevance, k):
    if type(k) is not int or k < 1 or len(set(ranking)) != len(ranking):
        raise ValueError("Distinct ranking and positive cutoff required")
    if any(d not in relevance for d in ranking):
        raise ValueError("Unjudged document")
    if any(type(v) is not int or v < 0 for v in relevance.values()):
        raise ValueError("Invalid grade")
    positives = {d for d, r in relevance.items() if r > 0}
    if not positives:
        return {"recall": None, "mrr": None, "ndcg": None}
    top = ranking[:k]
    dcg = sum((2 ** relevance[d] - 1) / math.log2(i + 2) for i, d in enumerate(top))
    ideal = sum(
        (2**r - 1) / math.log2(i + 2)
        for i, r in enumerate(sorted(relevance.values(), reverse=True)[:k])
    )
    first = next((i + 1 for i, d in enumerate(top) if relevance[d] > 0), None)
    return {
        "recall": len(positives.intersection(top)) / len(positives),
        "mrr": 0 if first is None else 1 / first,
        "ndcg": dcg / ideal,
    }


def worked_b():
    import numpy as np

    gold = {"a": 3, "b": 2, "c": 0, "d": 1}
    result = retrieval_metrics(["c", "d", "b"], gold, 2)
    expected = (1 / math.log2(3)) / (7 + 3 / math.log2(3))
    assert (
        result["recall"] == 1 / 3 and result["mrr"] == 0.5 and np.isclose(result["ndcg"], expected)
    )
    print("Weak ranking:", result)


worked_b()
```

## Averaging queries and handling missing judgments

Macro-averaging gives each query equal weight. Traffic-weighted averaging represents a different population. Multiple paraphrases from a family can also create dependence and unequal representation. The sampling and uncertainty rules from earlier units apply to ranking metrics just as they apply to answer correctness.

A query with no known relevant documents has an undefined recall denominator and zero ideal DCG. The helper returns explicit missing values for that case. This policy prevents a zero from being mistaken for evidence of a poor retriever or a one from being mistaken for a perfect one. A study may adopt another documented convention, but it should report how many queries fall into that category.

Judgment pooling can favor systems whose retrieved documents helped form the pool. Add new candidates for blinded relevance assessment when a different retriever discovers new material. Explain how the pool was constructed and consider sensitivity to unjudged documents. Do not use a silently incomplete gold set to claim exhaustive recall.

## Connect retrieval to the final decision

Measure latency, memory, update freshness and access policy alongside ranking quality. A retriever that returns a forbidden document is unacceptable even if the document is relevant. Keep pre-retrieval authorization and post-retrieval evidence checks distinct. Later units evaluate claim support and abstention after retrieval.

The programs operate on authored relevance tables and ordered identifiers. They do not call a search engine or evaluate a live vector database. Their exact counts make the definitions and invalid-input policies visible before using a larger system. To transfer the method, retain the query/corpus snapshot, all ranked IDs, judgments, tie rule and query weights so another analyst can reconstruct every aggregate.


## Six investigations

### 1. Separate recall from nDCG

Explain why case A has nDCG 1 but recall 2/3.

**Expected:** An ideal top two still omits one relevant document.

**Hint:** Compare the denominators.

### 2. Return no relevant hit

Rank only the irrelevant document at depth 1.

**Expected:** Recall, reciprocal rank and nDCG are 0.

**Hint:** The relevant denominator remains positive.

### 3. Repeat a document

Put the same relevant ID in two result positions.

**Expected:** The fixture rejects duplicates.

**Hint:** Evidence identity is part of the ranking contract.

### 4. Add an unjudged document

Return a document absent from the relevance map.

**Expected:** The calculation rejects it.

**Hint:** Unknown relevance is not proven irrelevance.

### 5. Empty relevant set

Evaluate a query for which every judged document has grade 0.

**Expected:** Recall and nDCG are reported as missing.

**Hint:** The denominator lacks relevant evidence.

### 6. Preserve target weights

Compare equal-query and traffic-weighted averages.

**Expected:** They can differ without a coding error.

**Hint:** Carry forward the estimand contract.

## Primary references

- [RAG evaluation dimensions](https://arxiv.org/abs/2309.15217)
- [scikit-learn nDCG definition](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.ndcg_score.html)

## Study companion

Use the repository learning-companion skill with this lesson ID and your own source/output. Ask for clarification of the estimand, probability distribution, data split or gradient before a hint. Keep claims about the authored fixture separate from claims requiring real population or model evidence.
