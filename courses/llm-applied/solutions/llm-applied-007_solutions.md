# llm-applied-007: explanatory solutions

Compare these answers only after an attempt or an explicit solution reveal. They use the same literal inputs as the guide, so a discrepancy can be localized to a specific step. The executable companion runs the assertions; the explanation states why those assertions test the subject. Passing a reference function is rehearsal, and should be followed by a new input chosen without looking at the answer.

## Mechanism review

Embedding retrieval maps queries and documents to vectors and compares their geometry. A learned embedding model can place related wording near each other, but that behavior depends on its training objective and domain coverage. A vector is not an explanation or a probability that a document answers a question. Cosine similarity compares direction after dividing by vector norms; a dot product also depends on magnitude. The choice affects rankings unless all vectors are normalized consistently.

This lesson uses a literal three-dimensional table whose axes are explicitly described as topic features. It demonstrates retrieval arithmetic and its limits without pretending that the fixed table is a pretrained semantic model. The synonym relation between purchase and buy is encoded by hand so you can see exactly where that knowledge enters. A real embedding system needs a pinned model revision, a consistent query/document encoding policy, domain relevance labels and evaluation against lexical retrieval. Zero vectors and incompatible dimensions should fail clearly rather than silently produce NaNs.

**Embedding:** A vector representation produced by a specified mapping.

**Cosine similarity:** The dot product of unit-normalized vectors.

**Embedding space:** The coordinate system defined by one model and preprocessing policy.

**Semantic retrieval:** Retrieval intended to match meaning rather than exact shared terms.

## Reading the implementation

Convert vectors to a float64 matrix with documents on rows and features on columns. Divide each row by its norm, rejecting zero or nonfinite norms. Normalize the query with the same convention, then matrix-multiply document rows by the query. Sort by descending score and stable document ID. Keep model identity and preprocessing policy with the index, because equal vector dimensions do not make two embedding spaces compatible.

## Exercise 1: Rank fixed topic vectors

The question is: Use query[1, 0, 0] and documents purchase[1, .1, 0], geometry[0, 1, 0], mixed[.5, .5, 0].

The ranking follows the declared topic geometry. The fixture does not demonstrate that a learned model will assign these vectors to arbitrary language.

```python
table={'purchase':np.array([1.,.1,0.]),'geometry':np.array([0.,1.,0.]),'mixed':np.array([.5,.5,0.])}
ranked=cosine_rank(np.array([1.,0.,0.]),table)
assert [key for key,score in ranked]==['purchase','mixed','geometry']
```

**Expected:** purchase ranks first, mixed second, geometry last.

**Verify:** Compare the computed values or written argument with purchase ranks first, mixed second, geometry last.

## Exercise 2: Separate cosine from magnitude

The question is: Scale the purchase vector by 10 and compare its cosine score with the original.

Normalization removes positive magnitude scaling from the score. A model trained for unnormalized dot products may use magnitude meaningfully, so the scoring convention must match the model contract.

```python
query=np.array([1.,0.,0.]); original=table['purchase']; scaled=10*original
np.testing.assert_allclose(unit(original)@unit(query),unit(scaled)@unit(query),atol=1e-12,rtol=0)
assert scaled@query==10*(original@query)
```

**Expected:** cosine unchanged within1e-12; raw dot product multiplies by 10.

**Verify:** Compare the computed values or written argument with cosine unchanged within1e-12; raw dot product multiplies by 10.

## Exercise 3: Expose hand-authored synonym knowledge

The question is: Assign buy the same literal vector as purchase and compare retrieval with an exact-token overlap baseline.

The semantic relation was supplied by the fixture author. A pretrained encoder would need to learn or represent it, and a domain-specific synonym may still be missed.

```python
word_vectors={'buy':np.array([1.,0.,0.]),'purchase':np.array([1.,0.,0.])}
assert set('buy'.split())&set('purchase'.split())==set()
np.testing.assert_array_equal(word_vectors['buy'],word_vectors['purchase'])
```

**Expected:** vector scores match; literal word overlap is empty.

**Verify:** Compare the computed values or written argument with vector scores match; literal word overlap is empty.

## Exercise 4: Reject zero and nonfinite vectors

The question is: Normalize[0, 0] and[1, NaN] through the checked helper.

A zero vector has no direction and NaN is not a valid coordinate. Returning a plausible similarity would hide an encoding or data-quality failure.

```python
for bad in [np.array([0.,0.]),np.array([1.,np.nan])]:
    try: unit(bad)
    except ValueError: pass
    else: raise AssertionError('invalid vector accepted')
```

**Expected:** both raise ValueError.

**Verify:** Compare the computed values or written argument with both raise ValueError.

## Exercise 5: Reject incompatible spaces

The question is: Compare query metadata modelA with an index encoded by modelB, even when both have width3.

Vector dimensions are only a shape contract. Two models can use unrelated coordinate systems with the same width, so their dot products are not meaningful cross-model similarities.

```python
query_meta={'model':'A','width':3,'normalization':'unit'}; index_meta={'model':'B','width':3,'normalization':'unit'}
assert query_meta!=index_meta
```

**Expected:** space identity mismatch blocks retrieval.

**Verify:** Compare the computed values or written argument with space identity mismatch blocks retrieval.

## Exercise 6: Measure a domain failure

The question is: Give an irrelevant document a high-scoring vector and record that geometric rank does not establish relevance.

A relevance-labelled counterexample separates the ranking mechanism from its task quality. Improving an embedding model requires evaluating these failures, not merely checking that cosine arithmetic is correct.

```python
misleading={'wrong':np.array([1.,0.,0.]),'relevant':np.array([.5,.5,0.])}; relevant={'relevant'}
top=cosine_rank(query,misleading)[0][0]
assert top=='wrong' and top not in relevant
```

**Expected:** top-ranked IDwrong is outside the authored relevant set.

**Verify:** Compare the computed values or written argument with top-ranked IDwrong is outside the authored relevant set.

## Review after comparison

Repeat one case with a changed fixture and explain the difference before running it. Keep the original failure case as well as the repaired result. Record a missing framework separately from a failing assertion. No solution downloads data, calls an online model, deploys a service or changes a database.
