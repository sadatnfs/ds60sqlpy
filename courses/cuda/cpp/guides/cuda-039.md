# cuda-039: Streams as dependency-ordered work queues

## Level and prerequisites

Intermediate; about 110 minutes, plus any optional hardware experiment. Direct prerequisites: `cuda-012`, `cuda-028`, `cuda-031`

The order supports learning at your own pace. Reading and CPU reasoning remain
available when NVIDIA hardware is absent. Advanced hardware features need their
own capability checks and are not prerequisites for opening this chapter.

## Learning objectives

Implement two-stream work with explicit event dependencies and annotate the resulting timeline.

Work through *Streams as dependency-ordered work queues* with the concrete cases below. Finish with this evidence:
correct results with explicit dependencies and an annotated timeline. Distinguish an algorithmic
calculation, a compiled artifact and an actual device observation when explaining
what your work establishes.

## Purpose, vocabulary and mental model

A stream is an ordered queue of work. Operations in one stream respect that stream's ordering, while separate streams need explicit dependencies when sharing data. Record an event after a producer and make the consumer stream wait for it before reading the result. Two streams allow concurrency; they do not guarantee simultaneous execution or isolated memory. Default-stream semantics depend on the selected configuration, so educational code should use explicit streams rather than relying on invisible ordering. Buffer lifetimes must cover all queued consumers, and a host completion check is required before validating or releasing their outputs.

### Key terms

- **Stream:** An ordered queue of device work in which operations run in submission order.
- **cudaStreamWaitEvent:** A call that makes later work in one stream wait until an event recorded in another stream completes.
- **Default stream:** The stream used when none is given, which can synchronize with other streams under legacy semantics.
- **Concurrency:** Independent work in different streams that the device may overlap when resources allow, without any guarantee that it will.

## How to run and study this lesson

Use the saved reading worksheet in `/classroom`; the reading pad does not execute
CUDA. For the bounded calculation, select **CPU model (Python)**, whose
answer-free starter supplies the literal fixtures and task contract. The
[CUDA C++ study workflow](../README.md) covers platforms, optional GPU
compilation and evidence labels. In a prepared Python environment you can also
run the separate [CPU reference](../references/cuda-039_cpu.py) from the
repository root:

```sh
python courses/cuda/cpp/references/cuda-039_cpu.py
```

Its assertions check the stated numerical result or model invariant; console
text is evidence of this CPU model only, not of CUDA execution.

## CUDA C++ kernel listing

The kernel below is an excerpt from the chapter's complete [GPU reference](../references/cuda-039_gpu.cu). The full program adds device discovery, checked allocation and launch, completion checks and host validation. Read it as CUDA C++ source; the classroom reading pad does not compile or run it.

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

The complete CPU model below intentionally models only the named arithmetic,
layout, dependency or capability decision. It does not model GPU scheduling,
caches, instruction timing or device memory visibility.

```python
x = [1, 2, 3]
a = [2 * value for value in x]
# CPU sequential phases stand in for an explicit dependency edge.
b = [value + 1 for value in a]
assert b == [3, 5, 7]
edges = [("produce_A", "record_event"), ("record_event", "wait_B"), ("wait_B", "consume_B")]
print({"reference": b, "required_order_edges": edges})
```

**Expected observation:** Every assertion succeeds. A representative CPU output is:

```text
{'reference': [3, 5, 7], 'required_order_edges': [('produce_A', 'record_event'), ('record_event', 'wait_B'), ('wait_B', 'consume_B')]}
```

Integers, shapes and ordering must match exactly; only assertions with an explicit
tolerance accept small floating-point differences. A printed duration is a model
output, not a measured GPU benchmark.

## Worked example 2: change a meaningful condition

Two independent vectors can be transformed in separate streams without a cross-stream dependency if they share no mutable storage. Their outputs remain correct even if hardware serializes them. Correctness must not depend on overlap being observed.

Before applying this example to your own program, write down which inputs are
read, which result is produced, and the condition that makes the comparison
valid. Keep the original case as a regression check when changing a boundary.

## Optional CUDA C++ laboratory

A complete [GPU reference](../references/cuda-039_gpu.cu) and separate
[GPU learner source](../lessons/cuda-039_gpu.cu) accompany this chapter.
They are standalone files with bounded fixtures, checked runtime calls and host
validation. The learner source intentionally reports incomplete implementation
until you add the chapter's algorithm and assertions. It must never return a
fake GPU success on a CPU machine. Follow the [manual GPU workflow](../README.md)
for exact compilation and execution paths. If the classroom offers the optional
CUDA C++ variant, its capability notice must confirm actual runtime readiness.

The reference contains an explicit no-device failure, launch and completion
checks, and returned-value validation. Source review and CPU reference checks do
not qualify this .cu file on your hardware. Preserve compilation, actual device
execution and sanitizer evidence separately. Exercise 4 is a reasoning diagnosis;
do not deliberately launch a hanging kernel or reset a shared GPU to reproduce it.

## Six progressive exercises

Exercises 1 and 2 are guided reconstructions of the worked examples; exercises
3-6 change an input, diagnose a defect, test a boundary and transfer the idea.
For each one, keep the calculation, output, diagram or failure policy you
produce so another reader can compare it with the worked cases. If the hint is
not enough, reread the mechanism paragraph and the bounded CPU assertion.

### Exercise 1

Predict and trace the first worked example before running its CPU reference. Write every intermediate quantity that leads to the stated result, including units or ownership where applicable.

**Hint:** Start with the literal input and intermediate quantities in worked example 1.

### Exercise 2

Reconstruct the second worked example without copying its conclusion. Identify the changed input or condition, show the resulting calculation or dependency, and explain why it differs from the first example.

**Hint:** Identify exactly which condition changes in worked example 2.

### Exercise 3

Draw the event edge for upload in A followed by compute in B.

**Hint:** Use the first worked example to establish the relevant quantities, then change only the requested input.

### Exercise 4

A stream is destroyed while another stream still borrows its buffer. What is the real ownership issue?

**Hint:** Locate the failed phase or violated dependency before proposing a repair.

### Exercise 5

How should an empty chunk affect the queue?

**Hint:** Check what the algorithm is allowed to read, write or assume at this boundary.

### Exercise 6

Transfer the pattern to framework interoperability.

**Hint:** State the output contract and which observations are needed in the new application.

## Common mistakes and diagnosis

A tempting but incorrect claim in this chapter is: **using two streams guarantees simultaneous execution or guarantees isolation between their buffers.**

For the concrete failure exercise, a stream is destroyed while another stream still borrows its buffer. What is the real ownership issue?
Preserve the original input and the stage where behavior diverged, and compare
with the CPU model before changing hardware configuration.

## Self-check, retrieval and transfer

Explain the first example without its code, then use the second example to state
one assumption that matters. Complete Exercise 3 independently, use Exercise 4 to
diagnose a plausible defect, check the boundary in Exercise 5, and retain the
application contract from Exercise 6. Compare the [separate explanations](../solutions/cuda-039_solutions.md)
only after your attempt or a deliberate reveal. A reading marker records your
choice; it does not certify hardware qualification or expert mastery.

## Primary references

Check the documentation that matches your prepared toolkit before optional
hardware execution.

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
