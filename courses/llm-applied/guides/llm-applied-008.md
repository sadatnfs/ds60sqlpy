# llm-applied-008: Hybrid retrieval, reciprocal-rank fusion and reranking

## Level and prerequisites

Intermediate; approximately 180 minutes. Direct prerequisites: `llm-applied-007`. The prerequisite sequence introduces the notation used here; revisit its worked examples if an axis, probability or gradient is unfamiliar.

## Learning objectives

Hybrid retrieval and reranking allocate different amounts of computation to different stages. This chapter develops a complete candidate-to-context pipeline, explains when combining rankers helps, and shows how to preserve the evidence needed to diagnose a failure at the correct stage.

## Purpose and mental model

Hybrid retrieval combines complementary candidate generators. Lexical ranking can preserve exact terms, while embedding ranking can recover paraphrases. Their raw scores are usually on different scales, so adding them without calibration can let one dominate for arbitrary numerical reasons. Reciprocal-rank fusion uses rank positions instead: each list contributes 1/(constant+rank) to a candidate. A document appearing near the top of both lists accumulates evidence from both methods. This is a ranking heuristic, not a probability model.

Reranking evaluates a smaller candidate set with a more expensive scoring function, often a cross-encoder that jointly reads query and document. This lesson uses a transparent deterministic relevance feature as a reranker so the candidate-stage limitation is visible. If a relevant document never enters the candidate set, no reranker can recover it. Measure candidate recall before judging reranker quality, and keep the query, candidate IDs, scores and final order in the evaluation trace.

## Two rankers can contribute different useful evidence

The Methods Desk now has a lexical branch that finds exact metric names and a dense branch that can recover paraphrases. Combining them is attractive when one finds a relevant passage the other misses. It adds little when they repeatedly return the same stale or incomplete chunk. Before choosing a fusion rule, inspect the overlap in their useful and harmful results.

For an eligibility question, the lexical branch might rank the metric definition first and an older definition second. The dense branch might rank the same current definition first and the exclusion rule second. Their union contains the two facts required for the answer, but a final context budget of two items can still be wasted on the two definitions. Candidate diversity is useful only if the later selection preserves complementary evidence.

Authorization and applicability should already restrict the candidate universe. Fusion is not the place to let an inaccessible or superseded document earn its way into the answer by receiving a high score. The next chapter examines that admission boundary in detail. Here the ranking methods operate on candidates already eligible for the request.

## Why rank fusion is an attractive baseline

Lexical and dense scores often have different scales. Adding them directly can let one branch dominate because of numerical units rather than useful evidence. Reciprocal-rank fusion replaces raw scores with contributions determined by position. The exact worked example below shows how one document's strong positions across both lists can overcome another's single high position.

The convenience has a cost. Rank fusion discards the magnitude of a lead. A ranker that barely prefers its first document and one that strongly separates it from all others contribute the same top-rank value. The fusion constant also changes how strongly position matters relative to appearing in several lists. Those are design choices that should be evaluated against the task, not hidden behind the claim that rank fusion is scale-free and therefore universally reliable.

Consensus can reinforce a shared error. Two encoders trained on related data, or two retrieval branches built from the same repeated headings, may both prefer the same misleading passage. Their agreement is not independent corroboration of the document's claim. A document also does not become more authoritative because it was returned by two algorithms. Source support and ranking consensus answer different questions.

Duplicate handling must distinguish those levels. Repeated IDs within one result list should not create extra votes. The same source returned by different branches can intentionally accumulate rank contributions, but the answer stage should still recognize that it is one source. Overlapping chunks from that source may need additional deduplication so they do not consume the entire context budget.

## Spend expensive reasoning on a bounded candidate set

A common second stage is a cross-encoder that reads the query and a candidate together. In a transformer implementation, tokens from both sides can interact inside the model, allowing finer comparisons than a single precomputed document vector. That flexibility is often useful for distinctions such as whether a passage answers a question, discusses an exception or merely mentions the same topic.

The extra interaction has a work cost. A standard dense self-attention layer over a combined sequence of length Q+D forms a score matrix proportional to(Q+D)^2. A bi-encoder can compute document representations in advance and encode a new query separately. These operation counts explain a design tradeoff; they are not measured latency or memory claims for every architecture, kernel or batch size.

A reranker is therefore usually applied to a smaller admitted candidate set. Its budget includes candidate count and passage length, not only the number of model calls. Increasing the candidate pool may improve recall while increasing latency and context-processing work. Compare quality at a declared budget, and record whether truncation removed the part of a candidate that made it relevant.

The runnable reranker here sorts authored features. It demonstrates the second-stage boundary without pretending to be a trained cross-encoder. The distinction matters because an observed order from a literal feature table says nothing about how a learned model interprets arbitrary query-passage pairs.

