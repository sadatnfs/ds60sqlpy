# torch-021: explanatory solutions

Compare these answers only after an attempt or an explicit solution reveal. They use the same literal inputs as the guide, so a discrepancy can be localized to a specific step. The executable companion runs the assertions; the explanation states why those assertions test the subject. Passing a reference function is rehearsal, and should be followed by a new input chosen without looking at the answer.

## Mechanism review

A padded sequence contains real positions and artificial storage positions. Embedding lookup takes token IDs to feature vectors, but padding does not become an observation merely because it has a vector. PyTorch Embedding can use padding_idx to prevent gradient updates for that row, but a recurrent network still needs length or mask information to avoid processing padding as real time steps.

pack_padded_sequence lets an RNN or GRU process the valid prefixes and return a final state after the last real position. Without packing, a GRU can continue to update on padding because its biases and recurrent state are still active, even when padding embeddings are zero. Loss averages must also divide by valid target count, not padded width. The lesson uses a literal embedding table and fixed GRU weights so the distinction is observable.

**Padding index:** A vocabulary entry reserved for artificial storage positions.

**P ac k e d sequence:** A representation allowing recurrent layers to skip invalid tail positions.

**Final valid state:** The hidden state after the last real observation.

**Valid-target denominator:** The count of supervised positions included in the loss.

## Reading the implementation

Use Embedding.from_pretrained with padding_idx0 and freeze=False for the known4x2table. Set batch_first=True on GRU so inputs are(batch, time, features). pack_padded_sequence receives CPU lengths and enforce_sorted=False for this tiny fixture. Compare the packed final state with an unpadded valid-prefix run. For loss, use an explicit boolean valid mask and reject an all-padding denominator.

## Exercise 1: Lookup and mark padding

The question is: Use IDs2, 3, 0 and a fixed4x2table with zero padding row.

The mask comes from the vocabulary policy. A real token could have a zero vector, so vector magnitude is not a reliable padding detector.

```python
table=torch.tensor([[0.,0.],[1.,0.],[2.,2.],[3.,-1.]])
embedding=nn.Embedding.from_pretrained(table,freeze=False,padding_idx=0); ids=torch.tensor([[2,3,0]]); values=embedding(ids); mask=ids!=0
assert tuple(values.shape)==(1,3,2) and mask.tolist()==[[True,True,False]]
```

**Expected:** embedding shape1, 3, 2; mask True, True, False.

**Verify:** Compare the computed values or written argument with embedding shape1, 3, 2; mask True, True, False.

## Exercise 2: Verify padding-row gradient behavior

The question is: Sum embedding outputs and backpropagate.

padding_id x controls that embedding row's gradient, but does not automatically mask every later operation in the model.

```python
values.sum().backward()
assert torch.count_nonzero(embedding.weight.grad[0]).item()==0
assert torch.count_nonzero(embedding.weight.grad[2:4]).item()>0
```

**Expected:** padding row gradient zero; rows2and3nonzero.

**Verify:** Compare the computed values or written argument with padding row gradient zero; rows2and3nonzero.

## Exercise 3: Compare packed and valid-prefix GRU state

The question is: Use fixed GRU parameters.1 and length2; compare packed run with the unpadded first two embeddings.

The packedsequence ends after two observations. This direct comparison establishes what the final state means without relying on a padded output index.

```python
gru=nn.GRU(2,2,batch_first=True)
with torch.no_grad():
    for parameter in gru.parameters(): parameter.fill_(.1)
packed=nn.utils.rnn.pack_padded_sequence(values.detach(),torch.tensor([2]),batch_first=True,enforce_sorted=False)
_,packed_state=gru(packed); _,prefix_state=gru(values.detach()[:,:2])
torch.testing.assert_close(packed_state,prefix_state,atol=1e-6,rtol=0)
```

**Expected:** final states match within1e-6.

**Verify:** Compare the computed values or written argument with final states match within1e-6.

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

The question is: Use losses log2, log2, 100with the valid mask.

The valid count is two. Zeroing the third numerator but dividing by three would make padding artificially improve the metric.

```python
losses=torch.tensor([[np.log(2),np.log(2),100.]],dtype=torch.float64)
mean=losses[mask].mean(); np.testing.assert_allclose(mean.item(),np.log(2),atol=1e-12,rtol=0)
```

**Expected:** mean log2, unchanged by the padding loss.

**Verify:** Compare the computed values or written argument with mean log2, unchanged by the padding loss.

## Exercise 6: Reject zero-length recurrent input

The question is: Attempt to pack a sequence with length0.

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
