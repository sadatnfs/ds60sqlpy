# cuda-073: A kernel is a restricted parallel program

**Route:** CUDA Python and machine learning. **Stage:** intermediate. **Prerequisites:** `cuda-066`, `cuda-072`.

Pacing, evidence labels and platform rules: [CUDA study guide](../../STUDY-GUIDE.md).

## Learning objectives

- Separate host and device statements.
- Implement the CPU oracle.
- Reject mismatched lengths.
- Move an allocation out of a kernel.
- Explain type specialization.
- List a prepared toolchain ledger.

## Mechanism and vocabulary

A Python GPU kernel is compiled from a restricted typed subset; the Python interpreter does not run independently on every GPU thread. Host-side allocation, file access, arbitrary objects and unsupported library calls stay outside the device function. Compilation specializes supported argument types and shapes or layouts according to the selected toolchain. The same syntax can therefore have different legality on host and device.

Keep allocation and validation in a host wrapper. The kernel receives fixed buffers and scalar parameters, calculates its index, checks bounds and writes only its assigned output. That separation makes errors easier to locate. The maintained numba-cuda distribution uses the numba.cuda namespace, so the import spelling alone does not identify which package supplied the implementation. Pin and record the distribution in a prepared environment.



### Key terms

- **Restricted typed subset:** The portion of Python that a kernel compiler can translate, with fixed scalar and array types and no arbitrary objects.
- **Device function:** A function compiled for the GPU that kernels can call but the host cannot launch directly.
- **Type specialization:** Compiling a separate machine-code version for each combination of argument types a function receives.
- **CPU oracle:** An independent, simple CPU implementation whose results serve as the expected values for a GPU kernel.

## Worked examples

### Worked example 1

A host wrapper allocates an output and checks equal input lengths. A device kernel writes `y[i] = 2*x[i]` only when i is in range.

### Worked example 2

A kernel that tries to open a text file violates the execution model. Move file reading to the host, convert values into a numeric buffer, then copy explicitly.

## How to run the CPU model

Edit the copy; the [reference](../references/cuda-073_cpu.py) adds assertions.

```sh
python courses/cuda/python/lessons/cuda-073_cpu.py
```

```python
def affine_reference(values, scale):
    return [scale * x for x in values]


assert affine_reference([1, -2, 3], 2) == [2, -4, 6]
assert affine_reference([], 2) == []
print("CPU kernel oracle:", affine_reference([1, -2, 3], 2))
```

**Expected observation:** [2, -4, 6], with empty input accepted by the oracle.

## Practice and transfer

Record each attempt in the [worksheet](../lessons/cuda-073.md) before opening hints.

### Exercise 1: Separate host and device statements

**Trap to avoid:** Moving the length check into the kernel, where each thread compares lengths and returns early, means a mismatch produces partial output instead of an error. The host never learns anything went wrong because a kernel cannot raise a Python exception.

### Exercise 2: Implement the CPU oracle

**Trap to avoid:** Writing the oracle with the same indexing code as the kernel, for example looping `i` over a launch-size range with the same guard, copies the kernel's bugs into the reference, so both can agree and still be wrong.

### Exercise 3: Reject mismatched lengths

**Trap to avoid:** Using `n = min(len(x), len(y))` to avoid the overflow silently drops elements. The program then returns a result of the wrong length, and the mismatch surfaces far from the call that caused it.

### Exercise 4: Move an allocation out of a kernel

**Trap to avoid:** Creating a list or calling `numpy.zeros` inside a `@cuda.jit` function fails to compile because those objects do not exist in device code. Working around it with a fixed-size local array caps the problem size silently.

### Exercise 5: Explain type specialization

**Trap to avoid:** Assuming the decorated function still behaves like ordinary Python leads to passing mixed types or calling unsupported library functions; the result is a typing error at compile time, or an unintended second specialization with different precision.

### Exercise 6: List a prepared toolchain ledger

**Trap to avoid:** Writing only the package name and the word CUDA tells a reader nothing about which runtime and driver were present, so a later failure on another machine cannot be compared with the original success.

## Progressive hints

Hint *k* belongs to exercise *k*; open one at a time.

1. Go line by line through the wrapper and the kernel and ask which lines touch Python objects, files or new allocations.
2. Write the plain Python loop the kernel replaces, element by element, and run it on the supplied input.
3. Decide where the length comparison belongs so that no launch happens with mismatched buffers.
4. Ask who should own the output buffer's lifetime: the host wrapper that launches, or each GPU thread.
5. Compare what the compiler knows about argument types with what an interpreter learns only at run time.
6. List every layer between your source and the device, from the Python package to the driver, and name what to record for each.

## Common mistakes and self-check

A common mistake is writing a device function as if each GPU thread ran a full Python interpreter, for example opening a file, building a list or calling an unsupported library inside the kernel. Those calls fail to compile or belong to the host. Fix it by splitting the work: the host wrapper validates lengths, reads files, allocates the output and copies data; the kernel computes one index, checks the bound and writes only its own element.

**Evidence limit:** The CPU oracle doubles `[1, -2, 3]` and accepts an empty input, which defines the expected values. It does not compile anything, so it cannot show which constructs the numba-cuda compiler accepts or how a specialized kernel behaves on a device.

1. Why can the same syntax be legal on the host and illegal in a device function?
2. What does a host wrapper do before launching the kernel?
3. Why does `numba.cuda` in an import line not identify the implementation?

Answers: [self-check answers](../solutions/cuda-073_solutions.md#self-check-answers).

## Primary references

- [NVIDIA CUDA Python introduction](https://docs.nvidia.com/cuda/cuda-programming-guide/02-basics/intro-to-cuda-python.html)

Full lists: [documentation and sources](../../STUDY-GUIDE.md#documentation-and-sources).

## Ask an AI tutor about this lesson

```text
Use the checked-in $guide-ds60sqlpy-learning skill for cuda-073: A kernel is a restricted parallel program.
Read courses/cuda/python/guides/cuda-073.md and courses/cuda/python/lessons/cuda-073.md.
Start with my current attempt and the two worked examples, and ask which backend actually ran.
Give one progressive hint at a time. Keep the separate solution closed and do not mark
progress unless I request it. Treat synthetic timings and CPU models as model evidence,
not as GPU or cluster measurements.
```
