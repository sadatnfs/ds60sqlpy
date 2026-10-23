# nlp-022: Explanatory solutions

The executable reference checks the declared fixtures. It is separate from the learner scaffold and does not certify general task quality.

## Exercise 1: Construct postings

The repeated router token changes its term frequency but not the number of documents containing it. Conflating those quantities corrupts IDF. Retain document IDs and the tokenization policy so the index can be reproduced.

**Expected:** router postings{d0,d1}; term frequency and document frequency remain distinct.

## Exercise 2: Reproduce BM25 by hand

The short document gets a favorable length normalization, while repetition in d1 saturates. The exact formula check identifies errors in scaling or denominator terms before relying on a plausible ranking.

**Expected:** Implementation matches the explicit formula; \(d_{0}>d_{1}>d_{2}=0\).

## Exercise 3: Handle unsupported queries

A dictionary of zero scores is a valid computational output but not a useful answer. The next layer needs an explicit no-evidence policy. A dense retriever might find a semantic match, but that would be a separately measured component.

**Expected:** All numerical scores zero; the application should report no lexical evidence rather than a meaningful top result.

## Exercise 4: Implement reciprocal-rank fusion

Rank fusion avoids assuming that lexical and dense raw scores share a scale. It still has a hyperparameter and can lose score-magnitude information. Evaluate its utility and cost against the components rather than assuming a fused result is always better.

**Expected:** b first with score1/62+1/61; duplicate IDs in one ranking rejected.

## Exercise 5: Compute nDCG and MRR

The first irrelevant result delays the first useful hit and discounts the highest relevance item. Different gain conventions produce different numbers, so the configuration belongs with the result. Required-evidence recall may still be needed for multi-source questions.

**Expected:** MRR.5 and nDCG=(7/log2(3)+3/2)/(7+3/log2(3)).

## Exercise 6: Enforce the permitted corpus

The boundary controls which text is eligible for retrieval, not just which text is displayed afterward. A production implementation needs authorization metadata and audit evidence; relevance scoring cannot replace those checks. A permitted high-scoring passage still needs a separate claim-support review.

**Expected:** Only d0 appears in results; a written handoff records source version and support limits.

## Transfer and limits

Retrieval finds candidate evidence from a corpus, and ranking orders those candidates for a query. A reliable pipeline preserves the distinction between locating related text and proving that it answers a question. The index must also respect which documents are current and permitted before passages reach a model or user.

This lesson implements an inverted index, a specified BM25 formula, reciprocal-rank fusion and exact ranking metrics over three authored documents. It is a real lexical retrieval calculation, with a separate demonstration of combining two supplied rankings. The second ranking is not falsely described as output from a trained dense model. You will see how to compare candidates, fuse ranks and interpret task-level evidence.

Candidate generation places a ceiling on the final system. If a required document never enters the candidate set, a reranker cannot recover it. If a document is retrieved but contradicts or fails to support the question, a high score does not turn it into a valid answer. Evaluate candidate coverage, order and final evidence use separately.

## Mechanism review and counterexample

Filter documents according to authorized scope before generating a context packet for a model. Retrieving private text and hoping the final answer omits it is not the same boundary. The fixture restricts the searchable dictionary to d0 and verifies that only d0 can appear in its score results.

A production system also needs version-aware indexing, tombstones for removed documents, freshness policy and a record of which source chunks entered an answer. A search score is not an authorization decision. Keep access logic deterministic and independently tested, then evaluate relevance inside the permitted corpus.
