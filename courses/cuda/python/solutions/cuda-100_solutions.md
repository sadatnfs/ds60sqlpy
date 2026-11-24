# cuda-100: explained solutions

These answers explain the six practice tasks. CPU reference programs are mathematical or semantic checks, not proof of CUDA execution.

## Exercise 1: Compute stable softmax

Subtract the maximum first.

**Approach.** Subtract the row maximum before exponentiating: scores `[1000, 1001]` become `[-1, 0]`, giving `exp` values about `[0.368, 1]` and probabilities about `[0.269, 0.731]`.

**Why it is correct here.** Softmax is unchanged by subtracting a constant from every score, since the factor cancels in the ratio. Shifting by the maximum keeps exponents at or below zero, so nothing overflows.

**A plausible wrong approach.** Exponentiating directly, `math.exp(1000)`, overflows to infinity in float64 and the division produces NaN. In float16 the overflow happens above about 11.

**How to verify.** The reference asserts the weights sum to 1 and that the second weight is larger. Compare with `torch.softmax` on the same scores.

## Exercise 2: Draw a causal mask

Allow key positions no greater than query position.

**Approach.** Build a causal mask where query position `i` may attend to key position `j` only if `j <= i`; for three tokens this is `[[1,0,0],[1,1,0],[1,1,1]]`.

**Why it is correct here.** A causal model must not use future tokens. The lower-triangular pattern allows each token to see itself and earlier tokens. Token 0 sees only itself and gets weight 1.

**A plausible wrong approach.** Using `j < i` excludes the diagonal, leaving row 0 with no allowed positions and producing NaN in softmax.

**How to verify.** The reference asserts the lower-triangular matrix. Apply it to random scores and confirm each row's weights above the diagonal are exactly zero.

## Exercise 3: Count score-matrix bytes

Batch times heads times sequence squared times itemsize.

**Approach.** Count score-matrix bytes as batch times heads times sequence squared times itemsize: batch 2, 8 heads, sequence 1024 in float16 gives `2*8*1024*1024*2 = 33554432` bytes, 32 MiB.

**Why it is correct here.** Naive attention materializes a score for every query and key pair, so memory grows with the square of sequence length. Doubling the sequence quadruples this term.

**A plausible wrong approach.** Estimating attention memory as linear in sequence length misses the quadratic term, which dominates for long sequences.

**How to verify.** Recompute with sequence 2048 and confirm 128 MiB. Fused kernels avoid storing this matrix.

## Exercise 4: Define fully masked behavior

Reject or use documented zero-output behavior.

**Approach.** Define behavior for a fully masked row: either reject inputs where some query has no allowed keys, or document a specific output such as zeros.

**Why it is correct here.** Softmax over a row of negative infinity divides zero by zero and yields NaN. Different kernels may handle this case differently, so the contract must say what is expected.

**A plausible wrong approach.** Leaving it undefined lets NaN appear only with certain padding patterns.

**How to verify.** Construct a batch with one padded sequence that masks every key for some query and assert the documented result.

## Exercise 5: Compare fused and reference gradients

Check masks dtypes and tolerances.

**Approach.** Compare fused attention against a reference implementation for forward outputs and gradients, using identical masks, dtypes and tolerances appropriate for float16 or bfloat16.

**Why it is correct here.** Fused kernels reorder computations and may use different accumulation precision. Agreement must hold within a tolerance chosen for the dtype, for both directions.

**A plausible wrong approach.** Comparing only forward outputs leaves backward bugs undetected, and comparing a float16 fused result to a float32 reference with float32 tolerance reports false failures.

**How to verify.** Use the same random inputs, run backward with the same upstream gradient, and compare with `torch.testing.assert_close` using dtype-specific tolerances.

## Exercise 6: Separate backend selection from API name

Inspect supported runtime evidence rather than guessing.

**Approach.** Separate the API name from the backend: `scaled_dot_product_attention` may dispatch to a flash, memory-efficient or math backend depending on hardware, dtype and mask.

**Why it is correct here.** The same call can run different kernels on different machines, so claims about memory or speed must name the backend actually selected.

**A plausible wrong approach.** Assuming the flash backend ran because the function was called leads to wrong memory estimates when it silently fell back to math.

**How to verify.** Restrict the allowed backends in a test and observe which configurations succeed, or inspect profiler kernel names.

## Reference observation

Stable probabilities sum to 1; lower-triangular causal mask.

The reference file is `courses/cuda/python/references/cuda-100_cpu.py`. It includes deterministic assertions. These assertions establish the supplied bounded CPU example; hardware execution and architecture-specific performance remain separate checks.
