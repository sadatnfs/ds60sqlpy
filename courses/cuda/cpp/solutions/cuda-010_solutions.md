# cuda-010: explanatory solutions

## Mechanism review

RAII connects resource lifetime to an owning C++ object's lifetime. Its constructor establishes an invariant, and its destructor releases the resource. Copying a unique owner is usually forbidden; moving transfers ownership and leaves the source empty. This is important for CUDA allocations, streams and events because a copied raw handle does not represent an independent resource. A destructor should not throw during stack unwinding. Error reporting for explicit completion and release should happen in a deliberate path, while final cleanup remains a last safeguard. Asynchronous use adds a further obligation: do not destroy the owner while a queued operation still borrows the resource.

The separate [CPU reference](../references/cuda-010_cpu.py) checks the chapter's bounded model. It does not execute CUDA or establish GPU timing. Compare after attempting the worksheet or explicitly choosing to reveal solutions.

## Exercise 1

An operation acquires buffer A, then fails to acquire B. If A already belongs to an automatic owner, stack unwinding releases A. The event trace is acquire-A, acquire-B-failed, release-A. If A is only a raw pointer and cleanup exists only at the normal return, the failure path leaks A.

## Exercise 2

Moving owner A into owner B changes who releases the allocation. The moved-from A stores an empty handle; only B releases the original resource. A default copy that leaves two nonempty owners would lead to two releases. Neither a destructor nor a smart-sounding class name alone proves this invariant.

## Exercise 3

Each live nonempty allocation has exactly one owner; borrowers never release it, moves empty the source, and destruction happens after outstanding uses finish.

## Exercise 4

An exception during unwinding can terminate the process. Keep destructor cleanup nonthrowing and report operational failures through an explicit checked path.

## Exercise 5

Nothing. Represent the empty state distinctly so partial initialization and moved-from objects are safe.

## Exercise 6

Record both consumers' completion dependencies before freeing or reusing the buffer. Host scope exit alone does not prove GPU completion.

## Numerical reference and its limits

The complete CPU model is [here](../references/cuda-010_cpu.py). Its assertions check the exact small model shown in the guide, including its explicit tolerance where present. It does not claim CUDA execution, concurrency safety or a performance measurement.

## Transfer review

Record both consumers' completion dependencies before freeing or reusing the buffer. Host scope exit alone does not prove GPU completion.

A complete explanation must name its inputs, the unchanged mathematical contract, the changed boundary or resource condition, and the evidence still needed on actual hardware. Preserve a CPU baseline even after a GPU path becomes available.
