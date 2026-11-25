# cuda-070: Memory pools, references and apparent leaks

**Route:** CUDA Python and machine learning. **Stage:** beginner. **Prerequisites:** `cuda-068`.

Pacing, evidence labels and platform rules: [CUDA study guide](../../STUDY-GUIDE.md).

## Learning objectives

- Compute live and reserved totals.
- Reuse a free block.
- Diagnose a retained-output list.
- Explain why cache clearing is insufficient.
- Design bounded snapshots.
- Separate host RAM and VRAM.

## Mechanism and vocabulary

A caching allocator distinguishes live allocations from reserved blocks. Releasing the last array reference can make a block reusable by the pool without returning it to the driver. Device-context overhead and library workspaces add further categories. A stable reserved total after repeated equal workloads can be normal. Growing live allocations after every step suggests retained tensors, outputs or computation graphs.

A pool can reduce allocation latency and fragmentation but cannot shrink the set of live tensors required by a model. Clearing unused cache blocks is not a repair for a workload whose live set exceeds memory. Measure at consistent synchronization points, account for delayed asynchronous frees, and avoid intentionally exhausting a shared GPU to demonstrate an OOM. A bounded allocation ledger teaches the same ownership distinction safely.



### Key terms

- **Caching allocator:** A framework memory manager that keeps freed device blocks for reuse instead of returning them to the driver.
- **Allocated memory:** Bytes currently held by live tensors or arrays.
- **Reserved memory:** Bytes the allocator holds from the driver, including cached blocks that no live tensor uses.
- **Retained reference:** A lingering Python name, list entry or graph edge that keeps a tensor alive and prevents its memory from being reused.
- **Cache clearing:** Returning unused cached blocks to the driver, which lowers reserved memory but does not free live tensors.

## Worked examples

### Worked example 1

An allocator reserves 1024 bytes, lends all 1024 to an array, then returns the array to its free list. Live bytes become zero while reserved bytes remain 1024.

### Worked example 2

Appending a fresh 1024-byte result to a Python list each step leaves every result live. After four steps live bytes are 4096; this is different from harmless pool reuse.

## How to run the CPU model

Edit the copy; the [reference](../references/cuda-070_cpu.py) adds assertions.

```sh
python courses/cuda/python/lessons/cuda-070_cpu.py
```

```python
reserved = 1024
live = 1024
live -= 1024
assert live == 0 and reserved == 1024
live += 1024
assert live <= reserved
retained = [1024 for _ in range(4)]
assert sum(retained) == 4096
print("CPU allocator model:", live, reserved, sum(retained))
```

**Expected observation:** Live 1024, reserved 1024, retained-output example 4096 bytes.

**Variable trace.** Before running the model, predict these final values; then compare:

| Variable | Final value |
|---|---|
| `reserved` | `1024` |
| `live` | `1024` |
| `retained` | `[1024, 1024, 1024, 1024]` |

## Practice and transfer

Record each attempt in the [worksheet](../lessons/cuda-070.md) before opening hints.

### Exercise 1: Compute live and reserved totals

**Trap to avoid:** Reading the device memory report and concluding there is a 1024-byte leak confuses reserved with live. The block is free in the pool and will be reused.

### Exercise 2: Reuse a free block

**Trap to avoid:** Expecting reserved to rise to 2048 after the second allocation assumes the pool never reuses blocks. That would make every loop iteration look like growth.

### Exercise 3: Diagnose a retained-output list

**Trap to avoid:** Calling the pool's free-all function every step does not release arrays still referenced by the list. Live bytes stay at 4096 and the clearing just costs time.

### Exercise 4: Explain why cache clearing is insufficient

**Trap to avoid:** Adding `free_all_blocks()` after every step makes the memory report drop slightly while the actual leak continues, giving false confidence.

### Exercise 5: Design bounded snapshots

**Trap to avoid:** Running until the device runs out of memory and reading the error message is unbounded and can disturb other users of a shared device.

### Exercise 6: Separate host RAM and VRAM

**Trap to avoid:** Setting a container memory limit and expecting it to prevent device out-of-memory errors gives no protection. The device can still fill up.

## Progressive hints

Hint *k* belongs to exercise *k*; open one at a time.

1. Follow the ledger step by step: after the array is released, which counter falls and which one stays?
2. Change one assumption in worked example 2 while preserving the declared contract: reuse a free block.
3. Find the Python object that still references each step's result, then decide what the loop actually needs to keep.
4. Ask whether returning the pool's free blocks can release memory that a live array still points to.
5. Fix a small step count and record live and reserved bytes at the same synchronization point before and after each step.
6. Separate the limit on host process memory from the limit on device memory, and check whether a container setting reaches both.

## Common mistakes and self-check

The most common mistake is reading a high reserved total in a device memory report as a leak. A caching pool keeps freed blocks for reuse, so reserved bytes can stay at 1024 while live bytes are zero. The opposite mistake is calling `free_all_blocks()` to fix a real leak: if a list still references every step's output, live bytes keep growing to 4096 and beyond. Diagnose by comparing live and reserved counts at fixed points, then remove the unneeded references.

**Evidence limit:** The allocator ledger is a bounded model with exact byte counts. It does not reproduce context overhead, library workspaces, delayed asynchronous frees or fragmentation, and it deliberately avoids exhausting a shared GPU to show an out-of-memory error.

1. What does a stable reserved total across repeated equal workloads usually mean?
2. Which signal suggests retained tensors, outputs or graphs?
3. Why is clearing the cache not a repair for a workload whose live set exceeds memory?

Answers: [self-check answers](../solutions/cuda-070_solutions.md#self-check-answers).

## Primary references

- [CuPy array and installation documentation](https://docs.cupy.dev/en/v13.6.0/)

Full lists: [documentation and sources](../../STUDY-GUIDE.md#documentation-and-sources).

## Ask an AI tutor about this lesson

```text
Use the checked-in $guide-ds60sqlpy-learning skill for cuda-070: Memory pools, references and apparent leaks.
Read courses/cuda/python/guides/cuda-070.md and courses/cuda/python/lessons/cuda-070.md.
Start with my current attempt and the two worked examples, and ask which backend actually ran.
Give one progressive hint at a time. Keep the separate solution closed and do not mark
progress unless I request it. Treat synthetic timings and CPU models as model evidence,
not as GPU or cluster measurements.
```
