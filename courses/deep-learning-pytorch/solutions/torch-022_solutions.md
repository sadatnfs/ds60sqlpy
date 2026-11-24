# torch-022: explanatory solutions

Open these answers only after attempting Attention, transformer masks and information boundaries yourself. They reuse the guide's literal inputs, starting from Example A, Compute uniform causal mixtures, so a discrepancy points at one step. The executable companion runs the assertions; this page explains why each one tests SDPA, Mask polarity, Prefix invariance. After a pass, choose a new input for exercise 6, Keep inference dropout disabled, without looking.

## Mechanism review

Attention forms weighted combinations of value vectors using query-key comparisons. A causal decoder restricts each query to current and earlier positions. PyTorch's functional scaled_dot_product_attention uses boolean True for allowed positions, while other attention APIs such as Multihead Attention key_padding_mask use True for ignored keys. Mask polarity belongs to the exact parameter contract, not to the framework name.

The functional API also applies dropout according to its `dropout_p` argument; calling an enclosing `module.eval` does not automatically change an explicit nonzero probability. For an evaluation oracle, pass `dropout_p=0`. Equal queries and keys make legal scores uniform, so the expected outputs are prefix means. Nonuniform scores and future-only perturbations add stronger checks than causal-looking triangles alone.

**SDPA:** Scaled dot-product attention implemented by a functional API.

**Mask polarity:** Whether True means allowed or excluded for this parameter.

**Prefix invariance:** Agreement between a full sequence prefix and independent prefix execution.

**Dropout argument:** An explicit stochastic policy in the functional attention call.

## Reading the implementation

The checked helper accepts nonempty 2 D self-attention matrices and a boolean square allowed mask. Reject fully masked rows before normalization. F.scaled_dot_product_attention supplies the \(\frac{1}{\sqrt{\mathrm{key}_{\mathrm{width}}}}\) scaling and normalizes over the key axis. A causal lower triangle includes its diagonal for shifted next-token targets. Independently recompute each prefix rather than slicing full weights.

## Derive attention values and information boundaries

Let Q have shape (L, d_k), K shape (S, d_k) and V shape (S, d_v). Scores \(S_{\mathrm{score}}=\frac{QK^{\mathsf T}}{\sqrt{d_k}}\) have shape (L, S): each row belongs to one query and each column to one key. Softmax runs across the key axis, and P@V produces (L, d_v). The lesson restricts L=S and matching query/key widths to make this map inspectable. Batched multihead code adds batch/head axes; those do not replace the query and key meanings.

When every score is zero, a legal row containing m keys assigns each probability \(\frac{1}{m}\). The causal rows here permit one, two and three keys, giving [2, 0], [1, 1] and [\(\frac{8}{3}\), \(\frac{8}{3}\)]. Multiplying an unrestricted uniform \(\frac{1}{3}\) distribution by the triangle afterward would instead leave row sums \(\frac{1}{3}\), \(\frac{2}{3}\), 1. Forbidden keys already participated in normalization, so masking must define the legal score set before softmax or be followed by a correctly specified renormalization.

The zero-score example cannot verify the scale factor: zero divided by any finite positive width factor remains zero. For the nonuniform second query [0, 1], the two legal keys [1, 0] and [0, 1] produce scores 0 and \(a=\frac{1}{\sqrt{2}}\). Let \(p=\frac{\exp(a)}{1+\exp(a)}\), approximately 0.669762. The correct mixture is [2(1-p), 2p], approximately [0.660477, 1.339523]. Omitting the scale changes p to \(\frac{\exp(1)}{1+\exp(1)}\), approximately 0.731059, while a causal prefix test can still pass. Thus nonuniform prefix agreement checks an information boundary but is not an independent numerical oracle for every score operation.

