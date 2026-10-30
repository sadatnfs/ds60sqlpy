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

## Derive the ranking and distinguish geometry from meaning

For nonzero vectors q and d, cosine is \(\frac{q^{\mathsf T}d}{\lVert q\rVert_2\lVert d\rVert_2}\). The query[1, 0, 0] already has norm one. The purchase vector[1, 0.1, 0] has norm \(\sqrt{1.01}\), so its cosine is \(1/\sqrt{1.01}\), about 0.995037. The mixed vector[0.5, 0.5, 0] has norm \(\sqrt{0.5}\), giving cosine \(1/\sqrt2\), about 0.707107. Geometry[0, 1, 0] gives zero. These calculations establish purchase, mixed, geometry as the order under the authored coordinates.

Positive scaling preserves direction: replacing d by 10d multiplies both numerator and norm by ten, leaving cosine unchanged. A raw dot product multiplies by ten. Negative scaling reverses direction and changes the cosine's sign, so the invariance claim is specifically about positive magnitude scaling. A document with a large norm can dominate dot-product search even when its direction is less aligned; whether that norm carries useful information depends on the encoder's training contract.

For unit-normalized vectors, squared Euclidean distance is \(\lVert q-d\rVert_2^2=2-2q^{\mathsf T}d\). Thus sorting by decreasing cosine and increasing squared distance gives the same exact order when both sides are unit vectors. This identity is conditional on normalization; it does not make every distance metric interchangeable on raw embeddings.

An embedding coordinate system has no universal axis meaning. Apply the same orthogonal rotation R to both q and d, and their dot product is unchanged because \({R}^{T}\) R is identity. Rotate only one side, and the cross-space comparison changes. For example, one encoder may represent the relevant concept by[1, 0] while another represents it by[0, 1]. Both vectors have width two and each can work correctly within its own space, but their cross-model dot product is zero. Equal width is therefore a shape check, not a semantic compatibility proof.

