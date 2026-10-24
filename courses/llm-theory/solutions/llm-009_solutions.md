# Worked solutions: llm-009

Open this file after an attempt or an explicit request for comparison. The
[learner guide](../guides/llm-009.md) contains the prediction, two examples and
six independent exercise contracts. Preserve the learner's own explanation
and failed checks. This is an authored beta lesson, not a claim that a complete language model
has been validated.

## Runtime and shared reference

Use the already prepared NumPy interpreter and the Windows or POSIX command
in the guide. No framework installation, tokenizer download, trained weights,
service, key or GPU is involved. The Shared reference and Exercises 1 through
6 code blocks form one executable Python script in order. Every comparison
uses `rtol=0, atol=1e-12`. Exact rational mixtures and independently recomputed
prefixes provide different forms of evidence.

The helper enforces square self-attention. It does not claim to support
batched attention, a cache, cross-attention or a full decoder. A boolean True
means allowed here. Transfer to a different API requires checking that API's
mask contract.

```python
import numpy as np


def attention(q, k, v, allowed):
    q, k, v = (np.asarray(value, dtype=np.float64) for value in (q, k, v))
    allowed = np.asarray(allowed)
    if any(value.ndim != 2 for value in (q, k, v)):
        raise ValueError("q, k and v must be matrices")
    count, width = q.shape
    if count == 0 or width == 0 or v.shape[1] == 0:
        raise ValueError("nonempty token and feature axes required")
    if k.shape != (count, width) or v.shape[0] != count:
        raise ValueError("self-attention shapes do not agree")
    if allowed.dtype != np.bool_:
        raise TypeError("allowed must be boolean")
    if allowed.shape != (count, count):
        raise ValueError("allowed must have shape (tokens, tokens)")
    if not allowed.any(axis=1).all():
        raise ValueError("each query needs at least one key")
    if not all(np.isfinite(value).all() for value in (q, k, v)):
        raise ValueError("finite inputs required")
    scores = (q @ k.T) / np.sqrt(width)
    if not np.isfinite(scores[allowed]).all():
        raise ValueError("finite allowed scores required")
    masked = np.where(allowed, scores, -np.inf)
    shifted = masked - masked.max(axis=1, keepdims=True)
    weights = np.exp(shifted)
    weights /= weights.sum(axis=1, keepdims=True)
    return weights @ v, weights


q = np.zeros((3, 2), dtype=np.float64)
k = q.copy()
v = np.array([[2.0, 0.0], [0.0, 2.0], [6.0, 6.0]])
allowed = np.tri(3, dtype=bool)
output, weights = attention(q, k, v, allowed)
expected = np.array([[2.0, 0.0], [1.0, 1.0], [8 / 3, 8 / 3]])
np.testing.assert_allclose(output, expected, rtol=0, atol=1e-12)
np.testing.assert_allclose(weights.sum(axis=1), 1.0, rtol=0, atol=1e-12)
for cut in range(1, 4):
    prefix, _ = attention(q[:cut], k[:cut], v[:cut], np.tri(cut, dtype=bool))
    np.testing.assert_allclose(output[:cut], prefix, rtol=0, atol=1e-12)
print(output)
```

## Exercise 1: trace three mixtures

Score row 0 can use only key 0, so its softmax puts all mass there. Row 1 has
two equal legal scores and therefore two weights of `1/2`. Row 2 has three
weights of `1/3`. Multiplying these rows by V gives the value at position 0,
the first-two mean, and then the three-value mean.

```python
expected_weights = np.array(
    [
        [1.0, 0.0, 0.0],
        [0.5, 0.5, 0.0],
        [1 / 3, 1 / 3, 1 / 3],
    ]
)
expected_output = np.array([[2.0, 0.0], [1.0, 1.0], [8 / 3, 8 / 3]])
np.testing.assert_allclose(weights, expected_weights, rtol=0, atol=1e-12)
np.testing.assert_allclose(output, expected_output, rtol=0, atol=1e-12)
np.testing.assert_allclose(weights.sum(axis=1), [1.0, 1.0, 1.0], rtol=0, atol=1e-12)
print("exercise 1: mixtures and row masses agree")
```

**Expected:** every assertion passes. **Verify:** the rows index queries and
the columns index keys. Each output has two feature coordinates inherited
from V. Their sum need not be 1; they are not probabilities over a token
vocabulary. Only the attention weights have that normalization contract.

## Exercise 2: change only the future

A causal earlier query has no legal route to the third value. Its output
therefore cannot depend on that value. The final query can use all values,
so its new average is `[(2+0+100)/3, (0+2+200)/3] = [34,202/3]`.

