# cuda-085: Choose a library before owning a kernel

**Route:** CUDA Python and machine learning. **Stage:** intermediate. **Prerequisites:** `cuda-068`, `cuda-071`.

Pacing, evidence labels and platform rules: [CUDA study guide](../../STUDY-GUIDE.md).

## Learning objectives

- Compute complete latency.
- List a numerical contract.
- Add temporary memory.
- Identify a maintenance cost.
- Choose two workload sizes.
- Write a keep-or-replace decision.

## Mechanism and vocabulary

Library selection is an engineering decision about contracts, algorithm quality, maintenance and deployment. A tuned reduction or matrix library usually handles more shapes and architectures than a teaching kernel. A custom implementation may be justified by fusion, unusual layout or a domain-specific operation, but the benefit must survive correctness checks and end-to-end measurement.

Make a comparison ledger: supported dtypes and layouts, temporary memory, numerical behavior, warmup, concurrency, packaging and fallback. Include input sizes where launch overhead dominates and sizes where useful work dominates. A slower educational kernel can still be successful learning evidence; it should not be presented as a production improvement. Prefer the simplest implementation that satisfies the real acceptance criteria.



### Key terms

- **Library baseline:** A tuned vendor or framework implementation used as the reference point before writing a custom kernel.
- **Numerical contract:** The dtype, accuracy, rounding and special-value behavior an implementation promises.
- **Workspace:** Temporary device memory a library routine needs in addition to its inputs and outputs.
- **Maintenance cost:** The ongoing effort to test, port and update custom code across hardware and library versions.

## Worked examples

### Worked example 1

A library pipeline takes 8 ms of kernels and 2 ms of transfer. A custom kernel saves 2 ms but adds 3 ms of packing, so total latency worsens from 10 to 11 ms.

### Worked example 2

A fused transformation reduces three launches to one and removes a large intermediate. It may win at some sizes while losing at tiny sizes where first-call compilation dominates.

## How to run the CPU model

Edit the copy; the [reference](../references/cuda-085_cpu.py) adds assertions.

```sh
python courses/cuda/python/lessons/cuda-085_cpu.py
```

```python
library = {"kernel": 8, "transfer": 2, "packing": 0}
custom = {"kernel": 6, "transfer": 2, "packing": 3}
assert sum(library.values()) == 10
assert sum(custom.values()) == 11
print("CPU decision model: library", sum(library.values()), "custom", sum(custom.values()))
```

**Expected observation:** Library 10 and custom 11 modeled milliseconds.

**Variable trace.** Before running the model, predict these final values; then compare:

| Variable | Final value |
|---|---|
| `library` | `{'kernel': 8, 'transfer': 2, 'packing': 0}` |
| `custom` | `{'kernel': 6, 'transfer': 2, 'packing': 3}` |

## Practice and transfer

Record each attempt in the [worksheet](../lessons/cuda-085.md) before opening hints.

### Exercise 1: Compute complete latency

**Trap to avoid:** Comparing kernel times alone, 6 against 8 ms, declares the custom version a win while ignoring the new packing step.

### Exercise 2: List a numerical contract

**Trap to avoid:** Testing only that the shapes match accepts any numbers of the right size, so a kernel that returns zeros, or that silently turns NaN inputs into finite outputs, would pass every check.

### Exercise 3: Add temporary memory

**Trap to avoid:** Summing only the input and output ignores intermediates, so the custom path can run out of memory at a size where the library path fit, even though both outputs are the same size.

### Exercise 4: Identify a maintenance cost

**Trap to avoid:** Counting only the development time ignores ongoing cost, which repeats every time the team adopts a new GPU or toolkit release and often exceeds the original effort.

### Exercise 5: Choose two workload sizes

**Trap to avoid:** Benchmarking only at the largest size that fits hides the small-input behavior, which matters when production calls are mostly small batches.

### Exercise 6: Write a keep-or-replace decision

**Trap to avoid:** Choosing the custom kernel because its compute portion, 6 ms against 8 ms, is faster ignores the stated total and the packing step that the custom path requires.

## Progressive hints

Hint *k* belongs to exercise *k*; open one at a time.

1. Add every stage a request pays for, not only the kernel time, for both the library and the custom path.
2. Write the shapes, dtypes, tolerance and edge inputs both implementations must accept before comparing them.
3. Find the moment when the most buffers are alive together and add their sizes.
4. Ask who requalifies the custom kernel when the GPU architecture or the compiler version changes.
5. Pick one size where launch overhead dominates and one representative size where useful work dominates.
6. State the measured benefit the custom path would need before its extra obligations are worth accepting.

## Common mistakes and self-check

A common mistake is comparing only kernel times. In worked example 1 the custom kernel saves 2 ms but adds 3 ms of packing, so complete latency worsens from 10 to 11 ms. Another mistake is presenting a slower teaching kernel as a production improvement. Fix both with a ledger that covers supported dtypes and layouts, temporary memory, numerical behavior, warmup, packaging and fallback, measured at a tiny and a representative size, and keep the library unless the full measurement favors the replacement.

**Misconception:** Writing a custom kernel is the more serious engineering choice, so a library call is only a stepping stone. **Correction:** A tuned library usually covers more shapes, dtypes and architectures, and its maintainers carry the testing and packaging burden. A custom kernel is justified only by a specific need such as fusion or an unusual layout, and it then becomes code you must test, package and maintain for every target you support.

**Evidence limit:** The reference adds modeled milliseconds, 10 for the library and 11 for the custom path. These are illustrative numbers, not timings; a real decision needs both implementations measured on the target device with the same inputs and checked outputs.

1. When can a custom kernel be justified over a library call?
2. Why include tiny inputs in the comparison?
3. What is an educational kernel's honest success claim?

Answers: [self-check answers](../solutions/cuda-085_solutions.md#self-check-answers).

## Primary references

- [CuPy interoperability](https://docs.cupy.dev/en/stable/user_guide/interoperability.html)

Full lists: [documentation and sources](../../STUDY-GUIDE.md#documentation-and-sources).

## Ask an AI tutor about this lesson

```text
Use the checked-in $guide-ds60sqlpy-learning skill for cuda-085: Choose a library before owning a kernel.
Read courses/cuda/python/guides/cuda-085.md and courses/cuda/python/lessons/cuda-085.md.
Start with my current attempt and the two worked examples, and ask which backend actually ran.
Give one progressive hint at a time. Keep the separate solution closed and do not mark
progress unless I request it. Treat synthetic timings and CPU models as model evidence,
not as GPU or cluster measurements.
```
