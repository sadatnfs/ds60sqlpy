# torch-021: explanatory solutions

Open these answers only after attempting Embeddings, padded sequences and recurrent models yourself. They reuse the guide's literal inputs, starting from Example A, Lookup and mark padding, so a discrepancy points at one step. The executable companion runs the assertions; this page explains why each one tests Padding index, Packed sequence, Final valid state. After a pass, choose a new input for exercise 6, Reject zero-length recurrent input, without looking.

## Mechanism review

A padded sequence contains real positions and artificial storage positions. Embedding lookup takes token IDs to feature vectors, but padding does not become an observation merely because it has a vector. PyTorch Embedding can use `padding_idx` to prevent gradient updates for that row, but a recurrent network still needs length or mask information to avoid processing padding as real time steps.

pack_padded_sequence lets an RNN or GRU process the valid prefixes and return a final state after the last real position. Without packing, a GRU can continue to update on padding because its biases and recurrent state are still active, even when padding embeddings are zero. Loss averages must also divide by valid target count, not padded width. The lesson uses a literal embedding table and fixed GRU weights so the distinction is observable.

**Padding index:** A vocabulary entry reserved for artificial storage positions.

**Packed sequence:** A representation allowing recurrent layers to skip invalid tail positions.

**Final valid state:** The hidden state after the last real observation.

**Valid-target denominator:** The count of supervised positions included in the loss.

## Reading the implementation

Use Embedding.from_pretrained with `padding_idx`=0 and freeze=False for the known 4-by-2 table. Set batch_first=True on GRU so inputs are (batch, time, features). pack_padded_sequence receives CPU lengths and enforce_sorted=False for this tiny fixture. Compare the packed final state with an unpadded valid-prefix run. For loss, use an explicit boolean valid mask and reject an all-padding denominator.

## Follow lookup, recurrent state and loss participation separately

The embedding table has shape (V, D)=(4, 2). IDs shaped (B, T)=(1, 3) select rows and produce values shaped (B, T, D)=(1, 3, 2). The mask has shape (1, 3), and the length vector has one entry per sequence, shape (1). IDs [2, 3, 0] select [2, 2], [3, -1], [0, 0], while the vocabulary rule marks only the first two positions valid. A genuine token could have a zero vector, so vector magnitude cannot replace that rule.

