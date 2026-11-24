# cuda-097: A Python API over a CUDA C++ operator

**Route:** CUDA Python and machine learning. **Stage:** advanced. **Prerequisites:** `cuda-011`, `cuda-013`, `cuda-017`, `cuda-082`, `cuda-084`, `cuda-087`. Allow several sessions when the hardware experiment is new; the chapter is not a deadline.

## What you will be able to explain

By the end, you can **write the operator schema**, **reject unsupported layout**, and **define fixed-project build evidence** with evidence. Start with the two worked cases, then use the editable CPU model to make the quantities concrete.

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

## Portable executable model

The **CPU reference model** variant runs this bounded worked example using `python-core`. It uses only the Python standard library, small synthetic values and no network. Its purpose is to expose the arithmetic or contract behind the chapter. The separate reference includes assertions for the stated observations.

```python
def fused_reference(values, scale=2.0, bias=1.0):
    return [max(0.0, scale * x + bias) for x in values]


assert fused_reference([-2, 0, 3]) == [0, 1, 7]
assert fused_reference([]) == []
print("CPU custom-op oracle:", fused_reference([-2, 0, 3]))
```

**Expected observation:** Fused affine-ReLU output [0,1,7].

Treat printed timing values as synthetic whenever the program says model, fixture or trace. They are not measurements of your GPU. Before editing, predict the output; after editing, compare your observation with the exact contract that changed.

## Equal framework lanes

### PyTorch

Use a prepared custom-operator project with a registered schema, dispatch implementation, metadata behavior where needed, and explicit mutation/alias contracts. Python-level callable success is insufficient.

### TensorFlow

Use a separately prepared TensorFlow custom-op project defining the op schema, shape behavior and device OpKernel. Match the framework build ABI and test placement and unsupported inputs independently.

Choose either lane first, then compare the other using identical mathematical inputs. Framework-specific shape, mode and optimizer rules must be checked separately. Both use offline synthetic examples; no model hub or dataset download is triggered.

## Practice and transfer

### Exercise 1: Write the operator schema

**Trap to avoid:** Leaving the schema implicit in a Python wrapper lets callers pass float64 or integers, which the C++ kernel then reinterprets.

Show the intermediate values or the boundary that rules this route out, then record your answer in the worksheet.

### Exercise 2: Derive output values

**Trap to avoid:** Clamping before the affine step, `2*max(0, x) + 1`, gives `[1, 1, 7]`, a different function.

Show the intermediate values or the boundary that rules this route out, then record your answer in the worksheet.

### Exercise 3: Specify aliasing

**Trap to avoid:** Writing the output into `x` without declaring it breaks autograd when `x` was saved for backward.

Show the intermediate values or the boundary that rules this route out, then record your answer in the worksheet.

### Exercise 4: Reject unsupported layout

**Trap to avoid:** Assuming every tensor reaching the operator is contiguous because the tests used fresh tensors misses views created by slicing or transposing.

Show the intermediate values or the boundary that rules this route out, then record your answer in the worksheet.

### Exercise 5: Compare framework registration mechanisms

**Trap to avoid:** Assuming a PyTorch extension can be loaded directly in TensorFlow treats a framework binding as a generic library. The library loads only if the framework finds a registered op, which it will not.

Show the intermediate values or the boundary that rules this route out, then record your answer in the worksheet.

### Exercise 6: Define fixed-project build evidence

**Trap to avoid:** Recording only that the build succeeded omits whether the kernel ran on a real device. A build can succeed on a machine with no GPU at all, so the record proves compilation only.

Show the intermediate values or the boundary that rules this route out, then record your answer in the worksheet.

## Progressive hints

Use one hint at a time. The separate solution explains each answer after you have recorded an attempt.

1. Start from worked example 1 and mark the quantities needed for the task "Write the operator schema".
2. Change one assumption in worked example 2 while preserving the declared contract: derive output values.
3. Trace the CPU program's variables before adding hardware behavior: specify aliasing.
4. Draw producers, consumers and the exact operation boundary for the task "Reject unsupported layout".
5. Separate what the small fixture establishes from what the real runtime must show: compare framework registration mechanisms.
6. Write a counterexample to an overbroad claim before you define fixed-project build evidence.

## Common mistakes and self-review

Confusing a correct tiny example with a general implementation is the central review risk. For this chapter, challenge the assumption in worked example 2, then ask whether your change preserves the mechanism described above. If you change dtype, layout, ordering, batch size or backend, update the acceptance contract rather than silently reusing the old observation. Explain an unexpected result before trying random configuration changes.

Keep a small evidence table with columns **claim**, **input**, **expected observation**, **actual observation** and **limit**. For the first claim use `Write the operator schema`. For the final claim use `Define fixed-project build evidence`. An unperformed GPU or cluster experiment remains pending even when the CPU model is correct.

## Platform and evidence contract

The reading worksheet and CPU reference model work through the ordinary Linux Docker classroom on macOS, Linux and Windows using WSL 2. They do not require an NVIDIA GPU. Their results are labeled CPU models or semantic oracles, not simulated hardware performance.

Real CUDA work needs supported NVIDIA hardware, a compatible host driver and an explicitly prepared GPU runtime. An Apple GPU does not execute CUDA kernels. PyTorch MPS on a supported native Mac, ROCm on supported AMD hardware, or other vendor backends can provide separate accelerator learning routes; they need their own package and operation qualification and are not CUDA evidence. The ordinary Linux Docker classroom does not expose native Mac MPS automatically.

Do not download packages, models or data by opening this lesson. Do not attach an engine socket, ambient cluster credentials or an arbitrary remote endpoint. A CPU pass, imported package, successful compilation, real GPU result and measured performance are distinct observations. Record the actual backend, data shape/dtype, source revision, versions and pending checks. A saved completion marker records learning progress, not hardware certification.

## Primary references

- [PyTorch CUDA semantics](https://docs.pytorch.org/docs/2.9/notes/cuda.html)
- [TensorFlow GPU guide](https://www.tensorflow.org/guide/gpu)

Use the version-matched documentation of your prepared environment. These references describe interfaces and supported boundaries; the chapter's synthetic examples and CPU models are original teaching material.

## Ask an AI tutor about this lesson

```text
Use the checked-in $guide-ds60sqlpy-learning skill for cuda-097: A Python API over a CUDA C++ operator.
Read courses/cuda/python/guides/cuda-097.md and courses/cuda/python/lessons/cuda-097.md.
Start with my current attempt and the two worked examples, and ask which backend actually ran.
Give one progressive hint at a time. Keep the separate solution closed and do not mark
progress unless I request it. Treat synthetic timings and CPU models as model evidence,
not as GPU or cluster measurements.
```
