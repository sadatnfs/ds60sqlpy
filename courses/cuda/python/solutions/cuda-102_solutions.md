# cuda-102: explained solutions

Compare with your [worksheet](../lessons/cuda-102.md) attempt.

## Exercise 1: Derive cache bytes

Multiply two for keys and values then all dimensions and width.

**Approach.** Multiply two, for keys and values, by layers, batch, sequence, KV heads, head dimension and element width: `2*2*1*16*4*8*2 = 4096` bytes.

**Why it is correct here.** Each layer stores one key and one value vector per KV head per position. The product counts every stored element, then multiplies by 2 bytes for float16.

**A plausible wrong approach.** Leaving out the factor two for keys and values gives 2048 bytes and underestimates the cache by half.

**How to verify.** The reference asserts `cache == 4096`. Compare with the sizes of the cache tensors in a framework.

## Exercise 2: Double the sequence

Cache grows linearly in stored positions.

**Approach.** Double the sequence to 32: the cache becomes 8192 bytes, as the reference asserts.

**Why it is correct here.** Cache size is linear in stored positions. Weights are unchanged, so the cache grows into a larger share of memory as context lengthens.

**A plausible wrong approach.** Lowering weight precision to reduce memory does nothing for this term, since the cache precision is set separately.

**How to verify.** Recompute with sequence 64 and confirm 16384 bytes, doubling again.

## Exercise 3: Distinguish query and KV heads

Use the model actual KV layout.

**Approach.** Use the model's actual KV head count, which can be smaller than the query head count in grouped-query attention, such as 4 KV heads shared by 16 query heads.

**Why it is correct here.** Only KV heads are cached. Using the query head count overestimates the cache by the grouping factor.

**A plausible wrong approach.** Assuming KV heads equal attention heads for every model gives a 4 times overestimate here.

**How to verify.** Read `num_key_value_heads` from the model configuration and check the cache tensor shapes. The KV head dimension of the cached key tensor should equal that configured value, not the query head count.

## Exercise 4: Compare cached logits

Compare each bounded step within tolerance.

**Approach.** Compare cached and uncached generation step by step: compute logits for each new token with the cache and by recomputing the full prefix, and compare within tolerance.

**Why it is correct here.** Caching should change cost, not results. A per-step comparison localizes a mismatch to the first step where positions or masks diverge.

**A plausible wrong approach.** Comparing only the final generated text hides small differences that alter sampling later. A wrong position offset in the cache can produce plausible text for many tokens before the output visibly drifts.

**How to verify.** Use greedy decoding for a bounded number of steps and assert each logits vector agrees.

## Exercise 5: Separate prefill and decode timing

They stress different operation shapes.

**Approach.** Separate prefill timing, which processes the whole prompt at once, from decode timing, which generates one token per step using the cache.

**Why it is correct here.** Prefill is large matrix work, while decode is small and often memory-bound, reading the full cache each step.

**A plausible wrong approach.** Reporting a single tokens-per-second number mixes two regimes. A long prompt with short output looks very different from a short prompt with long output under one combined number.

**How to verify.** Report time to first token and per-token decode time separately. Record prompt length and output length beside each number, since both affect the cache read per step.

## Exercise 6: Label fake versus real quantization

A rounding simulation is not a deployed quantized kernel.

**Approach.** Label fake quantization, which rounds values to a lower precision and dequantizes them in float, separately from a real quantized kernel that computes with low-precision integers.

**Why it is correct here.** Fake quantization estimates accuracy effects but does not reduce memory traffic or compute time.

**A plausible wrong approach.** Reporting speed or memory gains from a simulation claims benefits only a deployed kernel can show. Memory can even rise under simulation, because both the original float weights and rounding scales may be held.

**How to verify.** State in each result whether quantization was simulated or executed, and which kernel ran.

## Self-check answers

1. **How do prefill and decode differ?** Prefill processes the whole input sequence at once, while decode adds one token at a time and reuses cached keys and values.

2. **Which factors grow the KV cache?** Layers, batch, sequence length, KV head count, head dimension and element width.

3. **Why state positional-encoding and mask conventions when testing cache equivalence?** Cached and uncached paths must apply the same positions and masks, or matching logits cannot be expected.

## Reference observation

4096 bytes, doubling to 8192 at twice the sequence length.

Asserted by `courses/cuda/python/references/cuda-102_cpu.py`.
