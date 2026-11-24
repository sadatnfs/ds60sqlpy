# cuda-097: explained solutions

These answers explain the six practice tasks. CPU reference programs are mathematical or semantic checks, not proof of CUDA execution.

## Exercise 1: Write the operator schema

Name tensor inputs scalar parameters and output.

**Approach.** Write the operator schema: one input tensor `x` of float32, scalar parameters `scale` and `bias` as floats, and one output tensor of the same shape and dtype, for example `fused_affine_relu(Tensor x, float scale, float bias) -> Tensor`.

**Why it is correct here.** A schema lets the framework check argument types, dispatch to the right device implementation and reason about aliasing. It also documents the contract the CUDA kernel must satisfy.

**A plausible wrong approach.** Leaving the schema implicit in a Python wrapper lets callers pass float64 or integers, which the C++ kernel then reinterprets.

**How to verify.** Register the schema and confirm the framework rejects a call with a missing or wrong-typed argument before the kernel runs.

## Exercise 2: Derive output values

Apply affine then clamp.

**Approach.** Apply affine then clamp to `[-2, 0, 3]` with scale 2 and bias 1: preactivations `-3, 1, 7`, clamped at zero to `[0, 1, 7]`.

**Why it is correct here.** The fused operator must compute exactly `max(0, 2*x + 1)`. The reference asserts this output and the empty case.

**A plausible wrong approach.** Clamping before the affine step, `2*max(0, x) + 1`, gives `[1, 1, 7]`, a different function.

**How to verify.** Compare the CUDA output to `fused_reference` for these values exactly, since the inputs are exactly representable in float32.

## Exercise 3: Specify aliasing

State whether output shares storage.

**Approach.** State aliasing explicitly: the operator returns a new tensor that does not share storage with `x`, or, for an in-place variant, mark the input as mutated in the schema.

**Why it is correct here.** Frameworks use aliasing annotations to decide whether autograd and compilers can reorder or reuse buffers. A wrong annotation can corrupt saved values.

**A plausible wrong approach.** Writing the output into `x` without declaring it breaks autograd when `x` was saved for backward.

**How to verify.** Check the output's data pointer differs from the input's, and that the input values are unchanged after the call.

## Exercise 4: Reject unsupported layout

Check before launch or use deliberate packing.

**Approach.** Reject non-contiguous inputs before launch with `TORCH_CHECK(x.is_contiguous())`, or call `.contiguous()` deliberately and document the copy cost.

**Why it is correct here.** The raw-pointer kernel assumes consecutive elements. A transposed view has different strides, so reading `ptr[i]` returns the wrong elements.

**A plausible wrong approach.** Assuming every tensor reaching the operator is contiguous because the tests used fresh tensors misses views created by slicing or transposing.

**How to verify.** Call the operator on `x.t()` and confirm it raises or returns the same values as the reference applied to the view.

## Exercise 5: Compare framework registration mechanisms

Each framework needs its own registered implementation.

**Approach.** Compare registration mechanisms: PyTorch registers through `TORCH_LIBRARY` and dispatch keys, while TensorFlow uses `REGISTER_OP` and `REGISTER_KERNEL_BUILDER`, and each framework needs its own implementation registered.

**Why it is correct here.** The CUDA kernel can be shared, but each framework's dispatch, tensor types and memory management differ.

**A plausible wrong approach.** Assuming a PyTorch extension can be loaded directly in TensorFlow treats a framework binding as a generic library. The library loads only if the framework finds a registered op, which it will not.

**How to verify.** Build and call the operator in each framework separately and compare outputs with the shared reference.

## Exercise 6: Define fixed-project build evidence

Record build ABI architecture and real forward tests.

**Approach.** Record build evidence: compiler and CUDA toolkit versions, framework version and its C++ ABI flag, target architectures such as `sm_80`, and results of forward tests on a real device.

**Why it is correct here.** Extensions are tied to the framework build and ABI. A binary built against one version may fail to load against another.

**A plausible wrong approach.** Recording only that the build succeeded omits whether the kernel ran on a real device. A build can succeed on a machine with no GPU at all, so the record proves compilation only.

**How to verify.** Reload the built extension in a clean environment matching the record and rerun the forward tests.

## Reference observation

Fused affine-ReLU output [0,1,7].

The reference file is `courses/cuda/python/references/cuda-097_cpu.py`. It includes deterministic assertions. These assertions establish the supplied bounded CPU example; hardware execution and architecture-specific performance remain separate checks.
