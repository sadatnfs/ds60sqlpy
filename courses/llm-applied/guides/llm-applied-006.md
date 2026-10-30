# llm-applied-006: Lexical retrieval and BM25 from first principles

## Level and prerequisites

Beginner; approximately 180 minutes. Direct prerequisites: `llm-applied-005`. The prerequisite sequence introduces the notation used here; revisit its worked examples if an axis, probability or gradient is unfamiliar.

## Learning objectives

Lexical retrieval provides a transparent first ranking of the corpus. This chapter explains how term evidence becomes a score, why an inverted index is useful, and how exact terminology, tokenization and negation affect a data-science assistant's retrieval decisions.

## Purpose and mental model

Lexical retrieval ranks documents using observed terms. A simple overlap score treats every matching word equally, while BM25 combines inverse document frequency, term-frequency saturation and document-length normalization. A term present in many documents is less discriminating than a rare term. Repeating a query term several times in one document can help, but BM25 saturates that gain rather than increasing it without bound. Length normalization reduces the advantage of long documents that contain many words simply because they are long.

This implementation uses lowercase ASCII word tokens and a fixed local corpus. It is a real lexical retrieval calculation, not an embedding model or a language generator. Its limits are visible: synonyms that share no tokens are missed, tokenization policy can change matches, and a high score does not establish that the document answers the question. Stable document-ID tie-breaking makes results reproducible. Access filtering must happen before scoring in a later lesson, because ranking unauthorized documents and removing them afterward can leak metadata and distort result counts.

## Start with the words an analyst can name

An analyst asks the Methods Desk where the handbook discusses account randomization. The phrase contains an unusually useful term: randomization is more specific than account in this small corpus. A lexical retriever can use that distinction without training a language model. It looks for observed terms and ranks documents according to a declared weighting rule.

This transparency makes lexical retrieval a valuable baseline for technical domains. Analysts often know a metric name, an experiment identifier, a column name or an error message. Those strings can be more diagnostic than a broad semantic similarity. A learned retriever may add value for paraphrases, but it should be compared against the exact-match behavior that the task already supports.

The first step is tokenization. The fixture lowercases text and extracts ASCII letter/digit runs. That policy makes “Account” and “account” match, but it does not equate randomization with randomized or purchase with buy. It also chooses how punctuation-separated identifiers are split. A retrieval miss caused by that transformation should be diagnosed before changing the ranking formula.

## From documents to an inverted index

The reference implementation scans small dictionaries so the arithmetic remains visible. A larger lexical index commonly organizes postings by term: each term points to the documents containing it, together with information such as frequency. Document lengths and corpus-level counts provide the remaining statistics. A query then looks up its terms instead of rereading every source string from scratch.

This organization separates two jobs. Index construction records what terms occur under a particular tokenizer and source snapshot. Query scoring uses those recorded facts to rank candidates. If the source changes but the index does not, the scorer can be perfectly implemented and still rank stale content. If the tokenizer changes, the postings and their statistics must be rebuilt consistently.

Term frequency tells how often a term appears within a document. Document frequency tells in how many indexed documents it appears. The first can distinguish a passing mention from a repeated topic; the second estimates how discriminating the term is in the corpus. Counting occurrences when document presence was intended confuses these roles. Repeated text in one source is not equivalent to the term appearing across many sources.

BM25 combines rarity with diminishing returns from repetition and a document-length adjustment. The detailed calculation below derives each factor on the literal corpus. The important modeling idea is that a long document should not win merely because it has more opportunities to contain a term, and a document should not obtain unlimited advantage by repeating that term. The chosen parameters control those tradeoffs; they do not turn the score into a calibrated probability of correctness.

## A high lexical score can preserve an unresolved contradiction

Consider three equal-length documents: “exclude test accounts,” “include test accounts,” and “record eligible visits.” For the query “test accounts,” the first two have the same matching term frequencies and the same lengths. Each query term appears in two of three documents, so each contributes \(\log(1.6)\) under the fixture's IDF convention. Both documents score \(2\cdot \log(1.6)\), about 0.940007.