A backward trace separates the roles of Q, K and V. If upstream derivatives are \(G=\frac{\partial L}{\partial Y}\), then \(\frac{\partial L}{\partial V}=P^{\mathsf T}G\) and \(\frac{\partial L}{\partial P}=GV^{\mathsf T}\). For one softmax row p with incoming derivative u, the score derivative is p elementwise-multiplied by (u-sum(p*u)). This subtracts the probability-weighted mean because changing one score changes every normalized weight in that row. Then \(\frac{\partial L}{\partial Q}=\frac{(\partial L/\partial S_{\mathrm{score}})K}{\sqrt{d_k}}\), and \(\frac{\partial L}{\partial K}=\frac{(\partial L/\partial S_{\mathrm{score}})^{\mathsf T}Q}{\sqrt{d_k}}\). Shapes must match the corresponding inputs. At \(Q=K=0\), both query/key derivative paths can evaluate to zero even though the output still depends on V; that is another reason to use a nonuniform diagnostic.

Boolean mask meaning belongs to the parameter, not the word PyTorch:

| API parameter | Boolean True means | Typical role |
| --- | --- | --- |
| functional SDPA attn_mask | position participates | allowed query-key relation |
| nn.MultiheadAttention attn_mask | position is forbidden | blocked query-key relation |
| nn.MultiheadAttention key_padding_mask | key is ignored | padding keys per batch |
| paired manual TensorFlow where-mask | score is retained | allowed query-key relation |

