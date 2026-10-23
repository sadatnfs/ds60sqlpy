# llm-applied-006: Lexical retrieval and BM25 from first principles

Status: authored applied LLM content. The manifest inventories complete teaching files; runtime readiness remains a separate, measured property.

## Level and prerequisites

Beginner; approximately 180 minutes. Direct prerequisites: `llm-applied-005`. The prerequisite sequence introduces the notation used here; revisit its worked examples if an axis, probability or gradient is unfamiliar.

## Learning objectives

Lexical retrieval ranks documents using observed terms. The central investigation is concrete: Rank documents a=account randomization, b=visit counts and c=account outcomes for the query randomization. The finish condition is a ranks first with a positive score; the other scores are0. empty result for no documents; finite zero score for an empty document. A useful explanation connects the calculation to the reason it is needed, rather than treating a function name as a definition.

## Purpose and mental model

Lexical retrieval ranks documents using observed terms. A simple overlap score treats every matching word equally, while BM25 combines inverse document frequency, term-frequency saturation and document-length normalization. A term present in many documents is less discriminating than a rare term. Repeating a query term several times in one document can help, but BM25 saturates that gain rather than increasing it without bound. Length normalization reduces the advantage of long documents that contain many words simply because they are long.

This implementation uses lowercase ASCII word tokens and a fixed local corpus. It is a real lexical retrieval calculation, not an embedding model or a language generator. Its limits are visible: synonyms that share no tokens are missed, tokenization policy can change matches, and a high score does not establish that the document answers the question. Stable document-ID tie-breaking makes results reproducible. Access filtering must happen before scoring in a later lesson, because ranking unauthorized documents and removing them afterward can leak metadata and distort result counts.

## Design decisions and when to use this method

BM25 is a strong baseline when exact terminology, identifiers, code symbols or rare domain phrases matter. It requires no embedding service, can be rebuilt from local text and makes many ranking effects explainable. Domain tokenization is still an engineering choice: splitting SQL identifiers, preserving units or handling accented text can materially change retrieval.

Do not assume a more complex model automatically outperforms lexical retrieval. Compare both on the same relevance-labelled questions, including exact identifiers and synonym cases. Inspect failures before adding query expansion or a reranker. A score threshold calibrated on one corpus may not transfer to a new corpus because document frequencies and lengths change. Keep corpus version, tokenizer policy and ranking parameters in the evaluation trace.

## Vocabulary and concepts

**Term frequency:** Number of occurrences of a term in one document.

**Document frequency:** Number of documents containing a term.

**IDF:** Inverse document frequency, weighting rarer terms more strongly.

**BM25:** A lexical ranking formula combining rarity, saturation and length normalization.

## How to run this lesson

Use a prepared `python-core` environment. NumPy is a declared package. TensorFlow and PyTorch require their own prepared CPU profiles; a successful syntax check does not establish their runtime readiness. No package installation, dataset download, pretrained model or network service belongs in this lesson. Copy the learner source into ignored `.learning/expansion/llm-applied-006/` before editing, or use the application's saved pad. The examples use literal local data and a bounded number of operations. For Windows use the interpreter selected by setup: `& $CoursePython courses/llm-applied/lessons/llm-applied-006.py`. For macOS/Linux use `.venv/bin/python courses/llm-applied/lessons/llm-applied-006.py` from the repository root.

Run the three worked blocks in order in one scratch file; later blocks reuse the earlier helper and fixture state. To reproduce a later block in a fresh process, include its preceding blocks. Start by reading Example A without running it. Write the intermediate quantities and their units on paper. Run the entire example in a fresh process, not only the final line in a notebook with hidden variables. Examples B and C change assumptions that matter to this mechanism. Distinguish a retrieval or extraction baseline from an actual trained language model; each example names what it implements. Compare both observations before starting independent work. An assertion failure is a request to inspect an assumption, not a reason to widen every tolerance. For float64 arithmetic use an absolute tolerance of 1e-12 unless an exercise gives another bound. TensorFlow and PyTorch float32 comparisons use 1e-6. Integer counts, identities and boolean decisions should be exact.

## Syntax anatomy and reasoning sequence

For querytermq, BM25 usesidf=log(1+(N-df+.5)/(df+.5)). Each document contribution multipliesidf bytf*(k1+1)/(tf+k1*(1-b+b*length/avg_length)). The defaults here arek1=1.2, b=.75, declared as fixture choices. Count query terms once to avoid an accidental repeated-query weighting policy. Empty corpora and empty documents need explicit handling so average length never becomes an unexplained zero denominator.

## Worked example / walkthrough

### Example A: Rank a discriminating term

Only one document contains the query term. The result is a lexical match, and answer relevance still requires inspecting the actual content.

```python
import math,re
from collections import Counter
def tokens(text): return re.findall(r'[a-z0-9]+',text.lower())
def bm25(query,documents,k1=1.2,b=.75):
    if not documents: return []
    bags={key:Counter(tokens(text)) for key,text in documents.items()}; lengths={key:sum(v.values()) for key,v in bags.items()}
    average=sum(lengths.values())/len(lengths); terms=set(tokens(query)); scored=[]
    for key,bag in bags.items():
        score=0.
        for term in terms:
            tf=bag[term]
            if not tf: continue
            df=sum(term in other for other in bags.values()); idf=math.log(1+(len(bags)-df+.5)/(df+.5))
            score+=idf*tf*(k1+1)/(tf+k1*(1-b+b*lengths[key]/average))
        scored.append((key,score))
    return sorted(scored,key=lambda row:(-row[1],row[0]))
docs={'a':'account randomization','b':'visit counts','c':'account outcomes'}; scores=bm25('randomization',docs)
assert scores[0][0]=='a' and scores[0][1]>0 and all(score==0 for _,score in scores[1:])
```