The fixture assigns buy and purchase the same literal vector. Their equivalence is authored knowledge, not a measured generalization by a language model. Sentence-BERT is an example of learning sentence representations suitable for efficient similarity comparison; the local table does not reproduce its training or encode arbitrary text. [Sentence-BERT](https://arxiv.org/abs/1908.10084).

A real dual encoder permits document vectors to be computed in advance and query vectors at request time. Exact scoring over M documents of dimension D requires work proportional to \(M\cdot D\) and stored vectors proportional to \(M\cdot D\). Approximate nearest-neighbor methods trade search work against candidate recall. Measure that search recall against the exact vector ranking separately from semantic relevance recall against human-labeled evidence. An approximate index can perfectly imitate a bad semantic ranking, and a good encoder can lose its best document through approximation.

The helper rejects zero vectors, nonfinite coordinates and a norm that is zero or nonfinite after computation. That is a bounded numerical contract, not a promise to normalize every mathematically finite nonzero vector. Extremely large or tiny float64 coordinates can overflow or underflow during a naive norm calculation. A scaled norm can extend the useful range, but changing that implementation would require its own tests. The supplied tiny vectors stay well inside the demonstrated range.

### Interview reasoning with explanatory answers

**Is cosine0.9 a90% relevance probability?** No. It describes an angle under a particular representation. Relevance calibration needs labeled examples and can shift with corpus, encoder or task.

**Why keep exact identifiers in evaluation?** A semantic encoder can place a nearby but wrong identifier close to the query. Lexical and semantic mechanisms may make complementary errors, so average paraphrase quality does not settle the choice.

**How do you localize a missing relevant document?** Compare exact vector ranking, approximate-index candidates and relevance labels. That separates encoder geometry from search loss and downstream context truncation.

## Exercise 1: Rank fixed topic vectors

The question is: Use query[1, 0, 0] and documents purchase[1, .1, 0], geometry[0, 1, 0], mixed[.5, .5, 0].

The ranking follows the declared topic geometry. The fixture does not demonstrate that a learned model will assign these vectors to arbitrary language.

```python
table = {
    "purchase": np.array([1.0, 0.1, 0.0]),
    "geometry": np.array([0.0, 1.0, 0.0]),
    "mixed": np.array([0.5, 0.5, 0.0]),
}
ranked = cosine_rank(np.array([1.0, 0.0, 0.0]), table)
assert [key for key, score in ranked] == ["purchase", "mixed", "geometry"]
```

**Expected:** purchase ranks first, mixed second, geometry last.

**Verify:** Compare the computed values or written argument with purchase ranks first, mixed second, geometry last.

## Exercise 2: Separate cosine from magnitude

The question is: Scale the purchase vector by 10 and compare its cosine score with the original.

Normalization removes positive magnitude scaling from the score. A model trained for unnormalized dot products may use magnitude meaningfully, so the scoring convention must match the model contract.

```python
query = np.array([1.0, 0.0, 0.0])
original = table["purchase"]
scaled = 10 * original
np.testing.assert_allclose(
    unit(original) @ unit(query), unit(scaled) @ unit(query), atol=1e-12, rtol=0
)
assert scaled @ query == 10 * (original @ query)
```

**Expected:** cosine unchanged within1e-12; raw dot product multiplies by 10.

**Verify:** Compare the computed values or written argument with cosine unchanged within1e-12; raw dot product multiplies by 10.

## Exercise 3: Expose hand-authored synonym knowledge

The question is: Assign buy the same literal vector as purchase and compare retrieval with an exact-token overlap baseline.

The semantic relation was supplied by the fixture author. A pretrained encoder would need to learn or represent it, and a domain-specific synonym may still be missed.

```python
word_vectors = {"buy": np.array([1.0, 0.0, 0.0]), "purchase": np.array([1.0, 0.0, 0.0])}
assert set("buy".split()) & set("purchase".split()) == set()
np.testing.assert_array_equal(word_vectors["buy"], word_vectors["purchase"])
```

**Expected:** vector scores match; literal word overlap is empty.

**Verify:** Compare the computed values or written argument with vector scores match; literal word overlap is empty.

## Exercise 4: Reject zero and nonfinite vectors

The question is: Normalize[0, 0] and[1, NaN] through the checked helper.

A zero vector has no direction and NaN is not a valid coordinate. Returning a plausible similarity would hide an encoding or data-quality failure.

```python
for bad in [np.array([0.0, 0.0]), np.array([1.0, np.nan])]:
    try:
        unit(bad)
    except ValueError:
        pass
    else:
        raise AssertionError("invalid vector accepted")
```

**Expected:** both raise ValueError.

**Verify:** Compare the computed values or written argument with both raise ValueError.

## Exercise 5: Reject incompatible spaces

The question is: Compare query metadata modelA with an index encoded by modelB, even when both have width3.

Vector dimensions are only a shape contract. Two models can use unrelated coordinate systems with the same width, so their dot products are not meaningful cross-model similarities.

```python
query_meta = {"model": "A", "width": 3, "normalization": "unit"}
index_meta = {"model": "B", "width": 3, "normalization": "unit"}
assert query_meta != index_meta
```

**Expected:** metadata identity mismatch is detected; the caller must enforce the retrieval gate.

**Verify:** Compare the computed values or written argument with metadata identity mismatch is detected; the caller must enforce the retrieval gate.

## Exercise 6: Measure a domain failure

The question is: Give an irrelevant document a high-scoring vector and record that geometric rank does not establish relevance.

A relevance-labelled counterexample separates the ranking mechanism from its task quality. Improving an embedding model requires evaluating these failures, not merely checking that cosine arithmetic is correct.

```python
misleading = {"wrong": np.array([1.0, 0.0, 0.0]), "relevant": np.array([0.5, 0.5, 0.0])}
relevant = {"relevant"}
top = cosine_rank(query, misleading)[0][0]
assert top == "wrong" and top not in relevant
```

**Expected:** top-ranked ID wrong is outside the authored relevant set.

**Verify:** Compare the computed values or written argument with top-ranked ID wrong is outside the authored relevant set.

## Review after comparison

Repeat one case with a changed fixture and explain the difference before running it. Keep the original failure case as well as the repaired result. Record a missing framework separately from a failing assertion. No solution downloads data, calls an online model, deploys a service or changes a database.
