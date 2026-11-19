# llm-025: explanatory solutions

Compare these answers only after an attempt or an explicit solution reveal. They use the same literal inputs as the guide, so a discrepancy can be localized to a specific step. The executable companion runs the assertions; the explanation states why those assertions test the subject. Passing a reference function is rehearsal, and should be followed by a new input chosen without looking at the answer.

## Mechanism review

Memory estimates begin with tensor shapes and dtype sizes. An attention score matrix has a query and key axis, so its element count grows quadratically with context length. A key/value cache stores one key and one value per past position per layer, so its raw storage grows linearly with context when model width stays fixed. Heads split the width but do not multiply total width unless a different architecture explicitly does so. These counts omit parameters, activations, gradients, allocator overhead and temporary kernels. A small arithmetic estimate is useful for planning, but it is not a measured peak-memory receipt or a guarantee that a runtime fits.

**Quadratic growth:** Doubling a dimension multiplies a quantity by four.

**KV bytes:** Raw storage of keys and values under declared shapes and dtype.

**Peak memory:** Maximum observed runtime memory, including more than raw tensor sizes.

## Reading the implementation

For batch B, heads H, sequence length T, head width d and s bytes per element, scores contain \(B\cdot H\cdot T\cdot T\) elements. Full multi-head K/V storage contains \(2\cdot L\cdot B\cdot H\cdot T\cdot d\cdot s\) bytes across L layers. Model width is \(D=H\cdot d\); using D in place of d would count the heads twice. Convert bytes to KiB by dividing by 1024, not 1000. Change one dimension at a time to expose scaling.

## Exercise 1: Count scores for a larger configuration

The question is: Use batch 2, heads 4 and context 64 with 4-byte score elements.

Score elements scale with batch, heads and the square of the context. Doubling the context alone would multiply this count by four.

```python
scores_big = 2 * 4 * 64 * 64
assert scores_big == 32768 and scores_big * 4 == 131072
```

**Expected:** 32768 score elements; 131072 bytes (128 KiB).

**Verify:** In a fresh process, the exercise checks confirm `scores_big == 32768` and `scores_big * 4 == 131072`.

## Exercise 2: Predict cache growth with depth and context

The question is: Use 3 layers, 2 heads, width per head 16, 4-byte elements and contexts 48 and 96; compare with the growth of the score matrix.

The factor 2 counts keys and values. The cache grows linearly with context and with layers, while the per-layer score matrix grows quadratically with context.

```python
cache3 = [2 * 3 * 1 * 2 * t * 16 * 4 for t in [48, 96]]
assert cache3 == [36864, 73728] and cache3[1] == 2 * cache3[0]
assert (1 * 2 * 96 * 96) // (1 * 2 * 48 * 48) == 4
```

**Expected:** 36864 and 73728 cache bytes; the cache doubles while score elements quadruple.

**Verify:** In a fresh process, the exercise checks confirm `cache3 == [36864, 73728]`; `cache3[1] == 2 * cache3[0]` and `1 * 2 * 96 * 96 // (1 * 2 * 48 * 48) == 4`.

## Exercise 3: Compare element precision

The question is: Calculate cache bytes at context 32 using 2-byte versus 4-byte elements.

A storage reduction does not establish an acceptable accuracy change. Precision policy requires separate numerical evaluation.

```python
assert 2 * 1 * 1 * 2 * 32 * 16 * 2 == 4096
assert 2 * 1 * 1 * 2 * 32 * 16 * 4 == 8192
```

**Expected:** 4096 versus 8192 bytes.

**Verify:** In a fresh process, the exercise checks confirm `2 * 1 * 1 * 2 * 32 * 16 * 2 == 4096` and `2 * 1 * 1 * 2 * 32 * 16 * 4 == 8192`.

## Exercise 4: Scale batch size

The question is: Increase batch from 1 to 3 with context 32 and all other cache dimensions fixed.

Independent requests each need their own context state unless a documented sharing mechanism applies. Batching improves utilization in some systems but does not eliminate storage per request.

```python
assert 2 * 1 * 3 * 2 * 32 * 16 * 4 == 24576
```

**Expected:** 24576 raw cache bytes.

**Verify:** In a fresh process, the exercise checks confirm `2 * 1 * 3 * 2 * 32 * 16 * 4 == 24576`.

## Exercise 5: Preserve total width

The question is: Compare 4 heads of width 8 with 2 heads of width 16.

Head count and head width must be considered together. Multiplying by model width and by head count would double-count features.

```python
assert 2 * 4 * 32 * 8 * 4 == 2 * 2 * 32 * 16 * 4
```

**Expected:** equal raw cache bytes for the same context.

**Verify:** In a fresh process, the exercise checks confirm `2 * 4 * 32 * 8 * 4 == 2 * 2 * 32 * 16 * 4`.

## Exercise 6: State exclusions

The question is: Produce an estimate record naming omitted allocations and avoid calling it peak memory.

An honest estimate is still useful. It helps explain scaling while making clear that a real runtime measurement is needed before selecting resource limits.

```python
estimate = {
    "raw_kv_bytes": 8192,
    "excludes": ["parameters", "temporary tensors", "allocator overhead"],
    "measured_peak": False,
}
assert len(estimate["excludes"]) == 3 and not estimate["measured_peak"]
```

**Expected:** record identifies parameters, temporary tensors, allocator overhead as excluded.

**Verify:** In a fresh process, the exercise checks confirm `len(estimate['excludes']) == 3` and `not estimate['measured_peak']`.

## Review after comparison

Repeat one case with a changed fixture and explain the difference before running it. Keep the original failure case as well as the repaired result. Record a missing framework separately from a failing assertion. No solution downloads data, calls an online model, deploys a service or changes a database.
