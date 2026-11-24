# eval-008: explained reference

`eval-008_reference.py` asserts each answer below, from *Separate recall from nDCG* to *Preserve target weights*, on the authored recall at k and MRR fixture only. Before applying a conclusion to other data, recheck the assumption that *Repeat a document* tests.

## 1. Separate recall from nDCG

nDCG evaluates the quality of the available ranking positions. Recall asks what fraction of all known relevant documents was retrieved.

**Approach.** Read case A: gold grades `{"a": 3, "b": 2, "c": 0, "d": 1}`, ranking `["a", "b", "c"]`, cutoff 2. Count relevant documents (grade above 0) and see which appear in the top two.

**Why it holds for this fixture.** Three documents are relevant: a, b and d. The top two are a and b, so recall is 2 / 3. nDCG compares the top two with the ideal top two, grades 3 and 2, which is exactly what was returned, so nDCG is 1. The missing d does not fit in two positions anyway.

**A tempting wrong approach.** Expecting nDCG 1 to mean everything relevant was found is the mistake. nDCG at k only judges the k available slots. A cutoff smaller than the relevant set guarantees recall below 1 even for a perfect ranking.

**How to verify.** Worked case A asserts the result equals `{"recall": 2 / 3, "mrr": 1.0, "ndcg": 1.0}`. Raising k to 3 with `d` in third place would make recall 1.

**Expected observation:** An ideal top two still omits one relevant document.

## 2. Return no relevant hit

Zero is meaningful here because relevant documents exist in the judged corpus but none was retrieved.

**Approach.** Call `retrieval_metrics(["b"], {"a": 1, "b": 0}, 1)`. The single returned document has grade 0, and one relevant document, `a`, exists.

**Why it holds for this fixture.** Recall is 0 / 1 = 0. No relevant hit appears, so the first-hit position is `None` and reciprocal rank is 0. DCG is 0 while ideal DCG is positive, so nDCG is 0. Each zero is a real failure on a query where success was possible.

**A tempting wrong approach.** Treating these zeros like the missing values in exercise 5 would remove a real failure from the mean. The distinction is whether any relevant document exists in the judgments; here one does.

**How to verify.** The reference asserts the result equals `{"recall": 0.0, "mrr": 0, "ndcg": 0.0}`. Swap to `["a"]` with k 10 and confirm nDCG is 1.

**Expected observation:** Recall, reciprocal rank and nDCG are 0.

## 3. Repeat a document

Counting duplicates as new hits can inflate recall or distort position metrics.

**Approach.** Call `retrieval_metrics(["a", "a"], {"a": 1, "b": 0}, 2)`. The guard compares `len(set(ranking))` with `len(ranking)` and raises.

**Why it holds for this fixture.** A retriever that returns the same relevant ID twice would earn DCG credit at positions 1 and 2. If recall counted list entries rather than distinct IDs, it could exceed 1. Rejecting duplicates keeps every metric tied to distinct documents.

**A tempting wrong approach.** Deduplicating inside the metric seems kind, but it hides a retriever bug. A system that wastes slots on duplicates should be fixed upstream, and its effective depth reported, not scored as if its list were clean.

**How to verify.** The reference includes `(["a", "a"], 2)` in the invalid cases and fails with `Invalid ranking accepted` if it passes.

**Expected observation:** The fixture rejects duplicates.

## 4. Add an unjudged document

A separate assessment or a declared missing-judgment policy is needed before comparing systems fairly.

**Approach.** Call `retrieval_metrics(["x"], {"a": 1, "b": 0}, 1)`. Document `x` has no grade, so the check `d not in relevance` raises `Unjudged document`.

**Why it holds for this fixture.** Unjudged documents are common when a new retriever surfaces items the original assessors never saw. Treating them as irrelevant penalizes the new system for novelty, and treating them as relevant rewards it without evidence.

**A tempting wrong approach.** Filling missing grades with 0 is the usual shortcut. It biases comparisons in favor of the system whose results were used to build the judgment pool, which is usually the older one.

**How to verify.** The reference includes `(["x"], 1)` in the invalid cases. Either judge the new document or declare a policy (such as condensed lists that skip unjudged items) and apply it to every system.

**Expected observation:** The calculation rejects it.

## 5. Empty relevant set

Report the affected query count and its interpretation instead of silently mixing undefined scores into a mean.

**Approach.** Call `retrieval_metrics([], {"b": 0}, 1)`. No judged document has a positive grade, so the function returns `None` for all three metrics before computing anything.

**Why it holds for this fixture.** Recall divides by the number of relevant documents, here 0, and ideal DCG is also 0. Both ratios would be 0 / 0. Returning `None` keeps the query visible as undefined instead of assigning a misleading number.

**A tempting wrong approach.** Filling `None` with 1 (nothing to find, so perfect) or 0 (nothing found) changes the mean depending on how many such queries exist. A test set with many empty-relevance queries could then swing averages without any change in retrieval quality.

**How to verify.** The reference asserts `retrieval_metrics([], {"b": 0}, 1)["recall"] is None`. In a report, give the count of such queries and exclude them explicitly from each average.

**Expected observation:** Recall and nDCG are reported as missing.

## 6. Preserve target weights

The weighting rule defines whose query distribution the result represents; it should be shared by every compared retriever.

**Approach.** Take two queries with nDCG 1.0 and 0.5. Average them with equal weights, then with traffic weights such as 0.9 and 0.1.

**Why it holds for this fixture.** The equal average is 0.75 and the traffic-weighted average is 0.9 times 1.0 plus 0.1 times 0.5 = 0.95. Both are correct arithmetic. They answer different questions: typical query quality versus quality experienced by the average request.

**A tempting wrong approach.** Comparing retriever A's traffic-weighted mean with retriever B's equal-query mean is the mistake. The gap would come from the weighting, as in eval-005, not from the retrievers.

**How to verify.** Recompute both averages for each retriever with the same weight vector, and confirm the difference between retrievers is reported under one stated weighting.

**Expected observation:** They can differ without a coding error.
