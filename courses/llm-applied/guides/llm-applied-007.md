# llm-applied-007: Embedding retrieval, similarity and representation limits

## Level and prerequisites

Intermediate; approximately 180 minutes. Direct prerequisites: `llm-applied-006`. The prerequisite sequence introduces the notation used here; revisit its worked examples if an axis, probability or gradient is unfamiliar.

## Learning objectives

Embedding retrieval replaces exact vocabulary overlap with learned or authored geometry. This chapter explains how that geometry is produced and used, how to separate representation errors from search errors, and why a nearby passage is still only a candidate for a supported answer.

## Purpose and mental model

Embedding retrieval maps queries and documents to vectors and compares their geometry. A learned embedding model can place related wording near each other, but that behavior depends on its training objective and domain coverage. A vector is not an explanation or a probability that a document answers a question. Cosine similarity compares direction after dividing by vector norms; a dot product also depends on magnitude. The choice affects rankings unless all vectors are normalized consistently.

This lesson uses a literal three-dimensional table whose axes are explicitly described as topic features. It demonstrates retrieval arithmetic and its limits without pretending that the fixed table is a pretrained semantic model. The synonym relation between purchase and buy is encoded by hand so you can see exactly where that knowledge enters. A real embedding system needs a pinned model revision, a consistent query/document encoding policy, domain relevance labels and evaluation against lexical retrieval. Zero vectors and incompatible dimensions should fail clearly rather than silently produce NaNs.

## A synonym miss suggests a new representation

The Methods Desk lexical baseline misses a purchase question when the relevant passage uses buy. One possible intervention is a curated synonym rule. Another is an encoder trained to place useful paraphrases near each other. The second approach can handle relationships beyond a small dictionary, but it introduces a learned representation whose successes and failures must be measured.

An embedding is a vector produced by a specified mapping. For text, the mapping may tokenize the input, compute contextual hidden states and pool them into a fixed-width representation. Those transformations can retain useful task information while discarding other details. The vector's coordinates are not generally named concepts such as purchases or geometry. The literal table below gives its axes explicit meanings only so the arithmetic can be inspected.

A learned encoder's training objective influences what similarity means. A model trained on paraphrase pairs may behave differently from one trained to match questions with answer passages. A sentence that restates a question can be semantically similar without containing its answer. A long policy page can be relevant to the topic while failing to establish the requested exception. Retrieval evaluation must therefore use the intended query-to-evidence relationship, not a vague notion that the texts sound related.

## Queries and documents can have different roles

