# cuda-107: explained solutions

These answers explain the six practice tasks. CPU reference programs are mathematical or semantic checks, not proof of CUDA execution.

## Exercise 1: Trace stable sorting

Equal-key records preserve input order.

**Approach.** Trace a stable sort of `[(2, A), (1, B), (2, C)]` by key: B moves first, then A and C keep their input order, giving `[(1, B), (2, A), (2, C)]`.

**Why it is correct here.** A stable sort guarantees that records with equal keys appear in the same relative order as in the input. A came before C, so it stays before C.

**A plausible wrong approach.** Assuming every GPU sort is stable lets downstream code rely on an order an unstable sort may legally change, which then varies between runs or releases.

**How to verify.** The reference uses Python's stable `sorted` and asserts the order. For a GPU library, call the documented stable variant and compare with this result on many duplicate keys.

## Exercise 2: Specify duplicate semantics

State whether order is guaranteed.

**Approach.** Specify duplicate semantics in the contract: state whether equal keys keep input order, and if not, require downstream code to break ties with a secondary key.

**Why it is correct here.** When order among duplicates is unspecified, any consumer depending on it is relying on an accident. Stating the rule makes the dependence visible.

**A plausible wrong approach.** Leaving the rule unstated passes tests on small inputs where an unstable algorithm happens to preserve order, then fails on larger inputs that use a different internal path.

**How to verify.** Test with many equal keys and shuffled payloads, checking either preserved order or tie-breaker order as documented.

## Exercise 3: Calculate output shape

Outer dimensions become output.

**Approach.** Calculate the matrix-multiply output shape: a 2 by 3 matrix times a 3 by 4 matrix contracts the shared dimension 3 and gives 2 by 4.

**Why it is correct here.** The inner dimensions must match and disappear, while the outer dimensions form the result. The reference asserts `a[1] == b[0]` and reports `(a[0], b[1])`.

**A plausible wrong approach.** Taking the output as 3 by 3 or 2 by 3 confuses contracted and kept dimensions, and allocating the wrong output buffer causes a library error or an out-of-bounds write.

**How to verify.** Compare with `numpy.matmul` on random arrays of those shapes and check the result shape and values.

## Exercise 4: Account for temporary storage

Workspace can affect peak live memory.

**Approach.** Account for temporary storage: sorting and some matrix algorithms request a workspace buffer, so peak memory is inputs plus outputs plus workspace.

**Why it is correct here.** Workspace can be comparable to the input size for sorts, so it affects whether a large operation fits in memory alongside other live tensors.

**A plausible wrong approach.** Budgeting only inputs and outputs leads to out-of-memory errors that appear only on large arrays.

**How to verify.** Query the library's workspace size for the shape, or measure peak memory during the call, and compare with the budget.

## Exercise 5: Separate plan creation

Measure cold setup and steady execution.

**Approach.** Separate plan creation from execution: libraries such as FFT create a plan for a given shape and dtype, so measure cold setup once and steady execution over repeated calls.

**Why it is correct here.** Plan creation selects algorithms and allocates resources, and its cost is paid once per configuration. Including it in every timing misrepresents steady throughput.

**A plausible wrong approach.** Reusing a plan prepared for a different shape or dtype gives wrong results or errors, so caching must be keyed by both.

**How to verify.** Time the first call and the median of later calls separately, then call with a new shape and confirm a new plan is created.

## Exercise 6: Choose a release-specific contract

Use the documentation matching the prepared package.

**Approach.** Choose a release-specific contract: read the documentation version matching the library release installed, since stability guarantees and supported dtypes can change.

**Why it is correct here.** Function behavior, defaults and supported types differ between releases. Citing the matching documentation ties the contract to the tested code.

**A plausible wrong approach.** Relying on the latest online docs while running an older release can promise features or guarantees the installed version does not have.

**How to verify.** Record the installed version at runtime and link the documentation page for that version in the notes.

## Reference observation

Stable duplicate order and matrix output shape (2,4).

The reference file is `courses/cuda/python/references/cuda-107_cpu.py`. It includes deterministic assertions. These assertions establish the supplied bounded CPU example; hardware execution and architecture-specific performance remain separate checks.
