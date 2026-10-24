from readable_decoder import DECODER_SOURCE


def deepen(spec):
    spec['helper'] = DECODER_SOURCE
    spec['mental'] = '''A causal Transformer decoder turns a batch of token IDs into a next-token score vector at every input position. Its learned parameters are shared across token positions, apart from the explicit position table. The model does not store a separate neural network for every sentence length. Embedding lookup converts discrete identities into vectors; attention combines visible token representations; a feed-forward network transforms each resulting contextual vector; the final projection scores vocabulary choices.

This chapter exposes one pre-normalization decoder block rather than loading a pretrained package. The vocabulary has 16 IDs, the model width is 32, there are two attention heads, the feed-forward hidden width is 64 and the maximum learned position is bounded by a 32-row table. The exact model contains 10,464 trainable scalar parameters. It is small enough to trace every tensor axis and parameter group. Random initialization gives finite structured computations, not language understanding or useful generated text.

Attention and the feed-forward network have different jobs. Attention mixes information across permitted token positions. Each head computes its own query/key similarity distribution and weighted value mixture. The feed-forward block then applies the same nonlinear feature transformation independently at each position. Its input can already contain context from attention, but the feed-forward operation itself does not average or reduce the time axis.

Residual addition preserves a direct path from the input representation while adding the branch computation. In a pre-normalization block, the attention branch reads LayerNorm(x), then its projected output is added to x; the second branch reads a new LayerNorm of that sum. Residuals help provide an identity contribution to the derivative, but they do not guarantee that all gradients remain healthy. A branch Jacobian can still amplify, cancel or poorly condition directions. The later normalization chapter examines these derivatives more carefully.

The acceptance test is an information-flow contract: independently recomputing a prefix must reproduce the corresponding early logits of the full sequence. A future-token perturbation must also leave earlier logits unchanged. These are stronger observations than a plausible tensor shape or a decreasing training loss. They still do not establish that the objective uses correctly shifted targets or that evaluation data is uncontaminated; those are separate chapters.'''
    spec['anatomy'] = '''### Exact parameter ledger

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

Each head has width 32/2=16, so its dot products are divided by sqrt(16)=4. The Boolean triangle [4,4] broadcasts across batch and heads. Softmax reduces the final key axis, not the query axis or the vocabulary axis. The diagonal is allowed because the representation at input position t predicts the following token when training uses correctly shifted targets. The current input is therefore legal information under that objective.

After attention, transpose restores [batch,time,head,head_width]. contiguous makes the requested layout explicit before reshape combines the last two axes into model width. A reshape with the correct number of elements can still scramble token/head membership if the transpose order is wrong. The exact shape ledger and prefix checks are complementary; neither substitutes for the other.'''
    spec['mechanism_notes'] = '''## What the block computes

Write E_token[ids] + E_position[position] as x. The first branch is Attention(LayerNorm1(x)), followed by an output projection W_o. The residual result is h = x + projected_attention. The second branch is Linear2(ReLU(Linear1(LayerNorm2(h)))), and the second residual adds that branch back to h. Finally, a vocabulary projection produces logits. There is no softmax on the vocabulary output inside TinyDecoder because a later cross-entropy objective consumes logits directly; sampling converts them to a probability distribution under an explicit inference policy.

Combined QKV storage is an implementation convenience. The last dimension is split into three width-32 blocks, each with its own learned weights. Splitting into two heads then partitions each projected feature vector, not the token sequence: both heads can inspect every allowed earlier token. At fixed model width, increasing the number of heads changes head width and the attention distributions without multiplying the QKV parameter count by the head count. Assigning a full width-32 vector to each of two heads would be a different parameterization.

The model uses a learned absolute position table. Position 0 and position 1 can add different vectors even when the token IDs are equal. A 33-token request exceeds the 32-row table and is rejected. This explicit range bound is not a claim that formula-based position methods automatically generalize to arbitrary lengths; the later RoPE/ALiBi chapter distinguishes evaluable positions from validated long-context behavior.

## Prefix tests, model mode and gradient recording

The full input [2,5,7,3] produces four vocabulary-score vectors. A separately run prefix [2,5] should reproduce the first two vectors because tokenwise normalization and feed-forward maps do not use future rows, and causal attention masks the remaining key positions. Replacing only the final two tokens with [8,9] tests the same dependency claim from another direction. A test must rerun the entire forward pass; slicing a full computation cannot expose an upstream leak.

Call model.eval() for inference parity checks, but remember that eval does not disable autograd. This particular model has no dropout or batch normalization, so changing its mode does not introduce stochastic masks or running-statistic updates. Using torch.no_grad around parity probes avoids building an unnecessary training graph. The separate cache-inspection task intentionally runs with gradient recording so it can show that logits remain connected while the returned cache is detached.

## What the returned cache does and does not mean

After four tokens, each K or V cache has shape [1,2,4,16], or 128 float32 entries. Both together occupy 1,024 data bytes under this dtype, excluding Python/tensor-object overhead. At the maximum 32-token context, the same arithmetic gives 8,192 data bytes. Cache size depends on batch, heads, time, head width, layer count and element size; it is separate from the 10,464 learned parameters.

The helper returns detached keys and values for later incremental-inference lessons. Training in this chapter always uses cache=None. Reusing detached past state while expecting full-sequence backpropagation would truncate gradient paths and change the training computation. Incremental inference must also preserve position offsets: a new token after four cached tokens uses position 4, not position 0. Later cache lessons test full-sequence versus incremental equivalence and request isolation explicitly.

The [connected decoder walkthrough](../../../docs/learning/inside-a-transformer.md) supplies a separate inspectable numerical example. [Architecture families](llm-043.md), [positions](llm-044.md), [normalization and gated blocks](llm-045.md), and [grouped heads and cache dimensions](llm-046.md) extend the mechanisms without replacing the small model's evidence boundary.
'''
    spec['diagnosis'] = '''If construction fails, check positive dimensions and model-width divisibility by the head count before examining tensor reshapes. If an input fails, distinguish dtype from value range: embedding indices must be integer IDs, and valid IDs are 0 through 15. A float tensor containing 2.0 is not the declared ID representation. An empty time axis has no prediction position and is rejected.

If output shape is wrong, walk the table one transformation at a time. A [batch,heads,time,width] tensor is not interchangeable with [batch,time,heads,width], even when every dimension has the same element count. Inspect the softmax axis and confirm that its sums correspond to allowed keys for each query. A transposed causal mask can preserve square shape while exposing future information.

If prefix parity fails, inspect position offsets, mask direction, normalization axes and any mode-dependent component. Compare a deterministic evaluation pass before diagnosing optimization. If logits require gradients during evaluation, that is normal unless no_grad or inference_mode was used; eval controls module behavior, not gradient recording. If an incremental cache is detached, do not infer that earlier-token training gradients remain connected.

If the parameter count differs from 10,464, inspect bias settings, normalization gain/bias, vocabulary size and position-table length. If the count matches but values are wrong, the count has not validated the forward computation. These are complementary checks. Finally, random logits can satisfy every structural invariant while remaining useless for language tasks. Training and held-out evidence are required before making a capability claim.'''
    spec['terms'] = [('Decoder block', 'Causal token mixing and tokenwise transformations connected by residual additions.'), ('Logits', 'Unnormalized vocabulary scores at every input position.'), ('Head width', 'The feature dimension assigned to each attention head, here 16.'), ('Pre-normalization', 'Applying feature normalization before the residual branch computation.'), ('Context limit', 'The declared position range represented by this model, here 32.'), ('Detached cache', 'Stored K/V tensors disconnected from the prior autograd graph for inference use.')]
    codes = [
'''torch.manual_seed(7)
model = TinyDecoder().eval()
count = sum(parameter.numel() for parameter in model.parameters())
assert count == 10464
assert count < 50000''',
'''torch.manual_seed(7)
model = TinyDecoder().eval()
ids = torch.tensor([[2, 5, 7, 3]], dtype=torch.long)
with torch.no_grad():
    logits, _ = model(ids)
assert tuple(logits.shape) == (1, 4, 16)
assert logits.dtype == torch.float32
assert torch.isfinite(logits).all()''',
'''torch.manual_seed(7)
model = TinyDecoder().eval()
ids = torch.tensor([[2, 5, 7, 3]], dtype=torch.long)
with torch.no_grad():
    full, _ = model(ids)
    for length in range(1, 5):
        prefix, _ = model(ids[:, :length])
        torch.testing.assert_close(prefix, full[:, :length], atol=1e-6, rtol=0)''',
'''torch.manual_seed(7)
model = TinyDecoder().eval()
ids = torch.tensor([[2, 5, 7, 3]], dtype=torch.long)
changed = ids.clone()
changed[:, 2:] = torch.tensor([[8, 9]])
with torch.no_grad():
    original, _ = model(ids)
    perturbed, _ = model(changed)
torch.testing.assert_close(perturbed[:, :2], original[:, :2], atol=1e-6, rtol=0)
assert not torch.equal(ids, changed)''',
'''torch.manual_seed(7)
model = TinyDecoder().eval()
ids = torch.tensor([[2, 5, 7, 3]], dtype=torch.long)
logits, cache = model(ids)
assert logits.requires_grad
for tensor in cache.values():
    assert tuple(tensor.shape) == (1, 2, 4, 16)
    assert tensor.dtype == torch.float32
    assert not tensor.requires_grad
assert sum(tensor.numel() * tensor.element_size() for tensor in cache.values()) == 1024''',
'''model = TinyDecoder().eval()
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
        raise AssertionError('invalid model dimensions were accepted')''',
]
    for exercise, code in zip(spec['exercises'], codes, strict=True):
        exercise['code'] = code
    spec['exercises'][0]['prompt'] = 'Set seed 7, build the default decoder, count every trainable scalar and compare with the component ledger.'
    spec['exercises'][0]['expected'] = 'Exactly 10,464 trainable scalars, below the 50,000 teaching bound.'
    spec['exercises'][1]['prompt'] = 'Run the integer IDs [[2,5,7,3]] and trace the output shape and dtype.'
    spec['exercises'][1]['expected'] = 'Finite float32 logits with shape [1,4,16].'
    spec['exercises'][2]['prompt'] = 'Recompute prefixes of lengths 1 through 4 independently with the same initialized weights.'
    spec['exercises'][2]['expected'] = 'Every prefix matches the corresponding full-sequence early logits within 1e-6.'
    spec['exercises'][3]['prompt'] = 'Replace only positions 2 and 3 with IDs 8 and 9 and compare the first two logits.'
    spec['exercises'][3]['expected'] = 'The first two score vectors remain unchanged within 1e-6.'
    spec['exercises'][4]['prompt'] = 'Run without disabling autograd and inspect the returned K/V cache shapes, detachment and data-byte count.'
    spec['exercises'][4]['expected'] = 'Logits remain connected; each cache is detached float32 [1,2,4,16]; combined cache data occupies 1,024 bytes.'
    spec['exercises'][5]['prompt'] = 'Reject out-of-range IDs, wrong dtype, empty/excessive context and invalid head/width configurations.'
    spec['exercises'][5]['expected'] = 'Every invalid contract raises ValueError before a misleading reshape or embedding computation.'
