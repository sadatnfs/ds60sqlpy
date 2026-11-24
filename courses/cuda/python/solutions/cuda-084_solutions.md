# cuda-084: explained solutions

These answers explain the six practice tasks. CPU reference programs are mathematical or semantic checks, not proof of CUDA execution.

## Exercise 1: Derive expected affine output

Apply the formula elementwise.

**Approach.** Apply `y = 2*x + 1` to `[-1, 0, 3]`: `2*(-1)+1 = -1`, `2*0+1 = 1`, `2*3+1 = 7`, so the expected output is `[-1, 1, 7]`.

**Why it is correct here.** The kernel is elementwise and the inputs are small integers representable exactly in `float32`, so the device result should match the oracle exactly.

**A plausible wrong approach.** Comparing against `2*(x+1)` by mistake gives `[0, 2, 8]` and suggests the kernel is wrong when the oracle is.

**How to verify.** The reference asserts `affine([-1, 0, 3]) == [-1, 1, 7]`. Compare the CuPy result with `numpy.array_equal` after converting to host.

## Exercise 2: Calculate a nonmultiple launch

Ceiling division gives three blocks.

**Approach.** Compute the launch for 257 elements with 128 threads per block: `(257 + 127) // 128 = 3` blocks, which provide 384 lanes.

**Why it is correct here.** Two blocks give 256 lanes, one short. The third block covers index 256 plus 127 lanes beyond the data, and the guard `if (i < n)` inside the raw kernel source must skip them.

**A plausible wrong approach.** Using `257 // 128 = 2` blocks loses the final element silently, a bug invisible on sizes like 256.

**How to verify.** The reference asserts the block count is 3. A device test with 257 elements must show the last output equals `2*x[256] + 1`.

## Exercise 3: Explain symbol lookup

The compiled exported name must match.

**Approach.** Explain that `cupy.RawKernel(code, name)` compiles the source and then looks up the function by `name`, so the name must match the exported symbol, which usually means declaring the kernel `extern "C"`.

**Why it is correct here.** C++ compilers mangle function names to encode argument types. Without `extern "C"`, the exported symbol differs from the plain name and the lookup fails.

**A plausible wrong approach.** Assuming a lookup error means the source failed to compile misdirects debugging to the kernel body.

**How to verify.** Compile once with `extern "C"` and once without, and observe that only the first lookup by plain name succeeds.

## Exercise 4: Reject noncontiguous input or support strides

State one layout contract explicitly.

**Approach.** Decide the layout contract: either require C-contiguous input, checking `x.flags.c_contiguous` and raising otherwise, or pass strides to the kernel and index with them.

**Why it is correct here.** The raw kernel indexes `x[i]` assuming consecutive elements. A view like `x[::2]` has a larger stride, so the kernel would read the wrong elements.

**A plausible wrong approach.** Silently calling `cupy.ascontiguousarray` inside the wrapper fixes correctness but hides a copy, and with in-place updates it writes to the copy instead of the caller's array.

**How to verify.** Pass `x[::2]` and confirm the wrapper either raises or returns the same result as applying the formula to the strided view.

## Exercise 5: Separate compile timing

Warm the same code before steady-state samples.

**Approach.** Time the first call separately because it includes compilation and module loading. Warm up the same kernel with the same types, then time steady-state launches with synchronization.

**Why it is correct here.** CuPy compiles raw kernels lazily and caches them, so the first call measures compilation. Mixing it into an average distorts steady-state numbers.

**A plausible wrong approach.** Timing a single call and reporting it as kernel speed mostly measures the compiler.

**How to verify.** Record first-call and steady-state times separately. Timing without synchronization should be avoided, since it only measures the enqueue.

## Exercise 6: Compare raw and library paths

Compare outputs and complete work under the same tolerance.

**Approach.** Compare the raw kernel with the library expression `2*x + 1` in CuPy using the same input, dtype and tolerance, and time both on completed work.

**Why it is correct here.** The library path may fuse operations or launch one or two kernels. A fair comparison needs identical outputs first, then timings with synchronization.

**A plausible wrong approach.** Comparing a float32 raw kernel against a float64 library expression measures dtype rather than implementation.

**How to verify.** Assert both outputs are equal for the test input, record dtype, size and the timing method, and report the result as measured on a named device.

## Reference observation

Affine result [-1,1,7], with three blocks for 257 elements.

The reference file is `courses/cuda/python/references/cuda-084_cpu.py`. It includes deterministic assertions. These assertions establish the supplied bounded CPU example; hardware execution and architecture-specific performance remain separate checks.
