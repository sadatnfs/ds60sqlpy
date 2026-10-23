# llm-025: explanatory solutions

Compare these answers only after an attempt or an explicit solution reveal. They use the same literal inputs as the guide, so a discrepancy can be localized to a specific step. The executable companion runs the assertions; the explanation states why those assertions test the subject. Passing a reference function is rehearsal, and should be followed by a new input chosen without looking at the answer.

## Mechanism review

Memory estimates begin with tensor shapes and dtype sizes. An attention score matrix has a query and key axis, so its element count grows quadratically with context length. A key/value cache stores one key and one value per past position per layer, so its raw storage grows linearly with context when model width stays fixed. Heads split the width but do not multiply total width unless a different architecture explicitly does so. These counts omit parameters, activations, gradients, allocator overhead and temporary kernels. A small arithmetic estimate is useful for planning, but it is not a measured peak-memory receipt or a guarantee that a runtime fits.

**Quadratic growth:** Doubling a dimension multiplies a quantity by four.

**KV bytes:** Raw storage of keys and values under declared shapes and dtype.

**Peak memory:** Maximum observed runtime memory, including more than raw tensor sizes.

## Reading the implementation

For batch B, heads H, sequence length T, head width d and s bytes per element, scores contain B*H*T*T elements. Full multi-head K/V storage contains 2*L*B*H*T*d*s bytes across L layers. Model width is D=H*d; using D in place of d would count the heads twice. Convert bytes to KiB by dividing by 1024, not 1000. Change one dimension at a time to expose scaling.

## Exercise 1: Count attention scores

The question is: Use batch1,heads2 and contexts16,32.

Both the query and key axes double, producing four times as many scores. The number of heads remains fixed.

```python
b,h=1,2; counts=[b*h*t*t for t in [16,32]]
assert counts==[512,2048]
```

**Expected:** 512 and2048 score elements.

**Verify:** Compare the computed values or written argument with 512 and2048 score elements.

## Exercise 2: Count raw cache bytes

The question is: Use1 layer,2 heads,width per head16,float32 bytes4 and contexts16,32.

The factor two counts keys and values. Each past position adds a fixed number of features, so doubling context doubles this raw storage.

```python
cache=[2*1*1*2*t*16*4 for t in [16,32]]
assert cache==[4096,8192]
```

**Expected:** 4096 and8192 bytes.

**Verify:** Compare the computed values or written argument with 4096 and8192 bytes.

## Exercise 3: Compare element precision

The question is: Calculate cache bytes at context32 using2-byte versus4-byte elements.

A storage reduction does not establish an acceptable accuracy change. Precision policy requires separate numerical evaluation.

```python
assert 2*1*1*2*32*16*2==4096
assert 2*1*1*2*32*16*4==8192
```

**Expected:** 4096 versus8192 bytes.

**Verify:** Compare the computed values or written argument with 4096 versus8192 bytes.

## Exercise 4: Scale batch size

The question is: Increase batch from1 to3 with context32 and all other cache dimensions fixed.

Independent requests each need their own context state unless a documented sharing mechanism applies. Batching improves utilization in some systems but does not eliminate storage per request.

```python
assert 2*1*3*2*32*16*4==24576
```

**Expected:** 24576 raw cache bytes.

**Verify:** Compare the computed values or written argument with 24576 raw cache bytes.

## Exercise 5: Preserve total width

The question is: Compare4 heads of width8 with2 heads of width16.

Head count and head width must be considered together. Multiplying by model width and by head count would double-count features.

```python
assert 2*4*32*8*4==2*2*32*16*4
```

**Expected:** equal raw cache bytes for the same context.

**Verify:** Compare the computed values or written argument with equal raw cache bytes for the same context.

## Exercise 6: State exclusions

The question is: Produce an estimate record naming omitted allocations and avoid calling it peak memory.

An honest estimate is still useful. It helps explain scaling while making clear that a real runtime measurement is needed before selecting resource limits.

```python
estimate={'raw_kv_bytes':8192,'excludes':['parameters','temporary tensors','allocator overhead'],'measured_peak':False}
assert len(estimate['excludes'])==3 and not estimate['measured_peak']
```

**Expected:** record identifies parameters,temporary tensors,allocator overhead as excluded.

**Verify:** Compare the computed values or written argument with record identifies parameters,temporary tensors,allocator overhead as excluded.

## Review after comparison

Repeat one case with a changed fixture and explain the difference before running it. Keep the original failure case as well as the repaired result. Record a missing framework separately from a failing assertion. No solution downloads data, calls an online model, deploys a service or changes a database.
