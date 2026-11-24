# eval-009: explained reference

`eval-009_reference.py` asserts each answer below, from *One supported claim* to *Disentangle truth and support*, on the authored citation precision and claim coverage fixture only. Before applying a conclusion to other data, recheck the assumption that *Unknown support relation* tests.

## 1. One supported claim

Perfect precision does not imply that the full answer has adequate evidence coverage.

**Approach.** Use case A's claims `["c1", "c2", "c3"]` and keep only the first link, `("c1", "d1")`, which is judged `True`. Call `citation_metrics` and read both fields.

**Why it holds for this fixture.** One link is judged and it is supported, so link precision is 1 / 1 = 1. Only claim c1 has a supported link, so claim coverage is 1 / 3. The answer makes three claims and offers evidence for one of them.

**A tempting wrong approach.** Reporting precision alone as "citations are 100 percent accurate" is the mistake. A system can reach perfect precision by citing only its easiest claim and leaving the rest unsupported; coverage is what exposes that.

**How to verify.** Worked case A asserts `citation_metrics(claims, links[:1], support) == {"link_precision": 1.0, "claim_coverage": 1 / 3}`. The full three-link version gives 2 / 3 for both.

**Expected observation:** Precision 1, coverage 1/3.

## 2. No citations

There are no links to judge, but no eligible claim has supported evidence.

**Approach.** Call `citation_metrics(["c"], [], {})`. With no links the precision denominator is zero, so the function returns `None` for precision, and coverage is 0 / 1.

**Why it holds for this fixture.** Precision asks what share of offered links are supported; with no links offered, that share is undefined. Coverage asks what share of eligible claims have support; the one claim has none, so 0 is a real, defined failure.

**A tempting wrong approach.** Setting precision to 1 because no citation was wrong rewards an answer for citing nothing. Setting it to 0 confuses "no evidence offered" with "evidence offered and wrong," which the next check distinguishes.

**How to verify.** The reference asserts the result equals `{"link_precision": None, "claim_coverage": 0.0}`. Compare with one link judged `False`, which gives 0.0 for both.

**Expected observation:** Precision is missing; coverage is 0.

## 3. Unknown support relation

Retain missingness and acquire a label or use an explicit assessment-sampling protocol.

**Approach.** Pass a link `("c", "d")` with an empty support dictionary. The function checks `(c, d) not in support` for every link and raises `Unjudged or duplicate link`.

**Why it holds for this fixture.** No one has decided whether document d supports claim c. Including the link with any assumed value would make precision depend on a guess, and the guess would differ between assessors and between runs.

**A tempting wrong approach.** Treating unjudged links as unsupported looks conservative but is not neutral: it penalizes new citation patterns that assessors have not reached yet, which biases comparisons toward the system that produced the judged pool.

**How to verify.** The reference includes `([("c", "d")], {})` in its invalid list and fails with `Invalid citation accepted` if it passes. A `None` value in the support map is also rejected by the Boolean type check.

**Expected observation:** The helper rejects it.

## 4. Duplicate a citation

Duplicated markup should not increase the apparent amount of evidence.

**Approach.** Pass `[("c", "d"), ("c", "d")]` with the pair judged `True`. The guard `len(set(links)) != len(links)` raises before any metric is computed.

**Why it holds for this fixture.** Two identical links point to the same evidence for the same claim. Counting both would raise the numerator and denominator of precision together and could make an answer look as if it had twice the evidence it does.

**A tempting wrong approach.** Deduplicating quietly inside the metric hides a formatting bug in the system that produced the answer. The bug should be fixed or measured, not absorbed.

**How to verify.** The reference includes the duplicated pair in the invalid list. After removing the duplicate, `citation_metrics(["c"], [("c", "d")], {("c", "d"): True})` returns 1.0 for both fields.

**Expected observation:** The helper rejects it.

## 5. Use a newer document

A later correction cannot be treated as information the original system had at decision time.

**Approach.** Call `eligible_evidence({"id": "d1-v2", "published": 12}, 10, {"d1-v2"})`. The function requires both an allowed ID and `published <= cutoff`.

**Why it holds for this fixture.** The answer was produced at day 10, and document version d1-v2 appeared at day 12. The original system could not have cited it, so a historical reconstruction that accepts it rewards evidence from the future, the same leakage as a delayed label in eval-002.

**A tempting wrong approach.** Grading against the latest document version because it is more accurate mixes two questions: whether the system behaved well with the evidence it had, and whether the evidence later changed.

**How to verify.** Worked case B asserts the call returns `False` at cutoff 10 and `True` at cutoff 12. An ID not in the allowed set, such as `"restricted"`, is ineligible at any cutoff.

**Expected observation:** That version is ineligible for the historical reconstruction.

## 6. Disentangle truth and support

Citation evaluation measures a relation to supplied evidence. It does not establish that all evidence is correct or current.

**Approach.** Write a claim that quotes a source word for word, where the source itself states a wrong value. Judge support (does the cited passage say this?) and truth (is it correct?) separately.

**Why it holds for this fixture.** Support is `True` because the claim matches the passage. Truth is `False` because the passage is wrong. Worked case B encodes exactly this pair: `support = True`, `truth = False`.

**A tempting wrong approach.** Treating supported claims as verified facts is the mistake. Citation metrics measure faithfulness to supplied evidence; they cannot detect errors in that evidence, so a corpus with stale or wrong documents yields faithful but false answers.

**How to verify.** Worked case B asserts `support and not truth`. In a report, label the support metric explicitly as a relation to the corpus snapshot and track truth through a separate assessment.

**Expected observation:** Support can be true while truth is false.
