# llm-024: explanatory solutions

Compare these answers only after an attempt or an explicit solution reveal. They use the same literal inputs as the guide, so a discrepancy can be localized to a specific step. The executable companion runs the assertions; the explanation states why those assertions test the subject. Passing a reference function is rehearsal, and should be followed by a new input chosen without looking at the answer.

## Mechanism review

A key/value cache stores past attention keys and values so incremental generation can reuse them. The new query must see all prior keys and its own key, while its position embedding uses the accumulated offset. A cache is model- and request-specific state, not a general reusable feature table. Full-prefix inference is the independent oracle: process the same tokens all at once, then compare each position with one-token-at-a-time execution. Reusing a cache from another request changes context even when shapes look compatible. This lesson keeps one small decoder on CPU and explicitly tracks ownership outside its mathematical forward function.

**KV cache:** Stored attention keys and values for prior tokens.

**Position offset:** Number of previously processed positions in an incremental request.

**Cache ownership:** Identity policy preventing state reuse across incompatible requests.

## Reading the implementation

TinyDecoder.forward accepts new IDs and optional past K/V. It concatenates along the time dimension, uses offset=old_time for positions, and constructs allowed keys by comparing absolute positions. Returned cache tensors are detached for inference. An owner wrapper binds cache state to request ID and model version; a mismatch is rejected before the forward call.

## Exercise 1: Compute a full-prefix oracle

The question is: Initialize seed7 decoder and evaluate IDs2,5,7,3 at once.

The reference recomputes the complete context without relying on cached state. It provides a separate path for checking the incremental implementation.

```python
torch.manual_seed(7); model=TinyDecoder(); model.eval(); ids=torch.tensor([[2,5,7,3]])
with torch.no_grad(): full,_=model(ids)
assert tuple(full.shape)==(1,4,16)
```

**Expected:** logits shape(1,4,16).

**Verify:** Compare the computed values or written argument with logits shape(1,4,16).

## Exercise 2: Run one token at a time

The question is: Carry returned K/V through four one-token calls and concatenate logits.

Both key/value history and position offset must be correct. A cache with valid tensor shapes can still produce wrong logits if positions restart at zero.

```python
cache=None; outputs=[]
with torch.no_grad():
    for i in range(4):
        logits,cache=model(ids[:,i:i+1],cache); outputs.append(logits)
incremental=torch.cat(outputs,dim=1)
torch.testing.assert_close(incremental,full,atol=1e-6,rtol=0)
```

**Expected:** incremental logits match full within 1e-6.

**Verify:** Compare the computed values or written argument with incremental logits match full within 1e-6.

## Exercise 3: Inspect cache growth

The question is: Check final cache token count and per-head width.

The time dimension grows with consumed tokens. The head and feature dimensions are fixed by the model and should not grow during a request.

```python
assert tuple(cache['k'].shape)==tuple(cache['v'].shape)==(1,2,4,16)
```

**Expected:** cache shape(1,2,4,16).

**Verify:** Compare the computed values or written argument with cache shape(1,2,4,16).

## Exercise 4: Bind ownership

The question is: Associate the cache with requestA and modelv1; reject requestB.

The numerical decoder cannot infer which person or request owns a tensor. Ownership belongs at the caller boundary and must be tested explicitly.

```python
owned={'request':'A','model':'v1','state':cache}
def acquire(record,request,version):
    if record['request']!=request or record['model']!=version: raise ValueError('foreign cache')
    return record['state']
assert acquire(owned,'A','v1') is cache
try: acquire(owned,'B','v1')
except ValueError: pass
else: raise AssertionError('cross-request cache accepted')
```

**Expected:** ValueError for foreign request.

**Verify:** Compare the computed values or written argument with ValueError for foreign request.

## Exercise 5: Start a fresh request empty

The question is: Run token2 with no cache and compare with the first full-prefix position.

An empty cache resets both context and position offset. Clearing only metadata while retaining tensors would not restore a fresh request.

```python
with torch.no_grad(): fresh,_=model(torch.tensor([[2]]),None)
torch.testing.assert_close(fresh,full[:,:1],atol=1e-6,rtol=0)
```

**Expected:** logits match the original first position.

**Verify:** Compare the computed values or written argument with logits match the original first position.

## Exercise 6: Invalidate after a model change

The question is: Attempt to use the v1-owned cache with versionv2.

Keys and values were computed using specific weights and tokenization. Reusing them after either changes can produce inconsistent inference even if the dimensions remain compatible.

```python
try: acquire(owned,'A','v2')
except ValueError: pass
else: raise AssertionError('stale cache accepted')
```

**Expected:** ValueError for stale version.

**Verify:** Compare the computed values or written argument with ValueError for stale version.

## Review after comparison

Repeat one case with a changed fixture and explain the difference before running it. Keep the original failure case as well as the repaired result. Record a missing framework separately from a failing assertion. No solution downloads data, calls an online model, deploys a service or changes a database.