A query is often short and underspecified; a document passage can contain the explanation needed to answer it. A dual-encoder system can use a query encoder and a document encoder trained as a compatible pair. They need not have identical parameters or identical input formatting. What matters is that the resulting vectors are intended to be compared under the declared scoring function. Dense Passage Retrieval is one example of learning such query-passage representations. [Dense Passage Retrieval](https://arxiv.org/abs/2004.04906).

This refines the metadata lesson. Requiring a compatible encoder pair is stronger and more accurate than blindly requiring the same model-name string on both sides. An intentionally asymmetric pair can be valid; an unrelated query encoder and document encoder of the same width can be invalid. An index record should identify the document encoder and its compatible query-side configuration, including preprocessing, pooling and normalization policies.

Once document vectors are computed, they can be reused for many queries. A new question needs its own encoding and a search over those stored vectors. This is the efficiency advantage of separate encoding. It also creates a consistency obligation: changing the document encoder without rebuilding its vectors, or changing the query encoder outside the declared pair, can silently invalidate comparisons that remain dimensionally legal.

## Similarity is a geometric measurement with a task interpretation

Cosine similarity measures directional agreement after normalization. A dot product also responds to vector magnitude. The worked table calculates both and demonstrates positive-scale invariance for cosine. Neither score becomes a relevance probability merely because it lies in a familiar numeric range.

Consider an ambiguous question: “How should we handle variance?” A nearby passage about feature scaling may share vocabulary and topic associations with a passage about sampling uncertainty. Both may be legitimate candidates, but the analyst's intended task is unresolved. A strong similarity score cannot supply the missing context. The assistant may need the surrounding analytical question or an explicit clarification before selecting a method.

Negation, scope and exact quantities can be difficult in a different way. Two passages about including and excluding test accounts may have very similar overall topic representations. A passage with the wrong experiment identifier may also be close to the correct one. These are reasons to retain exact-match tests and claim-level support evaluation, not reasons to assume that all embeddings ignore such distinctions. The relevant question is how the particular encoder performs on those cases.

A threshold should be evaluated on labeled requests under the intended corpus and encoder. A score of 0.85 can have different implications across domains or after adaptation. Even a well-calibrated relevance estimate would not by itself establish source authority, freshness or entitlement to use the document. Those are separate parts of the evidence path.

## Localize the error before changing the encoder

There are at least three places a dense retrieval system can lose the answer. The encoder may assign poor geometry to the relevant passage. An approximate search index may miss a vector that exact search would have found. A later top-k or context-budget stage may discard a good candidate. Inspecting only the final answer hides these distinctions.

For a frozen set of vectors, exact search provides a useful search-mechanics reference. Approximate-index recall can then be measured against that ranking. Semantic relevance recall is a different comparison against authored or reviewed evidence labels. An index can perfectly reproduce an encoder's wrong ranking, while an excellent encoder can be undermined by an overly aggressive search approximation.

The literal implementation below performs exact scoring over a tiny table and rejects obvious shape and norm failures. It does not evaluate a learned text encoder or an approximate index. Its role is to make the geometry and numerical boundary visible before those components are introduced. A real retrieval-model training example later in the route changes a small projection through gradients, while still keeping its literal-feature scope explicit.

## Decide whether adaptation addresses the observed gap

If errors cluster around domain-specific meanings, a governed adaptation dataset may help. It should include positive query-passage pairs and negatives that are truly unsuitable under the task. A passage can be a hard negative because it is topically close, but it may also be another correct answer. Training against a false negative teaches the wrong geometry.

A useful evaluation includes exact identifiers, paraphrases, ambiguity, negation, numerical units and unseen document families. Keep a lexical baseline and measure the effects of any normalization or query-prefix convention. The goal is not to prove that vectors are generally more intelligent than words. It is to find which representation supplies the evidence the analyst needs under a stated cost and quality contract.

The next chapter combines those complementary sources of candidates. Fusion can help when their errors differ, but agreement between two rankers is still evidence about ranking behavior rather than a proof that the selected passage supports the answer.

## Design decisions and when to use this method

Use embedding retrieval when paraphrases and semantic relationships matter, but retain lexical baselines for rare terms, identifiers and exact phrases. Evaluate query and document encoding conventions separately: some models require different prefixes or instructions for each role. Normalize only when the model documentation and chosen similarity metric call for it. Store encoder revision, tokenizer revision, pooling strategy and vector dimension with the index.

Do not interpret a cosine score as calibrated relevance probability. Scores can cluster tightly or shift across domains, and a threshold chosen on one corpus may not transfer. Domain adaptation can improve useful relationships while degrading others, so evaluate held-out query families and exact-identifier cases after fine-tuning. The actual embedding and reranker training lesson later in this track updates a small model and measures its held-out behavior; this chapter establishes the geometry and failure vocabulary first.

Separate representation quality, similarity arithmetic and search approximation. The literal vectors test arithmetic only. A learned encoder needs relevance labels; an approximate index needs comparison with exact search over the same vectors. Improving one layer does not automatically repair another.

Treat model/tokenizer/pooling/normalization identity as part of the vector interface. The metadata exercise detects a mismatch with an assertion, but cosine_rank itself receives only arrays and cannot enforce encoder identity. A real caller must perform that gate before handing vectors to the numerical function.

## Vocabulary and concepts

**Embedding:** A vector representation produced by a specified mapping.

**Cosine similarity:** The dot product of unit-normalized vectors.

**Embedding space:** The coordinate system defined by one model and preprocessing policy.

**Semantic retrieval:** Retrieval intended to match meaning rather than exact shared terms.

## How to run this lesson

Use a prepared `python-core` environment. NumPy is a declared package. TensorFlow and PyTorch require their own prepared CPU profiles; a successful syntax check does not establish their runtime readiness. No package installation, dataset download, pretrained model or network service belongs in this lesson. Copy the learner source into ignored `.learning/expansion/llm-applied-007/` before editing, or use the application's saved pad. The examples use literal local data and a bounded number of operations. Use the Docker classroom as the default route and select the declared `python-core` profile. For a separately prepared native environment, invoke its explicitly selected interpreter on `courses/llm-applied/lessons/llm-applied-007.py` from the repository root. The general repository `.venv` is not assumed to include the heavy model dependencies.

Run the three worked blocks in order in one scratch file; later blocks reuse the earlier helper and fixture state. To reproduce a later block in a fresh process, include its preceding blocks. Start by reading Example A without running it. Write the intermediate quantities and their units on paper. Run the entire example in a fresh process, not only the final line in a notebook with hidden variables. Examples B and C change assumptions that matter to this mechanism. Distinguish a retrieval or extraction baseline from an actual trained language model; each example names what it implements. Compare both observations before starting independent work. An assertion failure is a request to inspect an assumption, not a reason to widen every tolerance. Use the tolerance stated in each assertion. Many analytic float64 fixtures use 1e-12 and float32 fixtures use 1e-6, but dtype alone does not determine a universal error bound. Integer counts, identities and boolean decisions should be exact.

## Syntax anatomy and reasoning sequence

Convert vectors to a float64 matrix with documents on rows and features on columns. Divide each row by its norm, rejecting zero or nonfinite norms. Normalize the query with the same convention, then matrix-multiply document rows by the query. Sort by descending score and stable document ID. Keep model identity and preprocessing policy with the index, because equal vector dimensions do not make two embedding spaces compatible.

## Derive the ranking and distinguish geometry from meaning

For nonzero vectors q and d, cosine is \(\frac{q^{\mathsf T}d}{\lVert q\rVert_2\lVert d\rVert_2}\). The query[1, 0, 0] already has norm one. The purchase vector[1, 0.1, 0] has norm \(\sqrt{1.01}\), so its cosine is \(\frac{1}{\sqrt{1.01}}\), about 0.995037. The mixed vector[0.5, 0.5, 0] has norm \(\sqrt{0.5}\), giving cosine \(\frac{1}{\sqrt{2}}\), about 0.707107. Geometry[0, 1, 0] gives zero. These calculations establish purchase, mixed, geometry as the order under the authored coordinates.

Positive scaling preserves direction: replacing d by 10d multiplies both numerator and norm by ten, leaving cosine unchanged. A raw dot product multiplies by ten. Negative scaling reverses direction and changes the cosine's sign, so the invariance claim is specifically about positive magnitude scaling. A document with a large norm can dominate dot-product search even when its direction is less aligned; whether that norm carries useful information depends on the encoder's training contract.

For unit-normalized vectors, squared Euclidean distance is \(\lVert q-d\rVert_2^2=2-2q^{\mathsf T}d\). Thus sorting by decreasing cosine and increasing squared distance gives the same exact order when both sides are unit vectors. This identity is conditional on normalization; it does not make every distance metric interchangeable on raw embeddings.

An embedding coordinate system has no universal axis meaning. Apply the same orthogonal rotation R to both q and d, and their dot product is unchanged because \({R}^{T}\) R is identity. Rotate only one side, and the cross-space comparison changes. For example, one encoder may represent the relevant concept by[1, 0] while another represents it by[0, 1]. Both vectors have width two and each can work correctly within its own space, but their cross-model dot product is zero. Equal width is therefore a shape check, not a semantic compatibility proof.

The fixture assigns buy and purchase the same literal vector. Their equivalence is authored knowledge, not a measured generalization by a language model. Sentence-BERT is an example of learning sentence representations suitable for efficient similarity comparison; the local table does not reproduce its training or encode arbitrary text. [Sentence-BERT](https://arxiv.org/abs/1908.10084).

A real dual encoder permits document vectors to be computed in advance and query vectors at request time. Exact scoring over M documents of dimension D requires work proportional to \(M\cdot D\) and stored vectors proportional to \(M\cdot D\). Approximate nearest-neighbor methods trade search work against candidate recall. Measure that search recall against the exact vector ranking separately from semantic relevance recall against human-labeled evidence. An approximate index can perfectly imitate a bad semantic ranking, and a good encoder can lose its best document through approximation.

The helper rejects zero vectors, nonfinite coordinates and a norm that is zero or nonfinite after computation. That is a bounded numerical contract, not a promise to normalize every mathematically finite nonzero vector. Extremely large or tiny float64 coordinates can overflow or underflow during a naive norm calculation. A scaled norm can extend the useful range, but changing that implementation would require its own tests. The supplied tiny vectors stay well inside the demonstrated range.

### Interview reasoning with explanatory answers

**Is cosine 0.9 a 90% relevance probability?** No. It describes an angle under a particular representation. Relevance calibration needs labeled examples and can shift with corpus, encoder or task.

**Why keep exact identifiers in evaluation?** A semantic encoder can place a nearby but wrong identifier close to the query. Lexical and semantic mechanisms may make complementary errors, so average paraphrase quality does not settle the choice.

**How do you localize a missing relevant document?** Compare exact vector ranking, approximate-index candidates and relevance labels. That separates encoder geometry from search loss and downstream context truncation.

## Worked example / walkthrough

### Example A: Rank fixed topic vectors

The ranking follows the declared topic geometry. The fixture does not demonstrate that a learned model will assign these vectors to arbitrary language.

```python
import numpy as np
def unit(value):
    value=np.asarray(value,dtype=np.float64)
    if value.ndim!=1 or not len(value) or not np.isfinite(value).all(): raise ValueError('finite vector required')
    norm=np.linalg.norm(value)
    if norm==0 or not np.isfinite(norm): raise ValueError('nonzero finite norm required')
    return value/norm
def cosine_rank(query,documents):
    q=unit(query); scores=[]
    for key,value in documents.items():
        v=unit(value)
        if v.shape!=q.shape: raise ValueError('embedding dimensions differ')
        scores.append((key,float(q@v)))
    return sorted(scores,key=lambda row:(-row[1],row[0]))
table={'purchase':np.array([1.,.1,0.]),'geometry':np.array([0.,1.,0.]),'mixed':np.array([.5,.5,0.])}
ranked=cosine_rank(np.array([1.,0.,0.]),table)
assert [key for key,score in ranked]==['purchase','mixed','geometry']
```

**Expected:** purchase ranks first, mixed second, geometry last.

### Example B: Separate cosine from magnitude

Normalization removes positive magnitude scaling from the score. A model trained for unnormalized dot products may use magnitude meaningfully, so the scoring convention must match the model contract.

```python
query=np.array([1.,0.,0.]); original=table['purchase']; scaled=10*original
np.testing.assert_allclose(unit(original)@unit(query),unit(scaled)@unit(query),atol=1e-12,rtol=0)
assert scaled@query==10*(original@query)
```

**Expected:** cosine unchanged within 1e-12; raw dot product multiplies by 10.

### Example C: Expose hand-authored synonym knowledge

The semantic relation was supplied by the fixture author. A pretrained encoder would need to learn or represent it, and a domain-specific synonym may still be missed.

```python
word_vectors={'buy':np.array([1.,0.,0.]),'purchase':np.array([1.,0.,0.])}
assert set('buy'.split())&set('purchase'.split())==set()
np.testing.assert_array_equal(word_vectors['buy'],word_vectors['purchase'])
```

**Expected:** vector scores match; literal word overlap is empty.

## Prediction before your attempt

For the supplied fixture, name the input unit, the intermediate state and the final quantity that changes. Predict one normal result and one failure result before touching the code. In particular, explain this lesson's acceptance condition in your own words: purchase ranks first, mixed second, geometry last. top-ranked IDwrong is outside the authored relevant set. Preserve the prediction beside your later observations so a correction is visible. A copied expected value is not a derivation.

## Exercises

1. **Rank fixed topic vectors.** Use query[1, 0, 0] and documents purchase[1, .1, 0], geometry[0, 1, 0], mixed[.5, .5, 0].
   **Expected:** purchase ranks first, mixed second, geometry last.
   **Verify:** Save the assertion results for exercise 1, including purchase ranks first, mixed second, geometry last.

2. **Separate cosine from magnitude.** Scale the purchase vector by 10 and compare its cosine score with the original.
   **Expected:** cosine unchanged within 1e-12; raw dot product multiplies by 10.
   **Verify:** Save the assertion results for exercise 2, including cosine unchanged within 1e-12; raw dot product multiplies by 10.

3. **Expose hand-authored synonym knowledge.** Assign buy the same literal vector as purchase and compare retrieval with an exact-token overlap baseline.
   **Expected:** vector scores match; literal word overlap is empty.
   **Verify:** Save the assertion results for exercise 3, including vector scores match; literal word overlap is empty.

4. **Reject zero and nonfinite vectors.** Normalize[0, 0] and[1, NaN] through the checked helper.
   **Expected:** both raise ValueError.
   **Verify:** Save the assertion results for exercise 4, including both raise ValueError.

5. **Reject incompatible spaces.** Compare query metadata modelA with an index encoded by modelB, even when both have width 3.
   **Expected:** metadata identity mismatch is detected; the caller must enforce the retrieval gate.
   **Verify:** Save the assertion results for exercise 5, including metadata identity mismatch is detected; the caller must enforce the retrieval gate.

6. **Measure a domain failure.** Give an irrelevant document a high-scoring vector and record that geometric rank does not establish relevance.
   **Expected:** top-ranked IDwrong is outside the authored relevant set.
   **Verify:** Save the assertion results for exercise 6, including top-ranked IDwrong is outside the authored relevant set.

## Common pitfalls and diagnosis

If scores become NaN or zero unexpectedly, inspect input shape, finite values and computed norms before changing a threshold. If shapes pass but ranks are nonsensical, verify encoder and preprocessing identities; the metadata demonstration does not automatically guard the numerical helper.

If exact search succeeds but approximate search misses, inspect index/search parameters under the same vectors. If both searches rank an irrelevant item first, inspect the representation and relevance labels. If a claimed synonym success comes from a hand-assigned table, label it as fixture geometry rather than learned semantic capability.

## Progressive hints

First draw the state described in the vocabulary section. Next use the smallest fixture that distinguishes the two interpretations in Example B. Finally compare your intermediate values with the exercise's expected count, shape or scalar. Ask for the first incorrect step, not a complete replacement implementation. Keep any counterexample that exposed the error as a regression test for the next lesson.

## Self-check and retrieval

Revisit the worked examples, then close them. Explain Embedding, Cosine similarity, Embedding space using the lesson fixture. Reconstruct one computation from its inputs. Then change one input while retaining the mechanism and predict whether the conclusion survives. Write which part is guaranteed by the code and which part would need new observations. This last distinction prevents a tiny deterministic teaching example from being presented as evidence about an unseen population or a production model.

## Next step

Revisit the direct prerequisite `llm-applied-006` if the calculation cannot be reconstructed without a solution. Otherwise preserve your independent implementation, the six exercise observations and a fresh transfer case, then continue along the course plan. For a capstone, treat a failed acceptance condition as a valid no-go decision and explain what evidence would be needed to revisit it.

## Sources and verification status

API and mechanism reference: [Sentence-BERT](https://arxiv.org/abs/1908.10084), reviewed 2026-10-22. The fixture, examples, counterexamples and exercise design are original course material. Current execution receipts are recorded in `docs/implementation/llm-applied-status.md`; authored content does not imply that a heavy runtime was executed.



## Ask Codex about this lesson

```text
Use the checked-in $guide-ds60sqlpy-learning skill for llm-applied-007, Embedding retrieval, similarity and representation limits.
Read courses/llm-applied/guides/llm-applied-007.md and courses/llm-applied/lessons/llm-applied-007.py. Direct prerequisites: `llm-applied-006`.
Explain the mental model, ask me to predict the worked example, review my attempt,
give one hint, request output evidence, and ask a fresh retrieval question.
Keep courses/llm-applied/solutions/ closed until I request comparison or show an attempt.
Use only the declared local fixtures. Distinguish arithmetic checks, code execution,
and evidence about generalization. Done when I can derive the worked values, pass all six exercise checks, explain a failed counterexample, and solve one fresh transfer case without solutions.
```
