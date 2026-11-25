# cuda-082: Streams and events across library boundaries

**Route:** CUDA Python and machine learning. **Stage:** intermediate. **Prerequisites:** `cuda-067`, `cuda-071`, `cuda-081`.

Pacing, evidence labels and platform rules: [CUDA study guide](../../STUDY-GUIDE.md).

## Learning objectives

- Draw the dependency graph.
- Locate a missing wait.
- Separate host wait and stream wait.
- Trace storage reuse.
- Design non-default stream test.
- Explain why global synchronization can mask bugs.

## Mechanism and vocabulary

A stream orders its submitted operations, but independent streams do not inherit every dependency you intend. A consumer on stream B must wait for the producer on stream A when it reads the produced buffer. An event records a point in one stream; a wait introduces a dependency without necessarily blocking the host. Synchronizing the entire device is a useful diagnostic but may destroy intended overlap.

Interop complicates the picture because libraries can have different current-stream conventions and allocator lifetimes. A correct pointer is insufficient if its write is still in flight or its storage is recycled before a consumer finishes. Draw the dependency graph first. Then use the documented stream-aware interchange and allocation recording mechanisms of the pinned libraries. Test a non-default stream to expose assumptions hidden by default execution.

## Build the dependency graph before writing the API calls

Consider two batches and two device streams. Stream A copies and transforms batch 0; stream B prepares batch 1. The host can submit both without waiting only when their allocations are distinct or their reuse is ordered. If both write the same staging buffer, the apparent overlap is a race. Double buffering introduces two owners and alternates them, but each buffer must still wait for its previous consumer before reuse.

An event is a marker in an ordered stream. Recording E after the transform means E becomes complete after earlier work in that stream. A wait for E in another stream places later consumer operations after that completion. This is different from waiting on the host: a host wait delays Python submission, while a stream wait can preserve useful overlap elsewhere. The resulting partial order is more precise than placing a device-wide synchronize after every statement.

The host can also accidentally serialize the graph. Calling `.item()`, `.get()` or `.numpy()` on a device result can require it to be ready on the host. Logging every intermediate scalar may insert repeated waits between kernels. This is not inherently wrong, but it changes the benchmark and can remove the overlap the program was supposed to measure. Aggregate bounded diagnostics where the application permits and preserve one explicit final output boundary.

Allocator reuse is the subtle companion to stream ordering. A library may know the allocation was used on its own stream but not that an external consumer still reads it. Use that library's documented external-stream or allocation-recording protocol. Do not solve this by keeping arbitrary global references forever: that trades a race for a memory leak. The acceptance test uses two non-default streams, repeated bounded inputs with distinct values, explicit producer/consumer ordering and a final comparison against the CPU oracle.


### Key terms

- **Stream:** An ordered queue of device work; operations in one stream run in issue order.
- **CUDA event:** A marker recorded in a stream that other streams or the host can wait on.
- **Stream wait:** A device-side dependency that makes one stream wait for an event without blocking the host.
- **Host synchronization:** A CPU wait for device work to finish, which blocks Python and removes overlap.
- **Cross-stream storage reuse:** Reuse of a freed block by the caching allocator while another stream may still use it, which is unsafe unless the block is recorded with that stream.

## Worked examples

### Worked example 1

Upload precedes transform, which precedes download. Independent preprocessing for the next batch may overlap only when it does not overwrite buffers still in use.

### Worked example 2

Producer A writes buffer X and records event E. Consumer B waits for E before reading X. The graph has an explicit edge even if host Python already returned from A.

## How to run the CPU model

Edit the copy; the [reference](../references/cuda-082_cpu.py) adds assertions.

```sh
python courses/cuda/python/lessons/cuda-082_cpu.py
```

```python
edges = [("upload", "transform"), ("transform", "download")]
order = ["upload", "transform", "download"]
positions = {name: i for i, name in enumerate(order)}
assert all(positions[a] < positions[b] for a, b in edges)
bad = ["download", "upload", "transform"]
assert not all(bad.index(a) < bad.index(b) for a, b in edges)
print("CPU dependency model: ordered pipeline accepted; premature download rejected")
```

**Expected observation:** Valid dependency order accepted; premature download rejected.

**Variable trace.** Before running the model, predict these final values; then compare:

| Variable | Final value |
|---|---|
| `edges` | `[('upload', 'transform'), ('transform', 'download')]` |
| `order` | `['upload', 'transform', 'download']` |
| `positions` | `{'upload': 0, 'transform': 1, 'download': 2}` |
| `bad` | `['download', 'upload', 'transform']` |

## Practice and transfer

Record each attempt in the [worksheet](../lessons/cuda-082.md) before opening hints.

### Exercise 1: Draw the dependency graph

**Trap to avoid:** Drawing edges from code order instead of data flow invents dependencies between unrelated work and hides real ones crossing library calls.

### Exercise 2: Locate a missing wait

**Trap to avoid:** Assuming the host Python call to A finishing means A's kernel finished confuses queuing with completion.

### Exercise 3: Separate host wait and stream wait

**Trap to avoid:** Using a host synchronize everywhere fixes correctness but serializes host and device.

### Exercise 4: Trace storage reuse

**Trap to avoid:** Freeing a buffer as soon as the host is done with its Python object assumes device work is done too.

### Exercise 5: Design non-default stream test

**Trap to avoid:** Testing only on the default stream passes even with the wait removed.

### Exercise 6: Explain why global synchronization can mask bugs

**Trap to avoid:** Treating a correct result with global waits as proof that dependencies are complete hides the missing event.

## Progressive hints

Hint *k* belongs to exercise *k*; open one at a time.

1. Draw one node per operation and an edge only where one operation reads what another wrote.
2. Find the read of a buffer whose producer has no recorded event that the consumer waits on.
3. Ask which call stops Python and which only tells the device queue to wait.
4. Follow buffer X after its last consumer is enqueued and ask when the allocator may hand it out again.
5. Use two streams and inputs with known outputs, so a missing wait shows up as a wrong value.
6. Ask which dependency a device-wide synchronization adds that your intended graph never declared.

## Common mistakes and self-check

A frequent mistake is assuming that operations on two streams run in the order they were written in Python. Without an event and a wait, a consumer on stream B may read buffer X before the producer on stream A finishes. Another mistake is adding a device-wide synchronization to make a bug vanish, which hides the missing edge and removes overlap. Fix both by drawing the dependency graph, recording an event after each producer and making each consumer wait on it.

**Evidence limit:** The reference accepts a valid dependency order and rejects a premature download in a sequential model. It cannot reproduce real stream timing, library current-stream conventions or allocator reuse while a kernel is still running.

1. What does an event record?
2. Why is a correct pointer not enough for interop?
3. Why test with a non-default stream?

Answers: [self-check answers](../solutions/cuda-082_solutions.md#self-check-answers).

## Primary references

- [CuPy interoperability](https://docs.cupy.dev/en/stable/user_guide/interoperability.html)

Full lists: [documentation and sources](../../STUDY-GUIDE.md#documentation-and-sources).

## Ask an AI tutor about this lesson

```text
Use the checked-in $guide-ds60sqlpy-learning skill for cuda-082: Streams and events across library boundaries.
Read courses/cuda/python/guides/cuda-082.md and courses/cuda/python/lessons/cuda-082.md.
Start with my current attempt and the two worked examples, and ask which backend actually ran.
Give one progressive hint at a time. Keep the separate solution closed and do not mark
progress unless I request it. Treat synthetic timings and CPU models as model evidence,
not as GPU or cluster measurements.
```
