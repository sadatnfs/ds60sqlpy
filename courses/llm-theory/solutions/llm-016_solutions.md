# llm-016: explanatory solutions

Compare these answers only after an attempt or an explicit solution reveal. They use the same literal inputs as the guide, so a discrepancy can be localized to a specific step. The executable companion runs the assertions; the explanation states why those assertions test the subject. Passing a reference function is rehearsal, and should be followed by a new input chosen without looking at the answer.

## Mechanism review

A causal Transformer decoder turns a batch of token IDs into a next-token score vector at every input position. Its learned parameters are shared across token positions, apart from the explicit position table. The model does not store a separate neural network for every sentence length. Embedding lookup converts discrete identities into vectors; attention combines visible token representations; a feed-forward network transforms each resulting contextual vector; the final projection scores vocabulary choices.

This chapter exposes one pre-normalization decoder block rather than loading a pretrained package. The vocabulary has 16 IDs, the model width is 32, there are two attention heads, the feed-forward hidden width is 64 and the maximum learned position is bounded by a 32-row table. The exact model contains 10,464 trainable scalar parameters. It is small enough to trace every tensor axis and parameter group. Random initialization gives finite structured computations, not language understanding or useful generated text.

Attention and the feed-forward network have different jobs. Attention mixes information across permitted token positions. Each head computes its own query/key similarity distribution and weighted value mixture. The feed-forward block then applies the same nonlinear feature transformation independently at each position. Its input can already contain context from attention, but the feed-forward operation itself does not average or reduce the time axis.

Residual addition preserves a direct path from the input representation while adding the branch computation. In a pre-normalization block, the attention branch reads LayerNorm(x), then its projected output is added to x; the second branch reads a new LayerNorm of that sum. Residuals help provide an identity contribution to the derivative, but they do not guarantee that all gradients remain healthy. A branch Jacobian can still amplify, cancel or poorly condition directions. The later normalization chapter examines these derivatives more carefully.

The acceptance test is an information-flow contract: independently recomputing a prefix must reproduce the corresponding early logits of the full sequence. A future-token perturbation must also leave earlier logits unchanged. These are stronger observations than a plausible tensor shape or a decreasing training loss. They still do not establish that the objective uses correctly shifted targets or that evaluation data is uncontaminated; those are separate chapters.

**Decoder block:** Causal token mixing and tokenwise transformations connected by residual additions.

**Logits:** Unnormalized vocabulary scores at every input position.

**Head width:** The feature dimension assigned to each attention head, here 16.

**Pre-normalization:** Applying feature normalization before the residual branch computation.

**Context limit:** The declared position range represented by this model, here 32.

**Detached cache:** Stored K/V tensors disconnected from the prior autograd graph for inference use.

## Reading the implementation

### Exact parameter ledger

| Component | Trainable shape or count | Scalars |
| --- | --- | ---: |
| Token embedding | 16 by 32 | 512 |
| Absolute position embedding | 32 by 32 | 1,024 |
| Two LayerNorm modules | two sets of gain32 plus bias32 | 128 |
| Combined Q/K/V projection | 96 by 32, no bias | 3,072 |
| Attention output projection | 32 by 32, no bias | 1,024 |
| Feed-forward first affine map | 64 by 32 plus bias64 | 2,112 |
| Feed-forward second affine map | 32 by 64 plus bias32 | 2,080 |
| Vocabulary output projection | 16 by 32, no bias | 512 |
| Total | sum of these parameter groups | 10,464 |

PyTorch Linear stores [out_features,in_features] and applies the transposed weight to a row-oriented input. That is why the QKV weight is [96,32], while a mathematical row-vector projection may be written as multiplication by a [32,96] matrix. Biases are omitted in the attention and vocabulary projections but present in both feed-forward Linear modules. Forgetting these 96 bias entries changes the parameter ledger.

### Trace batch 1, time 4 through the forward pass

| Stage | Shape | Meaning of the last axes |
| --- | --- | --- |
| Input IDs | [1,4], int64 | four discrete token identities |
| Token plus position vectors | [1,4,32], float32 | 32 features for each position |
| First LayerNorm | [1,4,32] | feature statistics within each token |
| Combined QKV projection | [1,4,96] | three width-32 projected vectors |
| Each split Q, K or V | [1,2,4,16] | head, token, head feature |
| Scores and weights | [1,2,4,4] | query position, key position |
| Weighted values | [1,2,4,16] | one mixture per head and query |
| Rejoined heads and output projection | [1,4,32] | model-width contextual branch |
| First residual | [1,4,32] | input plus contextual branch |
| Feed-forward hidden activation | [1,4,64] | expanded tokenwise feature space |
| Second residual | [1,4,32] | transformed contextual representation |
| Vocabulary logits | [1,4,16] | one score per vocabulary ID |

Each head has width \(\frac{32}{2}=16\), so its dot products are divided by \(\sqrt{16}=4\). The Boolean triangle [4,4] broadcasts across batch and heads. Softmax reduces the final key axis, not the query axis or the vocabulary axis. The diagonal is allowed because the representation at input position t predicts the following token when training uses correctly shifted targets. The current input is therefore legal information under that objective.

After attention, transpose restores [batch,time,head,head_width]. contiguous makes the requested layout explicit before reshape combines the last two axes into model width. A reshape with the correct number of elements can still scramble token/head membership if the transpose order is wrong. The exact shape ledger and prefix checks are complementary; neither substitutes for the other.

## Exercise 1: Build a bounded decoder

The question is: Set seed 7, build the default decoder, count every trainable scalar and compare with the component ledger.

