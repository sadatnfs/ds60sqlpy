# torch-021: explanatory solutions

Compare these answers only after an attempt or an explicit solution reveal. They use the same literal inputs as the guide, so a discrepancy can be localized to a specific step. The executable companion runs the assertions; the explanation states why those assertions test the subject. Passing a reference function is rehearsal, and should be followed by a new input chosen without looking at the answer.

## Mechanism review

A padded sequence contains real positions and artificial storage positions. Embedding lookup takes token IDs to feature vectors, but padding does not become an observation merely because it has a vector. PyTorch Embedding can use padding_idx to prevent gradient updates for that row, but a recurrent network still needs length or mask information to avoid processing padding as real time steps.

pack_padded_sequence lets an RNN or GRU process the valid prefixes and return a final state after the last real position. Without packing, a GRU can continue to update on padding because its biases and recurrent state are still active, even when padding embeddings are zero. Loss averages must also divide by valid target count, not padded width. The lesson uses a literal embedding table and fixed GRU weights so the distinction is observable.

**Padding index:** A vocabulary entry reserved for artificial storage positions.

**Packed sequence:** A representation allowing recurrent layers to skip invalid tail positions.

**Final valid state:** The hidden state after the last real observation.

**Valid-target denominator:** The count of supervised positions included in the loss.

## Reading the implementation

Use Embedding.from_pretrained with padding_idx0 and freeze=False for the known 4 x 2 table. Set batch_first=True on GRU so inputs are(batch, time, features). pack_padded_sequence receives CPU lengths and enforce_sorted=False for this tiny fixture. Compare the packed final state with an unpadded valid-prefix run. For loss, use an explicit boolean valid mask and reject an all-padding denominator.

## Follow lookup, recurrent state and loss participation separately

The embedding table has shape(V, D)=(4, 2). IDs shaped(B, T)=(1, 3) select rows and produce values shaped(B, T, D)=(1, 3, 2). The mask has shape(1, 3), and the length vector has one entry per sequence, shape(1). IDs[2, 3, 0] select[2, 2], [3, -1], [0, 0], while the vocabulary rule marks only the first two positions valid. A genuine token could have a zero vector, so vector magnitude cannot replace that rule.