## Read a failure as a pipeline trace

Consider an illustrative evaluation of ten questions. The first-stage candidates contain sufficient evidence for eight. The final context retains sufficient evidence for six of those eight. The answer stage produces a correct supported answer for five of those six. The observed end-to-end success count is five, while the conditional stage rates are 8/10,6/8 and 5/6. Their product is 5/10. This arithmetic is a diagnostic worksheet, not a recorded benchmark.

The two candidate misses and two context-selection losses require different interventions. If the required passage is absent from the candidate set, a better reranking order cannot recover it. If the passage is present but displaced by redundant chunks, the final selector needs attention. If sufficient evidence reaches the model but its answer is wrong, improving candidate recall alone may leave the error unchanged.

A reranker can also optimize the wrong target. Document-level relevance may be too broad when the answer needs a specific source span. A long passage can contain both relevant and contradictory material. A score that places the passage first does not determine which statement the generator will use. Retain claim-level evidence requirements when moving from ranking evaluation to answer evaluation.

## Compare a hybrid with the baseline fairly

Hold the authorized corpus, query families and final context budget fixed. Report the work used by each branch and the reranker. A hybrid supplied 100 candidates should not be compared with a five-candidate baseline and credited entirely for a better model. It may still be the better system, but the reason includes the additional retrieval budget.

Use ablations to identify what each component contributes: lexical only, dense only, their union/fusion and fusion with reranking. Preserve examples where the added component hurts as well as where it helps. This makes the result useful for deciding whether the complexity is justified and gives the analyst a way to diagnose future changes in corpus or query distribution.

## Design decisions and when to use this method

Use fusion when error analysis shows complementary retrieval strengths, and test whether the additional complexity improves held-out evidence coverage. A reranker is useful when the first-stage candidate set has good recall but poor ordering. Its compute cost grows with candidate count and input length, so measure quality against a fixed latency or work budget.

Do not compare a hybrid system with k=100 against a lexical baseline with k=5 and attribute all improvement to the model. Hold candidate and context budgets explicit. Raw-score normalization is another possible design, but it needs calibration evidence. RRF avoids raw-scale assumptions at the cost of discarding score gaps: a narrow first-place lead and an overwhelming lead receive the same rank contribution. Record that tradeoff rather than calling fusion universally optimal.

Measure complementarity before fusing retrieval systems. Two different model names can return nearly identical errors, while a simple lexical branch may recover important IDs missed by a dense branch. Compare union coverage and final context quality at a fixed work budget before assuming a hybrid is useful.

Use a reranker when good evidence is present among candidates but ordered poorly. Keep candidate generation, reranking and final context selection as separate stages, with their own IDs and costs. A reranker that secretly fetches new candidates changes the experiment and needs a separate admission step.

## Vocabulary and concepts

**Hybrid retrieval:** Combining candidate rankings from different retrieval mechanisms.

**RRF:** Reciprocal-rank fusion, combining inverse rank contributions.

**Reranker:** A second-stage scorer applied to a bounded candidate set.

**Candidate recall:** Relevant evidence coverage before reranking.

## How to run this lesson

Use a prepared `python-core` environment. NumPy is a declared package. TensorFlow and PyTorch require their own prepared CPU profiles; a successful syntax check does not establish their runtime readiness. No package installation, dataset download, pretrained model or network service belongs in this lesson. Copy the learner source into ignored `.learning/expansion/llm-applied-008/` before editing, or use the application's saved pad. The examples use literal local data and a bounded number of operations. Use the Docker classroom as the default route and select the declared `python-core` profile. For a separately prepared native environment, invoke its explicitly selected interpreter on `courses/llm-applied/lessons/llm-applied-008.py` from the repository root. The general repository `.venv` is not assumed to include the heavy model dependencies.

Run the three worked blocks in order in one scratch file; later blocks reuse the earlier helper and fixture state. To reproduce a later block in a fresh process, include its preceding blocks. Start by reading Example A without running it. Write the intermediate quantities and their units on paper. Run the entire example in a fresh process, not only the final line in a notebook with hidden variables. Examples B and C change assumptions that matter to this mechanism. Distinguish a retrieval or extraction baseline from an actual trained language model; each example names what it implements. Compare both observations before starting independent work. An assertion failure is a request to inspect an assumption, not a reason to widen every tolerance. Use the tolerance stated in each assertion. Many analytic float64 fixtures use 1e-12 and float32 fixtures use 1e-6, but dtype alone does not determine a universal error bound. Integer counts, identities and boolean decisions should be exact.

## Syntax anatomy and reasoning sequence

Use one-based ranks and a positive fusion constant. Deduplicate each input ranking before assigning contributions so repeated IDs do not gain extra votes. Sum contributions by document ID and sort with an explicit ID tie-breaker. The reranker receives only admitted candidates and returns a new ordering; it must not expand access scope or silently fetch new documents.

