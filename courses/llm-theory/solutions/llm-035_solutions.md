# llm-035: explanatory solutions

Compare these answers only after an attempt or an explicit solution reveal. They use the same literal inputs as the guide, so a discrepancy can be localized to a specific step. The executable companion runs the assertions; the explanation states why those assertions test the subject. Passing a reference function is rehearsal, and should be followed by a new input chosen without looking at the answer.

## Mechanism review

Inference scheduling interleaves work from multiple requests while preserving each request's context and budget. A batch dimension is a storage arrangement, not permission to mix caches. Requests with different prefix lengths have different position offsets, so a simple shared batch cache is insufficient unless padding and masks are handled deliberately. This lesson uses separate caches and round-robin single-token work, then compares each result with independent full-prefix inference. Model, tokenizer and request identities form the cache key. A change to any component invalidates the state even if tensor shapes still match.

**Scheduler:** A policy deciding which request performs the next unit of work.

**Request isolation:** One request cannot inherit another context state.

**Versioned cache key:** Identity binding between cache, model, tokenizer and request.

## Reading the implementation

Maintain a dictionary from(request,model_version,tokenizer_version) to K/V state. For each scheduled token, look up only that request cache and append one position. Track generated or consumed token counts separately per request. Compare concatenated per-request logits to a full-prefix oracle; never compare only aggregate tensor norms, which could hide cross-request swaps.

## Exercise 1: Define unequal requests

The question is: Use requestA tokens2,5,7 andB tokens1,3 with separate cache keys.

Different request lengths require different offsets. A shared cache tensor without per-request bookkeeping would confuse the next position.

```python
torch.manual_seed(7); model=TinyDecoder(); model.eval(); requests={'A':[2,5,7],'B':[1,3]}; keys={r:(r,'model-v1','tokens-v1') for r in requests}
assert len(set(keys.values()))==2 and [len(requests[r]) for r in ['A','B']]==[3,2]
```

**Expected:** lengths3 and2;distinct keys.

**Verify:** Compare the computed values or written argument with lengths3 and2;distinct keys.

## Exercise 2: Interleave bounded work

The question is: ProcessA0,B0,A1,B1,A2 with independent caches.

Each scheduling action advances one request only. The final cache lengths are conservation checks on the work assigned to each request.

```python
caches={}; outputs={r:[] for r in requests}
with torch.no_grad():
    for request,index in [('A',0),('B',0),('A',1),('B',1),('A',2)]:
        key=keys[request]; logits,state=model(torch.tensor([[requests[request][index]]]),caches.get(key)); caches[key]=state; outputs[request].append(logits)
assert caches[keys['A']]['k'].shape[2]==3 and caches[keys['B']]['k'].shape[2]==2
```

**Expected:** cache lengthsA3,B2.

**Verify:** Compare the computed values or written argument with cache lengthsA3,B2.

## Exercise 3: Compare independent inference

The question is: Run each complete request without a cache and compare its concatenated incremental logits.

Per-request equality catches state mixing that might be invisible in aggregate output statistics. The oracle does not reuse scheduler state.

```python
with torch.no_grad():
    for request,tokens in requests.items():
        full,_=model(torch.tensor([tokens])); incremental=torch.cat(outputs[request],dim=1); torch.testing.assert_close(incremental,full,atol=1e-6,rtol=0)
```

**Expected:** both requests match within 1e-6.

**Verify:** Compare the computed values or written argument with both requests match within 1e-6.

## Exercise 4: Invalidate a tokenizer change

The question is: Look upA under tokenizerv2 rather thanv1.

Token IDs can change meaning when tokenization changes. Reusing old vectors merely because the vocabulary size is equal would violate the model input contract.

```python
assert caches.get(('A','model-v1','tokens-v2')) is None
```

**Expected:** no cached state found.

**Verify:** Compare the computed values or written argument with no cached state found.

## Exercise 5: Invalidate a model change

The question is: Look upA under modelv2 with the same tokenizer.

Cached projections depend on the model weights. A new model version requires recomputing state from the request prefix.

```python
assert caches.get(('A','model-v2','tokens-v1')) is None
```

**Expected:** no cached state found.

**Verify:** Compare the computed values or written argument with no cached state found.

## Exercise 6: Respect independent caps

The question is: Set capsA3,B2 and verify scheduled counts; reject one extraB token.

A single global cap could allow one request to exceed its budget while another uses less. Count and enforce limits per request before scheduling additional work.

```python
caps={'A':3,'B':2}; consumed={r:len(outputs[r]) for r in requests}
assert consumed==caps and consumed['B']>=caps['B']
```

**Expected:** A andB at their own caps;B cannot advance.

**Verify:** Compare the computed values or written argument with A andB at their own caps;B cannot advance.

## Review after comparison

Repeat one case with a changed fixture and explain the difference before running it. Keep the original failure case as well as the repaired result. Record a missing framework separately from a failing assertion. No solution downloads data, calls an online model, deploys a service or changes a database.
