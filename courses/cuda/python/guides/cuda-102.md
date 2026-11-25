# cuda-102: LLM inference, KV caches and precision

**Route:** CUDA Python and machine learning. **Stage:** advanced. **Prerequisites:** `cuda-095`, `cuda-100`.

Pacing, evidence labels and platform rules: [CUDA study guide](../../STUDY-GUIDE.md).

## Learning objectives

- Derive cache bytes.
- Double the sequence.
- Distinguish query and KV heads.
- Compare cached logits.
- Separate prefill and decode timing.
- Label fake versus real quantization.

## Mechanism and vocabulary

Autoregressive generation separates prefill, which processes an input sequence, from decode, which adds one token repeatedly. A key-value cache stores previous attention projections so decode can reuse them. Cache size grows with layers, batch, sequence length, key/value head count, head dimension and element width. Grouped-query architectures require the actual KV-head count, not necessarily the query-head count.

Weight quantization changes one memory category; it does not automatically quantize the cache or every activation. Educational rounding examples demonstrate error but do not establish packed low-bit execution. Compare cached and uncached logits at each step, bound generation length, and measure prefill and token latency separately. State positional-encoding and mask conventions when testing cache equivalence.

## Derive a cache budget before serving requests

For a dense key/value cache with \(L\) layers, batch \(B\), stored positions \(T\), KV heads \(H_{kv}\), head width \(d_h\), and element width \(s\) bytes:

\[
\text{cache bytes}=2LBTH_{kv}d_hs.
\]

The factor two accounts for keys and values. This is the tensor payload, not allocator padding, fragmentation, page tables, temporary buffers or scheduler state. A paged cache changes allocation management but does not make its underlying values free. Grouped-query attention can use fewer KV heads than query heads, so inspect the model rather than assuming both counts match.

During prefill, many query positions are processed together. During decode, each new query reads the growing history, often producing a very different arithmetic-intensity pattern. Report time to first token and subsequent token latency separately, and state whether tokenization, sampling and output transfer are included. A throughput gain from batching may increase a single user's queueing delay.

Cache correctness requires position and mask consistency. Compare uncached and cached logits at every step for a small deterministic model, with dropout disabled and the same input prefix. Test batch members with different valid lengths and an explicit maximum generation length. If quantization is introduced, compare output quality and numerical error independently. A fake-quantization rounding exercise remains an educational approximation until a real packed low-bit backend executes and its memory/performance are measured.


### Key terms

- **Prefill:** The phase that processes the whole prompt in parallel and fills the KV cache.
- **Decode:** The token-by-token generation phase, usually limited by memory bandwidth.
- **KV cache:** Stored key and value tensors for earlier tokens, growing with layers, KV heads, head size and sequence length.
- **Grouped-query attention:** Sharing each key and value head across several query heads to shrink the KV cache.
- **Fake quantization:** Rounding values to a low-precision grid while keeping float storage, which models accuracy but not memory savings.

## Worked examples

### Worked example 1

For 2 layers, batch 1, sequence 16, 4 KV heads, head dimension 8 and 2-byte elements, keys and values consume 4096 bytes in the simple dense model.

### Worked example 2

Doubling sequence length doubles this cache payload even if model weights are unchanged. Reducing weight precision alone leaves this term unchanged.

## How to run the CPU model

Edit the copy; the [reference](../references/cuda-102_cpu.py) adds assertions.

```sh
python courses/cuda/python/lessons/cuda-102_cpu.py
```

```python
layers, batch, seq, heads, dim, width = 2, 1, 16, 4, 8, 2
cache = 2 * layers * batch * seq * heads * dim * width
assert cache == 4096
assert 2 * layers * batch * (2 * seq) * heads * dim * width == 8192
print("CPU KV-cache ledger:", cache, "bytes")
```

**Expected observation:** 4096 bytes, doubling to 8192 at twice the sequence length.

**Variable trace.** Before running the model, predict these final values; then compare:

