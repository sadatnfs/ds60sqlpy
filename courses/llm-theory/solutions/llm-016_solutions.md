# llm-016: explanatory solutions

Compare these answers only after an attempt or an explicit solution reveal. They use the same literal inputs as the guide, so a discrepancy can be localized to a specific step. The executable companion runs the assertions; the explanation states why those assertions test the subject. Passing a reference function is rehearsal, and should be followed by a new input chosen without looking at the answer.

## Mechanism review

A small causal decoder makes the transformer data path visible. Token IDs index a learned table, position IDs add order, and a tokenwise normalization feeds query/key/value projections. Two heads attend only to current and earlier positions. Their outputs are rejoined, projected and added through a residual connection. A second tokenwise normalization and feed-forward block produce another residual. The output projection creates one vocabulary score per token position. No pretrained model or downloaded corpus is needed. A parameter count and a context limit bound this teaching model; they do not make it a general-purpose language system.

**Decoder block:** Causal attention and tokenwise transformations with residual connections.

**Logits:** Unnormalized vocabulary scores for each prediction position.

**Context limit:** Maximum number of token positions represented by the model.

## Reading the implementation

The TinyDecoder helper uses width32,heads2,context32,vocabulary16. Its tensor path is(batch,time,width) to(batch,heads,time,head_width), then back. The boolean allowed matrix uses key_position<=query_position, so the diagonal is allowed for shifted targets. LayerNorm reduces features only. forward returns logits plus detached K/V state for later inference lessons; training in this lesson always passes cache=None.

## Exercise 1: Build a bounded decoder

The question is: Set seed7, construct the decoder and count trainable scalar parameters.

The exact count follows the embedding, projection and feed-forward shapes. A small parameter count bounds the fixture but says little about capability on unseen tasks.

```python
torch.manual_seed(7); model=TinyDecoder(); model.eval(); count=sum(p.numel() for p in model.parameters())
assert 0<count<50000
```

**Expected:** parameter count below50000.

**Verify:** Compare the computed values or written argument with parameter count below50000.

## Exercise 2: Trace output axes

The question is: Run input IDs[[2,5,7,3]] and inspect logits.

Every input position produces a distribution over the same sixteen-token vocabulary. The time axis is not a class axis and must not be reduced accidentally.

```python
ids=torch.tensor([[2,5,7,3]],dtype=torch.long); logits,_=model(ids)
assert tuple(logits.shape)==(1,4,16) and torch.isfinite(logits).all()
```

**Expected:** shape(1,4,16), all finite.

**Verify:** Compare the computed values or written argument with shape(1,4,16), all finite.

## Exercise 3: Recompute prefixes

The question is: Run prefix lengths1..4 independently in evaluation mode.

The check covers the whole block, including normalization and positions, rather than only the attention mask. Dropout is absent in this teaching decoder.

```python
with torch.no_grad():
    full,_=model(ids)
    for cut in range(1,5):
        prefix,_=model(ids[:,:cut]); torch.testing.assert_close(prefix,full[:,:cut],atol=1e-6,rtol=0)
```

**Expected:** prefix logits match full early logits within1e-6.

**Verify:** Compare the computed values or written argument with prefix logits match full early logits within1e-6.

## Exercise 4: Perturb only future tokens

The question is: Replace positions2,3 with8,9 and compare the first two outputs.

A future-only perturbation is a direct causal test. It can expose a leaking normalization or incorrect mask even when the model has never been trained.

```python
future=ids.clone(); future[:,2:]=torch.tensor([[8,9]])
a,_=model(ids); b,_=model(future); torch.testing.assert_close(a[:,:2],b[:,:2],atol=1e-6,rtol=0)
```

**Expected:** first two logits unchanged within1e-6.

**Verify:** Compare the computed values or written argument with first two logits unchanged within1e-6.

## Exercise 5: Inspect head shapes

The question is: Read the returned K/V state after four tokens.

Width32 is split into two sixteen-dimensional heads. The cached time dimension grows with processed tokens, while the feature width remains fixed.

```python
_,cache=model(ids)
assert tuple(cache['k'].shape)==tuple(cache['v'].shape)==(1,2,4,16)
```

**Expected:** each cache tensor shape(1,2,4,16).

**Verify:** Compare the computed values or written argument with each cache tensor shape(1,2,4,16).

## Exercise 6: Reject invalid token IDs

The question is: Pass vocabulary ID16 and a33-token context.

A fixed vocabulary and position table impose real bounds. Rejecting invalid requests makes the failure understandable before embedding indexing or an excessive context reaches deeper operations.

```python
for bad in [torch.tensor([[16]]),torch.zeros((1,33),dtype=torch.long)]:
    try: model(bad)
    except ValueError: pass
    else: raise AssertionError('model bound ignored')
```

**Expected:** both raise ValueError.

**Verify:** Compare the computed values or written argument with both raise ValueError.

## Review after comparison

Repeat one case with a changed fixture and explain the difference before running it. Keep the original failure case as well as the repaired result. Record a missing framework separately from a failing assertion. No solution downloads data, calls an online model, deploys a service or changes a database.