## Calculate the fused ordering and its limits

For constant c and one-based rank r, this fixture contributes 1/(c+r) from each list containing the document. Missing documents contribute zero. With lists[a, b, c] and[b, d, a] at constant 60, the scores are:

| Document | Contributions | Fused score |
| --- | --- | --- |
| b | 1/62+1/61 | about 0.032522 |
| a | 1/61+1/63 | about 0.032266 |
| d | 1/62 | about 0.016129 |
| c | 1/63 | about 0.015873 |

The b-minus-a gap is 1/62-1/63=1/3906, about 0.000256. Their common rank-one contribution cancels. This exact difference is useful for detecting an off-by-one or list-order mistake even when both scores round to 0.032 in a display. The reciprocal-rank fusion paper supplies the original method; the table is a calculation from the local fixture. [Reciprocal Rank Fusion](https://cormack.uwaterloo.ca/cormacksigir09-rrf.pdf).

The constant changes how strongly rank gaps matter. With a large constant relative to the list depth, each appearance contributes roughly 1/c, so cross-list occurrence count becomes influential and nearby ranks differ little. With a small positive constant, top ranks have much stronger relative weight. Neither setting is universally optimal. The fixture's60 is a declared choice, not a calibrated relevance probability or a domain-independent threshold.

RRF discards raw score gaps. A system giving its first document a tiny lead and another giving an overwhelming lead produce the same rank contribution. This makes fusion insensitive to raw score units, but it also discards potentially useful confidence information. A calibrated score-combination approach is a different design that needs validation of both scales and their transfer across query families.

Within one ranking, duplicate IDs are removed before ranks are assigned. Thus[a, b, b, c] becomes[a, b, c], preserving c's third position instead of penalizing it for a duplicate emission. Across lists, the same ID deliberately receives another contribution. If two lists are exact copies of the same retrieval run, that extra vote is not independent evidence. The method does not estimate correlation between retrievers; duplication at the system level can overweight one behavior.

Let R be the authored relevant set and C the admitted candidate set. Candidate recall is|R intersect C|/|R| when R is nonempty. Any reranker returning only items from C cannot exceed that evidence coverage, even if its ordering is perfect. A final top-k or token-budget selection can reduce coverage further. For R={a, d} and C={a, b, c}, candidate recall is one-half; no rearrangement can supply d. If both facts are necessary for the answer, the context may still be insufficient despite retrieving one relevant item.

The example reranker sorts authored features 0, 2, 1. It is neither a trained cross-encoder nor a measured inference cost. A learned cross-encoder jointly reads the query and each candidate, usually giving richer interactions at a cost tied to candidate count and length. Comparing it with a baseline supplied fewer candidates would mix model quality with resource allocation.

### Interview reasoning with explanatory answers

**Why not add BM25 and cosine directly?** Their raw scales and variation are not inherently comparable. One can dominate solely because of units. Rank fusion avoids that specific assumption but sacrifices score-gap information.

**Does duplicate removal solve correlated evidence?** It prevents repeated IDs within one list from earning extra ranks. It does not make two similar retrieval systems independent or turn overlapping chunks into independent support.

**What should be measured before tuning a reranker?** Candidate recall, authorization admission, candidate count/length and final context budget. Without sufficient candidates, reranker improvements cannot recover the missing evidence.

## Worked example / walkthrough

### Example A: Fuse two rankings

Documentb receives ranks 2 and 1, whilea receives 1 and 3. The difference comes from rank evidence rather than incompatible raw score scales.

```python
from collections import defaultdict
def rrf(rankings,constant=60):
    if constant<=0: raise ValueError('positive fusion constant required')
    scores=defaultdict(float)
    for ranking in rankings:
        unique=[]; seen=set()
        for key in ranking:
            if not isinstance(key,str): raise TypeError('string document ID required')
            if key not in seen: unique.append(key); seen.add(key)
        for position,key in enumerate(unique,1): scores[key]+=1/(constant+position)
    return sorted(scores.items(),key=lambda row:(-row[1],row[0]))
ranked=rrf([['a','b','c'],['b','d','a']],60)
assert [key for key,score in ranked][:2]==['b','a']
```

**Expected:** b ranks first, a second.

### Example B: Inspect one exact contribution

Writing the formula independently makes off-by-one rank errors visible. Zero-based rank would change every denominator.

```python
scores=dict(ranked)
assert abs(scores['b']-(1/62+1/61))<1e-12
```

**Expected:** computed b score equals that sum within 1e-12.

### Example C: Prevent duplicate votes

One retrieval list should contribute one rank per document. Otherwise a buggy candidate generator can inflate a result by emitting duplicates.

```python
assert rrf([['a','b','b','c']],60)==rrf([['a','b','c']],60)
```

**Expected:** fusion result unchanged.

## Prediction before your attempt

For the supplied fixture, name the input unit, the intermediate state and the final quantity that changes. Predict one normal result and one failure result before touching the code. In particular, explain this lesson's acceptance condition in your own words: b ranks first, a second. ValueError for nonpositive constant; TypeError for non-string ID. Preserve the prediction beside your later observations so a correction is visible. A copied expected value is not a derivation.

## Exercises

1. **Fuse two rankings.** Fuse lexical[a, b, c] and dense[b, d, a] with constant 60.
   **Expected:** b ranks first, a second.
   **Verify:** Save the assertion results for exercise 1, including b ranks first, a second.

2. **Inspect one exact contribution.** Calculate the fused score ofb as 1/62+1/61.
   **Expected:** computed b score equals that sum within 1e-12.
   **Verify:** Save the assertion results for exercise 2, including computed b score equals that sum within 1e-12.

3. **Prevent duplicate votes.** Repeatb inside one ranking and compare with its deduplicated form.
   **Expected:** fusion result unchanged.
   **Verify:** Save the assertion results for exercise 3, including fusion result unchanged.

4. **Rerank a bounded candidate set.** Use candidatesa, b, c with authored relevance features 0, 2, 1 and sort descending feature then ID.
   **Expected:** orderb, c, a.
   **Verify:** Save the assertion results for exercise 4, including orderb, c, a.

5. **Expose a candidate-recall ceiling.** Declare relevant documentd but supply only candidatesa, b, c.
   **Expected:** candidate recall 0 and reranker cannot return d.
   **Verify:** Save the assertion results for exercise 5, including candidate recall 0 and reranker cannot return d.

6. **Reject invalid fusion policy.** Use constant 0 or a repeated non-string identifier and apply the declared validation.
   **Expected:** ValueError for nonpositive constant; TypeError for non-string ID.
   **Verify:** Save the assertion results for exercise 6, including ValueError for nonpositive constant; TypeError for non-string ID.

## Common pitfalls and diagnosis

If a candidate receives an unexpectedly large score, inspect duplicate IDs within lists and duplicated retrieval runs across lists separately. If only the top two positions differ, calculate the exact reciprocal contributions rather than relying on rounded scores.

If the reranker fails a question, first verify that the required evidence was in its input. If it was absent, diagnose candidate generation or admission. If it was present but dropped before answering, inspect final context selection. The helper demonstrates finite positive constants and explicit zero rejection; a broader configurable API should also validate nonfinite values and resource bounds before treating it as production input validation.

## Progressive hints

First draw the state described in the vocabulary section. Next use the smallest fixture that distinguishes the two interpretations in Example B. Finally compare your intermediate values with the exercise's expected count, shape or scalar. Ask for the first incorrect step, not a complete replacement implementation. Keep any counterexample that exposed the error as a regression test for the next lesson.

## Self-check and retrieval

Revisit the worked examples, then close them. Explain Hybrid retrieval, RRF, Reranker using the lesson fixture. Reconstruct one computation from its inputs. Then change one input while retaining the mechanism and predict whether the conclusion survives. Write which part is guaranteed by the code and which part would need new observations. This last distinction prevents a tiny deterministic teaching example from being presented as evidence about an unseen population or a production model.

## Next step

Revisit the direct prerequisite `llm-applied-007` if the calculation cannot be reconstructed without a solution. Otherwise preserve your independent implementation, the six exercise observations and a fresh transfer case, then continue along the course plan. For a capstone, treat a failed acceptance condition as a valid no-go decision and explain what evidence would be needed to revisit it.

## Sources and verification status

API and mechanism reference: [Reciprocal Rank Fusion](https://plg.uwaterloo.ca/~gvcormac/cormacksigir09-rrf.pdf), reviewed 2026-10-22. The fixture, examples, counterexamples and exercise design are original course material. Current execution receipts are recorded in `docs/implementation/llm-applied-status.md`; authored content does not imply that a heavy runtime was executed.



## Ask Codex about this lesson

```text
Use the checked-in $guide-ds60sqlpy-learning skill for llm-applied-008, Hybrid retrieval, reciprocal-rank fusion and reranking.
Read courses/llm-applied/guides/llm-applied-008.md and courses/llm-applied/lessons/llm-applied-008.py. Direct prerequisites: `llm-applied-007`.
Explain the mental model, ask me to predict the worked example, review my attempt,
give one hint, request output evidence, and ask a fresh retrieval question.
Keep courses/llm-applied/solutions/ closed until I request comparison or show an attempt.
Use only the declared local fixtures. Distinguish arithmetic checks, code execution,
and evidence about generalization. Done when I can derive the worked values, pass all six exercise checks, explain a failed counterexample, and solve one fresh transfer case without solutions.
```
