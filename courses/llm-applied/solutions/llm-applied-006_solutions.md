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
