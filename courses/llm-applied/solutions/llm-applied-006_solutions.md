# llm-applied-006: explanatory solutions

Compare these answers only after an attempt or an explicit solution reveal. They use the same literal inputs as the guide, so a discrepancy can be localized to a specific step. The executable companion runs the assertions; the explanation states why those assertions test the subject. Passing a reference function is rehearsal, and should be followed by a new input chosen without looking at the answer.

## Mechanism review

Lexical retrieval ranks documents using observed terms. A simple overlap score treats every matching word equally, while BM25 combines inverse document frequency, term-frequency saturation and document-length normalization. A term present in many documents is less discriminating than a rare term. Repeating a query term several times in one document can help, but BM25 saturates that gain rather than increasing it without bound. Length normalization reduces the advantage of long documents that contain many words simply because they are long.

This implementation uses lowercase ASCII word tokens and a fixed local corpus. It is a real lexical retrieval calculation, not an embedding model or a language generator. Its limits are visible: synonyms that share no tokens are missed, tokenization policy can change matches, and a high score does not establish that the document answers the question. Stable document-ID tie-breaking makes results reproducible. Access filtering must happen before scoring in a later lesson, because ranking unauthorized documents and removing them afterward can leak metadata and distort result counts.

**Term frequency:** Number of occurrences of a term in one document.

**Document frequency:** Number of documents containing a term.

**IDF:** Inverse document frequency, weighting rarer terms more strongly.

**BM25:** A lexical ranking formula combining rarity, saturation and length normalization.

## Reading the implementation

For querytermq, BM25 usesidf=log(1+(N-df+.5)/(df+.5)). Each document contribution multipliesidf bytf*(k1+1)/(tf+k1*(1-b+b*length/avg_length)). The defaults here arek1=1.2, b=.75, declared as fixture choices. Count query terms once to avoid an accidental repeated-query weighting policy. Empty corpora and empty documents need explicit handling so average length never becomes an unexplained zero denominator.

## Calculate the score and isolate each modeling choice

The three documents each have two tokens, so average document length is two. The query randomization appears once in document a and nowhere else. With N=3, df=1, the implemented IDF is log(1+2.5/1.5)=log(8/3), about0.980829. The matching document's normalized length ratio is one. With tf=1 and k1=1.2, its frequency factor is2.2/(1+1.2)=1, so the final score is exactly that IDF. The other documents receive zero because the query term is absent.

For account, df=2 and IDF is log(1+1.5/2.5)=log(1.6), about0.470004. The rarer query term therefore receives more weight in this fixed corpus. Document frequency counts presence per document: repeating account ten times inside one document still contributes one to df. Token frequency and document frequency are different denominators.

Write K=k1*(1-b+b*L/avgL). The frequency factor is f(tf)=(k1+1)*tf/(tf+K). Holding document length and corpus statistics fixed, its derivative for positive K is(k1+1)*K/(tf+K)^2, positive and decreasing. The second derivative is negative, so additional repetitions have diminishing gain. As tf becomes large under that fixed-length mathematical comparison, the factor approaches k1+1. If actual repetitions also lengthen the document, K changes too; do not silently hold one effect fixed while interpreting a real edit.

With b=0, K=k1. For tf1, 2, 10 at k1=1.2, the factors are1, 1.375 and about1.964286. Ten repetitions do not create ten times the score. At b=1, the normalization depends fully on L/avgL; at b=0, document length does not enter K. For the same tf=1, k1=1.2 and b=0.75, a document twice the average length has K=2.1 and factor2.2/3.1, about0.709677. One half the average length has K=0.75 and factor2.2/1.75, about1.257143.

This positive-IDF convention and the roles of k1 and b are documented in Lucene's versioned BM25 API. The fixture is its own transparent calculation and does not execute Lucene or claim identical index-analysis behavior. [Lucene10.3.1 BM25Similarity](https://lucene.apache.org/core/10_3_1/core/org/apache/lucene/search/similarities/BM25Similarity.html).

The corpus definition changes the scores. Splitting one source into many chunks changes N, lengths and possibly df. Repeating the same heading in every chunk can make a previously rare term common. A score threshold learned before rechunking therefore may not retain the same meaning afterward. Authorization filtering also defines which corpus is eligible for ranking; the later access chapter makes that boundary explicit.

