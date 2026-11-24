# llm-044: explanatory solutions

Read these roPE, relative positions, ALiBi and long-context limits answers after attempting *Rotate a two-dimensional vector* through *Separate computability from extrapolation evidence*, or after asking for a reveal. They reuse the guide's literals, so a mismatch in *Inspect an ALiBi causal row* points to one step. `llm-044_solution.py` holds the assertions; this page explains how they test roPE. Then try *Separate computability from extrapolation evidence* on a fresh input you chose before looking.

## Mechanism review

Position mechanisms tell attention how token order or distance should influence a comparison. Learned absolute embeddings attach vectors to positions, while relative-position methods make pairwise relationships explicit. Rotary position embeddings, RoPE, rotate pairs of query and key features by position-dependent angles. The dot product between rotated vectors then depends on their relative offset through a rotation identity. Values are not automatically rotated by that standard construction.

ALiBi uses a different mechanism: it adds a distance-dependent bias directly to attention scores, typically penalizing distant allowed keys under a causal decoder. A bias is not an access mask. Future keys still need to be excluded. Different heads can use different slopes, which creates different recency preferences.

A formula accepting a large position index does not prove that a trained model will use long context reliably. Training length, frequency choices, precision, attention patterns and evaluation tasks all matter. This chapter tests exact geometric identities, causal bias behavior and cache-position bookkeeping. It makes no claim that a particular RoPE scaling or ALiBi configuration preserves quality outside its measured training/evaluation range.

**RoPE:** Rotary position embedding applied to query/key feature pairs.

**Relative offset:** The difference between two token positions.

**ALiBi:** Attention with linear distance biases added to scores.

**Position offset:** The absolute index of a newly appended cached token.

**Length extrapolation:** Using context lengths beyond those supported by the training/evaluation evidence.

## Reading the implementation

The RoPE helper pairs adjacent features and uses inverse frequencies base**(-2*i/d) for pair index i. For each position p, it applies a 2D rotation by p*frequency to the corresponding query or key pair. Head width must be positive and even. ALiBi scores add -slope*(query_position-key_position) for legal past/current keys, then apply the causal mask before softmax. Cached keys retain the position assigned when they were created; do not rotate an already rotated key again or restart offsets for a new token.

## Exercise 1: Rotate a two-dimensional vector

The question is: Rotate [1, 0] by \(\frac{\pi}{2}\) and check length preservation.

A rotation changes direction while preserving the Euclidean norm. This separates position encoding from arbitrary magnitude scaling.

```python
vector = np.array([1.0, 0.0])
rotated = rotate(vector, np.pi / 2)
np.testing.assert_allclose(rotated, [0, 1], atol=1e-12, rtol=0)
np.testing.assert_allclose(np.linalg.norm(rotated), 1, atol=1e-12, rtol=0)
```

**Expected:** approximately [0, 1]; norm 1.

**Verify:** For *Rotate a two-dimensional vector*, a fresh-process check confirms `rotated` matches `[0, 1]` within 1e-12 and `np.linalg.norm(rotated)` matches `1` within 1e-12.

## Exercise 2: Verify the relative dot-product identity

The question is: Use q = [1, 2], k = [3, -1] and angles m = 0.3, n = 1.1.

The transpose of a rotation is its inverse, so the absolute angles combine into their difference. This is an algebraic property, not a measured long-context quality result.

```python
q = np.array([1.0, 2.0])
k = np.array([3.0, -1.0])
m = 0.3
n = 1.1
left = rotate(q, m) @ rotate(k, n)
right = q @ rotate(k, n - m)
np.testing.assert_allclose(left, right, atol=1e-12, rtol=0)
```

**Expected:** dot(Rm q, Rn k)=dot(q, R(n-m)k) within 1e-12.

**Verify:** For *Verify the relative dot-product identity*, a fresh-process check confirms `left` matches `right` within 1e-12.

## Exercise 3: Inspect an ALiBi causal row

The question is: Use zero content scores for query position 2, keys 0, 1, 2 and slope \(\log 2\).