Example B differentiates the sum of all lookup outputs. Each used nonpadding row receives the sum of upstream vectors for its occurrences. Here rows 2 and 3 each receive[1, 1], unused row 1 receives zero, and padding row 0 receives zero from the lookup backward rule. If ID 2 appeared twice, its dense gradient contribution would be[2, 2]. Token indices themselves are discrete selectors, not floating parameters to differentiate through. [PyTorch 2.9 Embedding](https://docs.pytorch.org/docs/2.9/generated/torch.nn.Embedding.html).

padding_idx controls the embedding operation's gradient contribution. It does not automatically propagate a mask through a GRU, initialize every supplied pretrained padding row to zero, or protect a row from explicit mutation. Optimizer-wide operations such as decay on a nonzero row are a separate state/update question. The worked table deliberately supplies a zero padding row and performs no optimizer step, so its actual evidence is the stated gradient pattern. Keras mask_zero=True instead creates mask metadata for compatible consumers; that is not a mechanical synonym for PyTorch's padding-gradient rule.

With batch_first=True, the un-packed GRU input uses(B, T, D). Its final hidden state still uses(num_layers×directions, B, H), so the one-layer unidirectional fixture returns(1, 1, 2). batch_first does not reorder the hidden-state axes. A bidirectional final-state tensor has two directional entries per layer and cannot be replaced casually by the last padded output row. PackedSequence also carries ordering/length bookkeeping; enforce_sorted=False avoids requiring the caller to sort this tiny batch manually. Lengths describe positive valid prefixes and are supplied on CPU for this interface.

Why does a zero padding vector still change a recurrent state? A recurrent step includes the previous hidden state and biases. For a GRU, write r and z for reset/update gates, n for the candidate, and h_new=(1-z)n+z h_old. Even when \(x=0\), the recurrent affine terms and biases can make r, z, n nontrivial. The padded third step is therefore another computation, not an identity operation.

The fixed parameters make a compact analytic trace possible because both hidden coordinates remain equal. Let h denote either coordinate and let u be the sum of the two input features. With all weights and both bias vectors equal to 0.1, the gates are \(r=z=\operatorname{sigmoid}(0.1u+0.2h+0.2)\), the candidate is \(\tanh\!\bigl(0.1u+0.1+r(0.2h+0.1)\bigr)\), and the next coordinate is \((1-z)n+zh\). Starting at \(h=0\), the inputs have \(u=4\), 2, 0. The first two steps give the valid-prefix state; the third changes it even though \(u=0\). Packing with length 2 omits that third transition, which is why the packed and prefix states match while the full padded run differs.

Example C uses values.detach(). That explicitly disconnects the GRU comparison from the embedding graph whose backward was already exercised in Example B. It still permits gradients with respect to GRU parameters in an ordinary differentiable forward, but this fixture does not call a GRU backward or update them. Do not interpret matching packed/prefix forward states as evidence that an entire embedding-plus-GRU training graph was tested. In a fresh end-to-end training step, use a fresh lookup graph and preserve the intended gradient path instead of detaching it accidentally.

The masked token objective is L=(sum over b, t of m_bt×loss_bt)/(sum over b, t of m_bt). The two valid log 2 terms give numerator 2 log2 and denominator 2, so the mean is log 2. Dividing by padded width 3 gives 2 log2/3 and changes the scale whenever padding is appended. For this mean, the derivative with respect to each valid loss is \(\frac{1}{2}\) and the padding loss derivative is zero. An all-padding batch has no valid denominator and needs an explicit refusal or skip policy.

A per-sequence mean followed by averaging sequences is a different objective when lengths differ. A sequence with one token and one with nine tokens each receive half the weight under that policy, whereas a global token mean assigns one-tenth versus nine-tenths. Decide the statistical unit before implementing accumulation or batching. Keras mask propagation can help layers ignore padding, but it does not remove the need to inspect the objective's actual numerator and denominator.

## Exercise 1: Lookup and mark padding

The question is: Use IDs 2, 3, 0 and a fixed 4 x 2 table with zero padding row.

The mask comes from the vocabulary policy. A real token could have a zero vector, so vector magnitude is not a reliable padding detector.

```python
table=torch.tensor([[0.,0.],[1.,0.],[2.,2.],[3.,-1.]])
embedding=nn.Embedding.from_pretrained(table,freeze=False,padding_idx=0); ids=torch.tensor([[2,3,0]]); values=embedding(ids); mask=ids!=0
assert tuple(values.shape)==(1,3,2) and mask.tolist()==[[True,True,False]]
```

**Expected:** embedding shape 1, 3, 2; mask True, True, False.

**Verify:** Compare the computed values or written argument with embedding shape 1, 3, 2; mask True, True, False.

## Exercise 2: Verify padding-row gradient behavior

The question is: Sum embedding outputs and backpropagate.

padding_idx controls that embedding row's gradient, but does not automatically mask every later operation in the model.

```python
values.sum().backward()
assert torch.count_nonzero(embedding.weight.grad[0]).item()==0
assert torch.count_nonzero(embedding.weight.grad[2:4]).item()>0
```

**Expected:** padding row gradient zero; rows 2 and 3nonzero.

**Verify:** Compare the computed values or written argument with padding row gradient zero; rows 2 and 3nonzero.

## Exercise 3: Compare packed and valid-prefix GRU state

The question is: Use fixed GRU parameters.1 and length 2; compare packed run with the unpadded first two embeddings.

The packed sequence ends after two observations. This direct comparison establishes what the final state means without relying on a padded output index.

```python
gru=nn.GRU(2,2,batch_first=True)
with torch.no_grad():
    for parameter in gru.parameters(): parameter.fill_(.1)
packed=nn.utils.rnn.pack_padded_sequence(values.detach(),torch.tensor([2]),batch_first=True,enforce_sorted=False)
_,packed_state=gru(packed); _,prefix_state=gru(values.detach()[:,:2])
torch.testing.assert_close(packed_state,prefix_state,atol=1e-6,rtol=0)
```

**Expected:** final states match within 1e-6.

**Verify:** Compare the computed values or written argument with final states match within 1e-6.

## Exercise 4: Expose an unmasked recurrent tail

The question is: Run GRU overall three positions including zero embedding padding.

Zero input does not freeze are current state. Biases and hidden-to-hidden operations can continue changing it.

```python
_,padded_state=gru(values.detach())
assert not torch.allclose(padded_state,prefix_state,atol=1e-6,rtol=0)
```

**Expected:** final state differs from the valid-prefix state.

**Verify:** Compare the computed values or written argument with final state differs from the valid-prefix state.

## Exercise 5: Average only valid token losses

The question is: Use losses log 2, log 2, 100with the valid mask.

The valid count is two. Zeroing the third numerator but dividing by three would make padding artificially improve the metric.

```python
losses=torch.tensor([[np.log(2),np.log(2),100.]],dtype=torch.float64)
mean=losses[mask].mean(); np.testing.assert_allclose(mean.item(),np.log(2),atol=1e-12,rtol=0)
```

**Expected:** mean log 2, unchanged by the padding loss.

**Verify:** Compare the computed values or written argument with mean log 2, unchanged by the padding loss.

## Exercise 6: Reject zero-length recurrent input

The question is: Attempt to pack a sequence with length 0.

The application should detect empty records before this low-level call and choose an explicit policy. An undefined target mean must not be converted into perfect loss.

```python
try: nn.utils.rnn.pack_padded_sequence(values.detach(),torch.tensor([0]),batch_first=True,enforce_sorted=False)
except RuntimeError: pass
else: raise AssertionError('zero-length packed sequence accepted')
```

**Expected:** RuntimeError for invalid length.

**Verify:** Compare the computed values or written argument with RuntimeError for invalid length.

## Review after comparison

Repeat one case with a changed fixture and explain the difference before running it. Keep the original failure case as well as the repaired result. Record a missing framework separately from a failing assertion. No solution downloads data, calls an online model, deploys a service or changes a database.