The exact count follows the embedding, projection and feed-forward shapes. A small parameter count bounds the fixture but says little about capability on unseen tasks.

```python
torch.manual_seed(7)
model = TinyDecoder().eval()
count = sum(parameter.numel() for parameter in model.parameters())
assert count == 10464
assert count < 50000
```

**Expected:** Exactly 10,464 trainable scalars, below the 50,000 teaching bound.

**Verify:** Compare the computed values or written argument with Exactly 10,464 trainable scalars, below the 50,000 teaching bound.

## Exercise 2: Trace output axes

The question is: Run the integer IDs [[2,5,7,3]] and trace the output shape and dtype.

Every input position produces a distribution over the same sixteen-token vocabulary. The time axis is not a class axis and must not be reduced accidentally.

```python
torch.manual_seed(7)
model = TinyDecoder().eval()
ids = torch.tensor([[2, 5, 7, 3]], dtype=torch.long)
with torch.no_grad():
    logits, _ = model(ids)
assert tuple(logits.shape) == (1, 4, 16)
assert logits.dtype == torch.float32
assert torch.isfinite(logits).all()
```

**Expected:** Finite float32 logits with shape [1,4,16].

**Verify:** Compare the computed values or written argument with Finite float32 logits with shape [1,4,16].

## Exercise 3: Recompute prefixes

The question is: Recompute prefixes of lengths 1 through 4 independently with the same initialized weights.

The check covers the whole block, including normalization and positions, rather than only the attention mask. Dropout is absent in this teaching decoder.

```python
torch.manual_seed(7)
model = TinyDecoder().eval()
ids = torch.tensor([[2, 5, 7, 3]], dtype=torch.long)
with torch.no_grad():
    full, _ = model(ids)
    for length in range(1, 5):
        prefix, _ = model(ids[:, :length])
        torch.testing.assert_close(prefix, full[:, :length], atol=1e-6, rtol=0)
```

**Expected:** Every prefix matches the corresponding full-sequence early logits within 1e-6.

**Verify:** Compare the computed values or written argument with Every prefix matches the corresponding full-sequence early logits within 1e-6.

## Exercise 4: Perturb only future tokens

The question is: Replace only positions 2 and 3 with IDs 8 and 9 and compare the first two logits.

A future-only perturbation is a direct causal test. It can expose a leaking normalization or incorrect mask even when the model has never been trained.

```python
torch.manual_seed(7)
model = TinyDecoder().eval()
ids = torch.tensor([[2, 5, 7, 3]], dtype=torch.long)
changed = ids.clone()
changed[:, 2:] = torch.tensor([[8, 9]])
with torch.no_grad():
    original, _ = model(ids)
    perturbed, _ = model(changed)
torch.testing.assert_close(perturbed[:, :2], original[:, :2], atol=1e-6, rtol=0)
assert not torch.equal(ids, changed)
```

**Expected:** The first two score vectors remain unchanged within 1e-6.

**Verify:** Compare the computed values or written argument with The first two score vectors remain unchanged within 1e-6.

## Exercise 5: Inspect head shapes

The question is: Run without disabling autograd and inspect the returned K/V cache shapes, detachment and data-byte count.

Width32 is split into two sixteen-dimensional heads. The cached time dimension grows with processed tokens, while the feature width remains fixed.

```python
torch.manual_seed(7)
model = TinyDecoder().eval()
ids = torch.tensor([[2, 5, 7, 3]], dtype=torch.long)
logits, cache = model(ids)
assert logits.requires_grad
for tensor in cache.values():
    assert tuple(tensor.shape) == (1, 2, 4, 16)
    assert tensor.dtype == torch.float32
    assert not tensor.requires_grad
assert sum(tensor.numel() * tensor.element_size() for tensor in cache.values()) == 1024
```

**Expected:** Logits remain connected; each cache is detached float32 [1,2,4,16]; combined cache data occupies 1,024 bytes.

**Verify:** Compare the computed values or written argument with Logits remain connected; each cache is detached float32 [1,2,4,16]; combined cache data occupies 1,024 bytes.

## Exercise 6: Reject invalid token IDs

The question is: Reject out-of-range IDs, wrong dtype, empty/excessive context and invalid head/width configurations.

A fixed vocabulary and position table impose real bounds. Rejecting invalid requests makes the failure understandable before embedding indexing or an excessive context reaches deeper operations.

```python
model = TinyDecoder().eval()
invalid_inputs = [
    torch.tensor([[16]], dtype=torch.long),
    torch.tensor([[-1]], dtype=torch.long),
    torch.zeros((1, 33), dtype=torch.long),
    torch.zeros((1, 0), dtype=torch.long),
    torch.tensor([[2.0]], dtype=torch.float32),
]
for invalid in invalid_inputs:
    try:
        model(invalid)
    except ValueError:
        pass
    else:
        raise AssertionError('invalid token/context contract was accepted')
for options in [dict(width=5, heads=2), dict(heads=0), dict(context=0)]:
    try:
        TinyDecoder(**options)
    except ValueError:
        pass
    else:
        raise AssertionError('invalid model dimensions were accepted')
```

**Expected:** Every invalid contract raises ValueError before a misleading reshape or embedding computation.

**Verify:** Compare the computed values or written argument with Every invalid contract raises ValueError before a misleading reshape or embedding computation.

## Review after comparison

Repeat one case with a changed fixture and explain the difference before running it. Keep the original failure case as well as the repaired result. Record a missing framework separately from a failing assertion. No solution downloads data, calls an online model, deploys a service or changes a database.