**Expected:** a ranks first with a positive score; the other scores are0.

### Example B: Inspect term rarity

Document frequency counts documents, not total token occurrences. A term repeated many times in one source still appears in only one document for this calculation.

```python
rare=math.log(1+(3-1+.5)/(1+.5)); common=math.log(1+(3-2+.5)/(2+.5))
assert rare>common>0
```

**Expected:** the rarer term has larger IDF.

### Example C: Verify saturation

The denominator grows with term frequency, creating diminishing returns. This reduces the effect of repeated terms without treating repetition as irrelevant.

```python
k1=1.2; contribution=lambda tf:tf*(k1+1)/(tf+k1)
a,b,c=[contribution(n) for n in [1,2,10]]
assert a<b<c and c<10*a
```

**Expected:** scores increase, but10 occurrences yield less than10 times the single-occurrence score.

## Prediction before your attempt

For the supplied fixture, name the input unit, the intermediate state and the final quantity that changes. Predict one normal result and one failure result before touching the code. In particular, explain this lesson's acceptance condition in your own words: a ranks first with a positive score; the other scores are0. empty result for no documents; finite zero score for an empty document. Preserve the prediction beside your later observations so a correction is visible. A copied expected value is not a derivation.

## Exercises

1. **Rank a discriminating term.** Rank documents a=account randomization, b=visit counts and c=account outcomes for the query randomization.
   **Expected:** a ranks first with a positive score; the other scores are0.
   **Verify:** Save the assertion results for exercise 1, including a ranks first with a positive score; the other scores are0.

2. **Inspect term rarity.** Compare IDF for a term present in1 of 3 documents with a term present in2 of 3.
   **Expected:** the rarer term has larger IDF.
   **Verify:** Save the assertion results for exercise 2, including the rarer term has larger IDF.

3. **Verify saturation.** Disable length normalization with b=0 and compare term frequencies1, 2, 10 under the same IDF.
   **Expected:** scores increase, but10 occurrences yield less than10 times the single-occurrence score.
   **Verify:** Save the assertion results for exercise 3, including scores increase, but10 occurrences yield less than10 times the single-occurrence score.

4. **Expose a synonym miss.** Query purchase against a document containing only buy.
   **Expected:** score0 despite the semantic relationship.
   **Verify:** Save the assertion results for exercise 4, including score0 despite the semantic relationship.

5. **Make ties deterministic.** Query an absent word with document IDs z, a, b.
   **Expected:** order a, b, z with zero scores.
   **Verify:** Save the assertion results for exercise 5, including order a, b, z with zero scores.

6. **Check corpus edge cases.** Score an empty corpus and a corpus containing one empty document.
   **Expected:** empty result for no documents; finite zero score for an empty document.
   **Verify:** Save the assertion results for exercise 6, including empty result for no documents; finite zero score for an empty document.

## Common pitfalls and diagnosis

When a result disagrees, locate the first intermediate value that violates this explanation. Inspect shapes and identities before aggregates, and inspect counts before averages. Preserve the original fixture and introduce only one controlled change at a time. If an arithmetic identity passes but a data-boundary condition fails, the experiment is still invalid. If a runtime is unavailable, record the unexecuted code as unverified rather than replacing its output with the expected text. The separate explanation discusses why the tempting alternative in each case changes the result.

## Progressive hints

First draw the state described in the vocabulary section. Next use the smallest fixture that distinguishes the two interpretations in Example B. Finally compare your intermediate values with the exercise's expected count, shape or scalar. Ask for the first incorrect step, not a complete replacement implementation. Keep any counterexample that exposed the error as a regression test for the next lesson.

## Self-check and retrieval

Close both worked examples. Explain Term frequency, Document frequency, IDF using the lesson fixture. Reconstruct one computation from its inputs. Then change one input while retaining the mechanism and predict whether the conclusion survives. Write which part is guaranteed by the code and which part would need new observations. This last distinction prevents a tiny deterministic teaching example from being presented as evidence about an unseen population or a production model.

## Next step

Revisit the direct prerequisite `llm-applied-005` if the calculation cannot be reconstructed without a solution. Otherwise preserve your independent implementation, the six exercise observations and a fresh transfer case, then continue along the course plan. For a capstone, treat a failed acceptance condition as a valid no-go decision and explain what evidence would be needed to revisit it.

## Sources and verification status

API and mechanism reference: [BM25 and probabilistic relevance](https://www.staff.city.ac.uk/~sbrp622/papers/foundations_bm25_review.pdf), reviewed 2026-10-22. The fixture, examples, counterexamples and exercise design are original course material. Current execution receipts are recorded in `docs/implementation/llm-applied-status.md`; authored content does not imply that a heavy runtime was executed.



## Ask Codex about this lesson

```text
Use the checked-in $guide-ds60sqlpy-learning skill for llm-applied-006, Lexical retrieval and BM25 from first principles.
Read courses/llm-applied/guides/llm-applied-006.md and courses/llm-applied/lessons/llm-applied-006.py. Direct prerequisites: `llm-applied-005`.
Explain the mental model, ask me to predict the worked example, review my attempt,
give one hint, request output evidence, and ask a fresh retrieval question.
Keep courses/llm-applied/solutions/ closed until I request comparison or show an attempt.
Use only the declared local fixtures. Distinguish arithmetic checks, code execution,
and evidence about generalization. Done when I can derive the worked values, pass all six exercise checks, explain a failed counterexample, and solve one fresh transfer case without solutions.
```
