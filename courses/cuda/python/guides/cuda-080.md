# cuda-080: A simulator is a debugging tool

**Route:** CUDA Python and machine learning. **Stage:** intermediate. **Prerequisites:** `cuda-073`, `cuda-074`.

Pacing, evidence labels and platform rules: [CUDA study guide](../../STUDY-GUIDE.md).

## Learning objectives

- Classify a CPU result.
- Construct a race hidden by serialization.
- Name an unsupported feature.
- Design the validation ladder.
- Choose a tiny debugging input.
- Write an honest evidence label.

## Mechanism and vocabulary

A simulator reproduces selected semantics to help inspect indexing and values without requiring the actual device. It usually does not reproduce warp scheduling, memory transactions, concurrent timing, occupancy or all synchronization defects. A serialized execution can hide a race that real concurrent threads expose. Passing a simulator therefore belongs to a different evidence category from passing hardware execution.

Keep a validation ladder: mathematical reference, CPU mapping model, compiler acceptance, real-device output, diagnostic tooling and repeated stress cases. The simulator is useful early in that ladder, especially for small inputs you can inspect by hand. Do not generate invented GPU names, bandwidth or throughput from simulator output. If a feature is unsupported by the chosen simulator, state that instead of changing the algorithm silently.



### Key terms

- **CUDA simulator:** An interpreter that runs kernel code on the CPU for debugging, without real GPU timing or memory behavior.
- **Data race:** Unsynchronized accesses to the same address by several threads where at least one access is a write.
- **Serialized execution:** Running threads one at a time, which can hide races that would appear under true parallel execution.
- **Validation ladder:** A sequence of checks from simulator to CPU oracle to real hardware, where each step catches a different class of error.

## Worked examples

### Worked example 1

A CPU loop visiting all valid indices proves the intended index formula covers the array. It does not prove the GPU compiler generated a correct program for the target architecture.

### Worked example 2

A shared counter incremented serially yields the expected count even when the corresponding parallel code lacks an atomic operation. The serial result hides the race.

## How to run the CPU model

Edit the copy; the [reference](../references/cuda-080_cpu.py) adds assertions.

```sh
python courses/cuda/python/lessons/cuda-080_cpu.py
```

```python
serial_counter = 0
for _ in range(2):
    serial_counter += 1
parallel_reads = [0, 0]
lost_update = max(value + 1 for value in parallel_reads)
assert serial_counter == 2 and lost_update == 1
print("CPU race illustration:", serial_counter, lost_update)
```

**Expected observation:** Serial count 2 versus a possible lost-update count 1.

**Variable trace.** Before running the model, predict these final values; then compare:

| Variable | Final value |
|---|---|
| `serial_counter` | `2` |
| `parallel_reads` | `[0, 0]` |
| `lost_update` | `1` |

## Practice and transfer

Record each attempt in the [worksheet](../lessons/cuda-080.md) before opening hints.

### Exercise 1: Classify a CPU result

**Trap to avoid:** Calling the result GPU verified because the same Python source was used assumes the compiled device code behaves like the interpreter.

### Exercise 2: Construct a race hidden by serialization

**Trap to avoid:** Concluding the kernel needs no atomics because the simulator printed the right count treats a serial schedule as representative of every parallel schedule.

### Exercise 3: Name an unsupported feature

**Trap to avoid:** Assuming anything that runs in the simulator runs identically on hardware ignores that the simulator interprets kernels in Python.

### Exercise 4: Design the validation ladder

**Trap to avoid:** Collapsing the ladder into a single pass/fail end-to-end test hides where a failure came from.

### Exercise 5: Choose a tiny debugging input

**Trap to avoid:** Debugging with a million random elements makes a single wrong index hard to find. A size that is a multiple of the block hides tail bugs.

### Exercise 6: Write an honest evidence label

**Trap to avoid:** Writing only verified or tests pass gives no executor and invites the reader to assume GPU coverage.

## Progressive hints

Hint *k* belongs to exercise *k*; open one at a time.

1. Name the processor that executed the loop and pick the evidence label that matches it.
2. Let two simulated threads both read count 0 before either writes, and record the final value.
3. Look up the pinned simulator's documented support before assuming a feature behaves as it would on hardware.
4. Order the stages from mathematical reference to stress cases, and say what each stage adds that the earlier one could not.
5. Choose an input length that is not a multiple of the block size but is still small enough to trace by hand.
6. Write a label that names what ran and what remains pending, without any device name, bandwidth or throughput.

## Common mistakes and self-check

The central mistake is treating a passing simulator run as GPU correctness. A simulator usually serializes threads, so a shared counter incremented without an atomic still reaches 2, while real concurrent threads can lose an update and report 1. Another mistake is quietly rewriting the algorithm when a feature is unsupported by the simulator. Fix both by keeping the validation ladder stages separate, labeling simulator output as such, and recording unsupported features instead of working around them.

**Misconception:** If the simulator and the CPU reference agree, the kernel only needs a quick hardware run to measure its speed. **Correction:** Agreement on the early rungs of the validation ladder says nothing about concurrency, memory transactions or compiler output for the target architecture. Real-device output must be checked for correctness, not just timed, and repeated stress runs with varied sizes are needed because a race can pass many times before it fails. Memory and race checking tools belong on the ladder as well.

**Evidence limit:** The reference contrasts a serial count of 2 with a possible lost-update count of 1 by construction. It does not run a simulator or a GPU, so it cannot show which races your actual simulator hides or exposes.

1. Name three behaviors a simulator usually does not reproduce.
2. Why can a serialized run hide a race?
3. Where does the simulator belong in the validation ladder?

Answers: [self-check answers](../solutions/cuda-080_solutions.md#self-check-answers).

## Primary references

- [Maintained numba-cuda project](https://github.com/NVIDIA/numba-cuda)

Full lists: [documentation and sources](../../STUDY-GUIDE.md#documentation-and-sources).

## Ask an AI tutor about this lesson

```text
Use the checked-in $guide-ds60sqlpy-learning skill for cuda-080: A simulator is a debugging tool.
Read courses/cuda/python/guides/cuda-080.md and courses/cuda/python/lessons/cuda-080.md.
Start with my current attempt and the two worked examples, and ask which backend actually ran.
Give one progressive hint at a time. Keep the separate solution closed and do not mark
progress unless I request it. Treat synthetic timings and CPU models as model evidence,
not as GPU or cluster measurements.
```