The tie is correct for the stated lexical evidence. The two documents make opposite claims, but the query terms alone do not distinguish their policy meaning. A deterministic ID tie-break makes the output reproducible; it does not resolve which source is applicable. Version, authority and scope must be considered before an answer adopts either statement.

Adding more query words can help without solving entailment generally. A passage saying “Do not exclude test accounts” still contains exclude,test and accounts. A bag of terms does not represent the full effect of negation or the scope of an exception. Lexical retrieval is choosing candidates for inspection, not proving that their propositions answer the question correctly.

Technical quantities create another mismatch. “100 milliseconds” and “0.1 seconds” may describe the same duration while sharing little lexical form. A domain-aware normalization step could make the equivalence available, but it must preserve units and context. Blind text substitution can create false matches. The same caution applies to abbreviations, SQL identifiers and method names whose common-language meanings differ from their technical use.

## Diagnose the baseline before adding a learned model

For each missed question, inspect the emitted query tokens, the relevant source tokens and the scoring statistics. A zero score can mean no shared vocabulary, a tokenizer mismatch or evidence that is genuinely absent. Returning the first zero-score document by ID does not make the question answerable. A low score can also reflect a long chunk whose relevant sentence was diluted by unrelated material.

For a false positive, inspect why its terms matched. Was the query broad? Did a repeated header inflate document frequency? Did the source discuss a rejected method rather than recommend it? Did an old policy contain the same terminology as the current rule? These explanations point toward different changes: query formulation, chunking, metadata filtering or a richer relevance model.

Corpus changes affect the score distribution. Rechunking one long handbook into many passages changes document count, average length and term frequencies across indexed units. A threshold chosen before that change may not retain its earlier meaning. The score belongs to a particular corpus and analysis policy, so the evaluation trace should identify both.

A learned embedding branch is justified when failures show useful semantic relationships that lexical terms miss. A reranker is justified when candidates contain the needed evidence but ordering remains poor. The baseline is not a disposable stepping stone. It remains a comparison tool and can continue to supply strong candidates for exact identifiers and rare terminology in a hybrid system.

## Design decisions and when to use this method

BM25 is a strong baseline when exact terminology, identifiers, code symbols or rare domain phrases matter. It requires no embedding service, can be rebuilt from local text and makes many ranking effects explainable. Domain tokenization is still an engineering choice: splitting SQL identifiers, preserving units or handling accented text can materially change retrieval.

Do not assume a more complex model automatically outperforms lexical retrieval. Compare both on the same relevance-labelled questions, including exact identifiers and synonym cases. Inspect failures before adding query expansion or a reranker. A score threshold calibrated on one corpus may not transfer to a new corpus because document frequencies and lengths change. Keep corpus version, tokenizer policy and ranking parameters in the evaluation trace.

Use the literal BM25 implementation as an auditable ranking baseline. Before comparing a dense retriever, inspect exact terminology, rare identifiers, tokenization and zero-score questions. These often reveal whether a failure is missing vocabulary or missing evidence rather than insufficient model capacity.

The helper exercises the declared defaults and a small positive-k1 example. It does not validate arbitrary caller-supplied k1 or b values. A configurable service should validate its parameter domain separately; the lesson does not claim that every possible input combination is admitted safely.

## Vocabulary and concepts

**Term frequency:** Number of occurrences of a term in one document.

**Document frequency:** Number of documents containing a term.

**IDF:** Inverse document frequency, weighting rarer terms more strongly.

**BM25:** A lexical ranking formula combining rarity, saturation and length normalization.

## How to run this lesson

Use a prepared `python-core` environment. NumPy is a declared package. TensorFlow and PyTorch require their own prepared CPU profiles; a successful syntax check does not establish their runtime readiness. No package installation, dataset download, pretrained model or network service belongs in this lesson. Copy the learner source into ignored `.learning/expansion/llm-applied-006/` before editing, or use the application's saved pad. The examples use literal local data and a bounded number of operations. Use the Docker classroom as the default route and select the declared `python-core` profile. For a separately prepared native environment, invoke its explicitly selected interpreter on `courses/llm-applied/lessons/llm-applied-006.py` from the repository root. The general repository `.venv` is not assumed to include the heavy model dependencies.

