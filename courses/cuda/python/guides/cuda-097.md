# cuda-097: A Python API over a CUDA C++ operator

**Route:** CUDA Python and machine learning. **Stage:** advanced. **Prerequisites:** `cuda-011`, `cuda-013`, `cuda-017`, `cuda-082`, `cuda-084`, `cuda-087`.

Pacing, evidence labels and platform rules: [CUDA study guide](../../STUDY-GUIDE.md).

## Learning objectives

- Write the operator schema.
- Derive output values.
- Specify aliasing.
- Reject unsupported layout.
- Compare framework registration mechanisms.
- Define fixed-project build evidence.

## Mechanism and vocabulary

A framework operator is more than a callable function. Its contract includes name, argument and return types, dtype, shape, device, layout, aliasing and mutation. Dispatch chooses an implementation for the backend; compilation systems may also need metadata behavior that predicts output structure without running real data. A host wrapper must validate unsupported cases before handing pointers to a kernel.

PyTorch custom operator registration and TensorFlow REGISTER_OP/OpKernel follow different integration mechanisms and require independently prepared builds. Neither is implied by a Python pad accepting a source string. Use a fixed reviewed project with pinned compiler, toolkit and framework ABI. First compare a fused affine-plus-ReLU forward against the native expression, then verify invalid inputs and non-default stream behavior. Backward is a separate contract taught next.

## What a framework operator must promise

Start with a schema in words: the input is a contiguous float32 tensor on one declared device; scale and bias are finite host scalars; output has the same shape and dtype; output is newly allocated; empty input produces an empty output. Every clause becomes a validation or implementation obligation. If the accepted contract later includes noncontiguous tensors, the kernel must consume strides or the wrapper must explicitly pack data and expose the cost.

The CUDA entrypoint receives raw addresses and scalar values. It cannot infer a Python object's meaning from those bytes. The host wrapper validates metadata, allocates output through the framework's allocator, chooses the current execution stream correctly and submits a bounded launch. Submission errors can be immediate, while illegal device accesses may appear only at a later synchronization point. Preserve the first meaningful error instead of blaming whichever later call happened to synchronize.

PyTorch integration needs a registered operator and appropriate backend implementation, with metadata or fake-tensor behavior when the chosen compilation path requires it. TensorFlow integration defines the op and shape behavior and supplies a kernel implementation for its device placement system. These are separate projects with different build and registration contracts. One working C++ function does not qualify both.

The practical acceptance matrix includes normal data, zero elements, a nonmultiple tail, rejected dtype, rejected layout, wrong-device input, stream ordering and output aliasing. The custom operator should match a native framework expression before performance is considered. A classroom single-file Python pad can inspect or call a prepared operation; it cannot safely infer arbitrary build commands, download compilers or manufacture a multi-file extension project from lesson metadata.


### Key terms

- **Operator schema:** The declared name, argument and return types, and aliasing behavior of a framework operator.
- **Dispatch:** The framework mechanism that selects an operator implementation for the input's backend, such as CPU or CUDA.
- **Meta implementation:** A shape-only implementation that predicts output dtype, shape and device without real data, used by compilation systems.
- **Mutation annotation:** Schema markings that declare which inputs an operator modifies in place or aliases in its output.

## Worked examples

### Worked example 1

For \(y=\max(0,2x+1)\), inputs [-2,0,3] yield [0,1,7]. A custom kernel must match the chosen dtype and define behavior at the activation boundary.

### Worked example 2

A raw pointer kernel may return correct values for contiguous tensors but fail on a transposed view. Either implement strides or reject/pack the input explicitly and report copy cost.

## How to run the CPU model

Edit the copy; the [reference](../references/cuda-097_cpu.py) adds assertions.

```sh
python courses/cuda/python/lessons/cuda-097_cpu.py
```

```python
def fused_reference(values, scale=2.0, bias=1.0):
    return [max(0.0, scale * x + bias) for x in values]


assert fused_reference([-2, 0, 3]) == [0, 1, 7]
assert fused_reference([]) == []
print("CPU custom-op oracle:", fused_reference([-2, 0, 3]))
```

