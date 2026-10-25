# cuda-081: Sharing a buffer without sharing its meaning

**Route:** CUDA Python and machine learning. **Stage:** intermediate. **Prerequisites:** `cuda-066`, `cuda-070`, `cuda-072`. Allow several sessions when the hardware experiment is new; the chapter is not a deadline.

## What you will be able to explain

By the end, you can **distinguish copy and alias**, **explain missing autograd edges**, and **design mutation tests** with evidence. Start with the two worked cases, then use the editable CPU model to make the quantities concrete.

## Mechanism and vocabulary

Zero-copy interchange shares an allocation rather than creating independent values. Shape, dtype, strides, device, ownership and readiness remain part of the contract. A consumer must not outlive the allocation owner, and mutation through one view can affect another. A copied tensor has different independence from an alias even when both initially display the same numbers.

DLPack provides an interoperability protocol, not automatic gradient connectivity between arbitrary frameworks. Modern object exchange can negotiate stream readiness, while legacy capsule interfaces have their own ownership rules. Follow the pinned producer and consumer APIs. A CuPy-to-PyTorch exchange inside one process is different from separate workers that merely see the same physical GPU. The ordinary classroom cannot pass a live pointer between containers.

## Read a shared-buffer contract line by line

Suppose a producer owns a float32 matrix with shape `(2, 3)` and a consumer receives a view. There are three independent agreements. **Representation** says how six values are encoded and addressed. **Lifetime** says who keeps the allocation alive. **Ordering** says when the writes that initialized those values become visible to the consumer. Correct representation cannot repair an allocation freed too early, and a long-lived allocation cannot repair a missing synchronization edge.

A useful ownership drawing is `producer object -> allocation <- consumer view`. The arrows are lifetime dependencies, not copies. Deleting one Python name only removes one reference; another owner can keep storage alive. Conversely, a raw integer pointer is not necessarily an owner. Before passing a pointer to an asynchronous consumer, retain the appropriate owner through that consumer's completion. Avoid modifying either view concurrently unless the algorithm explicitly defines that sharing.

For modern DLPack object interchange, read the producer's `__dlpack__` and `__dlpack_device__` protocol and the consumer's documented import function. Stream negotiation exists so a consumer can ask for data ready on its execution stream. Legacy capsule interfaces can have different one-consumption ownership rules; do not copy an old capsule recipe into a modern object API without checking it. `copy=False` where supported expresses a copy constraint, not a promise that every other contract is automatically satisfied.

Autograd adds a fourth agreement: the computation graph. Sharing a tensor's storage with another library does not by itself add that library's arithmetic to the first framework's differentiation graph. A forward output may be numerically perfect while the gradient is absent or wrong. The test sequence is therefore storage/value parity, deliberate alias mutation, lifetime safety, non-default stream behavior, and then independent gradient behavior if gradients are part of the objective.


## Worked examples

### Worked example 1

A Python list alias sees a mutation made through the original name. A list copy retains the old value. This CPU analogy makes the ownership question visible before introducing device buffers.

### Worked example 2

A tensor passed to another array library may share bytes but not the originating autograd graph. Compute a numerical forward check and a separate gradient check rather than assuming both survive exchange.

## Portable executable model

The **CPU reference model** variant runs this bounded worked example using `python-core`. It uses only the Python standard library, small synthetic values and no network. Its purpose is to expose the arithmetic or contract behind the chapter. The separate reference includes assertions for the stated observations.

```python
owner = [1, 2, 3]
alias = owner
copied = list(owner)
alias[0] = 9
assert owner == [9, 2, 3]
assert copied == [1, 2, 3]
print("CPU alias reference:", owner, copied)
```

**Expected observation:** Alias changes to 9 while copied value remains 1.

Treat printed timing values as synthetic whenever the program says model, fixture or trace. They are not measurements of your GPU. Before editing, predict the output; after editing, compare your observation with the exact contract that changed.

## Practice and transfer

### Exercise 1: Distinguish copy and alias

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 1 targets **distinguish copy and alias** in the examples above.

### Exercise 2: Trace owner lifetime

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 2 targets **trace owner lifetime** in the examples above.

### Exercise 3: Describe metadata requirements

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 3 targets **describe metadata requirements** in the examples above.

### Exercise 4: Explain missing autograd edges

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 4 targets **explain missing autograd edges** in the examples above.

### Exercise 5: Name stream readiness evidence

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 5 targets **name stream readiness evidence** in the examples above.

### Exercise 6: Design mutation tests

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 6 targets **design mutation tests** in the examples above.

## Progressive hints

Use one hint at a time. The separate solution explains each answer after you have recorded an attempt.

1. Start from worked example 1 and mark the quantities needed for the task "Distinguish copy and alias".
2. Change one assumption in worked example 2 while preserving the declared contract: trace owner lifetime.
3. Trace the CPU program's variables before adding hardware behavior: describe metadata requirements.
4. Draw producers, consumers and the exact operation boundary for the task "Explain missing autograd edges".
5. Separate what the small fixture establishes from what the real runtime must show: name stream readiness evidence.
6. Write a counterexample to an overbroad claim before you design mutation tests.

## Common mistakes and self-review

Confusing a correct tiny example with a general implementation is the central review risk. For this chapter, challenge the assumption in worked example 2, then ask whether your change preserves the mechanism described above. If you change dtype, layout, ordering, batch size or backend, update the acceptance contract rather than silently reusing the old observation. Explain an unexpected result before trying random configuration changes.

Keep a small evidence table with columns **claim**, **input**, **expected observation**, **actual observation** and **limit**. For the first claim use `Distinguish copy and alias`. For the final claim use `Design mutation tests`. An unperformed GPU or cluster experiment remains pending even when the CPU model is correct.

## Platform and evidence contract

The reading worksheet and CPU reference model work through the ordinary Linux Docker classroom on macOS, Linux and Windows using WSL 2. They do not require an NVIDIA GPU. Their results are labeled CPU models or semantic oracles, not simulated hardware performance.

Real CUDA work needs supported NVIDIA hardware, a compatible host driver and an explicitly prepared GPU runtime. An Apple GPU does not execute CUDA kernels. PyTorch MPS on a supported native Mac, ROCm on supported AMD hardware, or other vendor backends can provide separate accelerator learning routes; they need their own package and operation qualification and are not CUDA evidence. The ordinary Linux Docker classroom does not expose native Mac MPS automatically.

Do not download packages, models or data by opening this lesson. Do not attach an engine socket, ambient cluster credentials or an arbitrary remote endpoint. A CPU pass, imported package, successful compilation, real GPU result and measured performance are distinct observations. Record the actual backend, data shape/dtype, source revision, versions and pending checks. A saved completion marker records learning progress, not hardware certification.

## Ask an AI tutor about this lesson

> I am studying `cuda-081` using `courses/cuda/python/guides/cuda-081.md` and `courses/cuda/python/lessons/cuda-081.md`. Help me reason about Sharing a buffer without sharing its meaning. Start with my current attempt and the two worked examples. Ask which backend actually ran, give one progressive hint, and do not reveal the separate solution or mark progress unless I request it.

## Primary references

- [DLPack Python specification](https://dmlc.github.io/dlpack/latest/python_spec.html)
- [CuPy interoperability](https://docs.cupy.dev/en/stable/user_guide/interoperability.html)

Use the version-matched documentation of your prepared environment. These references describe interfaces and supported boundaries; the chapter's synthetic examples and CPU models are original teaching material.