Run the three worked blocks in order in one scratch file; later blocks reuse the earlier helper and fixture state. To reproduce a later block in a fresh process, include its preceding blocks. Start by reading Example A without running it. Write the intermediate quantities and their units on paper. Run the entire example in a fresh process, not only the final line in a notebook with hidden variables. Examples B and C change assumptions that matter to this mechanism. Distinguish a retrieval or extraction baseline from an actual trained language model; each example names what it implements. Compare both observations before starting independent work. An assertion failure is a request to inspect an assumption, not a reason to widen every tolerance. Use the tolerance stated in each assertion. Many analytic float64 fixtures use 1e-12 and float32 fixtures use 1e-6, but dtype alone does not determine a universal error bound. Integer counts, identities and boolean decisions should be exact.

## Syntax anatomy and reasoning sequence

For query term q, BM25 uses \(\mathrm{idf}=\log(1+\frac{N-\partial f+0.5}{\partial f+0.5})\). Each document contribution multiplies idf by \(\frac{\mathrm{tf}\cdot (k_{1}+1)}{\mathrm{tf}+k_{1}\cdot (1-b+\frac{b\cdot \mathrm{length}}{\mathrm{avg}_{\mathrm{length}}})}\). The defaults here are \(k_{1}=1.2\), \(b=0.75\), declared as fixture choices. Count query terms once to avoid an accidental repeated-query weighting policy. Empty corpora and empty documents need explicit handling so average length never becomes an unexplained zero denominator.

## Calculate the score and isolate each modeling choice

The three documents each have two tokens, so average document length is two. The query randomization appears once in document a and nowhere else. With \(N=3\), \(\partial f=1\), the implemented IDF is \(\log(1+\frac{2.5}{1.5})=\log(\frac{8}{3})\), about 0.980829. The matching document's normalized length ratio is one. With \(\mathrm{tf}=1\) and \(k_{1}=1.2\), its frequency factor is \(\frac{2.2}{1+1.2}=1\), so the final score is exactly that IDF. The other documents receive zero because the query term is absent.

For account, \(\partial f=2\) and IDF is \(\log(1+\frac{1.5}{2.5})=\log(1.6)\), about 0.470004. The rarer query term therefore receives more weight in this fixed corpus. Document frequency counts presence per document: repeating account ten times inside one document still contributes one to df. Token frequency and document frequency are different denominators.

Write \(K=k_1\left(1-b+b\frac{L}{\overline L}\right)\). The frequency factor is \(f(\mathrm{tf})=\frac{(k_1+1)\mathrm{tf}}{\mathrm{tf}+K}\). Holding document length and corpus statistics fixed, its derivative for positive K is \(\frac{(k_1+1)K}{(\mathrm{tf}+K)^2}\), positive and decreasing. The second derivative is negative, so additional repetitions have diminishing gain. As tf becomes large under that fixed-length mathematical comparison, the factor approaches k1+1. If actual repetitions also lengthen the document, K changes too; do not silently hold one effect fixed while interpreting a real edit.

With \(b=0\), \(K=k_{1}\). For tf1, 2, 10 at \(k_{1}=1.2\), the factors are 1, 1.375 and about 1.964286. Ten repetitions do not create ten times the score. At \(b=1\), the normalization depends fully on L/avgL; at \(b=0\), document length does not enter K. For the same \(\mathrm{tf}=1\), \(k_{1}=1.2\) and \(b=0.75\), a document twice the average length has \(K=2.1\) and factor \(\frac{2.2}{3.1}\), about 0.709677. One half the average length has \(K=0.75\) and factor 2.2/1.75, about 1.257143.

This positive-IDF convention and the roles of k1 and b are documented in Lucene's versioned BM25 API. The fixture is its own transparent calculation and does not execute Lucene or claim identical index-analysis behavior. [Lucene 10.3.1 BM25Similarity](https://lucene.apache.org/core/10_3_1/core/org/apache/lucene/search/similarities/BM25Similarity.html).

