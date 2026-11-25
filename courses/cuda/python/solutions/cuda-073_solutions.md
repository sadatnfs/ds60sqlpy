# cuda-073: explained solutions

Compare with your [worksheet](../lessons/cuda-073.md) attempt.

## Exercise 1: Separate host and device statements

Validation and allocation are host work.

**Approach.** Split the doubling program into the host wrapper and the device body. The wrapper checks that `x` and `y` have equal lengths, allocates `y`, chooses a launch size and starts the kernel; the kernel body computes one index `i`, tests `i < n`, and writes `y[i] = 2*x[i]`.

**Why it is correct here.** Validation, allocation and launch decisions need Python objects, error raising and the driver API, none of which exist inside a compiled kernel. Only the per-element arithmetic and its bounds guard are data-parallel, so only they belong on the device in worked example 1.

**A plausible wrong approach.** Moving the length check into the kernel, where each thread compares lengths and returns early, means a mismatch produces partial output instead of an error. The host never learns anything went wrong because a kernel cannot raise a Python exception.

**How to verify.** Label every line of the wrapper and kernel as host or device and confirm that the only device lines are the index computation, the guard and the store. A reviewer should be able to delete the kernel body and still see every validation error raised by host code.

## Exercise 2: Implement the CPU oracle

Map each input to twice its value.

**Approach.** Write the CPU oracle as a list comprehension that maps each value to `scale*x`, with `scale = 2`, so `[1, -2, 3]` becomes `[2, -4, 6]` and `[]` stays `[]`.

**Why it is correct here.** The kernel's contract is elementwise: each output depends only on the input at the same index. A sequential map computes the same function without any parallel structure, which makes it a trustworthy reference for comparing the device output element by element.

**A plausible wrong approach.** Writing the oracle with the same indexing code as the kernel, for example looping `i` over a launch-size range with the same guard, copies the kernel's bugs into the reference, so both can agree and still be wrong.

**How to verify.** Run `courses/cuda/python/references/cuda-073_cpu.py`; it asserts `affine_reference([1, -2, 3], 2) == [2, -4, 6]` and that the empty input returns `[]`. A device result is accepted only if it matches this list exactly for these integer-valued inputs.

## Exercise 3: Reject mismatched lengths

Validate before launch.

**Approach.** Before computing the launch, compare `len(x)` with `len(y)` (or the output size the wrapper will allocate) and raise `ValueError` naming both lengths if they differ.

**Why it is correct here.** A kernel indexing `x[i]` and `y[i]` for `i < n` assumes both buffers hold at least `n` elements. If `y` is shorter, threads near the end write past its allocation, which may corrupt a neighboring buffer instead of failing visibly.

**A plausible wrong approach.** Using `n = min(len(x), len(y))` to avoid the overflow silently drops elements. The program then returns a result of the wrong length, and the mismatch surfaces far from the call that caused it.

**How to verify.** Call the wrapper with inputs of length 3 and 2 and assert it raises before any launch. Then call it with equal lengths and compare with the oracle; the error message should include both lengths so a caller can fix the input.

## Exercise 4: Move an allocation out of a kernel

Pass a preallocated buffer.

**Approach.** Allocate the output array in the host wrapper, for example `y = cupy.empty_like(x)`, and pass it to the kernel as an argument. The kernel only writes into memory it is given.

**Why it is correct here.** Kernels written with Numba CUDA or CuPy raw kernels cannot create Python arrays, and per-thread dynamic allocation would be one allocation per element. Worked example 1 already places allocation in the wrapper, which keeps the kernel a pure function of its buffers.

**A plausible wrong approach.** Creating a list or calling `numpy.zeros` inside a `@cuda.jit` function fails to compile because those objects do not exist in device code. Working around it with a fixed-size local array caps the problem size silently.

**How to verify.** Read the kernel source and confirm it has no allocation calls; the output buffer appears as a parameter. Then check that the wrapper allocates exactly `n` elements of the same dtype as `x`, so the size and dtype match the oracle output.

## Exercise 5: Explain type specialization

Typed compiled code is not arbitrary interpreter execution.

**Approach.** Explain that a JIT compiler such as Numba generates a separate machine-code version for each combination of argument types it sees, for example one for `float32` arrays and another for `float64`.

**Why it is correct here.** Device code cannot carry the Python interpreter, so each operation must be resolved to concrete types at compile time. That is why the doubling kernel can run on numeric arrays but not on a list of Python objects or strings.

**A plausible wrong approach.** Assuming the decorated function still behaves like ordinary Python leads to passing mixed types or calling unsupported library functions; the result is a typing error at compile time, or an unintended second specialization with different precision.

**How to verify.** Call the kernel or a CPU `@numba.njit` equivalent once with `float32` and once with `float64` inputs and inspect the compiled signatures list. Two entries confirm specialization; a typing error for a list of strings confirms the restriction.

## Exercise 6: List a prepared toolchain ledger

Record distribution, Python, toolkit, driver and device.

**Approach.** Record a toolchain ledger with the operating system distribution, Python version, the package versions (Numba or CuPy), CUDA toolkit or runtime version, driver version, GPU model and compute capability.

**Why it is correct here.** A kernel that compiles in one environment can fail to load in another because the driver is too old for the runtime, or the GPU architecture is not targeted. The doubling kernel's result is evidence only for the environment that produced it.

**A plausible wrong approach.** Writing only the package name and the word CUDA tells a reader nothing about which runtime and driver were present, so a later failure on another machine cannot be compared with the original success.

**How to verify.** Fill the ledger from `numba -s` or the equivalent library info call plus the driver tool output, and attach it to the result. Another person should be able to tell from the ledger alone whether their host matches.

## Self-check answers

1. **Why can the same syntax be legal on the host and illegal in a device function?** Device code is compiled from a restricted typed subset. Arbitrary objects, file access and unsupported library calls exist only in the host interpreter.

2. **What does a host wrapper do before launching the kernel?** It validates input lengths, allocates the output buffer, converts data to numeric buffers and copies them explicitly, so the kernel only reads fixed buffers and scalars.

3. **Why does `numba.cuda` in an import line not identify the implementation?** The maintained numba-cuda distribution uses the same namespace, so the spelling alone does not tell you which package and version supplied it. Record the pinned distribution.

## Reference observation

[2, -4, 6], with empty input accepted by the oracle.

Asserted by `courses/cuda/python/references/cuda-073_cpu.py`.