| Variable | Final value |
|---|---|
| `layers` | `2` |
| `batch` | `1` |
| `seq` | `16` |
| `heads` | `4` |
| `dim` | `8` |
| `width` | `2` |

## Equal framework lanes

### PyTorch

Keep cache tensors' batch, sequence, head and dtype contracts explicit. Compare cached token logits with uncached computation under inference mode and the same positional encoding.

### TensorFlow

Represent cache state with explicit tensors or model inputs/outputs and preserve graph signatures across accepted lengths. Compare each cached step with the uncached reference before export.

Lane rules: [framework labs](../../STUDY-GUIDE.md#python-gpu-and-framework-labs).

## Practice and transfer

Record each attempt in the [worksheet](../lessons/cuda-102.md) before opening hints.

### Exercise 1: Derive cache bytes

**Trap to avoid:** Leaving out the factor two for keys and values gives 2048 bytes and underestimates the cache by half.

### Exercise 2: Double the sequence

**Trap to avoid:** Lowering weight precision to reduce memory does nothing for this term, since the cache precision is set separately.

### Exercise 3: Distinguish query and KV heads

**Trap to avoid:** Assuming KV heads equal attention heads for every model gives a 4 times overestimate here.

### Exercise 4: Compare cached logits

**Trap to avoid:** Comparing only the final generated text hides small differences that alter sampling later. A wrong position offset in the cache can produce plausible text for many tokens before the output visibly drifts.

### Exercise 5: Separate prefill and decode timing

**Trap to avoid:** Reporting a single tokens-per-second number mixes two regimes. A long prompt with short output looks very different from a short prompt with long output under one combined number.

### Exercise 6: Label fake versus real quantization

**Trap to avoid:** Reporting speed or memory gains from a simulation claims benefits only a deployed kernel can show. Memory can even rise under simulation, because both the original float weights and rounding scales may be held.

## Progressive hints

Hint *k* belongs to exercise *k*; open one at a time.

1. Multiply 2 for keys and values by layers, batch, sequence, KV heads, head dimension and bytes per element.
2. Change only the sequence length and recompute.
3. Look up the model's key-value head count instead of assuming it equals the query head count.
4. Generate a few tokens with and without the cache and compare logits at every step.
5. Time prefill over the prompt separately from each decode step.
6. Ask whether rounding values in Python shows that a packed low-bit kernel ran.

## Common mistakes and self-check

A common mistake is estimating KV cache size with the query head count. Grouped-query models store fewer key-value heads, so the estimate is too large. Another mistake is assuming weight quantization also shrinks the cache. It does not: doubling sequence length doubles the cache even when weights are smaller. Fix both by using the model's actual KV layout, accounting for weights and cache separately and testing cached against uncached logits over bounded steps.

**Evidence limit:** The reference computes 4096 cache bytes, doubling to 8192, in a dense model. Real caches may use paging, padding or other layouts, and Python rounding does not demonstrate quantized execution, so serving memory must be measured on the deployed stack.

1. How do prefill and decode differ?
2. Which factors grow the KV cache?
3. Why state positional-encoding and mask conventions when testing cache equivalence?

Answers: [self-check answers](../solutions/cuda-102_solutions.md#self-check-answers).

## Primary references

- [PyTorch CUDA semantics](https://docs.pytorch.org/docs/2.9/notes/cuda.html)
- [TensorFlow GPU guide](https://www.tensorflow.org/guide/gpu)

Full lists: [documentation and sources](../../STUDY-GUIDE.md#documentation-and-sources).

## Ask an AI tutor about this lesson

```text
Use the checked-in $guide-ds60sqlpy-learning skill for cuda-102: LLM inference, KV caches and precision.
Read courses/cuda/python/guides/cuda-102.md and courses/cuda/python/lessons/cuda-102.md.
Start with my current attempt and the two worked examples, and ask which backend actually ran.
Give one progressive hint at a time. Keep the separate solution closed and do not mark
progress unless I request it. Treat synthetic timings and CPU models as model evidence,
not as GPU or cluster measurements.
```