The distance penalties produce exponentials 1/4, \(\frac{1}{2}\), 1 before normalization. The current key receives the largest weight under this illustrative slope.

```python
positions = np.arange(3)
score = -np.log(2) * (2 - positions)
mass = np.exp(score - score.max())
weights = mass / mass.sum()
np.testing.assert_allclose(weights, [1 / 7, 2 / 7, 4 / 7], atol=1e-12, rtol=0)
```

**Expected:** normalized weights [1/7, \(\frac{2}{7}\), 4/7].

**Verify:** For *Inspect an ALiBi causal row*, a fresh-process check confirms `weights` matches `[1 / 7, 2 / 7, 4 / 7]` within 1e-12.

## Exercise 4: Apply multi-frequency RoPE

The question is: Use width 4, base 10000 and positions 0, 1 on two fixed vectors; inspect pair norms.

Different feature pairs rotate at different rates. The fixture uses adjacent-pair layout; other implementations may store paired components differently and need a layout translation.

```python
values = np.array([[1.0, 0.0, 3.0, 4.0], [2.0, 1.0, 0.0, 2.0]])
encoded = rope(values, np.array([0, 1]), base=10000.0)
np.testing.assert_allclose(
    np.linalg.norm(encoded.reshape(2, 2, 2), axis=-1),
    np.linalg.norm(values.reshape(2, 2, 2), axis=-1),
    atol=1e-12,
    rtol=0,
)
np.testing.assert_allclose(10000.0 ** (-2 * np.arange(2) / 4), [1, 0.01], atol=1e-12, rtol=0)
```

**Expected:** frequencies 1 and 0.01; each pair norm preserved.

**Verify:** For *Apply multi-frequency RoPE*, a fresh-process check confirms `np.linalg.norm(encoded.reshape(2, 2, 2), axis=-1)` matches `np.linalg.norm(values.reshape(2, 2, 2), axis=-1)` within 1e-12 and `10000.0 ** (-2 * np.arange(2) / 4)` matches `[1, 0.01]` within 1e-12.

## Exercise 5: Catch a cache offset reset

The question is: Encode the third key at position 2 and compare with mistakenly encoding it at position 0.

A cache contains position-dependent key state. Correct tensor dimensions do not reveal that a new token was assigned the wrong position.

```python
keys = np.array([[1.0, 0.0], [0.0, 1.0], [1.0, 1.0]])
full = rope(keys, np.arange(3))
incremental = rope(keys[2:], np.array([2]))
reset = rope(keys[2:], np.array([0]))
np.testing.assert_allclose(incremental, full[2:], atol=1e-12, rtol=0)
assert not np.allclose(reset, full[2:])
```

**Expected:** correct incremental encoding matches full encoding; the reset differs.

**Verify:** For *Catch a cache offset reset*, a fresh-process check confirms `incremental` matches `full[2:]` within 1e-12 and `not np.allclose(reset, full[2:])`.

## Exercise 6: Separate computability from extrapolation evidence

The question is: Compute a finite encoding at position 1000000, then record that no trained-model quality was measured.

A valid sine/cosine calculation says nothing about whether a model learned useful behavior at that distance. The dimension check is a mathematical contract, the quality question is empirical.

```python
far = rope(np.array([[1.0, 0.0, 1.0, 0.0]]), np.array([1_000_000]))
assert np.isfinite(far).all()
report = {"formula_evaluated": True, "long_context_quality_verified": False}
assert not report["long_context_quality_verified"]
try:
    rope(np.ones((1, 3)), np.array([0]))
except ValueError:
    pass
else:
    raise AssertionError("odd rotary width accepted")
```

**Expected:** finite vector; long_context_quality_verified=False; odd width rejected.

**Verify:** For *Separate computability from extrapolation evidence*, a fresh-process check confirms `np.isfinite(far).all()`; `not report['long_context_quality_verified']` and `rope(np.ones((1, 3)), np.array([0]))` raises `ValueError`.

## Review after comparison

Change one input to *Apply multi-frequency RoPE* and predict the result first; keep *Separate computability from extrapolation evidence* failing beside the repair. Log a missing NumPy separately from a wrong roPE value in `llm-044`.