The corpus definition changes the scores. Splitting one source into many chunks changes N, lengths and possibly df. Repeating the same heading in every chunk can make a previously rare term common. A score threshold learned before rechunking therefore may not retain the same meaning afterward. Authorization filtering also defines which corpus is eligible for ranking; the later access chapter makes that boundary explicit.

The local tokenizer lowercases and retains ASCII letter/digit runs. It will split punctuation-delimited identifiers, discard non-ASCII letters under this pattern and treat exact spellings according to that policy. A query token absent from every document gives no positive contribution, while a repeated query term is counted once because the code uses a set. Those are concrete design choices, not intrinsic properties of every BM25 system.

### Interview reasoning with explanatory answers

**Is a BM25 score a relevance probability?** No. It is an ordering score under specified corpus statistics and parameters. A threshold needs task calibration, and changing the corpus can change its interpretation.

**Why can chunking change rankings even when the source text is unchanged?** The retrieval documents and their lengths/frequencies have changed. The scoring unit is the indexed chunk, not automatically the original source family.

**Why does a synonym query miss buy when searching purchase?** The implementation has no learned or curated equivalence between those tokens. Adding expansion or a dense branch is a separate intervention that needs both positive and false-match tests.

## Worked example / walkthrough

### Example A: Rank a discriminating term

Only one document contains the query term. The result is a lexical match, and answer relevance still requires inspecting the actual content.

```python
import math, re
from collections import Counter


def tokens(text):
    return re.findall(r"[a-z0-9]+", text.lower())


def bm25(query, documents, k1=1.2, b=0.75):
    if not documents:
        return []
    bags = {key: Counter(tokens(text)) for key, text in documents.items()}
    lengths = {key: sum(v.values()) for key, v in bags.items()}
    average = sum(lengths.values()) / len(lengths)
    terms = set(tokens(query))
    scored = []
    for key, bag in bags.items():
        score = 0.0
        for term in terms:
            tf = bag[term]
            if not tf:
                continue
            df = sum(term in other for other in bags.values())
            idf = math.log(1 + (len(bags) - df + 0.5) / (df + 0.5))
            score += idf * tf * (k1 + 1) / (tf + k1 * (1 - b + b * lengths[key] / average))
        scored.append((key, score))
    return sorted(scored, key=lambda row: (-row[1], row[0]))


docs = {"a": "account randomization", "b": "visit counts", "c": "account outcomes"}
scores = bm25("randomization", docs)
assert scores[0][0] == "a" and scores[0][1] > 0 and all(score == 0 for _, score in scores[1:])
```

**Expected:** a ranks first with a positive score; the other scores are 0.

### Example B: Inspect term rarity

Document frequency counts documents, not total token occurrences. A term repeated many times in one source still appears in only one document for this calculation.

```python
rare = math.log(1 + (3 - 1 + 0.5) / (1 + 0.5))
common = math.log(1 + (3 - 2 + 0.5) / (2 + 0.5))
assert rare > common > 0
```

**Expected:** the rarer term has larger IDF.

### Example C: Verify saturation

The denominator grows with term frequency, creating diminishing returns. This reduces the effect of repeated terms without treating repetition as irrelevant.

```python
k1 = 1.2
contribution = lambda tf: tf * (k1 + 1) / (tf + k1)
a, b, c = [contribution(n) for n in [1, 2, 10]]
assert a < b < c and c < 10 * a
```

**Expected:** scores increase, but 10 occurrences yield less than 10 times the single-occurrence score.

## Prediction before your attempt

For the supplied fixture, name the input unit, the intermediate state and the final quantity that changes. Predict one normal result and one failure result before touching the code. In particular, explain this lesson's acceptance condition in your own words: a ranks first with a positive score; the other scores are 0. empty result for no documents; finite zero score for an empty document. Preserve the prediction beside your later observations so a correction is visible. A copied expected value is not a derivation.

## Exercises

1. **Rank a discriminating term.** Rank documents a=account randomization, b=visit counts and c=account outcomes for the query randomization.
   **Expected:** a ranks first with a positive score; the other scores are 0.
   **Verify:** Save the assertion results for exercise 1, including a ranks first with a positive score; the other scores are 0.