```python
original_v = v.copy()
future_v = v.copy()
future_v[2] = [100.0, 200.0]
causal, _ = attention(q, k, future_v, np.tri(3, dtype=bool))
unmasked, _ = attention(q, k, future_v, np.ones((3, 3), dtype=bool))
np.testing.assert_allclose(causal[:2], expected_output[:2], rtol=0, atol=1e-12)
np.testing.assert_allclose(causal[2], [34.0, 202 / 3], rtol=0, atol=1e-12)
np.testing.assert_allclose(unmasked, np.tile([34.0, 202 / 3], (3, 1)), rtol=0, atol=1e-12)
np.testing.assert_array_equal(v, original_v)
assert not np.allclose(unmasked[:2], expected_output[:2])
print("exercise 2: causal prefix unchanged; unmasked prefix changed")
```

**Expected:** the first two causal rows stay fixed while the unmasked prefix
changes. **Verify:** the original V remains unchanged; otherwise a later test
might compare two accidentally mutated fixtures and pass for the wrong reason.
A causal failure is demonstrated by the changed early outputs, independently
of whether a generated sentence would appear plausible.

## Exercise 3: construct a nonuniform prefix oracle

The new Q and K make scores unequal, so a bug cannot pass merely by producing
a uniform average. Each prefix call below starts from sliced Q, K and V and
computes its own scores, normalization and matrix product. It never reuses
weights calculated from the full sequence.

```python
def check_prefixes(query, key, value):
    count = len(query)
    full, _ = attention(query, key, value, np.tri(count, dtype=bool))
    for cut in range(1, count + 1):
        prefix, _ = attention(query[:cut], key[:cut], value[:cut], np.tri(cut, dtype=bool))
        np.testing.assert_allclose(full[:cut], prefix, rtol=0, atol=1e-12)
    return full


nonuniform_q = np.array([[1.0, 0.0], [0.0, 1.0], [1.0, 1.0], [-1.0, 1.0]])
nonuniform_k = nonuniform_q.copy()
nonuniform_v = np.array([[1.0, 2.0], [3.0, 4.0], [5.0, 6.0], [7.0, 8.0]])
full = check_prefixes(nonuniform_q, nonuniform_k, nonuniform_v)
future_q, future_k, future_values = (
    value.copy() for value in (nonuniform_q, nonuniform_k, nonuniform_v)
)
future_q[2:] += 3.0
future_k[2:] *= -4.0
future_values[2:] += 100.0
changed = check_prefixes(future_q, future_k, future_values)
np.testing.assert_allclose(changed[:2], full[:2], rtol=0, atol=1e-12)
assert not np.allclose(changed[2:], full[2:])
print("exercise 3: all four cuts and future perturbations passed")
```

**Expected:** every cut passes; changing future-only Q, K and V preserves the
first two outputs. **Verify:** later rows really do change, so the perturbation
was not a no-op. This validates this attention function on the supplied
fixtures, not every implementation or every possible input. A full decoder
also needs tokenwise normalization, positions and cache behavior that respect
the same boundary.

## Exercise 4: diagnose a plausible-looking triangle

The broken computation assigns `1/3` to every key before applying a mask.
Removing forbidden mass afterward leaves the first two rows with less than
unit mass. The last row happens to be correct because it has no forbidden
keys. Seeing some correct output or a lower triangle therefore is insufficient.

```python
broken_weights = np.full((3, 3), 1 / 3) * np.tri(3, dtype=bool)
broken_output = broken_weights @ v
np.testing.assert_allclose(broken_weights.sum(axis=1), [1 / 3, 2 / 3, 1.0], rtol=0, atol=1e-12)
np.testing.assert_allclose(
    broken_output, [[2 / 3, 0.0], [2 / 3, 2 / 3], [8 / 3, 8 / 3]], rtol=0, atol=1e-12
)
repaired, repaired_weights = attention(q, k, v, np.tri(3, dtype=bool))
np.testing.assert_allclose(repaired, expected_output, rtol=0, atol=1e-12)
np.testing.assert_allclose(repaired_weights.sum(axis=1), 1.0, rtol=0, atol=1e-12)
print("exercise 4: masked-before-normalization repair passed")
```

**Expected:** broken row sums are `[1/3,2/3,1]` and the repaired output matches
the original oracle. **Verify:** the reference removes forbidden scores before
exponentiation, subtracts a row maximum, then normalizes over legal keys.
Post-softmax removal followed by explicit renormalization can be mathematically
equivalent for finite ordinary cases, but first computing forbidden
exponentials creates avoidable overflow/underflow and empty-row hazards. Keep
the pre-normalization mask as the canonical implementation here.