Example B differentiates the sum of all lookup outputs. Each used nonpadding row receives the sum of upstream vectors for its occurrences. Here rows 2 and 3 each receive [1, 1], unused row 1 receives zero, and padding row 0 receives zero from the lookup backward rule. If ID 2 appeared twice, its dense gradient contribution would be [2, 2]. Token indices themselves are discrete selectors, not floating parameters to differentiate through. [PyTorch 2.9 Embedding](https://docs.pytorch.org/docs/2.9/generated/torch.nn.Embedding.html).

`padding_idx` controls the embedding operation's gradient contribution. It does not automatically propagate a mask through a GRU, initialize every supplied pretrained padding row to zero, or protect a row from explicit mutation. Optimizer-wide operations such as decay on a nonzero row are a separate state/update question. The worked table deliberately supplies a zero padding row and performs no optimizer step, so its actual evidence is the stated gradient pattern. Keras `mask_zero=True` instead creates mask metadata for compatible consumers; that is not a mechanical synonym for PyTorch's padding-gradient rule.

With batch_first=True, the un-packed GRU input uses (B, T, D). Its final hidden state still uses (num_layers×directions, B, H), so the one-layer unidirectional fixture returns (1, 1, 2). batch_first does not reorder the hidden-state axes. A bidirectional final-state tensor has two directional entries per layer and cannot be replaced casually by the last padded output row. PackedSequence also carries ordering/length bookkeeping; enforce_sorted=False avoids requiring the caller to sort this tiny batch manually. Lengths describe positive valid prefixes and are supplied on CPU for this interface.

Why does a zero padding vector still change a recurrent state? A recurrent step includes the previous hidden state and biases. For a GRU, write r and z for reset/update gates, n for the candidate, and \(h_{\mathrm{new}}=(1-z)n+zh_{\mathrm{old}}\). Even when \(x=0\), the recurrent affine terms and biases can make r, z, n nontrivial. The padded third step is therefore another computation, not an identity operation.

The fixed parameters make a compact analytic trace possible because both hidden coordinates remain equal. Let h denote either coordinate and let u be the sum of the two input features. With all weights and both bias vectors equal to 0.1, the gates are \(r=z=\operatorname{sigmoid}(0.1u+0.2h+0.2)\), the candidate is \(\tanh\!\bigl(0.1u+0.1+r(0.2h+0.1)\bigr)\), and the next coordinate is \((1-z)n+zh\). Starting at \(h=0\), the inputs have \(u=4\), 2, 0. The first two steps give the valid-prefix state; the third changes it even though \(u=0\). Packing with length 2 omits that third transition, which is why the packed and prefix states match while the full padded run differs.

Example C uses values.detach(). That explicitly disconnects the GRU comparison from the embedding graph whose backward was already exercised in Example B. It still permits gradients with respect to GRU parameters in an ordinary differentiable forward, but this fixture does not call a GRU backward or update them. Do not interpret matching packed/prefix forward states as evidence that an entire embedding-plus-GRU training graph was tested. In a fresh end-to-end training step, use a fresh lookup graph and preserve the intended gradient path instead of detaching it accidentally.

The masked token objective is L=(sum over b, t of m_bt×loss_bt)/(sum over b, t of m_bt). The two valid log 2 terms give numerator 2 log 2 and denominator 2, so the mean is log 2. Dividing by padded width 3 gives 2 log2/3 and changes the scale whenever padding is appended. For this mean, the derivative with respect to each valid loss is \(\frac{1}{2}\) and the padding loss derivative is zero. An all-padding batch has no valid denominator and needs an explicit refusal or skip policy.

A per-sequence mean followed by averaging sequences is a different objective when lengths differ. A sequence with one token and one with nine tokens each receive half the weight under that policy, whereas a global token mean assigns one-tenth versus nine-tenths. Decide the statistical unit before implementing accumulation or batching. Keras mask propagation can help layers ignore padding, but it does not remove the need to inspect the objective's actual numerator and denominator.

## Exercise 1: Look up a short sequence

The question is: With the same 4-by-2 table and `padding_idx`=0, look up IDs [[1, 0, 0]] and build the validity mask.

The two padding positions read the zero row; only the mask says they are not real tokens.

```python
lookup_table = torch.tensor([[0.0, 0.0], [1.0, 0.0], [2.0, 2.0], [3.0, -1.0]])
lookup = nn.Embedding.from_pretrained(lookup_table, freeze=False, padding_idx=0)
short_ids = torch.tensor([[1, 0, 0]])
short_values = lookup(short_ids)
assert short_values.tolist() == [[[1.0, 0.0], [0.0, 0.0], [0.0, 0.0]]] and (
    short_ids != 0
).tolist() == [[True, False, False]]
```

**Expected:** values [[1, 0], [0, 0], [0, 0]]; mask [[True, False, False]].

**Verify:** In a fresh process, the exercise checks confirm `short_values.tolist() == [[[1.0, 0.0], [0.0, 0.0], [0.0, 0.0]]]` and `(short_ids != 0).tolist() == [[True, False, False]]`.

## Exercise 2: Count gradients for repeated IDs

The question is: Look up IDs [[2, 2, 3]] in that embedding, sum the outputs and backpropagate.

Each occurrence adds a gradient of ones to its row, so a repeated ID accumulates twice.

```python
lookup(torch.tensor([[2, 2, 3]])).sum().backward()
assert lookup.weight.grad.tolist() == [[0.0, 0.0], [0.0, 0.0], [2.0, 2.0], [1.0, 1.0]]
```

**Expected:** row 2 gradient [2, 2]; row 3 [1, 1]; rows 0 and 1 zero.

**Verify:** In a fresh process, the exercise checks confirm `lookup.weight.grad.tolist() == [[0.0, 0.0], [0.0, 0.0], [2.0, 2.0], [1.0, 1.0]]`.

## Exercise 3: Pack a batch with two lengths

The question is: Run a GRU(2, 2) whose parameters are all 0.1 on two padded sequences of lengths 2 and 1, packed, and compare each final state with its unpadded run.

Packing stops the second sequence after its one real step, so its final state ignores the padding row.

```python
rnn = nn.GRU(2, 2, batch_first=True)
with torch.no_grad():
    for weight in rnn.parameters():
        weight.fill_(0.1)
batch = torch.tensor([[[1.0, 0.0], [2.0, 2.0]], [[3.0, -1.0], [0.0, 0.0]]])
packed_batch = nn.utils.rnn.pack_padded_sequence(
    batch, torch.tensor([2, 1]), batch_first=True, enforce_sorted=False
)
_, states = rnn(packed_batch)
_, first = rnn(batch[:1, :2])
_, second = rnn(batch[1:, :1])
torch.testing.assert_close(states[:, 0], first[:, 0], atol=1e-6, rtol=0)
torch.testing.assert_close(states[:, 1], second[:, 0], atol=1e-6, rtol=0)
```

**Expected:** both final states match their unpadded runs within 1e-6.

**Verify:** In a fresh process, the exercise checks confirm `states[:, 0]` matches `first[:, 0]` within 1e-06 and `states[:, 1]` matches `second[:, 0]` within 1e-06.

## Exercise 4: Expose an unmasked recurrent tail

The question is: Run the GRU over all three positions, including the zero padding embedding.

Zero input does not freeze are current state. Biases and hidden-to-hidden operations can continue changing it.

```python
_, padded_state = gru(values.detach())
assert not torch.allclose(padded_state, prefix_state, atol=1e-6, rtol=0)
```

**Expected:** final state differs from the valid-prefix state.

**Verify:** In a fresh process, the exercise checks confirm `not torch.allclose(padded_state, prefix_state, atol=1e-06, rtol=0)`.

## Exercise 5: Average only valid token losses

The question is: Use losses log 2, log 2, 100 with the valid mask.

The valid count is two. Zeroing the third numerator but dividing by three would make padding artificially improve the metric.

```python
losses = torch.tensor([[np.log(2), np.log(2), 100.0]], dtype=torch.float64)
mean = losses[mask].mean()
np.testing.assert_allclose(mean.item(), np.log(2), atol=1e-12, rtol=0)
```

**Expected:** mean log 2, unchanged by the padding loss.

**Verify:** In a fresh process, the exercise checks confirm `mean.item()` matches `np.log(2)` within 1e-12.

## Exercise 6: Reject zero-length recurrent input

The question is: Attempt to pack a sequence with length 0.

The application should detect empty records before this low-level call and choose an explicit policy. An undefined target mean must not be converted into perfect loss.

```python
try:
    nn.utils.rnn.pack_padded_sequence(
        values.detach(), torch.tensor([0]), batch_first=True, enforce_sorted=False
    )
except RuntimeError:
    pass
else:
    raise AssertionError("zero-length packed sequence accepted")
```

**Expected:** RuntimeError for invalid length.

**Verify:** In a fresh process, the exercise checks confirm the invalid call raises `RuntimeError`.

## Review after comparison

Repeat exercise 4, Expose an unmasked recurrent tail, with one changed fixture value and predict the difference before running it. Keep your failing attempt at exercise 5, Average only valid token losses, beside the repaired result. A missing framework is not a failing assertion. These solutions use only local fixtures.