The local tokenizer lowercases and retains ASCII letter/digit runs. It will split punctuation-delimited identifiers, discard non-ASCII letters under this pattern and treat exact spellings according to that policy. A query token absent from every document gives no positive contribution, while a repeated query term is counted once because the code uses a set. Those are concrete design choices, not intrinsic properties of every BM25 system.

### Interview reasoning with explanatory answers

**Is a BM25 score a relevance probability?** No. It is an ordering score under specified corpus statistics and parameters. A threshold needs task calibration, and changing the corpus can change its interpretation.

**Why can chunking change rankings even when the source text is unchanged?** The retrieval documents and their lengths/frequencies have changed. The scoring unit is the indexed chunk, not automatically the original source family.

**Why does a synonym query miss buy when searching purchase?** The implementation has no learned or curated equivalence between those tokens. Adding expansion or a dense branch is a separate intervention that needs both positive and false-match tests.

## Exercise 1: Rank a discriminating term

The question is: Rank documents a=account randomization, b=visit counts and c=account outcomes for the query randomization.

Only one document contains the query term. The result is a lexical match, and answer relevance still requires inspecting the actual content.

```python
docs={'a':'account randomization','b':'visit counts','c':'account outcomes'}; scores=bm25('randomization',docs)
assert scores[0][0]=='a' and scores[0][1]>0 and all(score==0 for _,score in scores[1:])
```

**Expected:** a ranks first with a positive score; the other scores are0.

**Verify:** Compare the computed values or written argument with a ranks first with a positive score; the other scores are0.

## Exercise 2: Inspect term rarity

The question is: Compare IDF for a term present in1 of 3 documents with a term present in2 of 3.

Document frequency counts documents, not total token occurrences. A term repeated many times in one source still appears in only one document for this calculation.

```python
rare=math.log(1+(3-1+.5)/(1+.5)); common=math.log(1+(3-2+.5)/(2+.5))
assert rare>common>0
```

**Expected:** the rarer term has larger IDF.

**Verify:** Compare the computed values or written argument with the rarer term has larger IDF.

## Exercise 3: Verify saturation

The question is: Disable length normalization with b=0 and compare term frequencies1, 2, 10 under the same IDF.

The denominator grows with term frequency, creating diminishing returns. This reduces the effect of repeated terms without treating repetition as irrelevant.

```python
k1=1.2; contribution=lambda tf:tf*(k1+1)/(tf+k1)
a,b,c=[contribution(n) for n in [1,2,10]]
assert a<b<c and c<10*a
```

**Expected:** scores increase, but10 occurrences yield less than10 times the single-occurrence score.

**Verify:** Compare the computed values or written argument with scores increase, but10 occurrences yield less than10 times the single-occurrence score.

## Exercise 4: Expose a synonym miss

The question is: Query purchase against a document containing only buy.

Lexical ranking cannot infer a synonym absent from its token policy. Embeddings or curated query expansion can help, but need their own evaluation and may introduce false matches.

```python
assert bm25('purchase',{'d':'buy'})==[('d',0.0)]
```

**Expected:** score0 despite the semantic relationship.

**Verify:** Compare the computed values or written argument with score0 despite the semantic relationship.

## Exercise 5: Make ties deterministic

The question is: Query an absent word with document IDs z, a, b.

Deterministic ties are useful for tests and reproducibility. Zero-score results still need an answerability policy instead of being automatically treated as evidence.

```python
assert [key for key,score in bm25('missing',{'z':'x','a':'y','b':'z'})]==['a','b','z']
```

**Expected:** order a, b, z with zero scores.

**Verify:** Compare the computed values or written argument with order a, b, z with zero scores.

## Exercise 6: Check corpus edge cases

The question is: Score an empty corpus and a corpus containing one empty document.

The implementation handles no lexical evidence explicitly. It does not fabricate a relevant document or divide by an undefined average length.

```python
assert bm25('x',{})==[]
assert bm25('x',{'empty':''})==[('empty',0.0)]
```

**Expected:** empty result for no documents; finite zero score for an empty document.

**Verify:** Compare the computed values or written argument with empty result for no documents; finite zero score for an empty document.

## Review after comparison

Repeat one case with a changed fixture and explain the difference before running it. Keep the original failure case as well as the repaired result. Record a missing framework separately from a failing assertion. No solution downloads data, calls an online model, deploys a service or changes a database.