2. **Inspect term rarity.** Compare IDF for a term present in 1 of 3 documents with a term present in 2 of 3.
   **Expected:** the rarer term has larger IDF.
   **Verify:** Save the assertion results for exercise 2, including the rarer term has larger IDF.

3. **Verify saturation.** Disable length normalization with \(b=0\) and compare term frequencies 1, 2, 10 under the same IDF.
   **Expected:** scores increase, but 10 occurrences yield less than 10 times the single-occurrence score.
   **Verify:** Save the assertion results for exercise 3, including scores increase, but 10 occurrences yield less than 10 times the single-occurrence score.

4. **Expose a synonym miss.** Query purchase against a document containing only buy.
   **Expected:** score 0 despite the semantic relationship.
   **Verify:** Save the assertion results for exercise 4, including score 0 despite the semantic relationship.

5. **Make ties deterministic.** Query an absent word with document IDs z, a, b.
   **Expected:** order a, b, z with zero scores.
   **Verify:** Save the assertion results for exercise 5, including order a, b, z with zero scores.

6. **Check corpus edge cases.** Score an empty corpus and a corpus containing one empty document.
   **Expected:** empty result for no documents; finite zero score for an empty document.
   **Verify:** Save the assertion results for exercise 6, including empty result for no documents; finite zero score for an empty document.

## Common pitfalls and diagnosis

If an exact identifier is missed, inspect emitted tokens before changing ranking parameters. If every score is zero, verify whether the query shares any indexed terms and apply an answerability policy instead of treating the first ID tie-break as evidence. If a score changes after a corpus rebuild, compare document counts, chunk lengths, repeated headings and df.

If repetition overwhelms ranking, separate term-frequency saturation from the document-length effect and inspect the actual \(\frac{k_{1}}{b}\) configuration. If a dense retriever appears better, ensure both candidates see the same authorized corpus and context budget. Preserve the literal score calculation as an oracle for ranking arithmetic while evaluating task relevance independently.

## Progressive hints

First draw the state described in the vocabulary section. Next use the smallest fixture that distinguishes the two interpretations in Example B. Finally compare your intermediate values with the exercise's expected count, shape or scalar. Ask for the first incorrect step, not a complete replacement implementation. Keep any counterexample that exposed the error as a regression test for the next lesson.

## Self-check and retrieval

Revisit the worked examples, then close them. Explain Term frequency, Document frequency, IDF using the lesson fixture. Reconstruct one computation from its inputs. Then change one input while retaining the mechanism and predict whether the conclusion survives. Write which part is guaranteed by the code and which part would need new observations. This last distinction prevents a tiny deterministic teaching example from being presented as evidence about an unseen population or a production model.

## Next step

Revisit the direct prerequisite `llm-applied-005` if the calculation cannot be reconstructed without a solution. Otherwise preserve your independent implementation, the six exercise observations and a fresh transfer case, then continue along the course plan. For a capstone, treat a failed acceptance condition as a valid no-go decision and explain what evidence would be needed to revisit it.

## Sources and verification status

API and mechanism reference: [BM25 and probabilistic relevance](https://www.staff.city.ac.uk/~sbrp622/papers/foundations_bm25_review.pdf), reviewed 2026-10-22. The fixture, examples, counterexamples and exercise design are original course material. See [validation](../../../docs/validation.md) for execution gates. Check CI artifacts for the exact revision and platform to determine which runtime checks actually ran; authored content alone does not establish runtime execution.



## Ask an AI tutor about this lesson

```text
Use the checked-in $guide-ds60sqlpy-learning skill for llm-applied-006, Lexical retrieval and BM25 from first principles.
Read courses/llm-applied/guides/llm-applied-006.md and courses/llm-applied/lessons/llm-applied-006.py. Direct prerequisites: `llm-applied-005`.
Explain the mental model, ask me to predict the worked example, review my attempt,
give one hint, request output evidence, and ask a fresh retrieval question.
Keep courses/llm-applied/solutions/ closed until I request comparison or show an attempt.
Use only the declared local fixtures. Distinguish arithmetic checks, code execution,
and evidence about generalization. Done when I can derive the worked values, pass all six exercise checks, explain a failed counterexample, and solve one fresh transfer case without solutions.
```