The functional and module contracts are documented separately. [PyTorch 2.9 SDPA](https://docs.pytorch.org/docs/2.9/generated/torch.nn.functional.scaled_dot_product_attention.html), [PyTorch 2.9 MultiheadAttention](https://docs.pytorch.org/docs/2.9/generated/torch.nn.MultiheadAttention.html). Inverting polarity does not by itself translate shape: a square query-key mask and a batch-by-key padding mask are different objects. Ignoring padded keys also does not automatically remove padded query outputs from a later loss.

A float mask is an additive score bias, not a Boolean mask stored as 0.0 and 1.0 values. Adding one to an allowed score and zero to a forbidden score leaves the latter eligible for softmax. For a hard exclusion convention, the additive representation uses zero for allowed entries and negative infinity for excluded entries. The helper rejects rows with no legal key before calling the kernel so the lesson does not depend on backend-specific all-masked output behavior.

Causality also depends on position alignment. In the square shifted-target fixture, query i may attend to input positions j<=i because its target is the next token. If the target token itself was fed at the same input position without shifting, the diagonal would leak the answer even though the mask looks causal. With a cached prefix and one new query, query position is an offset into the full key history; a freshly constructed 1-by-S upper-left triangle is not automatically the desired cached-decoding mask. State the absolute position relation first.

Prefix invariance should recompute the shorter input, not slice a full attention matrix that already used future data. It is still only a test of the components exercised. Upstream bidirectional features, position-mixing normalization, target construction or contaminated retrieval can leak future information before a correct attention mask sees it. A full decoder needs a corresponding end-to-end boundary test.

Functional SDPA applies dropout according to `dropout_p`, including when an enclosing module is in evaluation mode. The unchanged helper passes 0 explicitly. A training wrapper must derive the argument from its mode deliberately. This CPU arithmetic fixture does not qualify a fused accelerator backend, memory scaling or generation quality; it establishes the stated finite values and mask behavior.

## Exercise 1: Mix new values causally

The question is: Use zero 3-by-2 queries and keys with values [4, 0], [0, 4], [1, 1] and a causal allowed mask.

Equal scores make each row the mean of its allowed values.

```python
zq = torch.zeros((3, 2), dtype=torch.float64)
vv = torch.tensor([[4.0, 0.0], [0.0, 4.0], [1.0, 1.0]], dtype=torch.float64)
causal = torch.ones((3, 3), dtype=torch.bool).tril()
torch.testing.assert_close(
    attention(zq, zq, vv, causal),
    torch.tensor([[4.0, 0.0], [2.0, 2.0], [5 / 3, 5 / 3]], dtype=torch.float64),
    atol=1e-12,
    rtol=0,
)
```

**Expected:** outputs [4, 0], [2, 2] and [5/3, 5/3].

**Verify:** In a fresh process, the exercise checks confirm `attention(zq, zq, vv, causal)` matches `torch.tensor([[4.0, 0.0], [2.0, 2.0], [5 / 3, 5 / 3]], dtype=torch.float64)` within 1e-12.

## Exercise 2: Predict a bidirectional change

The question is: Allow every position (an all-True mask) and change only the third value to [10, 10].

The mask, not the attention formula, decides whether later positions can influence earlier outputs.

```python
full_mask = torch.ones((3, 3), dtype=torch.bool)
moved = vv.clone()
moved[2] = torch.tensor([10.0, 10.0])
torch.testing.assert_close(
    attention(zq, zq, moved, full_mask),
    torch.full((3, 2), 14 / 3, dtype=torch.float64),
    atol=1e-12,
    rtol=0,
)
```

**Expected:** every row becomes [14/3, 14/3]; without a causal mask the change reaches all rows.

**Verify:** In a fresh process, the exercise checks confirm `attention(zq, zq, moved, full_mask)` matches `torch.full((3, 2), 14 / 3, dtype=torch.float64)` within 1e-12.

## Exercise 3: Compute one nonuniform weight

The question is: Use queries, keys and values equal to the 2-by-2 identity with a causal mask.

Row 1 compares scores 0 and \(1/\sqrt{2}\); a two-way softmax of a score difference is a sigmoid.

```python
qk = torch.eye(2, dtype=torch.float64)
weight = 1 / (1 + np.exp(-1 / np.sqrt(2)))
result = attention(qk, qk, qk, torch.ones((2, 2), dtype=torch.bool).tril())
torch.testing.assert_close(
    result,
    torch.tensor([[1.0, 0.0], [1 - weight, weight]], dtype=torch.float64),
    atol=1e-12,
    rtol=0,
)
```

**Expected:** row 0 is [1, 0]; row 1 is [1-p, p] with \(p=\sigma(1/\sqrt{2})\), about 0.6698.

**Verify:** In a fresh process, the exercise checks confirm `result` matches `torch.tensor([[1.0, 0.0], [1 - weight, weight]], dtype=torch.float64)` within 1e-12.

## Exercise 4: Reject an all-masked row

The question is: Set the second allowed row to False.

Different kernels may return zero for fully masked rows, but this course contract rejects a query with no legal probability support. The policy is explicit and portable.

```python
empty = allowed.clone()
empty[1] = False
try:
    attention(q, q, v, empty)
except ValueError:
    pass
else:
    raise AssertionError("undefined row accepted")
```

**Expected:** ValueError before the attention call.

**Verify:** In a fresh process, the exercise checks confirm `attention(q, q, v, empty)` raises `ValueError`.

## Exercise 5: Translate mask polarity explicitly

The question is: Invert the allowed matrix to obtain a forbidden mask for APIs using True as blocked.

Do not pass this inverted mask to functional SDPA under its boolean allowed convention. The translation depends on the exact API parameter.

```python
forbidden = ~allowed
assert forbidden[0].tolist() == [False, True, True]
```

**Expected:** first forbidden row False, True, True.

**Verify:** In a fresh process, the exercise checks confirm `forbidden[0].tolist() == [False, True, True]`.

## Exercise 6: Keep inference dropout disabled

The question is: Repeat functional attention with `dropout_p=0` and compare exact outputs.

The helper fixes `dropout_p=0`, so its behavior is independent of the mode of any surrounding module. A training wrapper must pass its chosen probability explicitly.

```python
again = attention(q, q, v, allowed)
torch.testing.assert_close(again, out, atol=0, rtol=0)
```

**Expected:** repeated evaluation matches.

**Verify:** In a fresh process, the exercise checks confirm `again` matches `out` exactly.

## Review after comparison

Repeat exercise 4, Reject an all-masked row, with one changed fixture value and predict the difference before running it. Keep your failing attempt at exercise 5, Translate mask polarity explicitly, beside the repaired result. A missing framework is not a failing assertion. These solutions use only local fixtures.