**Expected observation:** Fused affine-ReLU output [0,1,7].

## Equal framework lanes

### PyTorch

Use a prepared custom-operator project with a registered schema, dispatch implementation, metadata behavior where needed, and explicit mutation/alias contracts. Python-level callable success is insufficient.

### TensorFlow

Use a separately prepared TensorFlow custom-op project defining the op schema, shape behavior and device OpKernel. Match the framework build ABI and test placement and unsupported inputs independently.

Lane rules: [framework labs](../../STUDY-GUIDE.md#python-gpu-and-framework-labs).

## Practice and transfer

Record each attempt in the [worksheet](../lessons/cuda-097.md) before opening hints.

### Exercise 1: Write the operator schema

**Trap to avoid:** Leaving the schema implicit in a Python wrapper lets callers pass float64 or integers, which the C++ kernel then reinterprets.

### Exercise 2: Derive output values

**Trap to avoid:** Clamping before the affine step, `2*max(0, x) + 1`, gives `[1, 1, 7]`, a different function.

### Exercise 3: Specify aliasing

**Trap to avoid:** Writing the output into `x` without declaring it breaks autograd when `x` was saved for backward.

### Exercise 4: Reject unsupported layout

**Trap to avoid:** Assuming every tensor reaching the operator is contiguous because the tests used fresh tensors misses views created by slicing or transposing.

### Exercise 5: Compare framework registration mechanisms

**Trap to avoid:** Assuming a PyTorch extension can be loaded directly in TensorFlow treats a framework binding as a generic library. The library loads only if the framework finds a registered op, which it will not.

### Exercise 6: Define fixed-project build evidence

**Trap to avoid:** Recording only that the build succeeded omits whether the kernel ran on a real device. A build can succeed on a machine with no GPU at all, so the record proves compilation only.

## Progressive hints

Hint *k* belongs to exercise *k*; open one at a time.

1. List each tensor input, each scalar parameter and the output, with dtype, shape and device for every one.
2. Compute `2*x + 1` for each input, then replace any negative result with zero.
3. Decide whether the output gets new storage or writes into an input, and say so in the schema.
4. Ask what a raw pointer kernel reads when it receives a transposed view, and where the wrapper should catch that.
5. Ask whether registering the operator in one framework makes it callable from the other.
6. List what a reviewer needs to reproduce the build and to trust that the forward pass matches.

## Common mistakes and self-check

A common mistake is treating a working kernel as a finished operator. The kernel may return `[0, 1, 7]` for a contiguous tensor yet silently read wrong values from a transposed view, a different dtype or another device. Fix it by writing the full schema first, including aliasing and mutation, validating dtype, device and layout in the host wrapper before launch, and either implementing strides or packing the input deliberately and reporting the copy cost.

**Evidence limit:** The reference computes the fused affine-ReLU values `[0, 1, 7]` in Python. It builds no extension, so registration, dispatch, ABI compatibility and non-default stream behavior need a fixed, prepared project with a pinned toolkit and framework.

1. What belongs in an operator contract besides argument types?
2. Why can a Python pad accepting a source string not stand in for a registered operator?
3. Why is backward treated as a separate contract?

Answers: [self-check answers](../solutions/cuda-097_solutions.md#self-check-answers).

## Primary references

- [PyTorch CUDA semantics](https://docs.pytorch.org/docs/2.9/notes/cuda.html)
- [TensorFlow GPU guide](https://www.tensorflow.org/guide/gpu)

Full lists: [documentation and sources](../../STUDY-GUIDE.md#documentation-and-sources).

## Ask an AI tutor about this lesson

```text
Use the checked-in $guide-ds60sqlpy-learning skill for cuda-097: A Python API over a CUDA C++ operator.
Read courses/cuda/python/guides/cuda-097.md and courses/cuda/python/lessons/cuda-097.md.
Start with my current attempt and the two worked examples, and ask which backend actually ran.
Give one progressive hint at a time. Keep the separate solution closed and do not mark
progress unless I request it. Treat synthetic timings and CPU models as model evidence,
not as GPU or cluster measurements.
```
