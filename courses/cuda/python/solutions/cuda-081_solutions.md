# cuda-081: explained solutions

These answers explain the six practice tasks. CPU reference programs are mathematical or semantic checks, not proof of CUDA execution.

## Exercise 1: Distinguish copy and alias

An alias shares storage.

**Approach.** Contrast `alias = owner` with `copied = list(owner)`. After `alias[0] = 9`, `owner` is `[9, 2, 3]` while `copied` stays `[1, 2, 3]`.

**Why it is correct here.** Assignment binds a second name to the same list object, so a mutation through either name is visible through both. `list(owner)` allocates new storage with the same values.

**A plausible wrong approach.** Assuming any transfer between libraries copies data leads to surprises when a zero-copy exchange like DLPack shares storage and a later in-place edit changes both arrays.

**How to verify.** Run the reference: both assertions pass. For device arrays, compare data pointers; equal pointers mean an alias.

## Exercise 2: Trace owner lifetime

Keep the producer owner alive under the API contract.

**Approach.** Trace lifetime: when a consumer receives a view of a producer's buffer, the producer object must stay alive, or ownership must transfer under the exchange protocol's rules, until the consumer is finished.

**Why it is correct here.** If the producer's last reference disappears, its memory pool may reuse the bytes while the consumer still reads them. The consumer's view does not keep memory alive unless the protocol says so.

**A plausible wrong approach.** Deleting the original tensor right after the exchange to save memory assumes the consumer holds a copy.

**How to verify.** Keep a reference to the producer until the consumer's work completes. A test can delete the producer, allocate new data and check whether the consumer view changed.

## Exercise 3: Describe metadata requirements

Include dtype shape strides device and offset.

**Approach.** List the metadata a consumer needs to read a shared buffer: data pointer, byte offset, dtype, shape, strides and device identity.

**Why it is correct here.** The bytes have no meaning without metadata. The same 24 bytes can be three float64 values or six float32 values, and strides decide whether a 2 by 3 view is row-major or transposed.

**A plausible wrong approach.** Passing only the pointer and the shape forces the consumer to guess dtype and layout.

**How to verify.** Exchange a transposed 2 by 3 array and check the consumer's strides and values match the producer's.

## Exercise 4: Explain missing autograd edges

Storage protocols do not universally preserve graph semantics.

**Approach.** State that sharing storage with another library through a protocol such as DLPack does not carry the originating autograd graph, so gradients do not flow back through the exchange.

**Why it is correct here.** Storage protocols describe memory, not the operation history PyTorch records. The consumer sees plain data, and operations it performs are invisible to the producer's autograd.

**A plausible wrong approach.** Assuming a forward result that matches means gradients are also correct conflates two different checks.

**How to verify.** Run a forward comparison and a separate gradient check. A missing gradient shows up as `None` or zeros where nonzero values were expected.

## Exercise 5: Name stream readiness evidence

Record the producer event or negotiated stream.

**Approach.** Name the evidence that a shared buffer is ready: the producer's recorded CUDA event, or a stream negotiated in the exchange, for example the `stream` argument of `__dlpack__`.

**Why it is correct here.** Producer writes may still be queued when the exchange happens. The consumer must order its reads after the producer's work, which requires an event or a stream agreement.

**A plausible wrong approach.** Relying on the host call having returned treats Python completion as device completion.

**How to verify.** Record which event or stream was used. A test with a slow producer kernel should still show correct values in the consumer.

## Exercise 6: Design mutation tests

Change one view and inspect the other without unsafe concurrent writes.

**Approach.** Design mutation tests: change one element through the consumer view, synchronize, then read the producer to see whether the change is visible, avoiding concurrent writes from both sides.

**Why it is correct here.** Visibility after a sequential mutation determines whether the exchange produced an alias or a copy. Sequencing avoids a data race that would make the result undefined.

**A plausible wrong approach.** Writing from both libraries at once to see what happens produces a race whose outcome proves nothing.

**How to verify.** Record whether the mutation was visible and compare with the documented behavior of the exchange.

## Reference observation

Alias changes to 9 while copied value remains 1.

The reference file is `courses/cuda/python/references/cuda-081_cpu.py`. It includes deterministic assertions. These assertions establish the supplied bounded CPU example; hardware execution and architecture-specific performance remain separate checks.
