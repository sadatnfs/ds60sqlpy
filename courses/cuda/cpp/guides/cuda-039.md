# cuda-039: Streams as dependency-ordered work queues

## Level and prerequisites

Intermediate; about 110 minutes, plus any optional hardware experiment. Direct prerequisites: `cuda-012`, `cuda-028`, `cuda-031`

Pacing, evidence labels and platform rules for every chapter are in the [CUDA study guide](../../STUDY-GUIDE.md).

## Learning objectives

Implement two-stream work with explicit event dependencies and annotate the resulting timeline.

**Scope:** Ordering within a stream, dependencies across streams, events and host synchronization.

**Evidence to produce:** Correct results with explicit dependencies and an annotated timeline.

## Purpose, vocabulary and mental model

A stream is an ordered queue of work. Operations in one stream respect that stream's ordering, while separate streams need explicit dependencies when sharing data. Record an event after a producer and make the consumer stream wait for it before reading the result. Two streams allow concurrency; they do not guarantee simultaneous execution or isolated memory. Default-stream semantics depend on the selected configuration, so educational code should use explicit streams rather than relying on invisible ordering. Buffer lifetimes must cover all queued consumers, and a host completion check is required before validating or releasing their outputs.

### Key terms

- **Stream:** An ordered queue of device work in which operations run in submission order.
- **cudaStreamWaitEvent:** A call that makes later work in one stream wait until an event recorded in another stream completes.
- **Default stream:** The stream used when none is given, which can synchronize with other streams under legacy semantics.
- **Concurrency:** Independent work in different streams that the device may overlap when resources allow, without any guarantee that it will.

## How to run and study this lesson

Trace worked example 1 by hand, then run the [CPU reference](../references/cuda-039_cpu.py) from the repository root:

```sh
python courses/cuda/cpp/references/cuda-039_cpu.py
```

## CUDA C++ kernel listing

An excerpt from the chapter's complete [GPU reference](../references/cuda-039_gpu.cu); the reading pad does not compile it.

```cpp
__global__ void produce(int *values, std::size_t n) {
  const std::size_t i =
      static_cast<std::size_t>(blockIdx.x) * blockDim.x + threadIdx.x;
  if (i < n)
    values[i] = 2 * static_cast<int>(i);
}

__global__ void consume(int *values, std::size_t n) {
  const std::size_t i =
      static_cast<std::size_t>(blockIdx.x) * blockDim.x + threadIdx.x;
  if (i < n)
    values[i] += 1;
}
```

## Worked example 1: trace the mechanism

Stream A doubles \([1,2,3]\) to \([2,4,6]\), records an event, and stream B waits before adding one, producing \([3,5,7]\). The event creates the producer-consumer edge. Without that edge, B might read old or incomplete data even though both launches individually succeed.

**Why:** The event edge guarantees [2, 4, 6] is complete before B reads it, giving [3, 5, 7].

```python
x = [1, 2, 3]
a = [2 * value for value in x]
# CPU sequential phases stand in for an explicit dependency edge.
b = [value + 1 for value in a]
assert b == [3, 5, 7]
edges = [("produce_A", "record_event"), ("record_event", "wait_B"), ("wait_B", "consume_B")]
print({"reference": b, "required_order_edges": edges})
```

**Expected observation:** every assertion succeeds, and the CPU model prints:

```text
{'reference': [3, 5, 7], 'required_order_edges': [('produce_A', 'record_event'), ('record_event', 'wait_B'), ('wait_B', 'consume_B')]}
```

**Check:** The reference asserts b == [3, 5, 7] and lists the three order edges.

## Worked example 2: change a meaningful condition

Two independent vectors can be transformed in separate streams without a cross-stream dependency if they share no mutable storage. Their outputs remain correct even if hardware serializes them. Correctness must not depend on overlap being observed.

**Why:** With no shared data, any interleaving or serialization gives the same outputs.

**Check:** Compare outputs from separate streams with a single-stream run.

## Optional CUDA C++ laboratory

- [GPU learner source](../lessons/cuda-039_gpu.cu)
- [GPU reference](../references/cuda-039_gpu.cu)

Read the [laboratory rules](../../STUDY-GUIDE.md#optional-native-cuda-laboratories) before compiling.

## Six progressive exercises

### Exercise 1

Reconstruct worked example 1 on paper before running its CPU reference. Record an event in stream A after doubling, and make stream B wait on it before adding one.

**Trap to avoid:** Launching B's kernel after A's on the host assumes ordering that separate streams do not provide.

**Hint:** Start with the literal input and intermediate quantities in worked example 1.

### Exercise 2

Rework worked example 2 without copying its conclusion. Run two independent vectors in separate streams with no shared mutable storage.

**Trap to avoid:** Asserting that the streams must overlap turns a performance hope into a correctness requirement.

**Hint:** Identify exactly which condition changes in worked example 2.

### Exercise 3

Draw the event edge for upload in A followed by compute in B.

**Trap to avoid:** Recording the event before the upload makes the edge order nothing useful.

**Hint:** Use the first worked example to establish the relevant quantities, then change only the requested input.

### Exercise 4

A stream is destroyed while another stream still borrows its buffer. What is the real ownership issue?

**Trap to avoid:** Assuming destroying a stream waits for borrowers frees memory still in use.

**Hint:** Locate the failed phase or violated dependency before proposing a repair.

### Exercise 5

How should an empty chunk affect the queue?

**Trap to avoid:** Recording a done event as if output exists fabricates completion of real data.

**Hint:** Check what the algorithm is allowed to read, write or assume at this boundary.

### Exercise 6

Transfer the pattern to framework interoperability.

**Trap to avoid:** Passing only the pointer lets the consumer read before the producer finishes.

**Hint:** State the output contract and which observations are needed in the new application.

## Common mistakes and diagnosis

A tempting but incorrect claim: **Using two streams guarantees simultaneous execution or guarantees isolation between their buffers.** Streams express permitted concurrency, not a schedule, and the hardware may still run their work one after another. They also share the same device memory, so two streams touching one buffer need an event dependency. Worked example 2 stays correct because its vectors share no mutable storage, not because overlap was observed.

## Self-check, retrieval and transfer

1. In worked example 1, what does stream B wait for?
2. What is guaranteed about two operations in the same stream?
3. Why must correctness not depend on observed overlap?

Short answers are in the [separate explanations](../solutions/cuda-039_solutions.md#self-check-answers); compare only after an attempt.

## Primary references

Use the documentation that matches your prepared toolkit.

- [CUDA Programming Guide](https://docs.nvidia.com/cuda/cuda-programming-guide/)

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for cuda-039: Streams as dependency-ordered work queues.
Read courses/cuda/cpp/guides/cuda-039.md and courses/cuda/cpp/lessons/cuda-039.md.
Direct prerequisites: `cuda-012`, `cuda-028`, `cuda-031`
Review my own explanation and worksheet; give one progressive hint at a time.
Keep courses/cuda/cpp/solutions/cuda-039_solutions.md and GPU references closed until I request comparison.
Treat courses/cuda/cpp/references/cuda-039_cpu.py as CPU model evidence, never a CUDA execution receipt.
Do not install drivers, download packages, run external jobs, reset devices or change my saved work without my instruction.
Ask me to explain the boundary case and which observation would disprove my answer.
```
