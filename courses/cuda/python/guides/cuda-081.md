# cuda-081: Sharing a buffer without sharing its meaning

**Route:** CUDA Python and machine learning. **Stage:** intermediate. **Prerequisites:** `cuda-066`, `cuda-070`, `cuda-072`.

Pacing, evidence labels and platform rules: [CUDA study guide](../../STUDY-GUIDE.md).

## Learning objectives

- Distinguish copy and alias.
- Trace owner lifetime.
- Describe metadata requirements.
- Explain missing autograd edges.
- Name stream readiness evidence.
- Design mutation tests.

## Mechanism and vocabulary

Zero-copy interchange shares an allocation rather than creating independent values. Shape, dtype, strides, device, ownership and readiness remain part of the contract. A consumer must not outlive the allocation owner, and mutation through one view can affect another. A copied tensor has different independence from an alias even when both initially display the same numbers.

DLPack provides an interoperability protocol, not automatic gradient connectivity between arbitrary frameworks. Modern object exchange can negotiate stream readiness, while legacy capsule interfaces have their own ownership rules. Follow the pinned producer and consumer APIs. A CuPy-to-PyTorch exchange inside one process is different from separate workers that merely see the same physical GPU. The ordinary classroom cannot pass a live pointer between containers.

## Read a shared-buffer contract line by line

Suppose a producer owns a float32 matrix with shape `(2, 3)` and a consumer receives a view. There are three independent agreements. **Representation** says how six values are encoded and addressed. **Lifetime** says who keeps the allocation alive. **Ordering** says when the writes that initialized those values become visible to the consumer. Correct representation cannot repair an allocation freed too early, and a long-lived allocation cannot repair a missing synchronization edge.

A useful ownership drawing is `producer object -> allocation <- consumer view`. The arrows are lifetime dependencies, not copies. Deleting one Python name only removes one reference; another owner can keep storage alive. Conversely, a raw integer pointer is not necessarily an owner. Before passing a pointer to an asynchronous consumer, retain the appropriate owner through that consumer's completion. Avoid modifying either view concurrently unless the algorithm explicitly defines that sharing.

For modern DLPack object interchange, read the producer's `__dlpack__` and `__dlpack_device__` protocol and the consumer's documented import function. Stream negotiation exists so a consumer can ask for data ready on its execution stream. Legacy capsule interfaces can have different one-consumption ownership rules; do not copy an old capsule recipe into a modern object API without checking it. `copy=False` where supported expresses a copy constraint, not a promise that every other contract is automatically satisfied.

Autograd adds a fourth agreement: the computation graph. Sharing a tensor's storage with another library does not by itself add that library's arithmetic to the first framework's differentiation graph. A forward output may be numerically perfect while the gradient is absent or wrong. The test sequence is therefore storage/value parity, deliberate alias mutation, lifetime safety, non-default stream behavior, and then independent gradient behavior if gradients are part of the objective.


### Key terms

- **Zero-copy alias:** A view in another library that shares the same device buffer, so writes through one are visible through the other.
- **Explicit copy:** A new buffer with its own storage, independent of later changes to the original.
- **DLPack:** A tensor exchange protocol that passes a pointer, shape, strides, dtype and device between libraries without copying.
- **Ownership lifetime:** The rule that the original buffer must stay alive while any alias still references it.
- **Autograd boundary:** The point where a tensor leaves the framework's gradient tracking, so operations in another library are not differentiated.

## Worked examples

### Worked example 1

A Python list alias sees a mutation made through the original name. A list copy retains the old value. This CPU analogy makes the ownership question visible before introducing device buffers.

### Worked example 2

A tensor passed to another array library may share bytes but not the originating autograd graph. Compute a numerical forward check and a separate gradient check rather than assuming both survive exchange.

## How to run the CPU model

Edit the copy; the [reference](../references/cuda-081_cpu.py) adds assertions.

```sh
python courses/cuda/python/lessons/cuda-081_cpu.py
```

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

**Variable trace.** Before running the model, predict these final values; then compare:

| Variable | Final value |
|---|---|
| `owner` | `[9, 2, 3]` |
| `alias` | `[9, 2, 3]` |
| `copied` | `[1, 2, 3]` |

## Practice and transfer

Record each attempt in the [worksheet](../lessons/cuda-081.md) before opening hints.

### Exercise 1: Distinguish copy and alias

**Trap to avoid:** Assuming any transfer between libraries copies data leads to surprises when a zero-copy exchange like DLPack shares storage and a later in-place edit changes both arrays.

### Exercise 2: Trace owner lifetime

**Trap to avoid:** Deleting the original tensor right after the exchange to save memory assumes the consumer holds a copy.

### Exercise 3: Describe metadata requirements

**Trap to avoid:** Passing only the pointer and the shape forces the consumer to guess dtype and layout.

### Exercise 4: Explain missing autograd edges

**Trap to avoid:** Assuming a forward result that matches means gradients are also correct conflates two different checks.

### Exercise 5: Name stream readiness evidence

**Trap to avoid:** Relying on the host call having returned treats Python completion as device completion.

### Exercise 6: Design mutation tests

**Trap to avoid:** Writing from both libraries at once to see what happens produces a race whose outcome proves nothing.

## Progressive hints

Hint *k* belongs to exercise *k*; open one at a time.

1. Mutate the original list and check which of the two names reports the new value.
2. Ask what happens to the consumer's view if the producer's owning object is released first.
3. List every field a consumer needs to locate element (i, j) on the correct device.
4. Ask whether passing bytes to another library also passes the record of how they were computed.
5. Ask how the consumer knows the producer's writes have finished before it reads.
6. Change one view while nothing else writes, then inspect the other, and decide which outcome proves aliasing.

## Common mistakes and self-check

A common mistake is assuming DLPack exchange keeps autograd working across frameworks. The protocol shares storage and metadata, not the originating computation graph, so gradients can silently stop at the boundary. Another is letting the producer's owner be freed while the consumer still holds the buffer. Fix both by running a numerical forward check and a separate gradient check after exchange, and by keeping the producer alive according to the pinned API's ownership rules.

**Evidence limit:** The reference uses Python lists to show aliasing, where the alias changes to 9 and the copy stays 1. It does not exchange device buffers, so stream readiness, lifetime rules and autograd behavior across real frameworks remain untested.

1. Why is a zero-copy exchange not the same as two independent values?
2. Does sharing a physical GPU let two separate workers share a buffer?
3. What does the modern exchange interface add over legacy capsules?

Answers: [self-check answers](../solutions/cuda-081_solutions.md#self-check-answers).

## Primary references

- [DLPack Python specification](https://dmlc.github.io/dlpack/latest/python_spec.html)

Full lists: [documentation and sources](../../STUDY-GUIDE.md#documentation-and-sources).

## Ask an AI tutor about this lesson

```text
Use the checked-in $guide-ds60sqlpy-learning skill for cuda-081: Sharing a buffer without sharing its meaning.
Read courses/cuda/python/guides/cuda-081.md and courses/cuda/python/lessons/cuda-081.md.
Start with my current attempt and the two worked examples, and ask which backend actually ran.
Give one progressive hint at a time. Keep the separate solution closed and do not mark
progress unless I request it. Treat synthetic timings and CPU models as model evidence,
not as GPU or cluster measurements.
```