## Exercise 5: make invalid inputs fail clearly

An empty input has no attention distribution. A fully masked query has no
legal key to normalize. Neither should be silently converted into zeros or
NaNs. An integer mask is rejected because accepting arbitrary numeric values
would hide ambiguity about its meaning.

```python
def expect_failure(error_type, operation, message=None):
    try:
        operation()
    except error_type as error:
        if message is not None:
            assert message in str(error)
    else:
        raise AssertionError("invalid input was accepted")


empty = np.empty((0, 2))
expect_failure(ValueError, lambda: attention(empty, empty, empty, np.empty((0, 0), dtype=bool)))
expect_failure(TypeError, lambda: attention(q, k, v, np.tri(3, dtype=int)))
expect_failure(ValueError, lambda: attention(q, k, v, np.ones((3, 2), dtype=bool)))
no_key = np.tri(3, dtype=bool)
no_key[1] = False
expect_failure(ValueError, lambda: attention(q, k, v, no_key), "each query needs at least one key")
nonfinite = v.copy()
nonfinite[0, 0] = np.nan
expect_failure(ValueError, lambda: attention(q, k, nonfinite, allowed), "finite inputs required")
valid_again, _ = attention(q, k, v, allowed)
assert np.isfinite(valid_again).all()
np.testing.assert_allclose(valid_again, expected_output, rtol=0, atol=1e-12)
print("exercise 5: five rejected cases; valid fixture still works")
```

**Expected:** exactly the stated exception classes, the specific fully masked
message, and a valid finite result afterward. **Verify:** each invalid call is
isolated. An unexpected exception is not swallowed by a broad catch, and
returning a default matrix would fail the rejection contract. Finiteness checks
also do not mean every finite input can be represented safely: the helper
rejects overflow in allowed scores rather than claiming universal precision.

## Exercise 6: transfer to next-token labels

The current token is the input from which the next token is predicted. A
query may therefore use its own input position, including the diagonal.
Giving it the next input position would expose the label it is supposed to
predict. The causal boundary and the training/evaluation data boundary are
separate contracts.

```python
ids = np.array([2, 5, 7, 3], dtype=np.int64)
inputs, labels = ids[:-1], ids[1:]
np.testing.assert_array_equal(inputs, [2, 5, 7])
np.testing.assert_array_equal(labels, [5, 7, 3])
pairs = list(zip(inputs.tolist(), labels.tolist()))
assert pairs == [(2, 5), (5, 7), (7, 3)]
assert labels.size == 3
label_mask = np.tri(len(inputs), dtype=bool)
assert label_mask[0, 0]
assert not label_mask[0, 1]
np.testing.assert_array_equal(label_mask[0], [True, False, False])

# Two different filenames still belong to the same source-document family.
family = {"doc-a": "A", "doc-a-copy": "A"}
training_ids, validation_ids = ["doc-a"], ["doc-a-copy"]
training_families = {family[name] for name in training_ids}
validation_families = {family[name] for name in validation_ids}
assert training_families & validation_families == {"A"}
print("exercise 6:", pairs, "duplicate-family leakage detected")
```

**Expected:** three shifted pairs, an allowed diagonal, a forbidden next key,
and detected family overlap. **Verify:** a random file split alone would miss
this counterexample. Training a tokenizer on validation text is another form
of contamination even when every attention mask is correct. Freeze source
families and fit preprocessing on training only before selecting a model.

## Retrieval and evidence review

For the guide's fresh two-row V fixture `[[4,0],[0,4]]` with zero Q/K, the causal
outputs are `[[4,0],[2,2]]`. A teacher should choose a new fixture after this
answer is revealed. Ask for a drawn allowed row, an independently recomputed
prefix, and a leakage counterexample without opening the helper.

Use the guide's five-dimension rubric and its causal/leakage gates. Accept
other code when its axes, mask meaning, row mass, independent tests and
failure behavior satisfy the contracts. A successful local attention test is
useful implementation evidence. It does not establish language-model quality,
factual correctness, fairness, privacy or complete-system safety.

## Sources and execution status

Reviewed **2026-10-22**: [Attention Is All You Need](https://arxiv.org/abs/1706.03762)
supports the attention and causal-decoder background. The
[PyTorch attention documentation](https://docs.pytorch.org/docs/stable/generated/torch.nn.functional.scaled_dot_product_attention.html)
shows why API mask polarity and dropout need explicit interpretation. All
NumPy code blocks in this reference were executed together with an existing
prepared interpreter. No package, model or data download was performed.
