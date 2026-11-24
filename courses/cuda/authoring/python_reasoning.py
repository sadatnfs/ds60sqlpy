# ruff: noqa: E501
"""Per-exercise solution reasoning for the CUDA Python and GPU Spark chapters.

REASONING maps a chapter number (1 to 64, published as cuda-065 to cuda-128) to six
tuples in exercise order. Each tuple holds four non-empty strings: the approach, why it
is correct for this chapter's data, one plausible wrong approach and why it fails here,
and how to verify the result. Nothing here reports a GPU timing or device output; every
claim is derived from the chapter's code and its CPU reference.
"""

from __future__ import annotations

REASONING: dict[int, list[tuple[str, str, str, str]]] = {}

REASONING[1] = [
    (
        "Walk the GPU sum in time order and tag each step with the processor that does it: the Python list is built by the interpreter, a copy moves those three integers into a device allocation, a reduction kernel runs on the GPU, a completion point is reached, and a scalar copy brings the total back.",
        "Only the launch and the arithmetic run on the device. The interpreter creates `[1, 2, 3]` before any driver call, and the final `6` must be copied into host memory before Python can treat it as an `int`, so the first and last events belong to the host.",
        "Listing only three events (build, sum, print) merges the upload into construction and the download into printing. That hides exactly the two transfers worked example 2 names, so a later timing or residency question has no event to attach to.",
        "Write the five events in a table with a processor column and compare it with worked example 2. Then run `courses/cuda/python/references/cuda-065_cpu.py` and confirm its ledger reports CPU for every row, which is the honest result when no device participates.",
    ),
    (
        "Separate what `import cupy` establishes from what a GPU result requires: a package resolved on `sys.path`, then a visible device, an allocation, a launch, completion and a correct value. Each later fact needs its own observation.",
        "Python import only loads modules and may defer driver initialization. A machine without an NVIDIA driver can still import a wheel successfully, so the import line in this chapter says nothing about where the later `sum` executes.",
        "Treating a clean import as proof of GPU execution is the common shortcut. It fails on a CPU-only laptop where the import succeeds but the first allocation raises, and it fails silently when a framework falls back to CPU for unsupported work.",
        "On any host, note that import succeeded, then try a one-element device allocation and record the outcome separately. The reasoning is correct if your notes contain two distinct lines, one for import and one for allocation, rather than a single ready flag.",
    ),
    (
        "Replace `[1, 2, 3]` with `[]` and ask what the reduction must return. A sum of no terms is the additive identity, so the result is `0`, and on a GPU path the sensible move is to return that identity without launching anything.",
        "`sum([])` in Python returns `0` by definition, and the reference asserts exactly that. A device reduction with zero elements has no work, so any correct backend must agree with the host identity rather than read uninitialized storage.",
        "Launching a reduction with a grid computed from `n = 0` and then reading `out[0]` can return whatever bytes the allocation held. Another wrong move is raising an error, which breaks callers that legitimately pass empty batches.",
        "Run the reference and confirm the line `assert sum([]) == 0` passes. For a GPU variant, test the empty input explicitly and check that the returned value is `0` and that no kernel launch was recorded.",
    ),
    (
        "Look for the point where a device value becomes a Python object. Calling `print`, `float()`, `int()` or `.item()` on a device scalar requests its value on the host, which needs a device-to-host copy and therefore waits for the kernel that produces it.",
        "In worked example 2 the reduction result lives in device memory. Python cannot format bytes it does not hold, so printing forces the copy and the copy cannot begin until the producing kernel completes, which adds a synchronization the code never states.",
        "Assuming `print(total)` is free because it is one line leads to placing it inside a loop. Each iteration then stalls the host until the device catches up, and a timing taken around the loop measures synchronization rather than the reduction.",
        "Mark the print as event five in your trace and label it as both a transfer and a wait. On a real device, a profiler timeline would show a small device-to-host copy right before the host resumes; without a device, the trace table is the evidence.",
    ),
    (
        "Design a ledger row per object with four fields: the object name, the backend that owns it, the allocation that holds its bytes, and the event that proves it is complete. Fill it for input, sum and result.",
        'The reference ledger `[("input", "CPU"), ("sum", "CPU"), ("result", "CPU")]` records only the backend. Adding allocation and completion columns is what lets the same ledger describe the GPU path, where input and result have two copies each.',
        'A ledger keyed by package name ("numpy", "cupy") instead of by object fails as soon as one library holds both host and device arrays, and it cannot record whether the device result was actually ready when read.',
        'Fill the ledger for the CPU case and check that every row says CPU, matching the reference assertion `all(device == "CPU" ...)`. Then fill it for the five-event GPU trace and confirm the input and result each have a host row and a device row.',
    ),
    (
        'When a GPU path is unavailable and the program computes on the CPU instead, report it as a CPU reference result with the reason, for example "CPU reference: 6; device not visible", and never as a GPU pass.',
        "The reference in this chapter prints `CPU reference: 6` and every ledger entry is CPU. That value is mathematically right, but it is evidence that the algorithm is correct, not that any CUDA device executed it.",
        "Catching the CUDA error and silently computing with NumPy makes the program exit with status zero and the same answer. A dashboard reading only exit codes would then count a GPU lesson as qualified on a machine with no GPU.",
        "Run the reference on a CPU-only host and confirm the printed label starts with `CPU reference`. A correct fallback report contains the backend name, the reason, and the value, and a reviewer can see that the GPU stage was not attempted.",
    ),
]

REASONING[2] = [
    (
        "Use the address formula with the original matrix strides `(12, 4)`: offset equals `1*12 + 1*4`. Row index 1 skips one 12-byte row, column index 1 skips one 4-byte float32.",
        "The matrix is 2 by 3 float32 and row-major, so each row holds three 4-byte values and the row stride is 12 bytes. Element (1,1) is the fifth element in storage, and 4 elements times 4 bytes is 16.",
        "Computing `1*3 + 1` and calling the answer 4 gives an element index, not a byte offset. Using the sliced view strides `(12, 8)` gives 20, which is the address of a different element in the original storage.",
        "Plug `(1, 1)` and `(12, 4)` into the reference `offset` function; it returns 16. The reference also checks that `(1, 1)` with the slice strides `(12, 8)` gives 20, showing why the stride tuple, not the shape, decides the answer.",
    ),
    (
        "Change the itemsize from 4 to 8 and recompute strides: a contiguous 2 by 3 float64 matrix has strides `(24, 8)`, so every byte offset doubles while logical coordinates stay the same.",
        "Strides are byte displacements, and float64 uses 8 bytes per element. Element (1,2) moves from 20 to 40 bytes, and the allocation grows from 24 to 48 bytes, while the shape `(2, 3)` is unchanged.",
        "Keeping strides `(12, 4)` and only relabeling the dtype reads half of each float64 as a float32. The element count matches, which is why the bug is easy to miss, but every value is garbage.",
        "Compute `offset((1, 2), (24, 8))` and confirm 40, double the reference 20. With NumPy, `np.zeros((2, 3), np.float64).strides` should print `(24, 8)`.",
    ),
    (
        "Describe the transpose of the 2 by 3 matrix as a view with shape `(3, 2)` and strides `(4, 12)`: the axes and their strides swap and no bytes move.",
        "Moving one step along the new first axis walks to the next column of the original, which is 4 bytes away; moving along the new second axis walks to the next original row, 12 bytes away. The reference checks that `(2, 1)` with `(4, 12)` lands at byte 20, the same element as original `(1, 2)`.",
        "Assuming the transpose is contiguous and indexing it with `row*2 + col` reads the original storage in the wrong order. A raw kernel given only the data pointer and new shape silently computes on the untransposed matrix.",
        "Run the reference and check the third assertion, `offset((2, 1), (4, 12)) == 20`. In NumPy, `a.T.strides` on a `(2, 3)` float32 array should print `(4, 12)` and `a.T.flags.c_contiguous` should be `False`.",
    ),
    (
        "Find the line that computes an index as `row*width + col` and replace it with `row*stride0 + col*stride1` (in elements or bytes), or reject non-contiguous input before launch.",
        "That flat formula is only valid when the last stride equals itemsize and the row stride equals width times itemsize. The column slice in worked example 2 has strides `(12, 8)`, so the formula reads columns 0 and 1 instead of 0 and 2.",
        "Fixing it by calling a reshape on the slice can hide the bug: reshape may copy, so the kernel becomes correct but writes go to a temporary and the original view never changes.",
        "Feed the slice `a[:, ::2]` to both a contiguous-only model and a stride-aware model on the 2 by 3 array `[[0,1,2],[3,4,5]]`. The stride-aware version must return `[[0,2],[3,5]]`; the buggy one returns `[[0,1],[2,3]]`.",
    ),
    (
        "Decide explicitly: either validate that every stride is positive and raise a clear error, or support negative strides by allowing the view base to point at the last element and adding signed offsets.",
        "A reversed view such as `a[:, ::-1]` has a last stride of -4 for float32. The address formula still works with signed arithmetic, but only if the kernel uses signed index types and the base pointer includes the view offset.",
        "Taking absolute values of strides makes indices non-negative and appears to work, but it reads the columns in the original order, so a reversed view returns unreversed data.",
        "For the 2 by 3 example, compute addresses for `a[:, ::-1]` with base offset 8 and strides `(12, -4)`; element (0,0) must be at byte 8 (value 2). A rejection policy is verified by a test asserting that a negative-stride input raises before launch.",
    ),
    (
        "Write one test per layout class: contiguous `(2,3)`, the column slice with strides `(12,8)`, the transpose with `(4,12)`, an empty `(0,3)` array, and a float64 input that must be rejected or converted explicitly.",
        "Each case breaks a different assumption. The slice breaks row times width indexing, the transpose breaks C-contiguity, the empty case tests the launch guard, and the float64 case tests dtype validation instead of byte reinterpretation.",
        "Testing only random contiguous arrays of various sizes gives high coverage numbers but never exercises a non-unit stride, which is the exact contract this chapter is about.",
        "Each test compares the kernel or model output with a NumPy reference on the same view. The suite passes when all five cases agree, and the float64 case asserts a raised error or an explicit, counted conversion copy.",
    ),
]

REASONING[3] = [
    (
        "Count bytes per iteration for the round-trip version: one upload of B and one download of B, so `2B` per iteration and `20B` over ten iterations. With the reference size of 4096 bytes that is 81920.",
        "The reference sets `size = 4096`, `iterations = 10`, and asserts `round_trip == 81920`. The resident version uploads once and downloads once, giving `2 * 4096 = 8192`, a factor of ten fewer bytes.",
        "Counting only uploads (`10B`) treats the output copy as free. Many real pipelines download a result every step for logging, so omitting it halves the modeled traffic.",
        "Run `courses/cuda/python/references/cuda-067_cpu.py`: it asserts 81920 and 8192 and prints both. Change `iterations` to 20 and confirm the round-trip figure doubles while the resident figure does not change.",
    ),
    (
        "Model each transfer as `latency + bytes / bandwidth` and compare 100 copies of 40 bytes with one copy of 4000 bytes using the reference values `latency = 10e-6` and `bandwidth = 1e9`.",
        "Both cases move 4000 bytes, so the bandwidth term is identical. The batch pays the 10 microsecond latency once instead of 100 times, which is why the reference asserts `many > one`.",
        "Expecting batching to reduce the payload is the mistake. The bytes are the same; if your model shows the bandwidth term shrinking, you have double-counted or dropped rows.",
        "Compute by hand: 100 times 10 microseconds is 1 millisecond of latency versus 10 microseconds for one batch. The reference assertion `many > one` must pass, and the gap must be about 990 microseconds in the model.",
    ),
    (
        "Trace the buffer that an asynchronous copy reads from, and find any write to it before the copy's completion event. Insert a wait on that event (or the stream) before the overwrite.",
        "An asynchronous upload returns control to Python before the DMA engine has read the host buffer. Refilling that buffer for the next batch can change bytes still being copied, so the device sees a mix of two batches.",
        "Adding a sleep after the copy call seems to fix it in testing because the copy usually finishes. It is timing luck: a larger batch or a busy bus makes the race reappear.",
        "Write the event order for two batches and check that every refill of the host buffer comes after the previous copy's completion event. On a device, a test that fills the buffer with a known pattern per batch and checks the device copy catches the mix.",
    ),
    (
        "Keep the Python object that owns pinned host memory alive until every copy that reads or writes it has completed, and release it only after that wait.",
        "Pinned memory is page-locked so the copy engine can access it directly. If the owning object is garbage collected while a copy is pending, the pages can be unpinned or reused, and the copy touches memory it no longer owns.",
        "Pinning every array in the program to be safe consumes host memory the OS cannot page out, which can starve other processes. Pinning is a bounded resource, not a free speedup.",
        "In a code review, find each pinned allocation and the stream event it depends on, and check that the release path waits on that event. The model check is a written ordering: allocate, copy issued, copy completed, release.",
    ),
    (
        "Start the timer before input preparation and the host-to-device copy, and stop it only after the result has been copied back and is usable by host code.",
        "End-to-end latency is what a caller experiences. In this chapter the resident and round-trip versions differ mainly in transfer counts, so a timer that excludes transfers cannot see the difference the lesson is teaching.",
        "Stopping the timer right after the kernel call returns measures submission only, because the call is asynchronous; it reports a tiny number regardless of the 81920 versus 8192 byte difference.",
        "Write the timer boundaries next to each event of the pipeline and check that both copies and the completion wait are inside. Any timing you record must be labeled with those boundaries; this chapter's numbers are modeled, not measured.",
    ),
    (
        "Look for work where the fixed costs dominate: a small array used once, such as the 40-byte rows in worked example 1 processed one at a time, with a simple elementwise operation.",
        "With the reference model, a 40-byte transfer costs about 10 microseconds of latency and 40 nanoseconds of bandwidth time. A CPU can finish a few arithmetic operations on 10 floats far faster than that latency, before any kernel launch cost is added.",
        "Assuming the GPU always wins because it has more cores ignores the fixed costs. A benchmark on one tiny array would show the CPU ahead, and the conclusion that the GPU is slow would also be wrong.",
        "State the workload size and the transfer count, and compare modeled latency with an estimate of CPU work. The conclusion is valid when you can show that latency terms, not arithmetic, dominate the GPU total.",
    ),
]

REASONING[4] = [
    (
        "Compute each column mean over the two rows, then subtract it: column 0 is `(1+3)/2 = 2`, column 1 is `(3+7)/2 = 5`, giving centered rows `[[-1,-2],[1,2]]`.",
        "Centering subtracts the same per-column value from every row, which is a broadcast of a length-2 vector over a 2 by 2 array. Each centered column then sums to zero, a property the reference result satisfies.",
        "Subtracting row means instead is tempting because they are also 2 and 5 here, a coincidence of this data. Broadcasting them down the wrong axis gives `[[-1,1],[-2,2]]`; the shapes still match, so no error appears, and the columns no longer sum to zero.",
        "Run the cuda-068 reference: it asserts `centered == [[-1.0, -2.0], [1.0, 2.0]]`. With CuPy or NumPy, `x - x.mean(axis=0)` must match, and `centered.sum(axis=0)` must be zeros.",
    ),
    (
        "Append a column of a constant, for example 5, to both rows. Its mean is 5, so after centering that column is all zeros.",
        "Subtracting a column's mean from identical values always gives zero. On the GPU this is still exact for small integers stored as float32, so the result is a column of exact zeros.",
        "Dividing by the column standard deviation after centering, as in standardization, divides zero by zero for this column and produces NaN that spreads into later steps.",
        "Extend the reference rows to `[[1,3,5],[3,7,5]]` and confirm the third centered column is `[0.0, 0.0]`. If you also scale, assert that the policy for zero variance is explicit, such as leaving the column at zero.",
    ),
    (
        "Subtract coordinates first and then square and sum: `(1-4)**2 + (2-6)**2 = 9 + 16 = 25`.",
        "The direct form never forms large squares of the original values, so it has no cancellation. For the integers in this example it is exact, matching the reference assertion `distance == 25`.",
        "Taking a square root and reporting 5 answers a different question. The chapter defines squared distance, and mixing the two breaks comparisons against the reference.",
        "Run the reference and check `distance == 25`. With an array library, `((x - y) ** 2).sum()` on float32 inputs `[1,2]` and `[4,6]` must also give exactly 25.",
    ),
    (
        "Expand `|x-y|^2` as `|x|^2 + |y|^2 - 2 x.y` and construct inputs where the two first terms are large and nearly equal to the cross term, for example coordinates near `1e4` that differ by 1 in float32.",
        "For `[1,2]` and `[4,6]` the expanded form gives `5 + 52 - 2*16 = 25` exactly. With large nearly equal vectors, float32 keeps about seven significant digits, so `|x|^2` around `1e8` cannot represent a difference of a few units and the subtraction loses the answer.",
        "Concluding that the expanded form is safe because the small worked example matches is the trap. Exact agreement on tiny integers says nothing about inputs where the squared norms dominate.",
        "Compare the two forms in float32 and float64 on `x = [10000.0, 10000.0]`, `y = [10001.0, 10000.0]`. The direct form gives 1; check whether the float32 expanded form differs, and record the result as a CPU numeric observation.",
    ),
    (
        "Count the elements of the broadcast temporary `x[:, None, :] - y[None, :, :]`: it has shape `(N, M, D)`, so its size is `N*M*D` elements times itemsize.",
        "Pairwise distance on N rows against M rows by broadcasting materializes every coordinate difference before the reduction over D. For N = M = 10000 and D = 64 in float32 that is 25.6 GB, far above the size of the final `(N, M)` result.",
        "Counting only the output `N*M` elements underestimates peak memory by a factor of D. The allocation fails or swaps even though the result itself would fit.",
        "Compute `N*M*D*4` bytes for your chosen sizes and compare with device memory. A safe experiment checks the broadcast shape with tiny N and M first, for example `(2, 2, 2)` on the reference vectors.",
    ),
    (
        "Write the baseline with supported array operations, such as `x.mean(axis=0)` and broadcast subtraction, before writing any custom kernel, and keep it as the oracle.",
        "CuPy and NumPy implement these operations with tested dtype promotion and edge handling. The centering and distance in this chapter are a few library calls, so a custom kernel would have to beat a correct baseline rather than replace a missing one.",
        "Starting with a raw kernel for centering means writing reduction, broadcasting and tail handling by hand, with no reference to tell whether a wrong column mean is a kernel bug or a math bug.",
        "Keep the library result for `[[1,3],[3,7]]` and the distance 25 as fixed test cases. Any later kernel must reproduce `[[-1,-2],[1,2]]` and 25 under a stated tolerance before its speed is discussed.",
    ),
]

REASONING[5] = [
    (
        "Predict that two fresh generators seeded with 7, or one generator reseeded with 7, produce the same first draws. Reseeding resets the stream to its start.",
        "A seeded pseudo-random generator is deterministic: the seed fixes the internal state, and the state fixes every subsequent draw. Worked example 1 shows two `Random(7)` objects agreeing on four draws.",
        "Reseeding inside a training loop each step to get reproducibility makes every step see the same random numbers, so dropout masks or shuffles repeat and the experiment loses its randomness.",
        "Create `random.Random(7)` twice and compare the first four `random()` values; they must be equal. Then reseed one mid-stream and confirm it returns to the first value.",
    ),
    (
        "Keep one generator object alive across batches and draw from it; the second batch continues the stream instead of repeating the first.",
        "The reference draws `first`, then `second` from the same object and asserts `first != second`. The state after batch one is the starting point for batch two.",
        "Creating a new generator per batch with the same seed makes each batch identical. Creating one per batch with `seed + batch` gives distinct but correlated-by-construction streams that are harder to reason about.",
        "Run the cuda-069 reference and check that `first != second` holds. Record the first value of each batch to show the continuation.",
    ),
    (
        "Call `rng.getstate()` before drawing a batch, and later call `rng.setstate(saved)` to replay exactly that batch.",
        "The state captures the whole generator, not just the seed. The reference saves state, draws `first`, draws `second`, restores, and asserts the replay equals `first`.",
        "Saving state after drawing the batch captures the position for the next batch. Restoring it replays `second`, not `first`, which is an off-by-one in time.",
        "In the reference, the assertion `first == [rng.random() for _ in range(4)]` after `setstate` is the check. It passes only if state was saved before the first draw.",
    ),
    (
        "For a large sample, compare the sample mean and variance with the distribution's known values within a tolerance. For uniform on [0, 1), the mean is 0.5 and variance 1/12.",
        "Different backends implement different generators, so draw-by-draw equality is not a fair test across CPU and GPU. Statistical moments are a property every correct uniform generator shares.",
        "Requiring exact equality between CuPy and Python random draws fails even when both are correct, because their algorithms differ. Using a tolerance tighter than sampling error also fails randomly.",
        "Draw 100000 values, compute mean and variance, and accept if each is within a tolerance chosen from sampling error, for example about `0.0037` for the mean (four times `0.2887 / sqrt(100000)`) at four standard errors. Record seed and sample size.",
    ),
    (
        "Write the contract as numeric or statistical agreement across backends, and reserve exact-byte equality for replays within the same backend, version and seed.",
        "Worked example 2 notes that restoring Python state does not make CuPy or TensorFlow produce the same values. Their generators and parallel streams are different algorithms.",
        "Hashing the output bytes of a CPU run and a GPU run and calling the mismatch a bug wastes debugging time on something that is not a defect.",
        "Verify within-backend replay by comparing bytes for the same seed twice. Verify cross-backend agreement with the moment test or with a downstream metric tolerance.",
    ),
    (
        "List every source of randomness a resumed run needs: Python `random` state, NumPy generator state, the framework CPU and per-device generator states, and the data sampler or shuffler state.",
        "Training uses several generators at once. Restoring only the Python state, as in this chapter's reference, replays Python draws but not GPU dropout or the order the sampler yields batches.",
        "Saving only the initial seed and reseeding on resume restarts the streams at the beginning, so the resumed run repeats the first epoch's shuffles instead of continuing.",
        "Checkpoint, resume, and compare the next batch indices and a dropout mask with an uninterrupted run under the same backend. Both must match for the checkpoint to be complete.",
    ),
]

REASONING[6] = [
    (
        "Track two counters: reserved bytes held by the pool and live bytes owned by arrays. After the array is released, live drops to 0 and reserved stays at 1024.",
        "A memory pool keeps freed blocks to serve later requests without asking the driver again. The reference asserts `live == 0 and reserved == 1024` after the release.",
        "Reading the device memory report and concluding there is a 1024-byte leak confuses reserved with live. The block is free in the pool and will be reused.",
        "Run the cuda-070 reference and check the first assertion. With CuPy on a device, `pool.used_bytes()` and `pool.total_bytes()` would show the same split.",
    ),
    (
        "Request a new 1024-byte array after the release and observe that the pool hands back the free block, so live returns to 1024 and reserved stays 1024.",
        "The request size matches the free block exactly. The reference asserts `live <= reserved` after reuse, which holds because no new reservation was needed.",
        "Expecting reserved to rise to 2048 after the second allocation assumes the pool never reuses blocks. That would make every loop iteration look like growth.",
        "Model the allocate, release, allocate sequence and confirm reserved never exceeds 1024. On a device, repeat the cycle a few times and check that total pool bytes stay flat.",
    ),
    (
        "Find the list that appends each step's output and replace it with a detached scalar summary, or drop the reference when the step ends.",
        "Worked example 2 keeps four 1024-byte results live, so live bytes are 4096 and keep growing. Pool reuse cannot help because none of those arrays is ever freed.",
        "Calling the pool's free-all function every step does not release arrays still referenced by the list. Live bytes stay at 4096 and the clearing just costs time.",
        "The reference asserts `sum(retained) == 4096` for four steps. After the fix, record live bytes for steps 1 to 4 and confirm they stay at 1024.",
    ),
    (
        "Explain that clearing a cache returns only free blocks to the driver; arrays that are still referenced keep their storage no matter how often the cache is cleared.",
        "In the retained-list case all 4096 bytes are live. Clearing the cache may reduce reserved bytes in the healthy case of worked example 1 but cannot touch live bytes.",
        "Adding `free_all_blocks()` after every step makes the memory report drop slightly while the actual leak continues, giving false confidence.",
        "Compare live bytes before and after clearing in the retained-output model; they must be equal. The fix that changes live bytes is dropping references.",
    ),
    (
        "Take a memory snapshot before and after a fixed small number of steps, such as four, each with the same input size, and compare live and reserved separately.",
        "A bounded loop with a fixed size shows the pattern: healthy reuse keeps live at one result, retention grows by one result per step, exactly 1024 bytes in this chapter's model.",
        "Running until the device runs out of memory and reading the error message is unbounded and can disturb other users of a shared device.",
        "Record four snapshots; growth of 1024 live bytes per step identifies retention, flat live with flat reserved identifies reuse.",
    ),
    (
        "Separate host RAM limits from device memory: a container memory limit constrains host allocations, while VRAM is managed by the GPU driver.",
        "The pool in this chapter manages device memory. A container that limits RAM to 4 GB does not, in general, stop a process from reserving device memory.",
        "Setting a container memory limit and expecting it to prevent device out-of-memory errors gives no protection. The device can still fill up.",
        "List which tool reports each: host RSS from the OS, device usage from the GPU driver or the library pool. A correct note names both separately.",
    ),
]

REASONING[7] = [
    (
        "Place the stop point after the completion event, not after the call returns: the operation spans from submission at 2 microseconds to finish at 102 microseconds.",
        "The launch is asynchronous, so returning at 2 microseconds only means the work was queued. The output exists at 102, so the interval that measures finished work must include it.",
        "Stopping the timer at the return reports 2 microseconds and undercounts by the factor of 51 the reference computes.",
        "The reference asserts `finish_us / submit_us == 51`. In real code, place a synchronize or event wait before the stop timestamp and confirm the recorded interval includes it.",
    ),
    (
        "Sort the five samples `[10, 10, 11, 12, 100]` and take the middle value, 11.",
        "With an odd count the median is the third sorted value. The single 100 ms outlier does not move it, which is why the median describes typical completion.",
        "Reporting the mean, 28.6 ms, mixes the tail into the center and overstates the typical case by a factor of about 2.6.",
        "Run the cuda-071 reference: `statistics.median(samples) == 11` is asserted. Also report the maximum 100 so the tail is not lost.",
    ),
    (
        "Add both transfer costs to the kernel interval: host-to-device before and device-to-host after, so the end-to-end interval covers every byte the caller needs.",
        "A caller cannot use a device result until it is on the host. In this chapter's 2 to 102 microsecond trace, any copy time is additional end-to-end time.",
        "Reporting only the kernel interval as latency makes a GPU path look faster than a CPU path that includes its own I/O.",
        "Draw the timeline with upload, kernel and download, and check the timer brackets all three. Label any number as synthetic unless measured on a device.",
    ),
    (
        "Report the first call and later calls as separate distributions, because the first call can include JIT compilation, module loading and allocation.",
        "Numba and CuPy compile on first use. Folding that into a warm median hides it or, with few samples, distorts the median.",
        "Discarding the first call without reporting it hides a cost a real user pays at process start.",
        "Record cold and warm samples in two lists and check the median of the warm list does not include call one.",
    ),
    (
        "Use the same input data, dtype, output and tolerance for both backends, and time the same boundary (end-to-end or kernel-only) on each.",
        "A comparison is meaningful only when both sides do the same work. Different input sizes or a looser tolerance on one side make the ratio meaningless.",
        "Comparing a float32 GPU run with a float64 CPU run reports a speedup that is partly a precision change.",
        "Check outputs agree within the stated tolerance before timing. Record the shape, dtype, tolerance and boundary next to every number.",
    ),
    (
        "State that the trace numbers in this chapter are invented teaching values used to practice analysis, not measurements of any device.",
        "The reference script computes a median of a hard-coded list; nothing executes on a GPU. Reporting its output as performance would be fabricated evidence.",
        "Copying the 11 ms median into a report as GPU latency misrepresents a CPU script's constant as a hardware result.",
        "The reference prints `CPU trace analysis`, which is the correct label. A real benchmark records host, device, versions and raw samples.",
    ),
]

REASONING[8] = [
    (
        "Order the evidence as import, device visibility, allocation, kernel launch, completion and correctness, and record each as passed, failed or not attempted.",
        "Each stage depends on the previous one: no allocation without a visible device, no launch without an allocation, no correctness check without completion. The reference lists the six stages in this order and finds the first failure with `next(...)`, so a later stage is never credited when an earlier one is missing.",
        "Collapsing all stages into one boolean `gpu_ok` hides where a failure happened and makes a correctness failure look like a missing driver.",
        "Run the cuda-072 reference: it marks correctness false and asserts the first failed stage is `correctness`.",
    ),
    (
        "Classify a probe that imports CuPy but reports zero devices as a visibility failure, then check whether the runtime exposes devices and whether the host has an NVIDIA GPU.",
        "Worked example 1 shows that import succeeded, so the Python package and its modules are present. The failure sits at the next stage, visibility, and allocation and launch were never reached, so they must be recorded as not attempted rather than failed.",
        "Reinstalling CuPy treats the problem as a package issue when the package is fine; the missing piece is device exposure or hardware.",
        "Record import passed, visibility failed, allocation and later stages not attempted. Then check two independent facts: whether the container or process was started with the GPU exposed to it, and whether the host itself lists an NVIDIA device and a loaded driver.",
    ),
    (
        "Classify a probe that launched, completed, and returned wrong values as a correctness failure after execution.",
        "Worked example 2 describes exactly this. Launch and completion evidence are real and worth keeping, because they rule out driver and visibility problems, but readiness requires correct values, so the overall status is not ready and the investigation moves to the kernel or its inputs.",
        "Reporting the probe as ready because the exit code was zero ignores the value check. A probe that prints wrong numbers and exits normally is worse than one that crashes, because nothing downstream notices.",
        'The reference sets correctness to False and asserts `failed == "correctness"`, while every earlier stage is True. A real probe should compare its output with a known host value, such as doubling `[1, 2, 3]` to `[2, 4, 6]`, and fail with the mismatched values printed.',
    ),
    (
        "Make device selection fail closed: if the requested backend is CUDA and no visible device exists, raise an error instead of continuing on CPU.",
        "A GPU-labeled result must come from a GPU. When the caller asked for CUDA, the only honest outcomes are a CUDA result or an error; failing closed keeps the label attached to the backend that actually ran.",
        "Defaulting to CPU with a warning lets automated runs record a GPU pass for a CPU result.",
        "Run the selector on a CPU-only host requesting CUDA; it must raise. Run it requesting CPU explicitly; it must proceed with a CPU label.",
    ),
    (
        "After a fatal device error, end the process and start a fresh one rather than continuing to issue work in the same context.",
        "Some CUDA errors, such as an illegal memory access inside a kernel, are sticky: the context stays in an error state and later calls in the same process keep failing or cannot be trusted. A new process gets a new context.",
        "Catching the exception and retrying in the same process often fails again, and if it seems to succeed the evidence is suspect.",
        "Record the error, restart, rerun the probe stages, and require all six stages to pass in the new process.",
    ),
    (
        "Name the backend that ran: CUDA for NVIDIA, ROCm for AMD, MPS for Apple, or CPU, and never relabel one as another.",
        "Each backend has its own runtime, operator coverage and numerical behavior. A result on Apple MPS or AMD ROCm can be correct and useful, but it is not evidence that the CUDA path works.",
        "Calling any accelerator run a GPU pass loses which runtime produced it, so a CUDA requirement can be satisfied by an Apple run on paper.",
        "Check the device object's type string (for example `cuda:0` or `mps`) and record it beside every result.",
    ),
]

REASONING[9] = [
    (
        "Split the doubling program into the host wrapper and the device body. The wrapper checks that `x` and `y` have equal lengths, allocates `y`, chooses a launch size and starts the kernel; the kernel body computes one index `i`, tests `i < n`, and writes `y[i] = 2*x[i]`.",
        "Validation, allocation and launch decisions need Python objects, error raising and the driver API, none of which exist inside a compiled kernel. Only the per-element arithmetic and its bounds guard are data-parallel, so only they belong on the device in worked example 1.",
        "Moving the length check into the kernel, where each thread compares lengths and returns early, means a mismatch produces partial output instead of an error. The host never learns anything went wrong because a kernel cannot raise a Python exception.",
        "Label every line of the wrapper and kernel as host or device and confirm that the only device lines are the index computation, the guard and the store. A reviewer should be able to delete the kernel body and still see every validation error raised by host code.",
    ),
    (
        "Write the CPU oracle as a list comprehension that maps each value to `scale*x`, with `scale = 2`, so `[1, -2, 3]` becomes `[2, -4, 6]` and `[]` stays `[]`.",
        "The kernel's contract is elementwise: each output depends only on the input at the same index. A sequential map computes the same function without any parallel structure, which makes it a trustworthy reference for comparing the device output element by element.",
        "Writing the oracle with the same indexing code as the kernel, for example looping `i` over a launch-size range with the same guard, copies the kernel's bugs into the reference, so both can agree and still be wrong.",
        "Run `courses/cuda/python/references/cuda-073_cpu.py`; it asserts `affine_reference([1, -2, 3], 2) == [2, -4, 6]` and that the empty input returns `[]`. A device result is accepted only if it matches this list exactly for these integer-valued inputs.",
    ),
    (
        "Before computing the launch, compare `len(x)` with `len(y)` (or the output size the wrapper will allocate) and raise `ValueError` naming both lengths if they differ.",
        "A kernel indexing `x[i]` and `y[i]` for `i < n` assumes both buffers hold at least `n` elements. If `y` is shorter, threads near the end write past its allocation, which may corrupt a neighboring buffer instead of failing visibly.",
        "Using `n = min(len(x), len(y))` to avoid the overflow silently drops elements. The program then returns a result of the wrong length, and the mismatch surfaces far from the call that caused it.",
        "Call the wrapper with inputs of length 3 and 2 and assert it raises before any launch. Then call it with equal lengths and compare with the oracle; the error message should include both lengths so a caller can fix the input.",
    ),
    (
        "Allocate the output array in the host wrapper, for example `y = cupy.empty_like(x)`, and pass it to the kernel as an argument. The kernel only writes into memory it is given.",
        "Kernels written with Numba CUDA or CuPy raw kernels cannot create Python arrays, and per-thread dynamic allocation would be one allocation per element. Worked example 1 already places allocation in the wrapper, which keeps the kernel a pure function of its buffers.",
        "Creating a list or calling `numpy.zeros` inside a `@cuda.jit` function fails to compile because those objects do not exist in device code. Working around it with a fixed-size local array caps the problem size silently.",
        "Read the kernel source and confirm it has no allocation calls; the output buffer appears as a parameter. Then check that the wrapper allocates exactly `n` elements of the same dtype as `x`, so the size and dtype match the oracle output.",
    ),
    (
        "Explain that a JIT compiler such as Numba generates a separate machine-code version for each combination of argument types it sees, for example one for `float32` arrays and another for `float64`.",
        "Device code cannot carry the Python interpreter, so each operation must be resolved to concrete types at compile time. That is why the doubling kernel can run on numeric arrays but not on a list of Python objects or strings.",
        "Assuming the decorated function still behaves like ordinary Python leads to passing mixed types or calling unsupported library functions; the result is a typing error at compile time, or an unintended second specialization with different precision.",
        "Call the kernel or a CPU `@numba.njit` equivalent once with `float32` and once with `float64` inputs and inspect the compiled signatures list. Two entries confirm specialization; a typing error for a list of strings confirms the restriction.",
    ),
    (
        "Record a toolchain ledger with the operating system distribution, Python version, the package versions (Numba or CuPy), CUDA toolkit or runtime version, driver version, GPU model and compute capability.",
        "A kernel that compiles in one environment can fail to load in another because the driver is too old for the runtime, or the GPU architecture is not targeted. The doubling kernel's result is evidence only for the environment that produced it.",
        "Writing only the package name and the word CUDA tells a reader nothing about which runtime and driver were present, so a later failure on another machine cannot be compared with the original success.",
        "Fill the ledger from `numba -s` or the equivalent library info call plus the driver tool output, and attach it to the result. Another person should be able to tell from the ledger alone whether their host matches.",
    ),
]

REASONING[10] = [
    (
        "Use ceiling division: `blocks = (n + block - 1) // block`, which for `n = 17` and `block = 4` gives `(17 + 3) // 4 = 5` blocks and 20 lanes.",
        "Four blocks provide only 16 lanes and would skip index 16. Five blocks provide 20 lanes, which covers every index from 0 to 16 with three spare lanes in the last block.",
        "Computing `n // block = 4` blocks is the floor-division mistake; the program runs without error and the last element is never written, so its output slot keeps whatever value was in the allocation.",
        "Evaluate the expression in Python and confirm it returns 5. Extend the reference model with `n = 17`: the list `visits` must equal `list(range(17))`, which holds only with five blocks and the `< n` guard.",
    ),
    (
        "List the global indices of the last block for `n = 17`: block 4 covers `4*4 + t` for `t` from 0 to 3, which is 16, 17, 18 and 19. Only 16 is valid.",
        "The valid range is `0 <= i < 17`. Lanes 17, 18 and 19 exist only because the launch rounds up to whole blocks, so the tail guard `if i < n` must stop them before any load or store.",
        "Assuming only one lane is out of range, or guarding with `i <= n`, lets index 17 through. That reads one element past the end, which may return a neighbor's data or trip a memory checker.",
        "Write the four indices with a valid or invalid mark and confirm exactly three are invalid. The reference's comprehension uses `if b*block+t < n`, the same guard, and its assertion that visits equal `range(n)` passes.",
    ),
    (
        "Check `n == 0` in the host wrapper and return an empty output without computing a grid or launching.",
        "With `n = 0` the ceiling formula gives 0 blocks. Many runtimes reject a zero-sized grid as an invalid configuration, so the empty case must be handled before the launch, and the correct result is simply an empty array.",
        "Clamping the grid to at least one block avoids the launch error but runs lanes whose guard is always false. That works, but it hides the empty case inside the kernel and still pays launch overhead for no work.",
        "Call the wrapper with an empty input and assert the result is empty and that no launch was recorded, for example with a counter in a mock launcher. The CPU model should return `[]` for `n = 0` as well.",
    ),
    (
        "Write a grid-stride loop: each thread starts at its global index `t` and advances by the total number of threads, `stride = grid_size * block_size`, until it passes `n`.",
        "With 6 threads and `n = 14`, thread 0 visits 0, 6, 12, thread 1 visits 1, 7, 13, and threads 2 to 5 each visit two indices. Every index in 0 to 13 is visited exactly once, which the reference checks by sorting the union.",
        "Advancing by `block_size` instead of the total thread count makes threads in different blocks visit the same indices. The output may still look right for idempotent writes, but accumulations double count.",
        "Run the reference: `sorted(strided) == list(range(14))` is asserted. Add a check that `len(strided) == 14`, which fails if any index is visited twice.",
    ),
    (
        "Look for launch code using `n // block` and replace it with ceiling division, then keep the in-kernel guard.",
        "Floor division drops the remainder. For `n = 10` and `block = 4`, it launches two blocks, covering indices 0 to 7, so elements 8 and 9 are never processed.",
        "Fixing it by launching `n // block + 1` blocks always adds a block even when `n` is a multiple of the block size. That is safe with a guard but launches an entire idle block for `n = 8`.",
        "Test `n = 10`: the output must have all ten elements processed. Test `n = 8` and confirm the ceiling formula gives exactly two blocks.",
    ),
    (
        "Specify a separate run of the real kernel under the CUDA memory checker (`compute-sanitizer`) with a tail size such as `n = 17`, and record its report alongside the CPU model result.",
        "The CPU model proves the index arithmetic covers the range. It cannot detect an out-of-bounds access in compiled code, which is exactly what a missing tail guard causes.",
        "Treating the passing CPU model as proof that the kernel is memory safe confuses the model of the formula with the code a compiler generated.",
        "Run the sanitizer on a device with the guard removed to see it report invalid accesses, then with the guard restored to see a clean report. Without a device, mark this check as not attempted.",
    ),
]

REASONING[11] = [
    (
        "Pick a small tile, for example two rows by three columns starting at row 0 column 0, and write the row list `[0, 1]` and the column list `[0, 1, 2]` separately before forming the six coordinate pairs.",
        "In a 2D launch, `threadIdx.y` and `blockIdx.y` produce the row while the `.x` components produce the column. Listing them independently mirrors how the hardware generates them and makes it obvious which pair each thread owns.",
        "Writing pairs directly from a single flattened thread number tempts the reader to assign `x` to rows, because rows are listed first in mathematics. The tile then covers three rows and two columns, a transposed shape.",
        "Count the pairs: there must be rows times columns of them, six here, with no duplicates. Each pair should satisfy `row < 2` and `column < 3`, and the set should match a nested loop over rows then columns.",
    ),
    (
        "For row-major storage compute `offset = row * width + column`. With width 3, row 1 column 2 gives `1*3 + 2 = 5`, the last slot of a 2 by 3 image.",
        "Row-major layout stores each complete row contiguously, so moving down one row skips `width` elements and moving right one column skips one. The reference asserts `1*3+2 == 5`, the same arithmetic.",
        "Using `column * width + row` swaps the roles. For row 1 column 2 it gives `2*3 + 1 = 7`, which lies past the six-element allocation, so a kernel would read or write out of bounds.",
        "Enumerate all six coordinates with the formula and confirm the offsets are exactly 0 to 5 with no gaps or repeats. Also check that the largest offset is `height*width - 1`.",
    ),
    (
        "Replace the clamped neighbor reads with a zero-padded version: a neighbor outside the row contributes 0, so the average for `[3, 6, 9]` becomes `[(0+3+6)/3, 6, (6+9+0)/3] = [3, 6, 5]`.",
        "Changing padding changes the mathematical operation, not just an implementation detail. Clamping repeats the edge pixel, while zero padding assumes black outside the image, so border values differ and the documentation must say which is computed.",
        "Calling both versions a three-point average and comparing only the interior value 6 hides the change. Tests that skip the edges will pass for either padding and miss a semantic regression.",
        "Compute both lists and assert the clamped version equals `[4, 6, 8]` from the reference while the zero-padded one equals `[3, 6, 5]`. The difference must appear only in positions 0 and 2.",
    ),
    (
        "Trace an in-place stencil on `[3, 6, 9]`: if index 0 is updated to 4 before index 1 reads its left neighbor, index 1 computes `(4+6+9)/3` instead of `(3+6+9)/3`.",
        "A stencil needs every output computed from the original input. When the output overwrites the input, earlier writes become later reads, and on a GPU the order of those writes between threads is not defined, so results can also vary between runs.",
        "Assuming each thread writes only its own element and therefore cannot interfere ignores that neighbors read that element. Ownership of writes is not the same as ownership of reads.",
        "Run the in-place version sequentially and show index 1 becomes about 6.33 instead of 6. Then use separate input and output buffers and confirm the result returns to `[4, 6, 8]`.",
    ),
    (
        "Apply the clamped average to a single-column image, for example `[7]`. Both neighbor indices clamp to 0, so the output is `(7+7+7)/3 = 7`.",
        "With width 1 the left index `max(0, -1)` and right index `min(0, 1)` both collapse to 0. Clamping therefore repeats the only element, and the average equals the input, which is the expected degenerate behavior.",
        "Assuming width is always at least 3 and reading `values[i-1]` and `values[i+1]` directly fails: `values[-1]` silently returns the last element in Python, and `values[1]` raises IndexError. A device version reads out of bounds.",
        "Call the reference expression with `values = [7]` and assert the result is `[7.0]`. Add the same test for height 1 in a 2D stencil to exercise the vertical clamp.",
    ),
    (
        "In the 2D kernel guard with `if row < height and column < width:` before any load or store, since the grid is rounded up separately in each dimension.",
        "A 2D launch rounds the number of blocks up in both x and y. Threads past the last column exist in every block row, and threads past the last row exist in every block column, so each coordinate needs its own bound.",
        "Guarding only the flat offset with `offset < height*width` lets a thread with column 3 and row 0 in a width-3 image pass, because its offset 3 is valid. It then writes into row 1, column 0, corrupting another pixel.",
        "Use a 5 by 5 image with 4 by 4 blocks so both tails exist. Count the threads that pass the guard: it must be exactly 25, and the set of offsets must be 0 to 24 with no duplicates.",
    ),
]

REASONING[12] = [
    (
        "Pad inactive lanes of a sum reduction with 0, the additive identity. The reference stores `[2, 4, 6, 0]` in a four-lane tile and the block sum is 12.",
        "Adding zero does not change a sum, so the padded lane contributes nothing while still occupying its slot in the tree. Every lane can therefore follow the same reduction steps without branching on validity.",
        "Padding with the value of the last valid element, 6, changes the sum to 18. Such a pad looks harmless because it is in the data range, which is why it passes casual inspection.",
        "Evaluate `sum([2, 4, 6, 0])` and confirm it equals `sum([2, 4, 6]) = 12`. Repeat with a two-element tile padded with two zeros to show the identity holds for any pad count.",
    ),
    (
        "For a minimum reduction pad with a value that can never win, such as positive infinity for floats or the dtype maximum for integers, or carry a separate validity flag with each value.",
        "The pad must be the identity of `min`. If valid data can legally contain the dtype maximum, that sentinel ties with real data, so an explicit validity flag is safer when the whole domain is possible.",
        "Padding with 0 is the common mistake carried over from sums. For data `[2, 4, 6]` it reports a minimum of 0, a value not in the input.",
        "Compute `min([2, 4, 6, inf])` and confirm 2. Then try an input made entirely of the sentinel value and check that the validity-flag version reports no valid minimum rather than the sentinel.",
    ),
    (
        "List every lane of the block, `[0, 1, 2, 3]`, and mark each one as reaching the barrier, including lane 3, which has no input element.",
        "`cuda.syncthreads()` requires every thread in the block to arrive. The reference asserts `participants == [0,1,2,3]`, which models the rule that an inactive lane still participates in the collective operation.",
        "Listing only lanes 0 to 2 because they hold data treats the barrier as a data operation. On hardware, a barrier not reached by all threads is undefined behavior and can hang or corrupt shared memory.",
        "Check that the participant list equals `range(blockDim)` regardless of the input length. A trace for a two-element input with a four-lane block should still show four participants.",
    ),
    (
        "Replace `if i >= n: return` with a guarded load: `value = x[i] if i < n else 0`, store `value` in shared memory, then let every thread proceed to the barrier and the reduction.",
        "The guard now protects the memory access, not the control flow. The thread for index 3 never reads `x[3]`, yet it reaches every `syncthreads` call and contributes the identity value.",
        "Moving the early return below the first barrier but above the second still leaves later barriers missing a participant. Every barrier after the return is affected, not only the first.",
        "Read the kernel and confirm no `return` appears before the last barrier. Run the CPU model with a three-element input and four lanes: the sum must be 12 and all four lanes recorded.",
    ),
    (
        "State that a shared-memory array belongs to one block. A result needing data from several blocks requires a second step, such as writing per-block partials to global memory and reducing them in another launch or with atomics.",
        "Each block gets its own copy of the shared array, and `syncthreads` synchronizes only that block. Block 0 cannot see block 1's tile or wait for block 1 to finish.",
        "Reading another block's partial from shared memory assumes a grid-wide shared space. The read returns the current block's own data, so the total silently counts one block several times.",
        "Use a two-block input and show the reduction produces two partials. The final answer equals the sum of the partials only after a separate combination step.",
    ),
    (
        "Test with `n = blocksize + 1`, for example 5 elements and 4-lane blocks, using values whose sum is easy to compute by hand, like `[1, 2, 3, 4, 5]` with expected total 15.",
        "This input needs two blocks, one of them almost empty. It exercises the padded lanes, the barrier participation of three inactive lanes, and the combination of two block partials.",
        "Testing only with `n = 4` or `n = 8` makes every block full. Bugs in padding or early returns never execute, so the test passes against broken code.",
        "Write the expected partials explicitly, `[10, 5]`, and the total 15 before running. A mismatch in the second partial points directly to tail handling.",
    ),
]

REASONING[13] = [
    (
        "Compute the pair tree for `[1, 2, 3, 4, 5]` by hand: level one gives `[3, 7, 5]` with 5 carried, level two gives `[10, 5]`, level three gives `[15]`.",
        "The reference loop sums slices `items[i:i+2]`, so an odd element forms a one-item slice and passes to the next level. Each level halves the count, rounding up, until one value remains.",
        "Pairing only `range(0, len(items) - 1, 2)` drops the odd element at each odd level. For this input the result becomes 10 and the error looks small enough to mistake for rounding.",
        "Write each level and confirm the sum is preserved at every step: 15, 15, 15. The reference asserts `items == [15]`.",
    ),
    (
        "Add a test whose last element is distinctive, such as `[1, 2, 3, 4, 5]`, and assert the result is 15, not 10.",
        "Ignoring the tail removes exactly the fifth value, so the faulty total differs by 5. A large, exact gap with integer inputs is an indexing bug; rounding errors cannot produce it.",
        "Using a tolerance like `abs(result - 15) < 10` would accept 10. Picking tolerances that wide hides structural bugs inside numerical noise.",
        "Compare with exact equality, since integer sums are exact in floating point at this size. Repeat with seven elements to check that two carry steps also work.",
    ),
    (
        "Use `[1e16, 1.0, -1e16]`: a left-to-right float64 sum computes `1e16 + 1.0`, which rounds back to `1e16`, then subtracts to 0, while `math.fsum` returns 1.0.",
        "Doubles have 53 bits of mantissa, so near `1e16` the spacing between representable numbers is 2. Adding 1 is lost in rounding. The true sum is 1, which fsum tracks exactly with extra partials.",
        "Using `[1.0, 2.0, 3.0]` as the cancellation test shows nothing, since every order gives 6 exactly. A test needs magnitudes far enough apart to exceed the mantissa.",
        "Assert `sum(values) == 0.0` and `math.fsum(values) == 1.0` on standard IEEE doubles. The reference asserts the fsum result.",
    ),
    (
        "Compare GPU and CPU sums with `abs(a - b) <= atol + rtol * abs(b)`, choosing `rtol` from the dtype and the number of terms and an `atol` that reflects the scale of the inputs when the expected value is near zero.",
        "Relative tolerance scales with the expected value. When cancellation makes the expected result 1 or 0 while the terms are about 1e16, rounding error is proportional to the terms, so only an absolute term sized to them is meaningful.",
        "Using relative tolerance alone with an expected value of 0 requires exact equality. Any reordering then fails, even though both answers are within normal rounding of the large terms.",
        "Compute the bound for the cancellation input and confirm 0 and 1 both fit when `atol` reflects the term magnitude. Confirm an indexing error like 10 versus 15 still falls outside.",
    ),
    (
        "Contrast `cuda.atomic.add` on one global accumulator with a staged reduction: per-block shared-memory trees followed by a final pass over block partials.",
        "Atomics are short to write, but every thread serializes on one address, and the order of floating additions depends on scheduling. A staged tree has fixed pairing within each block and far fewer global updates.",
        "Claiming the atomic version is deterministic because each update is indivisible confuses atomicity with order. Each addition is safe, but the sequence of additions still varies.",
        "For integer inputs both must give the identical total. For float32 inputs, run the atomic version several times and look for differences in the last bits, while the staged version with a fixed launch stays stable.",
    ),
    (
        "Explain that deterministic library settings fix the order of operations for one configuration, but changing GPU model, library version or launch configuration may still change the floating-point result.",
        "Determinism guarantees repeatable results on the same software, hardware and inputs. Different hardware can choose different kernels, block counts or fused multiply-add usage, which changes rounding.",
        "Treating a deterministic flag as a promise of identical results across machines leads to bit-exact comparisons between environments that fail for legitimate reasons.",
        "Record the environment with each result. Expect bit-identical answers only within one environment, and use a tolerance when comparing across environments.",
    ),
]

REASONING[14] = [
    (
        "Trace two threads incrementing bin 0, which holds 2: both read 2, both compute 3, both store 3. The final count is 3, although two updates happened.",
        "A non-atomic increment is a read, an add and a write. If both reads happen before either write, the second write overwrites the first with the same value, and one increment disappears.",
        "Assuming the two writes collide in a visible way, raising an error or producing a garbled value, is incorrect. The lost update produces a plausible number, which is why it escapes notice.",
        "Write the interleaving as a table of read, add and write steps per thread. The final value must be 3, while an atomic or serial version gives 4.",
    ),
    (
        "Compute the histogram of `[0, 0, 0, 0, 0, 0]` with three bins: bin 0 holds 6 and the others hold 0.",
        "Every update targets bin 0, so this input is the worst case for contention. Correctness is easy to state, while performance depends on serialization at one counter.",
        "Using the uniform data `[0, 1, 2, 0, 1, 2]` as the contention test spreads updates evenly and measures the friendliest case instead.",
        "Run the reference loop on the six zeros and assert `bins == [6, 0, 0]`. The total of the bins must equal the input length, 6.",
    ),
    (
        "Merge per-block histograms by adding matching bins: `[2, 1, 0] + [0, 0, 3]` gives `[2, 1, 3]`.",
        "Each partial counts a disjoint subset of the input, so the full count for a bin is the sum of the partial counts. The reference asserts the merged list equals the direct histogram.",
        "Concatenating the partials or taking the bin-wise maximum produces wrong totals. The maximum here gives `[2, 1, 3]` by coincidence, so test with overlapping partials such as `[1, 1, 0]` and `[1, 0, 3]`.",
        "Use `zip(left, right, strict=True)` so different bin counts raise an error. Check that the sum of the merged bins equals the input length.",
    ),
    (
        "Compute private storage as partials times bins times counter width. For 1024 block partials, 256 bins and 4-byte counters, that is `1024*256*4 = 1048576` bytes.",
        "Privatization trades memory for reduced contention, since every partial needs a full copy of the bins. The cost grows linearly with each factor.",
        "Counting only bins times width, 1 KiB here, ignores that each partial owns its own copy and underestimates memory by a factor of the partial count.",
        "Recompute the product and confirm 1 MiB. Then halve the number of partials and confirm the bytes halve.",
    ),
    (
        "Explain that `atomic.add` on a float accumulator makes each addition indivisible but leaves the order of additions to the scheduler, so rounding may differ between runs.",
        "Floating addition is not associative. Different arrival orders round at different points, so atomic sums are correct within rounding but not bitwise reproducible.",
        "Expecting atomics to give the same bits as a sequential CPU sum confuses race-freedom with order. No update is lost, but the order is still free.",
        "Sum values of very different magnitudes atomically several times and compare the last bits. Integer counters give identical results every time.",
    ),
    (
        "Before reading bins on the host, wait for the histogram kernel and the merge to finish, for example with `cuda.synchronize()` or an implicit synchronization in a device-to-host copy on the same stream.",
        "Launches are asynchronous. Reading the bins before the merge completes can return partial counts.",
        "Reading after only the histogram kernel ignores the merge step, so the host sees one block's partial instead of the total.",
        "Assert that the copied bins sum to the input length. A smaller total signals that the read happened before all updates completed.",
    ),
]

REASONING[15] = [
    (
        "Apply the simplified rule: divide each byte offset by the 32-byte segment width with integer division and count the distinct quotients. Offsets `0, 4, ..., 28` all give quotient 0, so one segment is touched.",
        "Within this model a memory transaction moves an aligned 32-byte segment, so eight 4-byte loads that fall inside one segment cost one transaction. The `segments` helper implements exactly the set-of-quotients rule.",
        "Counting one transaction per lane, eight here, treats every load as independent and ignores coalescing. That would make the contiguous and strided patterns look equally expensive.",
        "Call `segments([4*i for i in range(8)])` and confirm 1; call it on `[32*i for i in range(8)]` and confirm 8. Label both numbers as model outputs, not profiler counters.",
    ),
    (
        "Shift the contiguous offsets by four bytes, giving `4, 8, ..., 32`, and recount: offsets 4 to 28 have quotient 0 and offset 32 has quotient 1, so two segments are touched.",
        "Only the last lane crosses the aligned boundary at byte 32, but that is enough to require a second segment. Alignment of the base address matters even when the access is perfectly contiguous.",
        "Assuming contiguity alone guarantees one segment ignores the boundary. A misaligned base can double the modeled transactions for the same amount of useful data.",
        "Compute `segments([4 + 4*i for i in range(8)])` and confirm 2. A shift of 0 or 32 bytes keeps the count at 1, which checks that only misalignment causes the change.",
    ),
    (
        "Model a stride of two elements: offsets `0, 8, ..., 56`. Integer division by 32 yields quotients 0 and 1, so two segments are touched to deliver 32 useful bytes.",
        "Half the bytes in each fetched segment are unused, so the useful fraction drops to one half. Larger strides keep spreading lanes until each one touches its own segment, as the 32-byte stride shows.",
        "Thinking stride only matters when it reaches the segment size misses the intermediate cost. Stride two already doubles the transactions in this model.",
        "Compute segments for strides 1, 2, 4 and 8 elements and confirm counts 1, 2, 4 and 8. The trend must be monotone for these aligned offsets.",
    ),
    (
        "Explain a tiled transpose: a block loads a tile with row-contiguous reads into a shared array, synchronizes, then writes the tile out with row-contiguous writes in the transposed position, reading shared memory by column.",
        "A naive transpose has either reads or writes with a stride of the matrix width. Staging through shared memory makes both global accesses contiguous, while the strided part happens in fast on-chip storage. The mathematical result is unchanged.",
        "Expecting the shared-memory version to change the output values, or to need a different verification, confuses reorganized traffic with a different algorithm.",
        "Compare the tiled result with `numpy.transpose` on a non-square matrix such as 3 by 5, including partial tiles. The outputs must be equal exactly.",
    ),
    (
        "Separate occupancy, the number of resident warps relative to the maximum, from throughput, the useful work per second. Raising occupancy helps hide latency only when warps are waiting on memory and resources allow.",
        "More resident warps also share registers, shared memory and memory bandwidth. A kernel that already saturates bandwidth gains nothing from more warps, and register pressure can force spills that slow it down.",
        "Treating the occupancy number as the performance goal leads to changes that raise the percentage while total runtime stays the same or rises.",
        "In a profiler, record achieved occupancy together with memory throughput and runtime for two block sizes. Only the runtime of a correct output decides which is better.",
    ),
    (
        "Design a profiler experiment that compares contiguous and strided kernels with the same dtype, element count, output and launch configuration, collecting real memory transaction and throughput counters.",
        "Holding everything else fixed isolates the access pattern as the cause. The CPU segment model predicts a direction, and only hardware counters can confirm it.",
        "Comparing kernels that differ in dtype or element count mixes several causes. A float64 strided kernel against a float32 contiguous one cannot attribute the difference to stride.",
        "Before reading counters, check both kernels produce the same output. Record GPU model, driver and profiler versions; without a GPU, report the experiment as designed but not run.",
    ),
]

REASONING[16] = [
    (
        "Label a passing CPU loop result as a CPU model or simulator result and state what it covered, such as index coverage for one size, without claiming GPU correctness.",
        "The CPU run checks the algorithm and index formula. It does not exercise the GPU compiler, the memory model or the hardware scheduler, so the label must match the evidence.",
        "Calling the result GPU verified because the same Python source was used assumes the compiled device code behaves like the interpreter.",
        "Read each recorded claim and check it names the executor. Any claim about GPU behavior must point to a device run with environment details.",
    ),
    (
        "Construct a race that serial execution hides: two lanes read a counter of 0, each adds 1, and each writes 1. The parallel result is 1 while the serial loop gives 2.",
        "In serial execution each increment completes before the next read, so no update is lost. The reference contrasts `serial_counter == 2` with `lost_update == 1`.",
        "Concluding the kernel needs no atomics because the simulator printed the right count treats a serial schedule as representative of every parallel schedule.",
        "Confirm both assertions in the reference pass. Then replace the plain increment with an atomic add in the kernel source and record that the race is now ruled out by construction.",
    ),
    (
        "Name a feature the simulator may not support or may behave differently with, such as particular atomic operations or memory model details, and look up the pinned simulator documentation for that version.",
        "Simulator coverage changes between versions, so the honest source is the documentation for the version in use. Guessing from memory risks citing a feature added or removed later.",
        "Assuming anything that runs in the simulator runs identically on hardware ignores that the simulator interprets kernels in Python.",
        "Record the simulator version and quote the relevant documentation line. If a kernel uses an unsupported feature, mark the simulator result as not applicable for that path.",
    ),
    (
        "Design a validation ladder: CPU oracle, simulator run, device compile, device run with a small input compared to the oracle, then a run under the memory checker.",
        "Each rung tests something the earlier rungs cannot. Keeping them separate means a failure points to one layer, such as compilation versus numerical disagreement.",
        "Collapsing the ladder into a single pass/fail end-to-end test hides where a failure came from.",
        "Record a status per rung: passed, failed or not attempted. Without a GPU, the last three rungs should read not attempted.",
    ),
    (
        "Choose a debugging input that is a non-multiple of the block size yet small enough to trace by hand, for example 5 elements with a block size of 4.",
        "The input creates a partial final block, so tail-guard bugs show up, while five values allow writing every index and output by hand.",
        "Debugging with a million random elements makes a single wrong index hard to find. A size that is a multiple of the block hides tail bugs.",
        "Write the expected output for all five indices first, then compare element by element and report the first mismatching index.",
    ),
    (
        "Write an evidence label such as: CPU oracle passed; simulator passed for n = 5; GPU correctness pending a real device run.",
        "The label states exactly which executors produced which results, so a reader knows what remains unproven. That keeps a simulator success from being reported as hardware validation.",
        "Writing only verified or tests pass gives no executor and invites the reader to assume GPU coverage.",
        "Check that every label names an executor and a status. A label that mentions a GPU must also cite device and driver details.",
    ),
]

REASONING[17] = [
    (
        "Contrast `alias = owner` with `copied = list(owner)`. After `alias[0] = 9`, `owner` is `[9, 2, 3]` while `copied` stays `[1, 2, 3]`.",
        "Assignment binds a second name to the same list object, so a mutation through either name is visible through both. `list(owner)` allocates new storage with the same values.",
        "Assuming any transfer between libraries copies data leads to surprises when a zero-copy exchange like DLPack shares storage and a later in-place edit changes both arrays.",
        "Run the reference: both assertions pass. For device arrays, compare data pointers; equal pointers mean an alias.",
    ),
    (
        "Trace lifetime: when a consumer receives a view of a producer's buffer, the producer object must stay alive, or ownership must transfer under the exchange protocol's rules, until the consumer is finished.",
        "If the producer's last reference disappears, its memory pool may reuse the bytes while the consumer still reads them. The consumer's view does not keep memory alive unless the protocol says so.",
        "Deleting the original tensor right after the exchange to save memory assumes the consumer holds a copy.",
        "Keep a reference to the producer until the consumer's work completes. A test can delete the producer, allocate new data and check whether the consumer view changed.",
    ),
    (
        "List the metadata a consumer needs to read a shared buffer: data pointer, byte offset, dtype, shape, strides and device identity.",
        "The bytes have no meaning without metadata. The same 24 bytes can be three float64 values or six float32 values, and strides decide whether a 2 by 3 view is row-major or transposed.",
        "Passing only the pointer and the shape forces the consumer to guess dtype and layout.",
        "Exchange a transposed 2 by 3 array and check the consumer's strides and values match the producer's.",
    ),
    (
        "State that sharing storage with another library through a protocol such as DLPack does not carry the originating autograd graph, so gradients do not flow back through the exchange.",
        "Storage protocols describe memory, not the operation history PyTorch records. The consumer sees plain data, and operations it performs are invisible to the producer's autograd.",
        "Assuming a forward result that matches means gradients are also correct conflates two different checks.",
        "Run a forward comparison and a separate gradient check. A missing gradient shows up as `None` or zeros where nonzero values were expected.",
    ),
    (
        "Name the evidence that a shared buffer is ready: the producer's recorded CUDA event, or a stream negotiated in the exchange, for example the `stream` argument of `__dlpack__`.",
        "Producer writes may still be queued when the exchange happens. The consumer must order its reads after the producer's work, which requires an event or a stream agreement.",
        "Relying on the host call having returned treats Python completion as device completion.",
        "Record which event or stream was used. A test with a slow producer kernel should still show correct values in the consumer.",
    ),
    (
        "Design mutation tests: change one element through the consumer view, synchronize, then read the producer to see whether the change is visible, avoiding concurrent writes from both sides.",
        "Visibility after a sequential mutation determines whether the exchange produced an alias or a copy. Sequencing avoids a data race that would make the result undefined.",
        "Writing from both libraries at once to see what happens produces a race whose outcome proves nothing.",
        "Record whether the mutation was visible and compare with the documented behavior of the exchange.",
    ),
]

REASONING[18] = [
    (
        "Draw the dependency graph for one batch as nodes upload, transform and download with edges upload to transform and transform to download, matching the `edges` list in the reference.",
        "Edges represent data dependencies: transform reads the uploaded buffer, and download reads the transform output. Any execution order respecting these edges is valid.",
        "Drawing edges from code order instead of data flow invents dependencies between unrelated work and hides real ones crossing library calls.",
        "Run the reference: the valid order passes the positions check. The order with download first fails, which the second assertion confirms.",
    ),
    (
        "Locate a missing wait: consumer B on stream 2 reads buffer X without waiting for event E recorded after producer A wrote X on stream 1.",
        "Streams are independent queues. Without an explicit wait on E, stream 2 may run B before A finishes, so B reads stale or partial data.",
        "Assuming the host Python call to A finishing means A's kernel finished confuses queuing with completion.",
        "Insert `stream2.wait_event(E)` before B, and show that with a slow producer the consumer output is correct only when the wait exists.",
    ),
    (
        "Separate `event.synchronize()`, which blocks the host thread until the event completes, from `stream.wait_event(event)`, which queues a device-side dependency and returns immediately.",
        "A host wait stalls Python and can prevent further work from being enqueued. A stream wait keeps the host free while ordering device work.",
        "Using a host synchronize everywhere fixes correctness but serializes host and device.",
        "Inspect a profiler timeline for both versions and confirm the outputs are identical.",
    ),
    (
        "Trace storage reuse: a buffer freed after its last consumer kernel is enqueued must not be handed to a new producer until that consumer completes on the device.",
        "Caching allocators reuse memory quickly. If the stream order between the old consumer and the new producer is not guaranteed, the new producer can overwrite data still being read.",
        "Freeing a buffer as soon as the host is done with its Python object assumes device work is done too.",
        "Use `record_stream` or an event so the allocator knows the last user, then test with a slow consumer.",
    ),
    (
        "Design a non-default stream test: create two non-default streams, write known values on stream 1, record an event, wait for it on stream 2 and compute on stream 2.",
        "The default stream may add implicit synchronization that hides missing waits. Using two explicit streams removes that safety net, so the test checks the intended ordering.",
        "Testing only on the default stream passes even with the wait removed.",
        "Run the test with the wait present and confirm the known result, then remove it and observe possible wrong values.",
    ),
    (
        "Explain that calling `cuda.synchronize()` everywhere can mask a missing dependency, because the global wait orders all prior work.",
        "The program then works only because of an extra global ordering, not because of explicit data edges. Removing the global wait later for performance exposes the bug.",
        "Treating a correct result with global waits as proof that dependencies are complete hides the missing event.",
        "Remove global waits one at a time in a test and keep only explicit events. Outputs must stay correct.",
    ),
]

REASONING[19] = [
    (
        "Write the kernel signature in full: `x` is a pointer to `float32`, `y` is a pointer to `float32`, and `n` is a 32-bit signed integer, then make the Python launcher pass exactly those types, for example `numpy.int32(n)`.",
        "Arguments cross the boundary as raw bytes laid out by the C ABI. The kernel reads 4 bytes for `n` and 8 bytes for each pointer, so the launcher must supply values of exactly those widths in that order.",
        "Passing a plain Python `int` for `n` and letting the wrapper guess the width may package it as 64 bits. On some interfaces that shifts the following arguments or truncates the value.",
        "Compare the launcher's argument tuple against the declared signature, type by type. A small launch with `n = 5` must produce five correct outputs.",
    ),
    (
        "Compute allocation bytes as elements times itemsize: five `float32` values need `5*4 = 20` bytes, while five `float64` values need 40.",
        "The `validate_contract` helper in the reference rejects an allocation smaller than `count*itemsize`. The call with itemsize 8 and 20 bytes fails because 40 bytes are needed.",
        "Sizing a buffer by element count alone, as if every element were one byte, under-allocates by the itemsize factor and lets the kernel write past the end.",
        "Run the reference: `validate_contract(5, 4, 20)` passes and `validate_contract(5, 8, 20)` raises. Add a negative count case and confirm it raises too.",
    ),
    (
        "Classify errors by stage: a syntax error or unknown identifier fails at compilation, while a missing device, an unsupported architecture or an invalid launch configuration fails at load or launch time.",
        "Compilation translates source for a target architecture and can succeed on a machine without that GPU. Launch requires a compatible device, driver and module, which are only checked when the kernel runs.",
        "Reporting compile success as working code treats the first stage as the whole contract. A module built for one architecture may still fail to load on another.",
        "Record three separate fields: compiled, launched and output matched. Without a device, only the first can be filled in.",
    ),
    (
        "Order cleanup so that every kernel and copy using a buffer has completed, for example by synchronizing the stream, before the buffer, the stream and the module are released.",
        "Freeing memory while queued work still reads it lets the allocator hand those bytes to new work. Destroying a stream or unloading a module with pending work is also undefined.",
        "Releasing resources in reverse creation order without waiting looks tidy, but order of creation says nothing about device completion.",
        "In a test, enqueue a long kernel, synchronize, then free, and check the output is intact. Code review should find a wait before each release.",
    ),
    (
        "Explain ABI mismatch with the example from the lesson: a kernel expecting `float32*` and a 32-bit length receives a `float64` buffer and a pointer where the integer belongs.",
        "The kernel reinterprets each 8-byte double as two 4-byte floats, producing garbage values, and reads part of a pointer as the length, which can be enormous.",
        "Expecting a type error from the device is the mistake: device code has no runtime type information about its arguments.",
        "Validate dtype and argument types in Python before launch. A test passing a `float64` array must raise in the launcher, not produce numbers.",
    ),
    (
        "Define release evidence as the exact kernel source or its hash, the compiler and runtime versions, the target architecture flags, the driver version, and the GPU used for the run.",
        "A kernel's behavior depends on how it was compiled and where it ran. Pinning those components lets someone reproduce or invalidate the result later.",
        "Recording only the Python package version omits the toolkit, driver and architecture, which are the usual causes of cross-machine failures.",
        "Another engineer should rebuild from the recorded source and versions and get the same compiled-module hash.",
    ),
]

REASONING[20] = [
    (
        "Apply `y = 2*x + 1` to `[-1, 0, 3]`: `2*(-1)+1 = -1`, `2*0+1 = 1`, `2*3+1 = 7`, so the expected output is `[-1, 1, 7]`.",
        "The kernel is elementwise and the inputs are small integers representable exactly in `float32`, so the device result should match the oracle exactly.",
        "Comparing against `2*(x+1)` by mistake gives `[0, 2, 8]` and suggests the kernel is wrong when the oracle is.",
        "The reference asserts `affine([-1, 0, 3]) == [-1, 1, 7]`. Compare the CuPy result with `numpy.array_equal` after converting to host.",
    ),
    (
        "Compute the launch for 257 elements with 128 threads per block: `(257 + 127) // 128 = 3` blocks, which provide 384 lanes.",
        "Two blocks give 256 lanes, one short. The third block covers index 256 plus 127 lanes beyond the data, and the guard `if (i < n)` inside the raw kernel source must skip them.",
        "Using `257 // 128 = 2` blocks loses the final element silently, a bug invisible on sizes like 256.",
        "The reference asserts the block count is 3. A device test with 257 elements must show the last output equals `2*x[256] + 1`.",
    ),
    (
        'Explain that `cupy.RawKernel(code, name)` compiles the source and then looks up the function by `name`, so the name must match the exported symbol, which usually means declaring the kernel `extern "C"`.',
        'C++ compilers mangle function names to encode argument types. Without `extern "C"`, the exported symbol differs from the plain name and the lookup fails.',
        "Assuming a lookup error means the source failed to compile misdirects debugging to the kernel body.",
        'Compile once with `extern "C"` and once without, and observe that only the first lookup by plain name succeeds.',
    ),
    (
        "Decide the layout contract: either require C-contiguous input, checking `x.flags.c_contiguous` and raising otherwise, or pass strides to the kernel and index with them.",
        "The raw kernel indexes `x[i]` assuming consecutive elements. A view like `x[::2]` has a larger stride, so the kernel would read the wrong elements.",
        "Silently calling `cupy.ascontiguousarray` inside the wrapper fixes correctness but hides a copy, and with in-place updates it writes to the copy instead of the caller's array.",
        "Pass `x[::2]` and confirm the wrapper either raises or returns the same result as applying the formula to the strided view.",
    ),
    (
        "Time the first call separately because it includes compilation and module loading. Warm up the same kernel with the same types, then time steady-state launches with synchronization.",
        "CuPy compiles raw kernels lazily and caches them, so the first call measures compilation. Mixing it into an average distorts steady-state numbers.",
        "Timing a single call and reporting it as kernel speed mostly measures the compiler.",
        "Record first-call and steady-state times separately. Timing without synchronization should be avoided, since it only measures the enqueue.",
    ),
    (
        "Compare the raw kernel with the library expression `2*x + 1` in CuPy using the same input, dtype and tolerance, and time both on completed work.",
        "The library path may fuse operations or launch one or two kernels. A fair comparison needs identical outputs first, then timings with synchronization.",
        "Comparing a float32 raw kernel against a float64 library expression measures dtype rather than implementation.",
        "Assert both outputs are equal for the test input, record dtype, size and the timing method, and report the result as measured on a named device.",
    ),
]

REASONING[21] = [
    (
        "Add every component of latency: the library path is 8 ms of kernels plus 2 ms of transfer, 10 ms; the custom path is 6 + 2 + 3 ms of packing, 11 ms.",
        "The custom kernel itself is 2 ms faster, but packing adds 3 ms. End-to-end latency is what callers experience, so the custom path is worse by 1 ms in this model.",
        "Comparing kernel times alone, 6 against 8 ms, declares the custom version a win while ignoring the new packing step.",
        "The reference asserts totals of 10 and 11. Recompute after removing packing to check the comparison flips only when packing is eliminated.",
    ),
    (
        "Write the numerical contract for the operation: input shape and dtype, output dtype, tolerance against a reference, and behavior on empty inputs, NaN and overflow.",
        "A replacement kernel must meet the same contract as the library. Without a written contract, a faster kernel that rounds differently or mishandles NaN looks like an improvement.",
        "Testing only that the shapes match accepts any numbers of the right size, so a kernel that returns zeros, or that silently turns NaN inputs into finite outputs, would pass every check.",
        "Turn each clause into a test and run it against both implementations: a random input compared with tolerance, an empty input, an input containing NaN, and an input near the dtype maximum. Both must pass the same suite.",
    ),
    (
        "Count temporary memory as the peak sum of buffers alive at the same time. For example, input, a packed copy and the output of `N` float32 values each give `3*4*N` bytes at peak, not `2*4*N`.",
        "Peak memory decides whether a workload fits. The packed buffer coexists with the input during packing and with the output during the kernel.",
        "Summing only the input and output ignores intermediates, so the custom path can run out of memory at a size where the library path fit, even though both outputs are the same size.",
        "Measure peak allocation with the library's memory pool statistics, such as CuPy's `get_default_memory_pool().used_bytes()`, for a known size and compare with the arithmetic. Free the pool between runs so caching does not hide the peak.",
    ),
    (
        "Name a maintenance cost: a custom kernel must be recompiled and requalified for new GPU architectures, toolkit versions and compiler changes, while the library vendor handles that work.",
        "Hand-tuned kernels encode assumptions about one generation's resources. A new architecture can change the best tile size or break inline assembly.",
        "Counting only the development time ignores ongoing cost, which repeats every time the team adopts a new GPU or toolkit release and often exceeds the original effort.",
        "List the owner of each requalification step and the test that must pass on each supported architecture. If no one owns the step, the kernel has no maintenance plan.",
    ),
    (
        "Choose two workload sizes: a tiny input, where launch and first-call overheads dominate, and a representative bounded input sized like production work.",
        "The fused kernel can win at the representative size by removing intermediates while losing at the tiny size because of compilation and launch cost.",
        "Benchmarking only at the largest size that fits hides the small-input behavior, which matters when production calls are mostly small batches.",
        "Report both sizes with the same correctness checks, warm-up policy and synchronized timing method, and state the device used. Without a GPU, mark both timings as not measured.",
    ),
    (
        "Write the decision: keep the library unless measured end-to-end gains on representative inputs exceed the added maintenance, testing and portability obligations. Here keep it, since the custom path is slower.",
        "The modeled custom path loses 1 ms end to end and adds obligations, so nothing justifies the switch.",
        "Choosing the custom kernel because its compute portion, 6 ms against 8 ms, is faster ignores the stated total and the packing step that the custom path requires.",
        "Include the totals, sizes, contract and the owner list in the decision record, so a later reviewer can repeat the decision if packing is removed or the library changes.",
    ),
]

REASONING[22] = [
    (
        "Compute the column means of `[[1, 2], [3, 4]]`: column 0 averages `(1+3)/2 = 2` and column 1 averages `(2+4)/2 = 3`, so the means are `[2, 3]`.",
        "Fitting is a reduction along rows for each column. The reference computes `sum(row[c] for row in rows)/len(rows)` per column, giving exactly `[2, 3]`.",
        "Averaging along columns, the per-row means, gives `[1.5, 3.5]` and centers the wrong axis.",
        "Assert `means == [2, 3]`. On a GPU, `cupy.mean(X, axis=0)` should match after transfer.",
    ),
    (
        "Center each row by subtracting the means, giving `[[-1, -1], [1, 1]]`, then score with weights `[2, -1]`: `2*(-1) + (-1)*(-1) = -1` and `2*1 + (-1)*1 = 1`.",
        "Scoring is a dot product of each centered row with the weights. The reference zips each centered row with the weights and asserts `scores == [-1, 1]`.",
        "Scoring the raw rows gives `[0, 2]`, which skips the fitted transformation.",
        "Assert the scores in the reference, and check that the GPU version uses the same means array as the training fit.",
    ),
    (
        "Add a constant column such as `[5, 5]`: its mean is 5 and centering produces zeros. State a scale policy, for example leave the column unscaled or drop it, because its standard deviation is 0.",
        "Centering is well defined for a constant, but dividing by a zero standard deviation produces NaN or infinity.",
        "Dividing by the standard deviation without a check fills the column with NaN, which spreads into the scores.",
        "Run the pipeline with a constant column and assert the output has no NaN and the column handling matches the stated policy.",
    ),
    (
        "Draw owners and waits: the training array owns the fitted means, the scoring step reads those means and the input batch, and the output buffer must stay alive until the final copy to host completes.",
        "Each buffer has a producer and a final consumer. Without an explicit wait, the host might read scores before the scoring kernel finishes.",
        "Drawing only the computation steps without owners loses track of when buffers can be freed.",
        "Annotate each edge with the event or synchronization that orders it, and check that every buffer's release comes after its last consumer.",
    ),
    (
        "Fit the means only on the training subset and reuse those means for validation rows, never recomputing them on the validation data.",
        "Recomputing means on validation data changes the transformation and leaks information about the evaluation set into preprocessing.",
        "Fitting on the concatenated train and validation data is a subtler leak with the same effect: validation scores look better than they would on truly unseen rows.",
        "Store the fitted means as an explicit object, then confirm validation centering uses them by testing a validation row with a known expected value.",
    ),
    (
        "Write the acceptance report with the computed values, tolerances, the timing method and boundaries such as whether transfers are included, plus unsupported cases like constant columns.",
        "A capstone result is useful only if a reader can see what was checked and what was not.",
        "Reporting a single speedup number leaves out correctness and the scope of the claim, so readers cannot tell whether transfers were timed or whether the means were reused.",
        "Check each report field against the pipeline tests. Mark device timings not attempted if no GPU ran.",
    ),
]

REASONING[23] = [
    (
        "Differentiate the mean squared error with respect to the scalar weight: the derivative is the average of `2*x*(w*x - y)`. At `w = 0` the two terms are `2*1*(0-2) = -4` and `2*2*(0-4) = -16`, so the mean gradient is -10.",
        "The loss is the average of `(w*x - y)**2` over the batch, and the chain rule gives `2*(w*x - y)*x` per example. Averaging matches the mean reduction used for the loss, which is 10 here from `(4 + 16)/2`.",
        "Dropping the factor 2 from the derivative, a common slip when writing it by hand, gives -5 and a half-size update. Autograd would then disagree with the hand derivation.",
        "Run the reference, which asserts `loss == 10` and `grad == -10`. In PyTorch, call `loss.backward()` on a tensor `w` with `requires_grad=True` and check `w.grad` equals -10.",
    ),
    (
        "Apply plain SGD with learning rate 0.1: `w = 0 - 0.1*(-10) = 1`.",
        "SGD subtracts the learning rate times the gradient. A negative gradient means increasing `w` lowers the loss, and the data satisfy `y = 2*x`, so moving from 0 toward 2 is the right direction.",
        "Adding the gradient instead of subtracting it gives `w = -1`, which raises the loss to `((-1-2)**2 + (-2-4)**2)/2 = 22.5`. The sign error is easy to miss when only the update size is checked.",
        "The reference asserts `w == 1` after the update. In a framework, compare the parameter after `optimizer.step()` with 1 and confirm the recomputed loss drops from 10 to 2.5.",
    ),
    (
        "Repeat the step with a sum loss instead of a mean: the loss becomes 20, the gradient `-4 + -16 = -20`, and the update moves `w` to 2.",
        "A sum reduction scales the gradient by the batch size, 2 here, which has the same effect as doubling the learning rate. The two runs are different training procedures.",
        "Comparing a sum-loss run with a mean-loss run and attributing the speed or convergence difference to the GPU confounds hardware with loss normalization.",
        "Compute both updates and confirm they differ by exactly the batch-size factor. Record the reduction mode in every training comparison.",
    ),
    (
        "List every tensor involved in the step, including inputs `x`, targets `y`, the parameter `w`, its gradient and any optimizer state such as momentum buffers, and print each one's `.device`.",
        "All operands of one operation must live on the same device. A target left on the CPU or an optimizer state created before `model.to(device)` produces an error or an unintended copy.",
        "Checking only the model parameters misses inputs and targets, and moving the model after creating the optimizer can leave the optimizer holding stale references in some setups.",
        "Write a helper that collects devices from all tensors in the step and asserts the set has one element. It should fail when `y` stays on the CPU.",
    ),
    (
        "Write one contract for both frameworks: the same `x`, `y`, initial `w = 0`, mean reduction, learning rate 0.1 and float32 dtype, then compare the loss, gradient and updated weight.",
        "PyTorch and TensorFlow use different APIs, but with identical data, initialization and reduction they must produce loss 10, gradient -10 and weight 1 up to float rounding.",
        "Letting each framework use its default initializer or loss reduction makes the numbers differ for reasons unrelated to correctness.",
        "Assert both frameworks produce 10, -10 and 1 within a small tolerance. A mismatch then points to a contract difference, which can be found field by field.",
    ),
    (
        "Separate correctness from performance: first confirm outputs and gradients agree with the oracle, and only then time the step on the device with synchronization.",
        "A fast step computing the wrong update is not an improvement. Timing results matter only after the numbers are known to be right.",
        "Reporting a speedup from a run that silently used a sum loss, or ran partly on the CPU, compares different computations.",
        "Store correctness results next to each timing, and reject any timing whose correctness check is missing or failed.",
    ),
]

REASONING[24] = [
    (
        "Add the stage times for a serial pipeline: 6 ms of preparation plus 4 ms of compute gives 10 ms per batch.",
        "In a serial loop the GPU waits while the CPU prepares the next batch, and the CPU waits while the GPU computes, so per-batch time is the sum of both stages.",
        "Reporting the 4 ms GPU compute time as the step time ignores the 6 ms the GPU spends idle waiting for input.",
        "The reference asserts `serial == 10`. On a real system, time the loop with the device synchronized at each step and compare with the sum.",
    ),
    (
        "Bound ideal overlapped throughput by the slowest stage: `max(6, 4) = 6` ms per batch in steady state after the first batch fills the pipeline.",
        "With prefetching, preparation of batch `k+1` overlaps compute of batch `k`. The GPU still waits 2 ms each batch because preparation is slower, so the bound is 6 ms, not 4.",
        "Claiming overlap reduces the step to 4 ms assumes the input stage becomes free. Only a faster or more parallel preparation stage can move the bound below 6 ms.",
        "The reference asserts `ideal == 6`. A trace of an overlapped run should show GPU idle gaps of about 2 ms per batch.",
    ),
    (
        "Budget the prefetch queue: three batches of 8 MiB need `3*8*1024*1024 = 25165824` bytes for payloads alone.",
        "Each queued batch holds its own tensors until consumed. Decoder buffers, pinned staging copies and framework overhead come on top of this floor.",
        "Budgeting one batch because only one is used at a time ignores that all queued batches are resident at once.",
        "The reference asserts the byte count. Watch host memory while increasing queue depth and confirm growth of roughly 8 MiB per extra batch.",
    ),
    (
        "Explain pinned host memory: page-locked buffers allow asynchronous DMA transfers with `non_blocking=True`, while ordinary pageable memory is staged through a driver buffer before copying.",
        "Pinning enables overlap of copy and compute and usually faster transfers, but pinned pages cannot be swapped, so pinning too much reduces memory available to the operating system.",
        "Pinning every buffer by default can starve the host and slow the whole machine.",
        "Compare a transfer from a pinned tensor with one from a pageable tensor in a profiler trace, and record pinned memory totals.",
    ),
    (
        "Run a diagnostic with a batch already resident on the GPU, repeating the compute step with no input pipeline, to measure the compute-only step time.",
        "If the resident-data step is much faster than the full pipeline, input preparation is the bottleneck. The diagnostic isolates one cause.",
        "Reporting the resident-data speed as production throughput ignores that real training must load new data every step.",
        "Report the resident and full-pipeline times side by side, labeled as a diagnostic and a production estimate.",
    ),
    (
        "Vary one loader setting at a time, such as worker count from 1 to 2 to 4 with a fixed queue depth, and stop at an explicit upper bound.",
        "Changing workers and queue depth together makes it impossible to attribute an improvement. Each extra worker also costs CPU memory and process startup.",
        "Raising all settings to their maximum at once may exhaust host memory or CPU cores and still hide which change helped.",
        "Record step time and host memory for each setting. The best setting should be confirmed by repeating it.",
    ),
]

REASONING[25] = [
    (
        "Build a ledger of training state for 1000 float32 parameters: parameters, gradients and two Adam moment arrays, four arrays of `1000*4` bytes, for 16000 bytes total.",
        "Each tensor that exists during training gets its own line with element count and itemsize. Adam keeps first and second moments per parameter, which doubles state beyond parameters and gradients.",
        "Counting parameters only, 4000 bytes, underestimates training memory by four times for this optimizer.",
        "The reference asserts `state_bytes == 16000`. In PyTorch, sum `numel()*element_size()` over parameters, gradients and optimizer state and compare.",
    ),
    (
        "Add saved activations as batch times elements per example times itemsize: `8*128*4 = 4096` bytes for one saved tensor of 128 float32 values per example.",
        "Autograd saves intermediate values for the backward pass, and their size scales with batch size. The reference adds two such tensors: `16000 + 2*4096 = 24192` bytes.",
        "Ignoring activations because they are temporary misses that they live from forward until backward, which is when memory peaks.",
        "Assert the 24192 total from the reference, then double the batch to 16 and confirm the activation portion doubles to 8192 bytes per tensor.",
    ),
    (
        "Distinguish reserved memory from allocated memory: `torch.cuda.memory_allocated` counts bytes held by live tensors, while `memory_reserved` also counts free blocks the caching allocator keeps.",
        "The allocator keeps freed blocks for reuse to avoid expensive device allocations, so reserved bytes can stay high after tensors are freed.",
        "Reading the reserved number in a monitoring tool and concluding tensors are leaking confuses cache with live usage. Tools such as `nvidia-smi` report the reserved total, so they show this inflated number.",
        "Allocate and delete a large tensor, then show allocated memory returns to its prior value while reserved memory stays higher.",
    ),
    (
        "Diagnose a retained graph: storing `losses.append(loss)` each step keeps each step's autograd graph alive. Store `loss.item()` or `loss.detach()` instead.",
        "A loss tensor that requires grad references its graph and saved activations. Keeping one per step grows memory linearly with step count, independent of batch size.",
        "Blaming a fixed-size growth per step on fragmentation or the allocator leads to tuning allocator settings that do not fix the reference leak.",
        "Track allocated memory per step with both versions. The detached version stays flat, while the retained version rises each step.",
    ),
    (
        "Explain that allowing memory growth in a framework changes how memory is reserved from the device, incrementally rather than all at once, but does not change the bytes the model needs at peak.",
        "Growth settings affect allocation policy and sharing with other processes. If the peak live bytes exceed the device, growth only delays the out-of-memory error.",
        "Turning growth on to fix an out-of-memory error treats a policy as a capacity increase.",
        "Compare the peak allocated bytes with growth on and off for the same step. They should match.",
    ),
    (
        "Design a batch-size experiment that steps through small fixed sizes such as 8, 16 and 32, records peak memory for each and stops well before the device limit.",
        "Peak memory grows roughly linearly with batch size, so a few points allow extrapolation. Bounded steps avoid crashing a shared GPU.",
        "Doubling until the program crashes uses an out-of-memory error as the measurement and can disrupt other users.",
        "Fit peak memory against batch size from the recorded points and check the slope matches the activation ledger.",
    ),
]

REASONING[26] = [
    (
        "Trace the scaled value: a gradient of 0.5 multiplied by scale 1024 becomes 512 during backpropagation, and dividing by 1024 once before the optimizer step restores 0.5.",
        "Loss scaling multiplies the loss so small gradients stay representable in float16, and every gradient is scaled by the same factor. Unscaling exactly once gives the true gradient.",
        "Unscaling twice, once manually and once by the scaler, produces `0.5/1024`, an update so small that training appears to stall without any error.",
        "Compute `512/1024 == 0.5` by hand. In PyTorch, call `scaler.unscale_(optimizer)` and inspect `p.grad` for a known small model, comparing with a float32 run.",
    ),
    (
        "Explain overflow handling: when scaled gradients contain infinity or NaN, the supported scaler skips the optimizer step and lowers the scale, then raises it again after a run of finite steps.",
        "A scale large enough to prevent underflow can overflow float16, whose largest finite value is 65504. Skipping the update avoids writing nonfinite values into parameters.",
        "Replacing infinities with zero, or clipping them, so the step can proceed corrupts the update with values unrelated to the true gradient.",
        "Force an overflow with a very large scale on a tiny model and confirm the parameters are unchanged after the step and the scale decreased.",
    ),
    (
        "Unscale before clipping: with gradient 0.5, unscaling 512 gives 0.5, and clipping to threshold 1 leaves 0.5, which is the intended clipped gradient.",
        "Clipping thresholds are defined in units of the true gradient. The reference computes `min(scaled/scale, 1.0) == 0.5` for the correct order.",
        "Clipping the scaled 512 to 1 and then unscaling gives `1/1024 = 0.0009765625`, the wrong value the reference asserts for the reversed order. Training then barely moves.",
        "Run the reference and confirm both assertions. In code, check that `unscale_` appears before `clip_grad_norm_`.",
    ),
    (
        "Compare float16 and bfloat16: float16 has 5 exponent bits and 10 mantissa bits, while bfloat16 has 8 exponent bits, the same as float32, and 7 mantissa bits.",
        "bfloat16 covers the float32 range, so gradients rarely underflow and loss scaling is usually unnecessary, but it has less precision. float16 is more precise but has a narrow range.",
        "Assuming both 16-bit formats behave the same leads to dropping loss scaling for float16, where small gradients flush to zero.",
        "Cast `1e-8` to both types: float16 gives 0, bfloat16 keeps a nonzero value. Cast `1 + 2**-9`: float16 keeps it, bfloat16 rounds to 1.",
    ),
    (
        "Run a float32 baseline with the same initialization, batches, loss and number of steps, and compare loss curves and final metrics with the mixed-precision run.",
        "Only a matched baseline can show whether reduced precision changed the training outcome. Differences in seeds or data order would otherwise be confused with precision effects.",
        "Comparing the mixed-precision run with an older float32 run using a different seed attributes noise to precision.",
        "Record seed, data order and step count for both runs and require the final loss to fall within an agreed tolerance.",
    ),
    (
        "Record quality metrics, such as final loss and validation accuracy, separately from throughput, such as samples per second, for both precision settings.",
        "Mixed precision can raise throughput while degrading quality. A combined score hides which side changed.",
        "Reporting the speedup without the quality comparison can justify a configuration that fails to train properly.",
        "Present a table with both metrics per configuration, and accept mixed precision only if quality meets the baseline tolerance.",
    ),
]

REASONING[27] = [
    (
        "Write the cross-correlation formula used by deep learning libraries: `out[i] = sum(x[i+j]*k[j] for j in range(len(k)))`, with no kernel flip.",
        "For `x = [1, 2, 3, 4]` and `k = [1, -1]`, each output is `x[i] - x[i+1] = -1`, giving `[-1, -1, -1]`. Mathematical convolution flips the kernel and gives `[1, 1, 1]`.",
        "Writing a reference with `k[len(k)-1-j]`, textbook convolution, flips every sign compared with the library, which looks like a broken GPU kernel.",
        "The reference asserts `out == [-1, -1, -1]`. Compare against `torch.nn.functional.conv1d` on the same values.",
    ),
    (
        "Compute the valid output length as input length minus kernel length plus one: `4 - 2 + 1 = 3`.",
        "With no padding, the kernel slides only over positions where it fits entirely. There are three such starting positions, 0, 1 and 2.",
        "Using input length as output length assumes same padding, adding an output whose computation needs a value beyond the input.",
        "Check the reference's `range(len(x)-len(k)+1)` produces three outputs, and confirm the library's output shape matches.",
    ),
    (
        "Include layout conversion in total latency: with conversion cost 2 ms and saving 1 ms per call against 2 ms unconverted, one call costs `2 + 1 = 3` ms against 2, while four calls cost `2 + 4 = 6` against 8.",
        "The conversion is paid once and the saving accrues per reuse, so it pays off only when the converted data is reused enough. The reference asserts both inequalities.",
        "Counting only the faster convolution, 1 ms against 2, declares conversion a win even for a single call.",
        "Evaluate both expressions and note the break-even at two calls, where both total 4 ms.",
    ),
    (
        "Compare forward and backward costs: training runs the forward convolution plus two backward convolutions, for input gradients and weight gradients, and each may choose a different algorithm.",
        "An algorithm or layout that speeds the forward pass can slow the backward ones. Training time depends on all three. Inference, by contrast, only runs the forward pass, so the best choice can differ between the two uses.",
        "Benchmarking only the forward pass and applying the result to training ignores roughly two thirds of the convolution work.",
        "Time forward and backward separately in a profiler for each candidate layout, and confirm gradients match a reference.",
    ),
    (
        "Explain algorithm warm-up: with benchmark mode enabled, cuDNN tries several algorithms for each new shape on the first call and caches the fastest.",
        "The first iteration for each shape includes that search, so it is much slower than steady state. New shapes trigger a new search.",
        "Timing the first iteration and concluding the configuration is slow measures the search.",
        "Discard warm-up iterations for every shape and record their count. Steady-state times should be stable. Without a GPU, record the plan and mark the timings as not measured.",
    ),
    (
        "Design two shape cases with unchanged semantics: a narrow batch such as 1 and a wider batch such as 32, same channels, kernel size and padding.",
        "The best algorithm and layout can differ by shape, so one size may not represent the workload. A batch of 1 may favor a different algorithm than a batch of 32, and conversion overhead weighs more when each call does little work.",
        "Testing a single shape and generalizing the chosen layout risks regressions at other batch sizes. Production traffic that mixes sizes then sees the slow path.",
        "Verify outputs for both shapes against a reference, then report time per sample for each.",
    ),
]

REASONING[28] = [
    (
        "Compute wall time as latest completion minus earliest start: preparation runs 0 to 6 ms and GPU work 2 to 10 ms, so the step takes `10 - 0 = 10` ms.",
        "The intervals overlap from 2 to 6 ms, so their durations cannot be added. Wall time is what the step costs end to end.",
        "Summing durations, `6 + 8 = 14` ms, double counts the 4 ms overlap and overstates the step.",
        "The reference asserts `summed == 14` and `wall == 10`. Read both numbers off the trace to confirm.",
    ),
    (
        "Find the overlap of the two intervals: `max(0, 2) = 2` to `min(6, 10) = 6`, so 4 ms of overlap.",
        "Two intervals overlap when each starts before the other ends. Here CPU preparation for the next step runs while the GPU executes.",
        "Treating events on different rows of the trace as sequential hides the concurrency that is already happening. The step then looks like it needs a faster GPU when the existing overlap is already working.",
        "Check `wall == summed - overlap`, which gives `14 - 4 = 10`, consistent with the reference.",
    ),
    (
        "Look for host reads of device scalars between kernels, such as `loss.item()` or `print(tensor)` each step, which appear in the trace as gaps followed by device-to-host copies.",
        "Materializing a device value on the host requires the GPU to finish queued work first, which forces the host to wait and stops it from enqueueing further work.",
        "Blaming the gaps on slow kernels leads to optimizing compute while the host dependency stays. Faster kernels only make the GPU wait longer for the next enqueue.",
        "Remove the per-step read in a test and confirm the gaps disappear. Then log aggregated values every N steps. The logged numbers must match the per-step values averaged over the same window.",
    ),
    (
        "Name the profiler's overhead: detailed tracing with stacks, memory recording and shape capture adds host work and memory, which changes timing.",
        "A profiler observes by instrumenting. The trace shows relative structure well, but absolute numbers include instrumentation cost.",
        "Quoting step times from a detailed profiler run as production numbers overstates the step time.",
        "Compare step times with profiling on and off. The difference estimates overhead. Also compare peak memory, since recording shapes and stacks keeps extra host and device allocations alive.",
    ),
    (
        "Propose one targeted change, such as replacing per-step `loss.item()` with an aggregated log every 100 steps, and leave everything else fixed.",
        "Changing one thing lets the trace before and after show its effect clearly. If the step time does not change, the hypothesis about the bottleneck was wrong, which is also useful evidence.",
        "Applying several optimizations at once makes it impossible to tell which helped or which hurt. One change might help while another reintroduces a synchronization.",
        "Take a new trace and confirm the forced synchronizations are gone while losses remain the same.",
    ),
    (
        "Verify the improvement outside the profiler: run synchronized, uninstrumented timings over many steps for both versions and confirm the outputs are equal.",
        "Profiler numbers include overhead, so the final claim must come from clean measurements. Equal outputs confirm the change did not alter what the step computes.",
        "Reporting the speedup measured under the profiler assumes overhead is equal in both versions. Removing host reads also removes instrumented events, so overhead itself changes.",
        "Report the median step time over a fixed number of steps after warm-up for both versions, with equal loss values.",
    ),
]

REASONING[29] = [
    (
        "Count specializations by collecting distinct shape signatures: the calls `(4, 8)`, `(4, 8)` and `(8, 8)` form the set `{(4, 8), (8, 8)}`, so the simplified cache compiles twice.",
        "A shape-specialized compiler such as `torch.compile` with static shapes keys its cache on input shapes and dtypes. A repeated signature reuses the cached code, while a new leading dimension triggers another compilation.",
        "Counting one compilation per call, three here, ignores the cache and overestimates startup cost. Counting one compilation total assumes the compiler generalizes across shapes, which static specialization does not.",
        "The reference asserts `len(set(shapes)) == 2`. With a real compiler, enable recompilation logging and confirm exactly two compile events for this call sequence.",
    ),
    (
        "Divide the compile cost by the per-call saving: `500 / 1 = 500` calls repay the 500 ms compilation, so at 500 calls the two paths tie and from call 501 the compiled path is ahead.",
        "Total compiled cost is `500 + c*(t-1)` against `c*t` uncompiled for `c` calls with per-call time `t`. The difference is `500 - c`, which is zero at 500 and negative afterward.",
        "Assuming compilation pays off immediately because each call is faster ignores the startup cost. A short-lived job of 100 calls loses 400 ms overall.",
        "The reference asserts the ratio is 500. Recompute with a 2 ms saving and confirm the break-even halves to 250 calls.",
    ),
    (
        "Describe a graph break: when the compiler meets something it cannot trace, such as a data-dependent Python branch on a tensor value or a call to an unsupported library, it ends the compiled region, runs that code eagerly and starts a new region.",
        "Each break splits the graph, reducing fusion opportunities and adding transitions between compiled and eager execution. Correctness is preserved, but expected speedups can disappear.",
        "Assuming a program that ran without errors under the compiler was compiled as one graph overlooks silent breaks, which are reported only when logging is enabled.",
        "Enable graph-break reporting, for example `torch._dynamo.explain`, and record the number of graphs and the reason for each break.",
    ),
    (
        "Specify the accepted shape set explicitly, such as batch sizes 4 and 8 with a fixed feature width 8 and float32 dtype, and reject or pad other inputs.",
        "A bounded set keeps compilation count bounded and predictable. Padding inputs to the nearest accepted size trades some wasted work for avoiding new compilations.",
        "Accepting arbitrary shapes in production lets each new batch size trigger a recompilation, causing latency spikes.",
        "Send an input outside the set and confirm it is rejected or padded, and that the compile count stays at the expected value.",
    ),
    (
        "Compare gradients between compiled and eager execution, not only forward outputs, by computing `backward()` in both and comparing parameter gradients with a tolerance.",
        "Compilers transform the backward graph separately and may fuse or reorder its operations. A forward match says nothing about backward correctness.",
        "Checking only that forward outputs match and assuming gradients follow can miss a backward bug that shows up only as slower training.",
        "Use the same inputs and initial parameters for both modes and compare every gradient tensor within float32 tolerance.",
    ),
    (
        "Separate compilation, which generates and optimizes kernels for a shape, from CUDA graph replay, which records a fixed sequence of launches and reissues it with low launch overhead.",
        "Replay requires static shapes and fixed memory addresses. It reduces CPU launch cost but does not by itself change the kernels.",
        "Expecting graph replay to speed up compute-bound kernels confuses launch overhead with kernel time.",
        "Profile a step before and after enabling graph capture and compare host launch time and kernel time separately.",
    ),
]

REASONING[30] = [
    (
        "List every field that affects the next update: model weights, optimizer state such as the momentum buffer `v`, the learning-rate scheduler state, the gradient scaler state, the step counter, random generator states and the position of the data sampler.",
        "Exact continuation means the resumed run computes the same next update as the uninterrupted run. Any omitted field that influences that update makes the two runs diverge.",
        "Saving only `model.state_dict()` because that is what inference needs leaves out optimizer and sampler state, which training needs.",
        "Save, reload, take one step, and compare with one step of the uninterrupted run. Every saved field should be justified by a change it causes when omitted.",
    ),
    (
        "Carry the velocity through the restart: with `w = 1.0`, `v = 0.5` and gradient 0.2, the next velocity is `0.9*0.5 + 0.2 = 0.65` and the new weight is `1.0 - 0.1*0.65 = 0.935`.",
        "Momentum SGD updates `v = 0.9*v + g` and then `w = w - lr*v`, so the previous velocity contributes `0.45` of the step. The reference asserts the continued weight is 0.935.",
        "Recomputing velocity from the current gradient alone, `v = g`, gives `1.0 - 0.1*0.2 = 0.98`, the weights-only value, which ignores accumulated history.",
        "Check `abs(continued - 0.935) < 1e-12` from the reference and that it differs from `weights_only`.",
    ),
    (
        "Diagnose a weights-only restart: velocity restarts at zero, so the first resumed step moves `w` to 0.98 instead of 0.935, and the trajectory differs from then on.",
        "The momentum state is part of the optimizer trajectory. Resetting it produces a different, slower update after each restart, so training curves show a visible discontinuity.",
        "Treating the difference as random noise from reloading misses that it is deterministic: the same restart always produces the same wrong value.",
        "Compare the first resumed step with the uninterrupted step. A difference equal to `lr*0.9*v`, 0.045 here, identifies the missing velocity.",
    ),
    (
        "Persist the sampler position, such as the next unconsumed batch index 3 or the sampler's random state plus epoch, so the resumed run starts at batch 3.",
        "A checkpoint taken after batch 2 represents a model that has seen batches 1 and 2. Resuming at batch 3 preserves exact data exposure.",
        "Restarting the epoch from the beginning replays batches 1 and 2, which double counts them, while skipping to a new shuffle may omit batch 3 entirely.",
        "Record the batch indices consumed before and after resume and assert their union is one complete pass with no repeats.",
    ),
    (
        "Save only at a boundary after a completed optimizer step, when weights, optimizer state and step counter are all consistent, not between `backward()` and `optimizer.step()`.",
        "Between backward and step, gradients exist but weights do not yet reflect them. A checkpoint there pairs updated statistics with old weights or loses gradients entirely.",
        "Saving from a signal handler at an arbitrary moment can capture a half-updated state.",
        "Add a check that the saved step counter equals the number of completed optimizer steps, and resume from a checkpoint to confirm the next step matches.",
    ),
    (
        "Define tolerance for resuming on different hardware: document an expected agreement, such as relative difference below a stated threshold on loss after N steps, instead of byte equality.",
        "Different GPUs and libraries may choose different kernels and summation orders, so floating results differ slightly even with identical state.",
        "Requiring byte-identical weights across hardware leads to false failures that obscure real restart bugs.",
        "Resume the same checkpoint on two machines and compare loss curves within the documented tolerance, recording both environments.",
    ),
]

REASONING[31] = [
    (
        "Compute throughput as items divided by completed seconds: 32 items in 0.008 s gives `32 / 0.008 = 4000` items per second.",
        "Throughput measures how much work finishes per unit of time over a completed batch. The reference asserts `throughput == 4000`, using the time at which the whole batch is done.",
        "Dividing by the time until the batch was enqueued rather than completed inflates throughput, because GPU work is asynchronous and the enqueue returns almost immediately.",
        "Synchronize before stopping the timer, and confirm the measured items per second times the batch time equals the batch size.",
    ),
    (
        "Separate amortized cost from latency: `0.008 / 32 = 0.00025` s is the cost per item averaged over the batch, but each request in the batch waits the whole 8 ms, plus any time spent queuing for the batch to fill.",
        "A request's latency runs from its arrival to its response. Batching shares the 8 ms of execution among 32 items, yet none of them finishes before the batch completes.",
        "Reporting 0.25 ms as request latency promises response times that no request experiences, and service level objectives built on it will fail.",
        "Record arrival and completion times per request in a serving test. The minimum latency should be at least the 8 ms batch time.",
    ),
    (
        "Call `model.eval()` to switch dropout and batch normalization to inference behavior, and wrap inference in `torch.inference_mode()` to disable gradient tracking.",
        "`eval()` changes module behavior, while `inference_mode` controls autograd. They are independent switches, so both are needed for correct and efficient inference.",
        "Using only `torch.no_grad()` keeps dropout active, so predictions vary between calls, and batch normalization keeps updating running statistics.",
        "Run the same input twice with dropout in the model: outputs must be identical after `eval()` and may differ without it.",
    ),
    (
        "In TensorFlow pass `training=False` when calling the Keras model for inference, which controls dropout and batch normalization behavior.",
        "Keras layers read the `training` argument to choose behavior. Calling `model(x)` directly in custom code may default to a mode that does not match evaluation.",
        "Assuming `model.predict` and `model(x)` behave the same in every custom layer is risky when a layer reads `training` differently.",
        "Compare outputs of `model(x, training=False)` across repeated calls; they must be identical when dropout is present.",
    ),
    (
        "Measure cold start as separate phases: process start and model load, first execution including any compilation or algorithm search, then steady-state execution.",
        "First requests after deployment pay one-time costs. Separating phases shows whether a slow first response comes from loading weights or from first-call compilation.",
        "Averaging cold start into steady-state latency hides a multi-second first response. Autoscaling services start new replicas often, so cold start can affect many users.",
        "Record a timestamp after each phase in a fresh process and report each phase separately.",
    ),
    (
        "Test the exported signature: send an input with an unsupported shape or dtype, such as float64 when the signature declares float32, and confirm a clear rejection.",
        "The exported model has a fixed contract. Explicit rejection is better than silent casting, which can change numerical behavior.",
        "Letting the runtime cast silently makes accepted inputs ambiguous. A float64 request cast to float32 loses precision without anyone noticing.",
        "Write tests for one valid and two invalid inputs and assert the error messages name the expected signature.",
    ),
]

REASONING[32] = [
    (
        "Compute the validation MSE for predictions `[1, 2, 3]` against targets `[1, 3, 2]`: squared errors `0, 1, 1` sum to 2, divided by 3 gives `2/3`.",
        "MSE averages squared errors over all validation examples. The reference computes this and asserts it is within `1e-12` of `2/3`.",
        "Reporting the training loss in place of the validation metric mixes data used for fitting with data held out for evaluation.",
        "Run the reference and confirm the printed report lists `examples` 3 and `mse` about 0.6667.",
    ),
    (
        "Write a sample ledger with counts for training, validation and consumed examples, such as 3 validation examples evaluated and the number of training samples seen at checkpoint time.",
        "Metrics depend on their denominators. A ledger makes it visible when an optimization changes how many examples were evaluated.",
        "Accepting a candidate that is twice as fast but evaluates only half the held-out examples compares different metrics.",
        "Assert the validation count in each report equals the full held-out set size before comparing metrics.",
    ),
    (
        "Define a memory budget with separate lines for weights, optimizer state, activations and allocator reserve, each in bytes for the chosen dtype and batch size.",
        "Separate lines show which component grows when batch size or optimizer changes, and the reserve line acknowledges caching allocator behavior.",
        "Giving a single total from a monitoring tool mixes reserved and live memory. It also hides which component to shrink when the budget is exceeded, such as switching optimizers or lowering the batch.",
        "Compare the budget with measured allocated memory at peak for one batch size. A gap larger than the reserve line means a component is missing from the ledger, often a framework workspace.",
    ),
    (
        "Design a restart comparison: run N steps uninterrupted, then run the same N steps with a save and resume midway, and compare final weights and losses.",
        "Equal results show the checkpoint captures all state affecting training. Any divergence points to missing fields.",
        "Testing only that the checkpoint loads without errors says nothing about continuation. A checkpoint missing momentum or sampler position loads cleanly and still diverges on the next step.",
        "Assert losses match step for step within tolerance and that weights agree at the end. Record the step at which any divergence first appears, since that step identifies the missing state.",
    ),
    (
        "Choose one optimization tied to a measured bottleneck, such as removing a per-step host synchronization seen in a trace, and leave other settings fixed.",
        "Linking the change to evidence makes the outcome interpretable: the bottleneck should shrink and outputs stay equal.",
        "Applying a popular optimization without measuring may target a stage that is not the bottleneck. Mixed precision, for example, does little when the GPU sits idle waiting for host input.",
        "Compare traces before and after and confirm the metric and sample counts are unchanged. If the MSE or validation count changes, the optimization altered the computation and cannot be reported as a pure speedup.",
    ),
    (
        "State hardware evidence separately: the report sets `backend` to `CPU reference` and `gpu_verified` to `False`, and lists the GPU checks still pending.",
        "A trustworthy report never implies that a CPU run validated GPU behavior. Explicit fields prevent a reader from assuming coverage.",
        "Leaving out the verification field lets readers assume the GPU path was tested. A later reader cannot then distinguish a validated deployment from a desk check.",
        'The reference asserts `not report["gpu_verified"]`. Only a real device run with recorded environment may set it to true.',
    ),
]

REASONING[33] = [
    (
        "Write the operator schema: one input tensor `x` of float32, scalar parameters `scale` and `bias` as floats, and one output tensor of the same shape and dtype, for example `fused_affine_relu(Tensor x, float scale, float bias) -> Tensor`.",
        "A schema lets the framework check argument types, dispatch to the right device implementation and reason about aliasing. It also documents the contract the CUDA kernel must satisfy.",
        "Leaving the schema implicit in a Python wrapper lets callers pass float64 or integers, which the C++ kernel then reinterprets.",
        "Register the schema and confirm the framework rejects a call with a missing or wrong-typed argument before the kernel runs.",
    ),
    (
        "Apply affine then clamp to `[-2, 0, 3]` with scale 2 and bias 1: preactivations `-3, 1, 7`, clamped at zero to `[0, 1, 7]`.",
        "The fused operator must compute exactly `max(0, 2*x + 1)`. The reference asserts this output and the empty case.",
        "Clamping before the affine step, `2*max(0, x) + 1`, gives `[1, 1, 7]`, a different function.",
        "Compare the CUDA output to `fused_reference` for these values exactly, since the inputs are exactly representable in float32.",
    ),
    (
        "State aliasing explicitly: the operator returns a new tensor that does not share storage with `x`, or, for an in-place variant, mark the input as mutated in the schema.",
        "Frameworks use aliasing annotations to decide whether autograd and compilers can reorder or reuse buffers. A wrong annotation can corrupt saved values.",
        "Writing the output into `x` without declaring it breaks autograd when `x` was saved for backward.",
        "Check the output's data pointer differs from the input's, and that the input values are unchanged after the call.",
    ),
    (
        "Reject non-contiguous inputs before launch with `TORCH_CHECK(x.is_contiguous())`, or call `.contiguous()` deliberately and document the copy cost.",
        "The raw-pointer kernel assumes consecutive elements. A transposed view has different strides, so reading `ptr[i]` returns the wrong elements.",
        "Assuming every tensor reaching the operator is contiguous because the tests used fresh tensors misses views created by slicing or transposing.",
        "Call the operator on `x.t()` and confirm it raises or returns the same values as the reference applied to the view.",
    ),
    (
        "Compare registration mechanisms: PyTorch registers through `TORCH_LIBRARY` and dispatch keys, while TensorFlow uses `REGISTER_OP` and `REGISTER_KERNEL_BUILDER`, and each framework needs its own implementation registered.",
        "The CUDA kernel can be shared, but each framework's dispatch, tensor types and memory management differ.",
        "Assuming a PyTorch extension can be loaded directly in TensorFlow treats a framework binding as a generic library. The library loads only if the framework finds a registered op, which it will not.",
        "Build and call the operator in each framework separately and compare outputs with the shared reference.",
    ),
    (
        "Record build evidence: compiler and CUDA toolkit versions, framework version and its C++ ABI flag, target architectures such as `sm_80`, and results of forward tests on a real device.",
        "Extensions are tied to the framework build and ABI. A binary built against one version may fail to load against another.",
        "Recording only that the build succeeded omits whether the kernel ran on a real device. A build can succeed on a machine with no GPU at all, so the record proves compilation only.",
        "Reload the built extension in a clean environment matching the record and rerun the forward tests.",
    ),
]

REASONING[34] = [
    (
        "Derive the input vector-Jacobian product for `y = max(0, a*x + b)`: the gradient of x is `upstream * a * mask`, where `mask` is 1 where the preactivation is positive and 0 otherwise.",
        "The chain rule multiplies the upstream gradient by the derivative of the ReLU, the mask, and by the derivative of the affine part, `a`. At `x = 2` with `a = 2`, `b = 1`, the preactivation is 5 and the derivative is 2.",
        "Using the output `y` instead of a mask, `upstream * a * y`, scales gradients by activation values and is wrong for every positive input not equal to 1.",
        "Compare the custom backward with autograd of the reference expression on random inputs away from the kink.",
    ),
    (
        "Derive the bias gradient as the sum of masked upstream values: with upstream `[1, 3]` and mask `[0, 1]`, it is `1*0 + 3*1 = 3`.",
        "The bias is shared across all elements, so its gradient accumulates over them. Only positions with positive preactivation pass gradient through the ReLU.",
        "Returning the upstream sum without masking gives 4, including a contribution from a position where the ReLU blocked gradient.",
        "The reference asserts `bias_grad == 3`. Compare against autograd for a tensor with mixed signs.",
    ),
    (
        "Run central finite differences away from the kink: at `x = 2` with `eps = 1e-5`, `(f(x+eps) - f(x-eps)) / (2*eps)` is about 2.",
        "Both perturbations stay in the linear region, so the central difference equals the derivative up to rounding. The reference asserts agreement within `1e-8` in float64.",
        "Running the check in float32 with a tiny epsilon loses precision to cancellation and fails even when the analytic gradient is right.",
        "Use float64 inputs, as `torch.autograd.gradcheck` expects, and check a few points on both sides of the kink.",
    ),
    (
        "Explain a gradcheck failure at `x = -0.5`, where the preactivation is 0: the central difference straddles the kink and gives `(2*eps - 0)/(2*eps) = 1`, while PyTorch's ReLU chooses subgradient 0 there.",
        "The derivative is not unique at the kink, so any value between 0 and the right derivative is a valid subgradient choice. Finite differences pick an average.",
        "Changing the backward to return 1 at the kink so the check passes chooses a convention for the test's sake.",
        "Test the kink separately with the documented subgradient, and run gradcheck only at points away from it.",
    ),
    (
        "Specify higher-order support explicitly: if the backward is not itself differentiable, mark the operator as first-order only, for example with `once_differentiable`.",
        "A correct first derivative says nothing about whether the backward function supports differentiation again, which methods like gradient penalties require.",
        "Assuming double backward works because first-order gradcheck passed leads to silent zero second derivatives.",
        "Run `gradgradcheck` if second order is supported, or confirm a clear error is raised.",
    ),
    (
        "Compare each framework's native reference separately: PyTorch autograd of the reference expression and TensorFlow's `GradientTape` of the same expression, each for forward and backward.",
        "Each framework binding may differ in subgradient conventions or dtype handling. Separate comparisons localize a mismatch.",
        "Comparing PyTorch's custom op with TensorFlow's custom op only checks they agree with each other.",
        "Use the same inputs and upstream values in both frameworks and compare forward and backward results within tolerance.",
    ),
]

REASONING[35] = [
    (
        "Weight each microbatch mean gradient by its sample count: `(3*2 + 1*8) / (3 + 1) = 14/4 = 3.5`.",
        "The effective-batch gradient is the mean over all four examples. Microbatch means already divide by their own sizes, so multiplying back by the sizes recovers the sums before dividing by the total.",
        "Averaging the two means, `(2 + 8)/2 = 5`, gives the single example in the second microbatch the same weight as the three in the first, so it counts three times as much as it should.",
        "The reference asserts `weighted == 3.5` and `wrong == 5`. Compare with the mean gradient of one batch containing all four examples.",
    ),
    (
        "Find the normalization error in an accumulation loop that divides each microbatch loss by the number of microbatches regardless of their sizes, which equals averaging unequal means.",
        "Dividing by the microbatch count is correct only when all microbatches have the same size. A short final microbatch then gets too much weight in every epoch.",
        "Trusting that the loop is right because it matches the full-batch gradient on evenly divisible data hides the error, which only appears for an uneven final microbatch.",
        "Test with sizes 3 and 1 and compare the accumulated gradient with 3.5. Scaling each loss by `size/total` fixes it, and the test should then pass.",
    ),
    (
        "Place `optimizer.step()` and `optimizer.zero_grad()` once per effective batch, after the last microbatch's `backward()`, not after each microbatch.",
        "Gradients accumulate in `.grad` across backward calls. Stepping after each microbatch applies several smaller updates with different parameters, which is a different algorithm from one large-batch update.",
        "Calling `zero_grad()` inside the microbatch loop discards earlier contributions, so only the last microbatch affects the update.",
        "Count optimizer steps per epoch and confirm it equals the number of effective batches. Compare the updated weights with a single full-batch step.",
    ),
    (
        "Explain activation checkpointing: selected layers discard their intermediate activations after the forward pass and recompute them during backward from saved inputs.",
        "Memory falls because only the segment inputs stay alive, an illustrative 20 MiB saved in the lesson's example, but each checkpointed segment runs its forward computation twice.",
        "Checkpointing every layer when memory is not the constraint adds recomputation with no benefit.",
        "Measure peak allocated memory and step time with checkpointing on and off. Gradients must match within tolerance, since recomputation changes time but not the math.",
    ),
    (
        "Account for frozen weights: setting `requires_grad=False` removes gradient and optimizer state for those parameters, but the parameters themselves stay in memory.",
        "Freezing saves gradient storage and optimizer moments, three times the parameter bytes for Adam, but the forward pass still reads every frozen weight.",
        "Assuming a frozen model costs nothing in memory leads to under-budgeting by the full parameter size.",
        "Compare allocated memory before and after freezing and confirm the reduction matches gradient plus optimizer bytes while parameter bytes remain.",
    ),
    (
        "Design tests for equal updates: compare accumulated microbatch training with full-batch training using the same data order, loss reduction, initial state and disabled randomness such as dropout.",
        "Accumulation is meant to reproduce the large-batch update. Holding every other factor fixed isolates the accumulation logic.",
        "Running the comparison with dropout enabled and different seeds produces differences that hide or mimic accumulation bugs.",
        "Assert weights after one effective step agree within float tolerance, and repeat with an uneven final microbatch.",
    ),
]

REASONING[36] = [
    (
        "Subtract the row maximum before exponentiating: scores `[1000, 1001]` become `[-1, 0]`, giving `exp` values about `[0.368, 1]` and probabilities about `[0.269, 0.731]`.",
        "Softmax is unchanged by subtracting a constant from every score, since the factor cancels in the ratio. Shifting by the maximum keeps exponents at or below zero, so nothing overflows.",
        "Exponentiating directly, `math.exp(1000)`, overflows to infinity in float64 and the division produces NaN. In float16 the overflow happens above about 11.",
        "The reference asserts the weights sum to 1 and that the second weight is larger. Compare with `torch.softmax` on the same scores.",
    ),
    (
        "Build a causal mask where query position `i` may attend to key position `j` only if `j <= i`; for three tokens this is `[[1,0,0],[1,1,0],[1,1,1]]`.",
        "A causal model must not use future tokens. The lower-triangular pattern allows each token to see itself and earlier tokens. Token 0 sees only itself and gets weight 1.",
        "Using `j < i` excludes the diagonal, leaving row 0 with no allowed positions and producing NaN in softmax.",
        "The reference asserts the lower-triangular matrix. Apply it to random scores and confirm each row's weights above the diagonal are exactly zero.",
    ),
    (
        "Count score-matrix bytes as batch times heads times sequence squared times itemsize: batch 2, 8 heads, sequence 1024 in float16 gives `2*8*1024*1024*2 = 33554432` bytes, 32 MiB.",
        "Naive attention materializes a score for every query and key pair, so memory grows with the square of sequence length. Doubling the sequence quadruples this term.",
        "Estimating attention memory as linear in sequence length misses the quadratic term, which dominates for long sequences.",
        "Recompute with sequence 2048 and confirm 128 MiB. Fused kernels avoid storing this matrix.",
    ),
    (
        "Define behavior for a fully masked row: either reject inputs where some query has no allowed keys, or document a specific output such as zeros.",
        "Softmax over a row of negative infinity divides zero by zero and yields NaN. Different kernels may handle this case differently, so the contract must say what is expected.",
        "Leaving it undefined lets NaN appear only with certain padding patterns.",
        "Construct a batch with one padded sequence that masks every key for some query and assert the documented result.",
    ),
    (
        "Compare fused attention against a reference implementation for forward outputs and gradients, using identical masks, dtypes and tolerances appropriate for float16 or bfloat16.",
        "Fused kernels reorder computations and may use different accumulation precision. Agreement must hold within a tolerance chosen for the dtype, for both directions.",
        "Comparing only forward outputs leaves backward bugs undetected, and comparing a float16 fused result to a float32 reference with float32 tolerance reports false failures.",
        "Use the same random inputs, run backward with the same upstream gradient, and compare with `torch.testing.assert_close` using dtype-specific tolerances.",
    ),
    (
        "Separate the API name from the backend: `scaled_dot_product_attention` may dispatch to a flash, memory-efficient or math backend depending on hardware, dtype and mask.",
        "The same call can run different kernels on different machines, so claims about memory or speed must name the backend actually selected.",
        "Assuming the flash backend ran because the function was called leads to wrong memory estimates when it silently fell back to math.",
        "Restrict the allowed backends in a test and observe which configurations succeed, or inspect profiler kernel names.",
    ),
]

REASONING[37] = [
    (
        "Count low-rank adapter parameters as rank times the sum of dimensions: `8*(1024 + 1024) = 16384` for a 1024 by 1024 weight.",
        "A low-rank update factors the change as a 1024 by 8 matrix times an 8 by 1024 matrix, so its parameters are `1024*8 + 8*1024`.",
        "Computing rank times the product of dimensions, `8*1024*1024`, gives eight times the original matrix. That figure would make the adapter larger than the weight it adapts, which should immediately signal an error.",
        "The reference asserts `adapter == 16384`. In a framework, sum `numel()` over adapter parameters and compare.",
    ),
    (
        "Include base storage in the memory ledger: the 1048576 base parameters stay in memory, so the total is `1048576 + 16384`.",
        "Adapters reduce trainable parameters, gradients and optimizer state, but the forward pass still needs the frozen base weights.",
        "Budgeting memory from adapter parameters alone underestimates by the full base model. For this matrix the adapter is about 1.6 percent of the total, so the omitted base dominates the real footprint.",
        "The reference asserts `base + adapter > base`. Measured parameter memory should include the base.",
    ),
    (
        "Inspect the optimizer's parameter groups and confirm only adapter tensors are present, such as by filtering `p.requires_grad`.",
        "An optimizer built from `model.parameters()` includes frozen base weights, creating optimizer state for them even if gradients are absent.",
        "Assuming freezing alone excludes parameters from the optimizer can waste memory. Some optimizers skip parameters whose `.grad` is None, but weight decay or other per-parameter bookkeeping may still allocate state, so membership should be explicit rather than implied.",
        "Count parameters in the optimizer groups and assert the count equals 16384. Also check that each base tensor reports `requires_grad == False`, so the two facts agree.",
    ),
    (
        "Compare memory at two sequence lengths, such as 512 and 1024, since activations and attention intermediates grow with sequence geometry while parameters stay constant.",
        "Activation memory grows at least linearly with sequence length and naive attention grows quadratically, so long sequences can exceed memory even with small adapters.",
        "Assuming adapters make long-sequence fine-tuning cheap confuses parameter savings with activation savings. Gradients must still flow back through the frozen layers to reach adapters in earlier layers, so those activations are kept during the forward pass.",
        "Measure peak allocated memory at both lengths and check the growth against the ledger.",
    ),
    (
        "Design a tiny offline training run with generated token IDs, a small model or a few layers, and a bounded number of steps such as 20.",
        "Synthetic tokens avoid licensing and download needs, and a small bounded run checks wiring and memory behavior safely.",
        "Using a full public model and dataset for a first test risks long downloads and exhausting memory. A failure in that setting is also harder to localize, because data, model size and wiring all vary at once.",
        "Confirm the loss decreases on a repeated tiny batch, showing gradients reach the adapter.",
    ),
    (
        "Keep a held-out evaluation set that is never used for fitting or hyperparameter tuning, and report its metric separately.",
        "Fine-tuning can overfit small datasets quickly. Separate evaluation measures generalization.",
        "Reporting the training loss as model quality overstates performance. Choosing the rank or learning rate by repeatedly looking at the evaluation set leaks it into tuning in the same way.",
        "Assert there is no overlap between training and evaluation example IDs, then report both metrics.",
    ),
]

REASONING[38] = [
    (
        "Multiply two, for keys and values, by layers, batch, sequence, KV heads, head dimension and element width: `2*2*1*16*4*8*2 = 4096` bytes.",
        "Each layer stores one key and one value vector per KV head per position. The product counts every stored element, then multiplies by 2 bytes for float16.",
        "Leaving out the factor two for keys and values gives 2048 bytes and underestimates the cache by half.",
        "The reference asserts `cache == 4096`. Compare with the sizes of the cache tensors in a framework.",
    ),
    (
        "Double the sequence to 32: the cache becomes 8192 bytes, as the reference asserts.",
        "Cache size is linear in stored positions. Weights are unchanged, so the cache grows into a larger share of memory as context lengthens.",
        "Lowering weight precision to reduce memory does nothing for this term, since the cache precision is set separately.",
        "Recompute with sequence 64 and confirm 16384 bytes, doubling again.",
    ),
    (
        "Use the model's actual KV head count, which can be smaller than the query head count in grouped-query attention, such as 4 KV heads shared by 16 query heads.",
        "Only KV heads are cached. Using the query head count overestimates the cache by the grouping factor.",
        "Assuming KV heads equal attention heads for every model gives a 4 times overestimate here.",
        "Read `num_key_value_heads` from the model configuration and check the cache tensor shapes. The KV head dimension of the cached key tensor should equal that configured value, not the query head count.",
    ),
    (
        "Compare cached and uncached generation step by step: compute logits for each new token with the cache and by recomputing the full prefix, and compare within tolerance.",
        "Caching should change cost, not results. A per-step comparison localizes a mismatch to the first step where positions or masks diverge.",
        "Comparing only the final generated text hides small differences that alter sampling later. A wrong position offset in the cache can produce plausible text for many tokens before the output visibly drifts.",
        "Use greedy decoding for a bounded number of steps and assert each logits vector agrees.",
    ),
    (
        "Separate prefill timing, which processes the whole prompt at once, from decode timing, which generates one token per step using the cache.",
        "Prefill is large matrix work, while decode is small and often memory-bound, reading the full cache each step.",
        "Reporting a single tokens-per-second number mixes two regimes. A long prompt with short output looks very different from a short prompt with long output under one combined number.",
        "Report time to first token and per-token decode time separately. Record prompt length and output length beside each number, since both affect the cache read per step.",
    ),
    (
        "Label fake quantization, which rounds values to a lower precision and dequantizes them in float, separately from a real quantized kernel that computes with low-precision integers.",
        "Fake quantization estimates accuracy effects but does not reduce memory traffic or compute time.",
        "Reporting speed or memory gains from a simulation claims benefits only a deployed kernel can show. Memory can even rise under simulation, because both the original float weights and rounding scales may be held.",
        "State in each result whether quantization was simulated or executed, and which kernel ran.",
    ),
]

REASONING[39] = [
    (
        "With two replicas of equal batch size and mean gradients 2 and 4, all-reduce the gradients and divide by the world size: `(2 + 4)/2 = 3`.",
        "When every replica holds the same number of examples, the mean of replica means equals the mean over all examples. This is why data-parallel training divides the summed gradient by the number of ranks.",
        "Summing gradients without dividing by world size gives 6, which effectively doubles the learning rate whenever another GPU is added, so changing the device count silently changes training dynamics.",
        "Run a single-device step on the concatenated batch and compare its gradient to the averaged replica gradient. The reference asserts `sum(gradients)/2 == 3.0` for the equal-size case.",
    ),
    (
        "For unequal counts 3 and 1 with gradients 2 and 4, weight by examples: `(3*2 + 1*4)/(3 + 1) = 10/4 = 2.5`, or adopt a documented policy that every rank processes equal-size batches.",
        "The global sample mean counts each example once. A plain average of replica means treats the rank with one example as if it held three, giving 3 instead of 2.5.",
        "Relying on the default world-size average when the sampler gives the last rank a short batch introduces a small bias every epoch, which is hard to notice because loss still falls.",
        "The reference asserts `weighted == 2.5` and that the unweighted mean is 3.0. In a framework, all-reduce both the gradient sum and the example count, then divide.",
    ),
    (
        "Assign each process one rank and one device explicitly, such as `torch.cuda.set_device(local_rank)` before creating tensors or the process group, with the launcher supplying `LOCAL_RANK`.",
        "Collective libraries expect each rank to own one device. Without explicit assignment several processes default to device 0, oversubscribing its memory while the other GPUs sit idle.",
        "Creating the model before setting the device places every replica on GPU 0, and the first out-of-memory error appears far from its cause.",
        "Have each rank log its rank, local rank and `torch.cuda.current_device()`, and confirm the mapping is one to one across the job.",
    ),
    (
        "Check that the distributed sampler covers every example exactly once per epoch: union the indices each rank processed and compare with the dataset index set.",
        "Samplers pad or drop examples so that ranks get equal counts. Padding duplicates a few examples and dropping omits some, and either changes the gradient accounting.",
        "Assuming coverage because each rank processed `len(dataset)/world_size` batches ignores padding and the `drop_last` setting.",
        "Gather index lists from all ranks for one epoch and assert no duplicates and no missing indices, or record the documented padding count if padding is intended.",
    ),
    (
        "Design collective failure handling: set a bounded timeout on process-group operations and make the launcher terminate every rank it started when one fails.",
        "A rank that crashes leaves the others blocked inside an all-reduce indefinitely. A timeout turns the hang into an error, and owned-process cleanup releases the GPUs.",
        "Letting surviving ranks wait without a timeout keeps the devices occupied by a job that cannot finish, and nobody receives an error to act on.",
        "Inject a failure by exiting one rank early in a small test, and confirm the others exit with a timeout error within the configured bound.",
    ),
    (
        "Compare distribution contracts across frameworks: PyTorch DDP, Horovod, JAX `pmap` and TensorFlow strategies each define gradient reduction, sampler behavior and launch differently.",
        "Defaults differ, such as whether the gradient is summed or averaged and how uneven final batches are handled, so a result validated under one framework does not transfer.",
        "Porting a training script between frameworks and assuming identical gradients because both are data-parallel skips the place where the semantics actually differ.",
        "Write an integration test per framework that compares the two-rank gradient with a single-device reference on the same examples.",
    ),
]

REASONING[40] = [
    (
        "Write three measurable constraints with units, such as peak memory at most 8 GiB, p95 latency at most 20 ms and held-out accuracy at least 0.9.",
        "Constraints with units and thresholds can be checked mechanically against candidate measurements. Vague goals such as fast enough cannot reject any candidate.",
        "Writing a single goal of maximizing speed ignores memory and quality, so the fastest candidate wins even when it cannot run on the device or produces worse answers.",
        "Each constraint should map to a field in the candidate records: `memory`, `latency` and `quality` in the reference fixture, with a comparison operator and threshold.",
    ),
    (
        "Filter infeasible candidates before ranking by speed: B needs 12 GiB on an 8 GiB device and C has quality 0.80 below 0.9, so only A remains.",
        "A candidate that violates a hard constraint cannot be deployed whatever its speed. B's 10 ms timing is irrelevant because the model does not fit.",
        "Ranking all candidates by latency first and picking B, then trying to make it fit later, wastes effort and treats a hard constraint as a preference.",
        "The reference asserts `valid == ['A']`. Change B's memory to 8 and confirm it then becomes valid, showing the filter responds to the constraint.",
    ),
    (
        "Choose one bottleneck hypothesis tied to a trace, such as the latency dominated by host-to-device copies, and name the change that would test it.",
        "A hypothesis grounded in a measured trace predicts which change should help. If the change does not move the measured stage, the hypothesis was wrong.",
        "Making several optimizations at once without a hypothesis means any improvement cannot be attributed to a cause, and regressions get hidden by gains elsewhere.",
        "Record the trace before and after the single change and check that the targeted stage shrank while results stayed the same.",
    ),
    (
        "Preserve a rollback path: keep the unchanged baseline runnable with its configuration and recorded metrics so it can be restored if the new candidate fails.",
        "A rollback provides a known-good fallback and a reference for comparing later measurements, so deployment risk stays bounded.",
        "Replacing the baseline code in place leaves no way to reproduce earlier results or revert quickly.",
        "Run the baseline from its saved configuration and confirm it reproduces the recorded metric within tolerance.",
    ),
    (
        "Design failure tests with bounded invalid inputs, such as wrong dtype, oversized batch and empty input, and test that resource refusal produces a clear error.",
        "A GPU service should fail predictably. Rejecting an oversized request is better than an out-of-memory crash that also affects other requests.",
        "Testing only valid inputs leaves error paths untested, and those paths are where GPU services typically fail in production.",
        "Assert each invalid input yields a specific error and that the service still answers a valid request afterward.",
    ),
    (
        "State evidence gaps explicitly: candidate measurements in the fixture are illustrative, and any GPU timing not measured on target hardware stays marked as pending validation.",
        "A decision record must show which numbers were measured and which were assumed. Hiding gaps makes an unverified choice look final.",
        "Presenting fixture numbers such as 18 ms as measured performance claims evidence that does not exist.",
        "Include a section listing each unmeasured quantity and the hardware run that would measure it, and check that no unmeasured value is labeled as measured.",
    ),
]

REASONING[41] = [
    (
        "With ranks taking 10, 12 and 30 ms before a barrier, the compute phase takes at least `max(10, 12, 30) = 30` ms, not the mean of about 17.3 ms.",
        "A barrier releases only when every rank arrives. The two fast ranks spend 20 and 18 ms waiting, so the slowest rank sets the step time.",
        "Reporting the average rank time predicts 17.3 ms and hides 13 ms of idle time per step, which makes adding ranks look more efficient than it is.",
        "The reference asserts `max(rank_ms) == 30`. In a real trace, compare the per-rank time spent waiting in the collective with the gap to the slowest rank.",
    ),
    (
        "Compare data parallelism, which replicates the model and splits examples, with tensor, pipeline and sharded-state parallelism, which partition operations, layers or optimizer state.",
        "Data parallelism needs the whole model on each device and communicates gradients. Partitioning methods fit larger models but add communication inside the forward and backward passes.",
        "Using data parallelism for a model that does not fit on one device fails immediately, because each replica needs all parameters, gradients and optimizer state.",
        "For each method write down what is replicated, what is partitioned and what is communicated per step, then check the per-device memory against device capacity.",
    ),
    (
        "Diagnose a missing rank by bounding waits: a collective timeout turns a hang into an error that names the operation, after which the launcher stops all owned processes.",
        "Without a bound, ranks that reached the collective wait forever for a rank that crashed or never started, and no error reaches anyone.",
        "Restarting only the missing rank while the others wait in a collective fails, because the new process does not join the existing communicator state.",
        "Simulate the failure by delaying one rank past the timeout in a small job and confirm every rank exits with an error inside the configured bound.",
    ),
    (
        "Define checkpoint consistency as every rank saving at the same completed update step; a checkpoint with rank 0 at step 10 and rank 1 at step 11 is rejected.",
        "Ranks share parameters or hold partitions of the same model. Mixing steps combines states that never coexisted, so resuming does not continue any real training run.",
        "Accepting each rank's latest file independently produces mixed-step checkpoints whenever a failure occurs during saving.",
        "The reference computes `consistent = len(set(steps.values())) == 1` and asserts it is false. Store the step in each shard and check equality before loading.",
    ),
    (
        "Budget communication by counting bytes and frequency for each collective, such as an all-reduce of gradient bytes once per step for data parallelism.",
        "Communication time depends on the bytes moved and link bandwidth, so the byte count per step shows whether the network can keep up with compute.",
        "Estimating communication from the parameter count without element size or frequency misses that float32 gradients are four bytes and some collectives run several times per step.",
        "Compute bytes per step from parameter count and dtype, then compare against bytes recorded by the communication library's logging for one step.",
    ),
    (
        "Design owned-host cleanup: on failure, terminate only processes and resources the job created, recorded by process IDs or job labels, and keep completed checkpoints.",
        "Shared hosts run other jobs. Ownership records make cleanup safe, and keeping checkpoints allows resuming from the last consistent step.",
        "Killing every GPU process on a host stops other users' jobs, while deleting the output directory loses valid checkpoints.",
        "List the recorded process IDs before cleanup and confirm afterward that only those exited and checkpoints remain.",
    ),
]

REASONING[42] = [
    (
        "Create tile boundaries as half-open intervals `[start, min(start + tile, n))` with `start` stepping by 4 from 0: for `n = 10` this yields `[0..3]`, `[4..7]` and `[8, 9]`.",
        "Half-open intervals tile the index range without overlap or gaps, because each tile ends exactly where the next begins. The `min` call caps the last tile at `n`.",
        "Using closed intervals `[start, start + tile]` makes adjacent tiles share an element, so index 4 is processed twice and a sum reduction double counts it.",
        "The reference asserts the three tiles and that their flattened concatenation equals `list(range(10))`, which checks both coverage and the absence of duplicates.",
    ),
    (
        "Mask the final tile: the third tile has lanes for offsets 8 through 11, of which only 8 and 9 are valid, so loads and stores both take a mask `offsets < n`.",
        "A tile DSL operates on fixed-size tiles, so lanes beyond the array exist in the computation. Masking the load prevents reading past the buffer, and masking the store prevents writing past it.",
        "Masking only the store still issues out-of-bounds loads, which can fault or read unrelated memory, and an unmasked reduction then includes garbage values.",
        "Run with `n = 10` and a tile of 4, fill a guard region after the output with a sentinel, and confirm the sentinel is untouched and outputs match the reference.",
    ),
    (
        "Compare abstractions: in thread-level CUDA the programmer maps each thread to elements and manages shared memory, while in a tile DSL the programmer writes operations on whole tiles and the compiler decides thread mapping, vectorization and staging.",
        "The tile model moves decisions such as which thread loads which element into the compiler. That reduces code for common patterns but limits control when the compiler's choice is poor.",
        "Assuming a tile kernel behaves like a thread kernel with the same block size misreads the model, since a tile program instance is not a single thread.",
        "Write the same vector add in both styles and list which decisions appear explicitly in each source, such as index computation and bounds checks.",
    ),
    (
        "State compiler requirements: record the exact DSL release, the backend compiler version it needs and the supported GPU architectures, since tile DSLs change quickly.",
        "Tile DSLs often support only recent architectures and change their APIs between releases. Without recorded versions a kernel that compiled once may not compile later.",
        "Writing that the kernel requires a recent version gives no way to reproduce the build.",
        "Put pinned versions in the lesson's requirements and check them at the start of the GPU run, failing with a clear message when they do not match.",
    ),
    (
        "Design a comparison against a library routine with the same data shape, dtype and timing boundary, such as both including or both excluding the first compile.",
        "Tile DSL kernels usually compile on first call. If one side includes compilation and the other does not, the comparison measures setup rather than execution.",
        "Timing the DSL kernel once against a warmed library call reports the DSL as much slower purely because of compilation.",
        "Report the first-call time and the steady-state median separately for both implementations, and check outputs agree before comparing times.",
    ),
    (
        "Explain the resource tradeoff of larger tiles: they can increase reuse of loaded data but hold more values in registers or shared memory, which can reduce how many tile instances run concurrently.",
        "Concurrency hides memory latency. If larger tiles reduce occupancy enough, the reuse gain can be outweighed, so the net effect depends on the device and shape.",
        "Concluding that larger tiles are always faster because they reuse more data predicts a direction that only device evidence can establish.",
        "Measure several tile sizes on the target device and record register usage and achieved occupancy beside timings.",
    ),
]

REASONING[43] = [
    (
        "Trace a stable sort of `[(2, A), (1, B), (2, C)]` by key: B moves first, then A and C keep their input order, giving `[(1, B), (2, A), (2, C)]`.",
        "A stable sort guarantees that records with equal keys appear in the same relative order as in the input. A came before C, so it stays before C.",
        "Assuming every GPU sort is stable lets downstream code rely on an order an unstable sort may legally change, which then varies between runs or releases.",
        "The reference uses Python's stable `sorted` and asserts the order. For a GPU library, call the documented stable variant and compare with this result on many duplicate keys.",
    ),
    (
        "Specify duplicate semantics in the contract: state whether equal keys keep input order, and if not, require downstream code to break ties with a secondary key.",
        "When order among duplicates is unspecified, any consumer depending on it is relying on an accident. Stating the rule makes the dependence visible.",
        "Leaving the rule unstated passes tests on small inputs where an unstable algorithm happens to preserve order, then fails on larger inputs that use a different internal path.",
        "Test with many equal keys and shuffled payloads, checking either preserved order or tie-breaker order as documented.",
    ),
    (
        "Calculate the matrix-multiply output shape: a 2 by 3 matrix times a 3 by 4 matrix contracts the shared dimension 3 and gives 2 by 4.",
        "The inner dimensions must match and disappear, while the outer dimensions form the result. The reference asserts `a[1] == b[0]` and reports `(a[0], b[1])`.",
        "Taking the output as 3 by 3 or 2 by 3 confuses contracted and kept dimensions, and allocating the wrong output buffer causes a library error or an out-of-bounds write.",
        "Compare with `numpy.matmul` on random arrays of those shapes and check the result shape and values.",
    ),
    (
        "Account for temporary storage: sorting and some matrix algorithms request a workspace buffer, so peak memory is inputs plus outputs plus workspace.",
        "Workspace can be comparable to the input size for sorts, so it affects whether a large operation fits in memory alongside other live tensors.",
        "Budgeting only inputs and outputs leads to out-of-memory errors that appear only on large arrays.",
        "Query the library's workspace size for the shape, or measure peak memory during the call, and compare with the budget.",
    ),
    (
        "Separate plan creation from execution: libraries such as FFT create a plan for a given shape and dtype, so measure cold setup once and steady execution over repeated calls.",
        "Plan creation selects algorithms and allocates resources, and its cost is paid once per configuration. Including it in every timing misrepresents steady throughput.",
        "Reusing a plan prepared for a different shape or dtype gives wrong results or errors, so caching must be keyed by both.",
        "Time the first call and the median of later calls separately, then call with a new shape and confirm a new plan is created.",
    ),
    (
        "Choose a release-specific contract: read the documentation version matching the library release installed, since stability guarantees and supported dtypes can change.",
        "Function behavior, defaults and supported types differ between releases. Citing the matching documentation ties the contract to the tested code.",
        "Relying on the latest online docs while running an older release can promise features or guarantees the installed version does not have.",
        "Record the installed version at runtime and link the documentation page for that version in the notes.",
    ),
]

REASONING[44] = [
    (
        "Group `[(A, 2), (A, null), (B, 5)]` with the skip-null sum rule: A totals 2 and B totals 5, while A has a row count of 2.",
        "Under the declared contract, nulls do not contribute to the sum but the row still exists. Sum and row count therefore answer different questions about group A.",
        "Treating the null as an error and dropping group A entirely, or failing the whole aggregation, contradicts the stated skip-null rule.",
        "The reference asserts `totals == {'A': 2, 'B': 5}` and `counts['A'] == 2`. Compare with a cuDF or pandas `groupby` sum and size on the same rows.",
    ),
    (
        "Distinguish null from zero: a null value means unknown and is skipped by the sum, while a zero is a real value that contributes 0 and counts as non-null.",
        "The difference matters for means and non-null counts. Group A has mean 2 over one non-null value, but filling the null with 0 gives a mean of 1.",
        "Filling nulls with zero before aggregation silently changes averages and counts, which then disagree with reports computed by a SQL engine that skips nulls.",
        "Compute `count` and `mean` for group A with and without filling, and confirm the skip-null version gives count 1 and mean 2.",
    ),
    (
        "Define the category mapping once on training data, such as A to 0 and B to 1, and reserve a code for unknown categories such as C.",
        "Model features depend on consistent codes. A mapping fitted once and reused gives every partition and later batch the same meaning for each code.",
        "Fitting category codes independently in each partition assigns code 0 to whatever category appears first there, so the same code means different things to the model.",
        "Encode two partitions with the saved mapping and assert A has the same code in both, and that C maps to the unknown code.",
    ),
    (
        "Preserve row identity by carrying a stable key column through filtering, joins and conversions, so outputs can be matched back to inputs.",
        "GPU dataframe operations may reorder rows, for example in hash joins or group operations. A key column allows correct alignment without relying on position.",
        "Matching rows by position after a join or a GPU to CPU conversion can attach predictions to the wrong records.",
        "Shuffle input rows, run the pipeline and join results on the key, then check each output matches its input.",
    ),
    (
        "Count conversion bytes: moving a column to the GPU moves its values plus a null mask, and dtype conversions such as int64 to float32 or object strings to device strings create extra buffers.",
        "Transfer and conversion costs can exceed the computation for small operations, so the ledger shows whether staying on the device is worthwhile.",
        "Counting only the numeric values misses null masks, string offsets and temporary converted copies.",
        "Compute expected bytes for a column of known length and dtype, then compare with the device memory reported after transfer.",
    ),
    (
        "Distinguish cuDF, a dataframe library with a pandas-like API on the GPU, from the RAPIDS Accelerator for Spark, which replaces Spark physical operators with GPU implementations.",
        "cuDF code calls GPU operations directly, while Spark acceleration keeps Spark's API and planner and changes how the plan executes, falling back to CPU for unsupported operators.",
        "Assuming a Spark job uses the GPU because cuDF is installed confuses a library with a plugin that needs its own configuration.",
        "For Spark, inspect the physical plan for GPU operators. For cuDF, check that the objects are cuDF dataframes.",
    ),
]

REASONING[45] = [
    (
        "Define the shape envelope: batch from 1 to 8, sequence length from 1 to 32 and the accepted dtypes, written as explicit bounds the service checks.",
        "Deployment engines are often built for bounded dimensions. A declared envelope tells callers what is supported and lets the service reject anything outside it.",
        "Leaving the envelope implicit means unsupported shapes reach the engine and fail with internal errors or are padded and truncated without notice.",
        "The reference `accepted(batch, sequence)` asserts that `(1, 32)` is accepted and `(9, 16)` and `(2, 0)` are rejected. Add both boundary values to the test.",
    ),
    (
        "Reject an invalid request such as batch 9 before execution with an error naming the violated bound, rather than truncating input to 8.",
        "Silent truncation returns results for fewer examples than requested and the caller cannot tell. An explicit error is safe and actionable.",
        "Splitting batch 9 into 8 and 1 automatically may be reasonable, but only as a documented path. Doing it implicitly changes latency and behavior without a contract.",
        "Send a batch of 9 and assert the error message, then send 8 and confirm success.",
    ),
    (
        "Separate export, engine build and execution as distinct evidence steps: exporting the model graph, building an engine for a device and running inference each can fail independently.",
        "A successful export does not mean the engine builds, and a successful build does not mean outputs are correct. Recording each step shows how far validation reached.",
        "Reporting the deployment as working because the export succeeded skips build and execution, where unsupported operators and precision problems usually appear.",
        "Record pass or fail for each step with its version, and run inference on known inputs before calling the deployment validated.",
    ),
    (
        "Choose calibration data for lower precision from representative training-side samples, never from the held-out evaluation set.",
        "Calibration sets scale factors from observed value ranges, so unrepresentative data gives poor ranges. Using evaluation data leaks it into the build.",
        "Calibrating on a handful of constant inputs gives ranges that clip real activations, which lowers accuracy. Values outside the calibrated range saturate at the limit, so large activations lose their differences entirely.",
        "Record which samples were used and assert no overlap with evaluation example IDs.",
    ),
    (
        "Record engine compatibility metadata: the runtime version, device model and compute capability, precision mode and shape envelope used during the build.",
        "Built engines are often tied to a runtime version and GPU architecture. Metadata allows a service to refuse an engine built for a different setup.",
        "Copying an engine file to a different GPU model or runtime release can fail to load or behave differently. Rebuilding per target from the same exported graph is the safer pattern.",
        "Check stored metadata against the current environment when loading and fail clearly on mismatch.",
    ),
    (
        "Compare task quality between the original model and the built engine on the same held-out examples with the same metric, such as classification accuracy.",
        "Lower precision can change outputs. A successful build only shows the engine runs, so quality must be measured against the application's tolerance.",
        "Comparing only a few output tensors for closeness can miss a quality drop concentrated in some classes.",
        "Report both accuracies on the same examples and accept only if the drop is within the declared tolerance.",
    ),
]

REASONING[46] = [
    (
        "List compatibility axes for a custom operator: Python version, framework version and ABI, compiler, CUDA toolkit, operating system, host architecture, driver and device targets.",
        "A compiled extension links against framework internals and CUDA runtime libraries. A mismatch on any axis can prevent loading or cause a failure at the first kernel launch.",
        "Recording only the Python version suggests one wheel works everywhere that Python runs, while a framework ABI change alone can break the import.",
        "The reference asserts the manifest keys equal the required set and that `driver` is absent from the build ledger, since the driver belongs to the runtime environment.",
    ),
    (
        "Separate import from execution: importing proves the host shared library loaded, while only launching a real kernel on the device tests that compatible device code exists.",
        "Device code is selected at the first launch. A package built without code for the device architecture imports cleanly and then fails with a no-kernel-image error.",
        "Treating a successful import as proof of portability passes packages that cannot run any kernel on the target GPU.",
        "Add a smoke test that runs the operator on a small tensor on the device and compares with a CPU reference.",
    ),
    (
        "Explain native device code versus intermediate code: native binaries for an architecture run only on compatible devices, while embedded PTX can be compiled by the driver for newer architectures.",
        "Including PTX for the newest targeted architecture lets future GPUs load the kernel through driver compilation, at the cost of a first-launch delay.",
        "Shipping native code only for the build machine's GPU makes the package fail on any older or newer architecture.",
        "Inspect the binary's embedded architectures with `cuobjdump --list-elf` and `--list-ptx` and compare with the declared device targets.",
    ),
    (
        "Design a build ledger that records source revision, toolkit and compiler versions, framework version, architecture flags and output hashes in a reviewed build recipe.",
        "A ledger allows rebuilding the same artifact and explains why two builds differ. Hashes tie a distributed file to the recorded inputs.",
        "Building from a developer machine without recording flags yields an artifact nobody can reproduce or audit.",
        "Rebuild from the ledger and compare the resulting hash, or explain any difference by a recorded input change.",
    ),
    (
        "Test an unsupported dtype, such as float64 for an operator implemented only for float32, and require a clear contract error before any kernel launch.",
        "Passing unsupported types to a kernel can reinterpret bytes as the wrong type and return plausible but wrong numbers.",
        "Silently casting to float32 hides precision loss and gives callers a different result from what they requested.",
        "Call the operator with float64 and assert the error message names the supported types.",
    ),
    (
        "Define a release gate requiring functional tests in every declared supported environment, so each combination of framework, toolkit and device target in the matrix runs the smoke and correctness tests.",
        "The compatibility matrix is a claim, and only tests in each environment support it. A gate stops a release with untested combinations.",
        "Testing one environment and declaring the whole matrix supported presents untested claims as verified.",
        "Store test results per environment with the release and reject it if any declared row lacks a passing result.",
    ),
]

REASONING[47] = [
    (
        "Calculate arithmetic intensity: 4096 operations over 8192 bytes moved gives 0.5 operations per byte, as the reference asserts.",
        "Arithmetic intensity compares work with data movement. At 0.5 operations per byte, the kernel needs memory bandwidth far more than compute throughput on typical GPUs.",
        "Dividing bytes by operations gives 2 and inverts the conclusion, suggesting the kernel is compute-heavy.",
        "Recompute from element counts and element size in the code, then compare with profiler-measured operations and DRAM bytes.",
    ),
    (
        "Count eliminated bytes from fusion: an intermediate of 1024 float32 values is 4096 bytes, and fusion avoids both writing and reading it, saving 8192 bytes.",
        "Without fusion the first kernel writes the intermediate to global memory and the second reads it back. Fusion keeps the value in registers, so both transfers disappear.",
        "Counting only the avoided write gives 4096 bytes and underestimates the saving by half.",
        "The reference asserts `saved == 8192`. Compare DRAM bytes in the profiler before and after fusion.",
    ),
    (
        "Name a relevant profiler counter, such as DRAM bytes read and written or the memory-throughput percentage, since the hypothesis is about memory traffic.",
        "A counter tied to the hypothesis can confirm or reject it. If DRAM bytes do not fall after fusion, the expected saving did not happen.",
        "Using only total kernel time cannot separate fewer bytes from other effects. Time can also change because of clock variation or a different compiled instruction mix, so a timing-only comparison leaves the mechanism unknown.",
        "Collect the counter for both versions on the same shape, record the values with the profiler version, and compare them.",
    ),
    (
        "Design one controlled change: apply fusion while keeping the shape, dtype, launch configuration rules, warm-up and timing method fixed.",
        "Changing one factor attributes any difference in time or counters to that change. Repeating each configuration several times also shows whether the difference exceeds normal run-to-run variation.",
        "Applying fusion and a new block size together leaves the source of a speedup ambiguous. If one change helps and the other hurts, the combined result may even show no difference and hide both effects.",
        "Diff the two configurations and confirm that only the fusion setting differs.",
    ),
    (
        "Test a boundary shape such as 1023 elements, not a multiple of the block size, and a tiny case such as 1 element.",
        "Fused kernels combine index logic from both stages, so bounds checks are a common source of errors. Odd sizes exercise partial blocks.",
        "Testing only 1024 elements misses an off-by-one bounds check that writes past the end on 1023.",
        "Compare outputs with the unfused reference for both shapes and use a guard region to detect stray writes.",
    ),
    (
        "Explain a failed optimization: if fusion raises register use so occupancy falls, throughput may drop even though DRAM bytes fell, and the hypothesis that traffic limited performance is rejected for that shape.",
        "Profiler evidence shows which resource changed. Fewer bytes with lower occupancy suggests latency hiding, not bandwidth, became the limit.",
        "Reporting the fused version as an improvement because bytes fell ignores the measured timing. The bytes counter confirms the mechanism worked, but the goal was throughput, and that goal was not met for this shape.",
        "Record registers per thread, achieved occupancy, DRAM bytes and time for both versions, then decide from all four.",
    ),
]

REASONING[48] = [
    (
        "Compute the median speedup: baseline samples `[10, 11, 9]` have median 10 and candidate `[8, 8, 9]` has median 8, so the ratio is `10/8 = 1.25`.",
        "Medians resist a single outlier sample, and the ratio of medians states how much faster the typical candidate run is in this fixture.",
        "Computing the ratio of the fastest samples, `9/8`, picks favorable outliers, while three samples are too few to support a precise estimate either way.",
        "The reference asserts `speedup == 1.25` and labels the report `gpu_benchmark: False`, since these are synthetic numbers rather than measurements.",
    ),
    (
        "Preserve raw observations: store each sample together with the conditions under which it was measured, such as the device, clocks, versions and input shape.",
        "Summaries can be recomputed from raw data, and conditions explain variation. Keeping only the median prevents checking spread or outliers later.",
        "Reporting only the speedup ratio discards the information needed to judge whether it is meaningful. With samples such as 9, 10 and 11, the spread is as large as part of the claimed gain, which a single ratio hides.",
        "Recompute the median from the stored samples and confirm it matches the reported value.",
    ),
    (
        "Check equivalence first: compare candidate output with baseline output within tolerance before evaluating performance.",
        "A faster kernel that computes something different is not an optimization. The speed ratio then measures two different behaviors.",
        "Accepting a candidate on speed and checking correctness afterward risks deploying a wrong result if the check is skipped. A kernel that skips work, for example by mishandling the tail, will often look faster precisely because it is wrong.",
        "Make the correctness assertion a gate that stops the review before timing results are reported.",
    ),
    (
        "Separate cold and warm costs: report the first run, with compilation, plan creation and allocation, separately from the steady-state median.",
        "Short jobs pay cold costs every time, while long-running services amortize them. Both boundaries are needed for different uses.",
        "Mixing the cold run into warm samples raises one sample sharply and can shift the median with only three samples.",
        "Label each sample cold or warm and compute statistics on warm samples only. Keep the cold sample in the report as its own number, since it is a real cost for short-lived processes.",
    ),
    (
        "Write the supported platform scope naming exactly the tested hardware, driver, toolkit and framework versions.",
        "Performance results apply to the tested platform. Naming it prevents readers from assuming the result holds on other GPUs.",
        "Stating the speedup for all NVIDIA GPUs generalizes from one device. Memory bandwidth, cache size and clock behavior differ by architecture, so the ratio can change or reverse on other hardware.",
        "Compare the scope statement with the recorded environment from the run and confirm every item is listed.",
    ),
    (
        "Prepare a reproducibility checklist with source revision, input data or generator, exact commands, versions, metrics, and unresolved limitations such as small sample count.",
        "A checklist allows someone else to rerun the review and see what is still uncertain.",
        "Leaving out the limits, such as only three samples, presents a fragile result as settled. A reader then cannot tell whether a follow-up run that disagrees reveals a regression or ordinary noise.",
        "Have another person or a clean environment follow the checklist and confirm it reproduces the medians. Any step that required undocumented knowledge to complete should be added to the checklist before the review is closed.",
    ),
]

REASONING[49] = [
    (
        "Classify four execution layers: a local dataframe library such as cuDF on one process, Spark physical operators planned by Catalyst, Python UDF worker processes, and model training code that consumes the results.",
        "Each layer has a different owner of execution. Catalyst can replace operators it understands, but it cannot see inside UDF processes or training code, so GPU use must be checked per layer.",
        "Calling the whole pipeline GPU-accelerated because one layer uses the GPU hides the layers that still run on CPU and the transfers between them, which often dominate.",
        "For one sample pipeline, write each step beside its layer and the evidence that would show its device, such as a plan node name or the library object type.",
    ),
    (
        "Explain the relationship: cuDF is a GPU dataframe library, while the RAPIDS Accelerator is a Spark plugin that uses cuDF kernels to execute Spark physical operators in place of CPU ones.",
        "Spark code keeps the Spark API, and the plugin rewrites the physical plan at execution time. cuDF code calls GPU functions directly and has no Spark planner.",
        "Assuming installing cuDF on executors accelerates Spark SQL confuses the two, since without the plugin configured Spark never routes operators to cuDF.",
        "Check the Spark configuration for the plugin class and inspect the executed plan for GPU operator names. In a cuDF script, check the dataframe type.",
    ),
    (
        "Identify an opaque UDF: a Python function applied row by row, such as one that parses a string with custom logic, is arbitrary host code that Catalyst cannot translate.",
        "Spark sends rows to a Python worker and receives results back. The plugin cannot run arbitrary Python on the GPU, so the plan gains a CPU section around the UDF.",
        "Assuming a UDF runs on the GPU because surrounding operators do ignores the boundary, and the measured time then includes conversions the plan does not advertise.",
        "Look for the Python evaluation node in the executed plan and the transitions immediately before and after it.",
    ),
    (
        'Write equivalent expressions: Scala `df.groupBy("label").agg(sum("value"))` and PySpark `df.groupBy("label").agg(F.sum("value"))`, both with the same schema and null policy, giving A 6 and B 14 for values `[2, 4, 6, 8]`.',
        "Both front ends produce the same logical plan through Catalyst, so the language does not change the relational result.",
        "Writing the PySpark version with a Python loop over collected rows changes where the work happens and loses the equivalence, even if the totals match.",
        "The reference asserts `totals == {'A': 6, 'B': 14}`. Run both versions and compare their outputs and physical plans.",
    ),
    (
        "Define CPU-only progress: run semantic references such as the grouped totals, and inspect teaching plans, without claiming any GPU execution.",
        "On a machine without a GPU, correct semantics and plan reading are real progress. GPU behavior remains unverified, and saying so keeps the record honest.",
        "Reporting a CPU run as evidence that the GPU path works confuses semantic parity with accelerated execution.",
        "Each CPU result should be labeled as a CPU reference, as the reference output does with `no GPU execution claimed`.",
    ),
    (
        "List real GPU evidence: a compatible GPU runtime, plugin enabled, the executed physical plan showing GPU operators, operator metrics from the run, and results equal to the CPU reference.",
        "Each item rules out a separate failure, such as a plugin that is configured but falls back on every operator, or a GPU run that computes a different result.",
        "Presenting only a configuration file as GPU evidence shows intent but not execution.",
        "Collect each item from a single run on the target host and attach them together in the validation record.",
    ),
]

REASONING[50] = [
    (
        "List the compatibility matrix axes: Spark version, Scala binary line, Java version, plugin release, CUDA runtime, host architecture, driver, GPU model and operating system.",
        "The plugin jar links against Spark and Scala internals and loads native libraries for a host architecture and CUDA. Each axis can independently break loading or execution.",
        "Treating the jar name as proof of compatibility ignores axes the name does not encode, such as the driver or GPU architecture.",
        "Fill one row of the matrix for the target cluster and confirm each value is recorded from the environment rather than assumed.",
    ),
    (
        "Identify a Scala mismatch: a jar built for Scala 2.12 on a Spark distribution built for 2.13 is rejected, as `compatible('2.13', '2.12', 'x86_64', 'x86_64')` returns False.",
        "Scala binary lines are not compatible with each other, so classes compiled for one may reference methods that do not exist in the other, which shows up as `NoSuchMethodError`.",
        "Matching only the Spark version number while ignoring the Scala suffix in the jar name leads to runtime linkage errors before any query runs.",
        "The reference asserts the matching case is accepted and the mismatched case rejected. Read the Scala version from the Spark distribution and the jar's artifact suffix.",
    ),
    (
        "Distinguish toolkit and driver: the CUDA toolkit is a build-time and library dependency, while the driver is installed on the host and determines which CUDA runtime versions can run.",
        "A plugin built with a newer CUDA runtime may require a minimum driver version. Having the toolkit installed does not satisfy a missing or older driver.",
        "Checking `nvcc --version` and concluding the host is ready tests the compiler, not the driver the executors will use.",
        "Record the driver version reported by `nvidia-smi` on each executor host and compare it with the plugin release's stated minimum.",
    ),
    (
        "Record artifact provenance: the plugin release version, the checksum of the downloaded jar and the primary source URL it came from.",
        "Provenance lets reviewers confirm the jar is the published artifact and not a modified or mismatched copy.",
        "Copying a jar from a shared folder without a checksum leaves no way to tell which build it is.",
        "Compute the checksum of the jar on the cluster and compare with the published value.",
    ),
    (
        "Design a CPU rollback: keep an ordinary Spark configuration without the plugin, plus the same query, so the job can run on CPU if the GPU setup fails.",
        "The rollback provides both an operational fallback and a semantic reference for comparing GPU results.",
        "Removing CPU configuration once the plugin works means a driver or library failure stops the job entirely.",
        "Periodically run the rollback configuration and confirm it produces the expected result.",
    ),
    (
        "Define compatibility acceptance as import, executor startup, a bounded query and the expected result, all on the selected host with the recorded versions.",
        "Each step tests a deeper level of integration. A row in the matrix is accepted only when all steps pass there.",
        "Accepting a host because the Spark session started with the plugin listed skips native library loading on executors and actual query execution.",
        "Store the result of each step for each row and accept the row only with all four passing.",
    ),
]

REASONING[51] = [
    (
        "Draw the logical plan as intent, such as a scan, a filter and an aggregate, and the physical plan as the chosen execution, such as a file scan, a filter operator, a partial aggregate, an exchange and a final aggregate.",
        "Catalyst optimizes the logical plan and then picks physical operators. Only physical nodes show where data is shuffled and which implementation runs.",
        "Reading device placement from the logical plan fails, because logical nodes carry no device information and the plugin acts only on the physical plan.",
        'Print `explain(mode="formatted")` and match each logical step to the physical nodes that implement it.',
    ),
    (
        "Mark GPU candidate nodes using the actual operator names from the selected plugin release, such as names beginning with `Gpu`, in the synthetic plan the filter and aggregate.",
        "Plugin operator names identify replaced nodes directly. Names can differ between releases, so the release documentation is the authority.",
        "Guessing GPU placement from operator type, for example assuming all aggregates run on the GPU, ignores expression-level fallback.",
        "Count nodes with GPU names in the executed plan; the reference counts two GPU nodes in its synthetic plan.",
    ),
    (
        "Locate transitions between CPU and GPU nodes. The synthetic plan `scan CPU, filter GPU, aggregate GPU, collect CPU` has two, one into and one out of the GPU section.",
        "Each transition can copy data between host and device or convert between row and columnar format, so transitions carry cost not shown by operator names.",
        "Counting GPU nodes and ignoring transitions makes a plan with many short GPU sections look better than one long section.",
        "The reference computes `transitions == 2`. In a real plan, count the row to columnar and columnar to row nodes.",
    ),
    (
        "Explain lazy evaluation: building a DataFrame with filters and aggregations creates a plan only, and an action such as `count()` or `collect()` triggers execution.",
        "Spark delays work so it can optimize the whole plan. Before an action, no tasks run and no runtime metrics exist.",
        "Timing the line that defines the DataFrame and reporting it as query time measures plan construction, which is nearly instant.",
        "Watch the Spark UI and confirm that a job appears only after the action is called.",
    ),
    (
        "Compare the initial and final adaptive query execution plans: AQE can change join strategies or coalesce partitions during execution, so the final plan shows what ran.",
        "AQE uses runtime statistics. The plan printed before execution is a starting point that may be replaced.",
        "Citing the pre-execution plan as the executed plan can report a join strategy that never ran.",
        "After the action, read the final plan from the SQL tab in the Spark UI and compare it with the initial `explain` output.",
    ),
    (
        "Choose operator metrics together: output rows, batches, operator time, spill bytes and GPU memory observations, so that one metric does not mislead.",
        "Rows confirm correctness of scale, time shows cost, and spill reveals memory pressure. A fast operator that spilled heavily may not stay fast with larger data.",
        "Reporting only total job time hides which operator dominates and whether spilling occurred.",
        "Collect metrics for each GPU operator from the SQL view after the action and check row counts against expectations.",
    ),
]

REASONING[52] = [
    (
        "Classify the two states: a machine with no visible GPU and the plugin disabled runs the CPU baseline, while a GPU machine with the plugin enabled can still run one operator on CPU through fallback.",
        "Fallback is a per-operator decision inside a valid plugin environment. An unavailable device is an environment condition that requires the CPU configuration for the whole job.",
        "Calling a GPU-less run a fallback suggests the plugin was active and made per-operator choices, when actually it never started.",
        "The reference asserts the first state has `plugin_enabled` False and the second has a CPU operator inside an enabled plugin. Check `spark.plugins` and plan names for each state.",
    ),
    (
        "Find an unsupported expression by consulting the plugin's supported operators and expressions for the selected release, and by reading fallback explanations the plugin can log.",
        "Support depends on the operator, the expression and the data types involved. An aggregate can be supported while a specific function inside it is not.",
        "Assuming support from the operator name alone misses expression-level and type-level restrictions, which are the usual cause of fallback.",
        "Enable the plugin's explain output for fallback reasons and confirm the listed reason names the expression found in the documentation.",
    ),
    (
        "Count boundary costs for GPU aggregate, CPU UDF, GPU projection: two transitions, each converting columnar device batches to host rows or back, with data copies in both directions.",
        "Every transition copies data and changes representation. Two transitions around a single UDF can cost more than the UDF itself.",
        "Assuming only the UDF runs slower and the rest stays fast ignores that the transitions stall the GPU sections on both sides.",
        "Read the transition nodes and their metrics in the executed plan, and compare their time with the UDF node's time.",
    ),
    (
        "Rewrite an opaque function declaratively when an equivalent built-in exists, such as replacing a Python UDF that uppercases and trims with `upper(trim(col))`.",
        "Built-in expressions are visible to Catalyst and can be supported by the plugin, removing the transitions around the UDF.",
        "Rewriting with a built-in that differs on edge cases, such as whitespace or null handling, changes results while appearing equivalent.",
        "Run parity tests on nulls, empty strings and Unicode before accepting the rewrite, then confirm the transitions disappeared from the plan.",
    ),
    (
        "Preserve edge semantics: test nulls, integer overflow, strings with multibyte characters and timestamps across time zones on both the CPU and GPU paths.",
        "GPU implementations aim to match Spark semantics, but edge cases are where differences appear, and some may be documented incompatibilities.",
        "Testing only typical values passes implementations that disagree exactly where production data is unusual.",
        "Build a small table containing each edge case and compare CPU and GPU outputs row by row.",
    ),
    (
        "Design a mixed-plan report listing each CPU node in an otherwise GPU plan, the reason given for fallback, and the transitions it created.",
        "A report connects each fallback to its cause, guiding which rewrite or configuration change would help.",
        "Reporting only the percentage of GPU operators hides which fallback is expensive. One fallback on a small lookup table may be harmless, while one on the widest projection can dominate the job.",
        "Generate the report from the executed plan and fallback log, and check each listed transition appears in the plan.",
    ),
]

REASONING[53] = [
    (
        "Calculate both counts over `[2, null, 5]`: `COUNT(*)` is 3 because it counts rows, and `COUNT(value)` is 2 because it counts non-null values; `SUM(value)` is 7.",
        "SQL defines `COUNT(*)` on rows and `COUNT(expr)` on non-null expression values, and aggregate functions such as SUM skip nulls.",
        "Treating null as zero gives the same sum but makes `COUNT(value)` 3 and the average 7/3 instead of 3.5, which disagrees with Spark.",
        "The reference asserts row count 3, non-null count 2 and sum 7. Run the same aggregates in Spark on CPU and GPU and compare.",
    ),
    (
        "Handle an all-null aggregate: under Spark SQL semantics, `SUM` and `AVG` over only null values return null, while `COUNT(value)` returns 0.",
        "Null means no defined value, so a sum over no values is null rather than zero. Count still has a defined answer.",
        "Returning 0 for the sum of an all-null group makes a group with no data look like a group whose values cancel out.",
        "Create a group with only nulls and assert the documented null and zero results on both paths. Include a second group with mixed values so the test also confirms nulls are skipped there.",
    ),
    (
        "Compare decimal values with an exact decimal type and scale: `Decimal('1.10') + Decimal('2.20')` equals `Decimal('3.30')`.",
        "Decimals represent base-ten fractions exactly within their precision, so equality is exact. Spark also tracks result precision and scale.",
        "Using float64 for the same values gives `3.3000000000000003`, which fails an exact comparison and suggests a bug that exists only in the test.",
        "The reference asserts the decimal equality. In Spark, check the result schema's precision and scale as well as the value.",
    ),
    (
        "Name the session timezone explicitly, such as `spark.sql.session.timeZone = UTC`, and record it with every timestamp result.",
        "Spark renders and parses timestamps using the session timezone. Two runs with different defaults can show different values for the same instant.",
        "Relying on the machine's default timezone gives results that depend on where the job runs. Executors and the driver may also disagree, producing values that differ between stages of one job.",
        "Run the same query under two timezone settings and confirm the stored instant is equal while the rendered strings differ as expected.",
    ),
    (
        "Choose float tolerances based on dtype, algorithm and magnitude, such as a relative tolerance near float64 epsilon times the number of summed terms for a parallel sum.",
        "GPU aggregations may sum in a different order, which changes rounding. Tolerance should cover that difference without hiding real errors.",
        "Using exact equality for float sums fails on correct results, while using a very loose tolerance passes wrong ones.",
        "Compare CPU and GPU sums for a fixed dataset and confirm the differences fall within the chosen tolerance.",
    ),
    (
        "Design an ordered comparison: sort both results by stable keys, including all columns needed to order duplicates, before comparing, and keep duplicate rows.",
        "Spark does not guarantee output order without `ORDER BY`, and GPU execution may produce a different order.",
        "Converting results to sets before comparing removes duplicates and hides a missing or extra row.",
        "Compare sorted lists and also compare row counts. When duplicates are expected, compare per-key counts too, so a duplicated row and a missing row cannot cancel each other out.",
    ),
]

REASONING[54] = [
    (
        "Count fixed-width payload as rows times element width: 1000 float64 values occupy `1000*8 = 8000` bytes before masks and metadata.",
        "Fixed-width columns store values contiguously, so payload is exactly rows times width.",
        "Counting 1000 values as 4000 bytes by assuming float32 underestimates the transfer by half when the schema says double. Schema inference from CSV or pandas commonly produces double even when the data looks like small decimals.",
        "The reference asserts `payload == 8000`. Read the schema to confirm the type, then compare with Arrow buffer sizes.",
    ),
    (
        "Count validity bytes as the ceiling of rows over eight: nine rows need `(9 + 7)//8 = 2` bytes of mask at one bit per row.",
        "Arrow-style formats store one validity bit per row, padded to whole bytes, separate from the values.",
        "Using `9//8 = 1` floors the division and leaves the ninth row without a bit. The ninth row's null state would then be read from whatever byte follows the mask.",
        "The reference asserts `mask == 2`. Check 8 rows gives 1 and 16 gives 2. Some implementations pad buffers to 8 or 64 bytes, so measured sizes can exceed this minimum, which the ledger should note.",
    ),
    (
        "Explain string offsets: a string column stores all characters in one buffer and an offsets array marking where each string begins and ends; `['a', 'longer', '']` has 7 bytes of characters.",
        "Variable-length data needs boundaries. Offsets allow empty strings and long strings in the same column without padding.",
        "Estimating string columns as rows times an average length ignores the offset array and the UTF-8 encoding of multibyte characters.",
        "The reference sums UTF-8 lengths to 7. Add offsets of four entries for three strings to the ledger. With 32-bit offsets that adds 16 bytes, more than the 7 bytes of characters in this tiny column.",
    ),
    (
        "Locate row to column transitions in the physical plan, which appear where a row-based operator meets a columnar one.",
        "Each transition converts representation, which costs time and memory proportional to the data size. Columnar to row conversion must also rebuild each row object, which is expensive for wide schemas.",
        "Assuming the whole query is columnar because the source is a Parquet file ignores row-based operators later in the plan. A Python UDF or an unsupported expression in a later stage forces a conversion back to rows at that point.",
        "Count the transition nodes in the executed plan and read their metrics. Rows and time per transition node show which conversion costs most.",
    ),
    (
        "Budget transfer payload as values plus validity masks plus string offsets plus temporary copies created during conversion.",
        "Each buffer moves across the bus, and conversions may hold two copies at once, raising peak memory.",
        "Budgeting only values underestimates both transfer time and peak memory. For string-heavy tables, offsets and variable character data can exceed the numeric payload by a wide margin.",
        "Compute the ledger for a test table and compare with measured buffer sizes in Arrow or device memory reports. A table with nulls, empty strings and multibyte text exercises every term in the ledger.",
    ),
    (
        "Design a conversion parity test comparing schema, row identity, nulls and values before and after converting between Spark rows, Arrow and back.",
        "A conversion can drop null information, change types or reorder rows. Checking each property catches each failure.",
        "Comparing only values with nulls replaced by zero erases the distinction the mask exists to keep. A conversion bug that turns nulls into zeros would then pass the test unnoticed.",
        "Use a key column, compare schemas exactly, and compare null positions as well as values.",
    ),
]

REASONING[55] = [
    (
        "Compute resource-share slots: an executor with one GPU and tasks requesting `spark.task.resource.gpu.amount = 0.25` admits `1/0.25 = 4` tasks by GPU accounting.",
        "Spark's resource scheduler treats the GPU as a divisible amount for admission. Four tasks of one quarter each exhaust the executor's one unit.",
        "Reading 0.25 as a quarter of the device's memory reserved for each task treats an admission count as a hardware partition, which Spark does not create.",
        "The reference uses `Fraction` to compute `slots == 4` exactly. Check the executor's task count in the Spark UI while a stage runs.",
    ),
    (
        "Combine CPU and GPU limits: the effective number of concurrent tasks is the minimum of GPU shares, executor cores divided by cores per task, and the plugin's concurrent GPU task limit; with a plugin limit of 2 the active bound is `min(4, 2) = 2`.",
        "Each control gates a different resource. Spark may run four tasks, but the plugin lets only two use the GPU at once, so the others wait inside the plugin.",
        "Tuning only the GPU amount and expecting four concurrent GPU tasks ignores the plugin limit, and the extra tasks hold CPU slots while waiting.",
        "The reference asserts `active == 2`. Record each setting and compare with observed concurrent GPU tasks in plugin metrics.",
    ),
    (
        "Explain that fractional GPU amounts do not partition VRAM: four tasks sharing one GPU allocate from the same device memory pool as their work demands.",
        "Scheduling shares limit how many tasks start, but each task's memory use depends on its batch and operators. One large task can use most of the memory.",
        "Planning each task to have a quarter of device memory leads to out-of-memory errors when tasks use more than that share.",
        "Monitor device memory during a stage with several tasks and observe that usage varies by task rather than splitting evenly.",
    ),
    (
        "Verify device addresses: check that each executor discovers its GPUs through the configured discovery script and that task resource info lists the assigned address.",
        "Explicit discovery prevents two executors on a host from both using GPU 0 while another GPU sits idle.",
        "Assuming the default device assignment is correct on multi-GPU hosts risks oversubscribing one device.",
        "Log `TaskContext.get().resources()['gpu'].addresses` in a small job and confirm addresses are distinct across executors on the same host.",
    ),
    (
        "Design a concurrency experiment that varies only the task concurrency setting while holding the query, partition count and data fixed.",
        "Partition count and data size both affect stage time, so they must stay constant for differences to be attributed to concurrency.",
        "Changing concurrency and partition count together makes it impossible to tell which caused the change.",
        "Record settings and stage metrics for each run, and confirm the outputs match across runs.",
    ),
    (
        "Describe oversubscription failure: too many live tasks on one GPU can exhaust device memory, causing spills or task failures without any syntax or configuration error.",
        "Memory demand appears only at runtime, so a configuration that looks valid can fail on larger data.",
        "Concluding from a successful small test that a concurrency setting is safe misses failures that appear with real data volumes.",
        "Increase concurrency on a representative dataset and watch spill metrics and task failures to find the safe bound.",
    ),
]

REASONING[56] = [
    (
        "Compute concurrent live memory: three tasks at 2 GiB each plus 1 GiB shared workspace need `3*2 + 1 = 7` GiB, and four tasks need 9 GiB.",
        "Tasks running at the same time each hold their live set, and the shared workspace is counted once. Peak demand is the sum at the point of greatest overlap.",
        "Counting the shared workspace once per task gives 10 GiB for three tasks and wrongly rejects a configuration that fits.",
        "The reference asserts 7 and 9 and finds safe task counts `[1, 2, 3]` for an 8 GiB capacity.",
    ),
    (
        "Lower concurrency from four to three tasks to bring demand under the 8 GiB budget, since each task removed frees its 2 GiB live set.",
        "Fewer simultaneous tasks reduce peak demand while each task's work is unchanged. The cost is less parallelism, which may lengthen the stage.",
        "Raising batch size to finish faster increases per-task memory and makes the overflow worse. It may also push the job into heavier spilling, which slows the stage more than the larger batches speed it up.",
        "Run with three tasks and confirm that spill metrics fall and the stage completes without memory errors. Compare total stage time with the four-task run, since lower concurrency can still win once spilling stops.",
    ),
    (
        "Separate JVM heap and device memory: Spark executor memory settings control the JVM heap on the host, while the plugin manages a separate GPU memory pool.",
        "The two allocators serve different data and have different limits, so a GPU out-of-memory is not fixed by increasing the executor heap.",
        "Raising `spark.executor.memory` after a GPU memory error adds host memory and leaves the device budget unchanged.",
        "Read the error message to see which allocator failed, and change the matching setting.",
    ),
    (
        "Budget spill disk with an explicit, disposable path and known capacity, since spilled batches are written to local storage.",
        "Spill files consume disk space proportional to the spilled data. An unbounded spill can fill a shared disk.",
        "Leaving spill on the default temporary directory of a small root volume risks filling it and affecting other processes.",
        "Configure the local directories, check free space before the run and record spill bytes after it.",
    ),
    (
        "Design safe batch changes by bounding rows and bytes per batch before launch, such as limiting the target batch size, and change one setting at a time.",
        "Batch size drives per-task memory. A bounded batch gives a predictable live set.",
        "Doubling the batch size without a memory budget can turn a working job into an out-of-memory failure. The failure may appear only on the largest partitions, so small test inputs can pass while production data fails.",
        "Compute the per-task live set for the new batch size, compare with the budget, and then run.",
    ),
    (
        "Interpret a successful run with spills: the result is valid, but the report should state spill bytes and the added serialization and I/O time.",
        "Spilling trades speed for completion. Reporting it explains slowdowns and warns that larger data may spill more.",
        "Comparing only kernel times between a spilling run and a non-spilling run misses the end-to-end slowdown.",
        "Include spill bytes and stage time in the report next to the correctness check. Also record the spill path and peak disk use, since a later run with more data may exceed that capacity.",
    ),
]

REASONING[57] = [
    (
        "Calculate duplicate join output by multiplying key multiplicities: A appears twice on each side, so the inner join produces `2*2 = 4` rows for A.",
        "Each left row with key A pairs with each right row with key A. Duplicates multiply rather than add.",
        "Expecting the output size to be at most the smaller input underestimates joins with duplicate keys, which can grow much larger than either input.",
        "The reference asserts four joined rows, all with key A. Compute the per-key product before running large joins.",
    ),
    (
        "Add unmatched keys: B on the left and C on the right have no partners, so an inner join drops them, while a full outer join keeps each with nulls on the other side.",
        "Join type defines what happens to unmatched rows. The outer join here would return six rows.",
        "Using an inner join where unmatched records must be preserved silently drops them. Downstream totals then shrink without any error, which is harder to detect than a failure.",
        "Run inner, left and full outer joins on this fixture and count rows: 4, 5 and 6.",
    ),
    (
        "Identify skew by comparing the maximum partition with the distribution: one partition of 900 rows beside nine of about 11 has a small average but one task dominates.",
        "Stage time is set by the slowest task. The maximum matters more than the mean for wall time.",
        "Reporting the average partition size of about 100 rows hides the 900-row partition.",
        "Report maximum, median and percentiles of task durations or input sizes for the join stage.",
    ),
    (
        "Compare broadcast and shuffle joins: a broadcast join copies the small side to every executor, while a shuffle join redistributes both sides by key.",
        "Broadcast avoids shuffling the large side but requires the small side to fit in memory on every executor.",
        "Broadcasting a table that is large after a filter misestimate can exhaust executor memory. The driver also collects the broadcast side before sending it, so a too-large table can fail on the driver first.",
        "Check the size estimate and the chosen strategy in the executed plan. Compare the estimated size with the actual rows read for the small side, to see whether the threshold decision was based on accurate statistics.",
    ),
    (
        "Design a safe skew rewrite, such as salting a hot key, that preserves duplicates and null-key semantics.",
        "Salting splits a hot key across partitions and must reunite the rows so the join output is the same. The other side's rows for that key are replicated across every salt value, so each salted left row still meets every matching right row.",
        "Dropping null keys or deduplicating to reduce skew changes results. Salting only one side without replicating the other loses matches, which reduces output silently rather than raising an error.",
        "Compare the rewritten join output with the original on the fixture, including duplicates and nulls. Then compare the maximum task duration before and after, which is the quantity the rewrite targeted.",
    ),
    (
        "Inspect the final AQE decision after the action, since adaptive execution may switch to a broadcast join or split skewed partitions at runtime.",
        "AQE uses statistics from completed stages, so the executed plan may differ from the initial one.",
        "Citing the pre-execution plan reports a strategy that may not have run. Skew handling in particular appears only in the final plan, so the initial plan cannot show whether a skewed partition was split.",
        "Compare the initial explain output with the final plan in the SQL tab. Record the AQE settings with the plan, since disabling adaptive execution changes which plan runs.",
    ),
]

REASONING[58] = [
    (
        "Compute the transfer lower bound as bytes over effective bandwidth: 10 GiB at 1 GiB/s takes at least 10 seconds before serialization, connection setup or retries.",
        "No implementation can move the payload faster than the link allows, so this bound is a floor on the shuffle stage regardless of kernel speed.",
        "Spending effort to halve a 100 ms kernel, saving 50 ms, addresses less than 1 percent of the 10-second floor, as the reference asserts with `kernel_saving/seconds < 0.01`.",
        "The reference asserts `seconds == 10`. Compare with measured shuffle read and write time for the stage.",
    ),
    (
        "Identify local versus network time by measuring the whole stage, including shuffle write, fetch wait time and local compute, from Spark stage metrics.",
        "Stage metrics separate time spent waiting for remote blocks from time spent computing. The larger component is the target for optimization.",
        "Profiling only the GPU kernels shows local compute and misses fetch wait time, which may dominate. A GPU profile of a shuffle-bound stage can look idle for long stretches, and that idle time is exactly the network wait.",
        "Read shuffle fetch wait time and executor compute time from the stage summary and compare them.",
    ),
    (
        "Explain pre-aggregation: computing partial sums on each map task before the shuffle sends one value per key per task rather than every row.",
        "Sum is associative and commutative, so combining partial sums gives the same total and greatly reduces shuffled bytes for keys with many rows.",
        "Pre-aggregating a non-associative operation, such as a median computed from partial medians, produces wrong results.",
        "Compare shuffle bytes and results with and without pre-aggregation on the same data, and confirm totals match.",
    ),
    (
        "List transport qualification for an accelerated shuffle transport: supported network devices, topology, matching library versions and a test with real traffic between hosts.",
        "Accelerated transports depend on specific hardware and libraries, and a misconfiguration may fall back to a slower path without obvious errors.",
        "Enabling the transport setting and assuming it is active skips checking whether it actually carried traffic. A missing library on one host can silently route that host's traffic over the default path.",
        "Check transport logs or metrics on both sides of a test shuffle and confirm bytes went over the intended path.",
    ),
    (
        "Separate startup settings: some shuffle manager and transport choices are read when executors start, so changing them requires a fresh application.",
        "Settings fixed at startup cannot change for a running session. Changing them mid-session has no effect.",
        "Setting a shuffle manager in an existing session and attributing later timing changes to it measures noise. Any improvement seen there comes from caching, warm JIT code or variation between runs.",
        "Restart the application with the new setting and confirm it appears in the environment tab.",
    ),
    (
        "Design a bounded shuffle comparison using identical partitioned fixtures for both configurations, capturing shuffle bytes, spills and output.",
        "Same data and partitioning make byte counts comparable, and equal outputs confirm the change preserved results.",
        "Comparing configurations on different data sizes confounds the transport effect with payload size. Different partition counts also change the number of shuffle blocks, which affects per-block overhead independently of bandwidth.",
        "Assert outputs are equal, then report bytes and stage times side by side. Repeat each configuration at least three times and keep every sample, since network contention varies between runs.",
    ),
]

REASONING[59] = [
    (
        "Calculate partition averages: one million rows over 100 partitions averages 10000 rows, and over 10 partitions averages 100000.",
        "Fewer partitions mean more rows per task, which raises per-task memory and can cause spills even though scheduling overhead falls.",
        "Reducing partitions to cut scheduling overhead without checking per-task memory can turn a working job into a spilling one.",
        "The reference asserts both averages. Compare with actual task input sizes in the Spark UI.",
    ),
    (
        "Explain skew beyond averages: report the maximum and tail of partition sizes, since one large partition sets the stage time.",
        "An average of 10000 rows can hide a single partition of 200000, and that task runs much longer than the rest.",
        "Reporting only the average leaves skew invisible. Adding partitions does not fix skew either, because a hot key still lands in one partition however many there are.",
        "Collect per-task input rows and report median, 95th percentile and maximum. A maximum several times the median marks a stage worth investigating for key skew.",
    ),
    (
        "Capture the final AQE plan after the action, since adaptive execution may coalesce small partitions or split large ones at runtime.",
        "The partition counts in the initial plan may not be the ones that ran.",
        "Reporting partition counts from the pre-execution plan can describe a configuration AQE changed. Coalescing may reduce 200 shuffle partitions to a handful, which changes per-task memory considerably.",
        "Read the final plan from the SQL tab and record partition counts per stage. Record the AQE advisory partition size alongside, since it drives the coalescing result.",
    ),
    (
        "Define a cache policy with equivalent states for both runs, either both cold or both warm with the same data cached.",
        "Reading cached data is faster than downloading or reading from disk, so a warm GPU run against a cold CPU run measures caching, not execution.",
        "Comparing those runs reports a speedup partly caused by the cache, as the reference rejects for unmatched cache states.",
        "Record cache state for each run and reject comparisons where the states differ. Clearing caches or restarting the application before cold runs, and running a discarded warm-up before warm runs, makes the states reproducible.",
    ),
    (
        "Choose fixtures for different purposes: tiny bounded data for semantic correctness and representative data sizes for performance measurement.",
        "Tiny data finishes quickly and exercises edge cases, but its timings are dominated by overhead.",
        "Reporting performance from the tiny correctness fixture gives timings that say nothing about production scale. At a few rows, Spark job scheduling dominates and both backends look the same, or the GPU looks slower.",
        "Label each fixture by purpose and use only the representative one for timing claims. Run the correctness fixture on both backends too, so the representative timings are known to come from equivalent computations.",
    ),
    (
        "Separate estimated and observed speedup: an estimate from a model remains a prediction until a run on target hardware measures it.",
        "Estimates guide which experiments to run, while observations support claims. Keeping them separate prevents treating predictions as results.",
        "Writing an estimated 3 times speedup into a report as achieved presents unverified data as fact. Readers then plan hardware purchases or migrations around a number nobody measured.",
        "Mark each speedup in the report as estimated or observed, and for observed values cite the run. If an observation disagrees with the estimate, keep both and note which model assumption failed.",
    ),
]

REASONING[60] = [
    (
        "Classify four API surfaces: built-in SQL and DataFrame expressions, row-at-a-time Python UDFs, pandas-style vectorized UDFs that receive Arrow batches, and a local GPU dataframe library such as cuDF called inside a task.",
        "Each surface hands data to a different executor. Built-in expressions stay in the planner's view, while the other three move data into Python processes where Catalyst and the plugin cannot follow.",
        "Treating a pandas UDF as equivalent to a built-in because it is vectorized ignores the process boundary and serialization that still surround it.",
        "For one example transformation, write it on all four surfaces and inspect the executed plan for Python evaluation nodes in the last three.",
    ),
    (
        "Replace a simple UDF that returns `x*2` with the built-in expression `col('x') * 2`, after confirming the null and type semantics match: null input gives null output in both.",
        "The built-in expression is visible to the optimizer and can run on the GPU through the plugin, removing the transitions to and from a Python worker.",
        "Replacing a UDF that maps null to 0 with the built-in, which keeps null, changes results while appearing to be the same arithmetic.",
        "The reference asserts `[2, None, 6]` from `[1, None, 3]`. Run the built-in on the same values and compare, including the null position and the result type.",
    ),
    (
        "Explain Arrow limits: Arrow is an in-memory columnar interchange format that lets Spark pass batches to Python efficiently, but it is not an execution device.",
        "Arrow reduces serialization cost at the boundary. The UDF body still runs wherever its own code runs, usually on the CPU.",
        "Assuming that enabling Arrow moves UDF work to the GPU confuses data format with execution location.",
        "Compare UDF time with Arrow enabled and disabled on CPU, and check the plan for the same Python evaluation node in both.",
    ),
    (
        "Define GPU-aware UDF ownership: each task records which device address it was assigned, bounds the batch it moves to that device, and frees device memory before returning.",
        "Several Python workers can share one GPU. Without explicit ownership they all default to device 0 and their memory adds up without any coordination.",
        "Calling a GPU library from every partition with no device assignment risks oversubscription and out-of-memory errors that appear only at higher concurrency.",
        "Log the assigned address and the peak device memory per task, and confirm memory returns to its baseline after each task finishes.",
    ),
    (
        "Distinguish SQL acceleration, which replaces Spark operators through the plugin, from ML acceleration, which uses separate GPU training libraries with their own integration.",
        "The two have different configuration, support lists and evidence. A GPU-accelerated ETL plan says nothing about whether the training step used the GPU.",
        "Reporting the whole pipeline as accelerated because the SQL plan shows GPU operators omits the training step.",
        "Collect evidence separately: the executed plan for SQL and the training library's device logs or metrics for ML.",
    ),
    (
        "Design quality parity tests for GPU and CPU model training: same train and test split, same target, same metric and same preprocessing, comparing the metric within a stated tolerance.",
        "Training algorithms on different backends can differ in floating-point order and defaults, so model quality, not identical weights, is the right comparison.",
        "Comparing a GPU model trained on a different split with a CPU model attributes data differences to the backend.",
        "Fix the split by a seeded key, record preprocessing steps, and report both metrics with the tolerance used.",
    ),
]

REASONING[61] = [
    (
        "Draw scheduler layers: Kubernetes schedules driver and executor pods onto nodes based on resource requests such as `nvidia.com/gpu: 1`, and Spark then schedules tasks onto executors.",
        "A GPU executor must first be placed on a node that advertises the GPU resource. Only after that does Spark's task scheduling apply.",
        "Debugging Spark task settings when executors never started confuses the two layers, since the problem sits at pod placement.",
        "The reference finds `eligible == ['gpu-node']`. In a cluster, check node allocatable resources for the GPU resource name.",
    ),
    (
        "Name ownership boundaries: the exact cluster context, a dedicated namespace and labels identifying the job, so every created resource can be identified.",
        "Shared clusters host other workloads. Explicit namespace and labels allow inspection and cleanup without touching unrelated resources.",
        "Running in the default namespace without labels mixes lab resources with others, making safe cleanup impossible. It also makes the cluster context easy to get wrong, so commands meant for a lab cluster can reach a shared one.",
        "List resources with the job label and confirm they are all in the lab namespace. Print the current context before each command so the target cluster is visible in the session log.",
    ),
    (
        "Diagnose Pending executors by reading pod events and comparing requested resources with node availability, such as a GPU request when no free GPU node exists.",
        "Events state why the scheduler could not place the pod. A running driver with Pending executors proves submission worked but placement did not.",
        "Changing Spark code or increasing memory without reading events addresses the wrong layer. Raising executor memory can even make placement harder, since larger requests fit on fewer nodes.",
        "Run `kubectl describe pod` on a Pending executor and act on the scheduling message. Messages such as insufficient GPU resources or an untolerated node taint each point to a different fix.",
    ),
    (
        "Verify device visibility with a bounded probe executor that lists GPUs inside its container and exits.",
        "A pod scheduled on a GPU node still needs the device plugin and container runtime to expose the device.",
        "Assuming visibility because the node has a GPU misses runtime misconfiguration that leaves the container without the device. The executor would then start and the plugin would fail at initialization, or the job would run entirely on CPU.",
        "Check the probe output for the expected device, then delete the probe pod. Also confirm the driver version reported inside the container meets the plugin release's minimum.",
    ),
    (
        "Design private networking: keep the Spark UI, driver service and any internal endpoints private, reachable only through controlled port forwarding.",
        "Spark services can expose job details and accept connections. Public exposure creates risk with no benefit for a lab.",
        "Exposing the driver UI with a public load balancer for convenience makes job data reachable from outside. Query plans and configuration can include paths, table names and connection details.",
        "List services in the namespace and confirm none has a public external address. Use `kubectl port-forward` for temporary UI access and close it after inspection.",
    ),
    (
        "Write scoped cleanup that deletes only resources carrying the lab's labels in its namespace, after saving the logs requested for the record.",
        "Label-scoped deletion protects other workloads, and preserving logs first keeps evidence.",
        "Deleting by broad name patterns or whole namespaces you did not create can remove unrelated work. Deleting before saving logs also destroys the evidence needed to explain a failed run.",
        "List labeled resources before and after cleanup and confirm only those were removed and the logs remain saved.",
    ),
]

REASONING[62] = [
    (
        "Classify the failure layer from the first evidence: a device out-of-memory error while JVM heap is below its limit places the failure in GPU memory, not the JVM.",
        "The first error message names the allocator that failed. Later errors are often consequences, such as lost executors or retried tasks.",
        "Increasing JVM heap after a device OOM changes an unrelated limit and leaves the GPU live set unchanged.",
        "Find the earliest error in executor logs and record which layer it names before changing any setting.",
    ),
    (
        "Correlate job identities: link the application ID, executor ID, stage ID, task attempt and SQL execution ID for the failing task.",
        "These IDs connect logs, metrics and plans. Without them, evidence from different sources may describe different tasks.",
        "Matching logs by timestamp alone can mix events from concurrent tasks. Clock differences between hosts make timestamp matching even less reliable across executors.",
        "Use the IDs from the Spark UI to find the matching executor log lines and SQL plan. Record the chain of IDs in the incident notes so the correlation can be checked later.",
    ),
    (
        "Budget before changing settings: count the actual live-set and spill categories from metrics, then choose a change such as lower concurrency or smaller batches.",
        "A budget explains why memory ran out and predicts whether a change will fit.",
        "Trying random settings until the job passes may hide the cause and fail again on larger data. Several simultaneous changes also make it impossible to say which one fixed the failure.",
        "Compare the predicted peak after the change with measured peak in the next run. A large mismatch means a memory category is missing from the budget and should be found before more tuning.",
    ),
    (
        "Analyze retry side effects: two attempts writing key-7 are 2 raw writes but 1 logical key, so retries can duplicate external effects.",
        "Spark retries failed tasks, giving at-least-once execution for side effects outside its commit protocol.",
        "Sending messages directly from tasks without idempotency produces duplicates after a retry. Speculative execution can run two attempts at once, duplicating writes even without any failure.",
        "The reference asserts `raw == 2` and `idempotent == 1`. Use idempotent keys or a transactional sink, and test with an injected retry.",
    ),
    (
        "Define process cleanup that terminates only the job's own processes and pods, identified by recorded IDs or labels.",
        "Owned cleanup prevents harming other jobs on shared hosts. Orphaned executor processes holding GPU memory are a common cause of the next job failing, so cleanup also protects later runs.",
        "Killing all Java or Python processes on a node stops unrelated work. It can also kill the node's own agents, which are often Java or Python processes.",
        "List the job's processes before cleanup and confirm only those exited. Afterward, check that device memory on the GPU returned to its idle level.",
    ),
    (
        "Preserve an incident packet with sanitized configuration, plans, logs, metrics and the identity of the input data.",
        "The packet lets someone reproduce and analyze the failure later without access to the live system. Logs and metrics often expire on a retention schedule, so the packet may be the only lasting copy.",
        "Keeping raw configuration with credentials risks leaking secrets. Dropping configuration entirely, on the other hand, removes the settings needed to reproduce the failure.",
        "Check the packet for secrets and confirm it contains each listed item. Record the input data identity as a path and version or checksum rather than copying sensitive data.",
    ),
]

REASONING[63] = [
    (
        "Derive expected revenue by joining sales to prices and summing quantity times price per product: A is `(2 + 4)*10 = 60` and B is `3*20 = 60`.",
        "Each sale row matches exactly one price row, so revenue per product is the sum of quantities times that price. The integer fixture gives exact output with no tolerance needed.",
        "Summing prices per product before multiplying, or multiplying the total quantity by the sum of all prices, mixes products and gives wrong totals such as 180 for A.",
        "The reference asserts `[('A', 60), ('B', 60)]`. Both the Scala and PySpark pipelines must produce exactly these rows after sorting by product.",
    ),
    (
        'Write the Scala pipeline with an explicit schema for both tables, `sales.join(prices, "product")`, a column `quantity * price`, and `groupBy("product").agg(sum(...))`.',
        "An explicit schema fixes column types, so integer arithmetic stays exact and the join key types match. Each step maps directly to the reference loop.",
        "Relying on schema inference from text files can type numbers as strings or doubles, changing join behavior or output types between runs.",
        "Print the schema and the sorted result, and compare the result with the reference revenue.",
    ),
    (
        'Write the PySpark pipeline with the same schema, join, product column and aggregation, then `orderBy("product")` so output order is defined.',
        "Both languages build the same logical plan through Catalyst, so the outputs must be equal. Sorting removes order differences that are not semantic.",
        "Collecting rows into Python and summing in a loop changes where the work runs and stops being a Spark pipeline comparison.",
        "Compare the PySpark output rows with the Scala output rows and with the reference, and compare the physical plans for the same operators.",
    ),
    (
        "Test duplicate dimension keys: adding a second price row for A doubles A's matches, so the contract must either reject non-unique prices or explicitly accept the multiplicity.",
        "A join multiplies rows for duplicate keys. If the business rule says one price per product, a uniqueness check protects revenue from silent doubling.",
        "Running the join without checking lets a duplicate price row double A to 120 with no error, which looks like a real sales increase.",
        "Add the duplicate row, assert the uniqueness check fails with a clear message, and confirm revenue is unchanged when the check passes.",
    ),
    (
        "Capture executed GPU evidence on actual hardware: the final physical plan showing GPU operators for the join and aggregate, operator metrics, and output equal to the CPU result.",
        "Each piece rules out a different gap, such as configuration without execution or execution with different results.",
        "Claiming GPU execution from a CPU-only environment, or from a configuration file alone, reports evidence that does not exist.",
        "Store the plan, metrics and comparison from one run, and mark the item pending if no GPU host was available.",
    ),
    (
        "Prepare a balanced capstone report separating verified CPU functionality, such as matching Scala and PySpark outputs, from pending GPU validation and its limitations.",
        "A reader needs to know what was proven and what remains open. Mixing them overstates the result.",
        "Writing the report as if GPU acceleration was demonstrated when only CPU runs happened misleads anyone deciding on deployment.",
        "Check each claim in the report against a recorded run, and list every item that still requires hardware.",
    ),
]

REASONING[64] = [
    (
        "Compute the end-to-end tradeoff by summing every changed cost: the GPU query saves 30 seconds of compute but adds 40 seconds of transfers and conversions, so the net is 10 seconds slower.",
        "Users wait for the whole application, not only the arithmetic. The decision must use the total, including costs the GPU path introduces.",
        "Reporting the 30-second compute saving alone recommends a change that makes the application slower overall.",
        "The reference asserts `net == 10`. In practice, compare complete application times for both configurations on the same input.",
    ),
    (
        "Choose a tiny-data tool: for an analysis that a local CPU dataframe finishes in about 0.1 seconds, use that tool rather than starting a Spark application that takes seconds just to begin.",
        "Startup dominates small jobs. No kernel speedup can remove fixed overhead that is larger than the entire local computation.",
        "Using GPU Spark for every analysis because it is available adds startup and operational overhead to jobs that never needed distribution.",
        "The reference asserts the local candidate is faster than Spark startup alone. Time both on the actual small dataset to confirm.",
    ),
    (
        "Separate setup cost, such as application startup, executor allocation and compilation, from steady-state processing time for repeated queries.",
        "A long-running service pays setup once, while a one-off job pays it every time. Both numbers matter for different usage patterns.",
        "Reporting only steady-state throughput favors GPU Spark for interactive one-off use, where setup actually dominates.",
        "Report setup and steady-state times separately and state which applies to the intended workflow.",
    ),
    (
        "Include operational cost: maintaining the compatibility matrix, upgrading plugin and drivers together, and owning GPU resources and their cleanup.",
        "These costs recur and fall on the team running the system. A small performance gain may not justify them.",
        "Comparing only query time ignores the work of keeping a GPU Spark stack compatible across upgrades. A Spark upgrade can be blocked until a matching plugin release exists, which delays security patches.",
        "List each recurring task with an owner and an estimate, then include it in the recommendation. Tasks without a willing owner are a risk signal in their own right.",
    ),
    (
        "Define a reevaluation trigger, such as data growing past a stated size or the workload gaining operators the plugin supports, that would justify revisiting the decision.",
        "A decision based on current data and support may change. Named triggers tell the team when to measure again.",
        "Rejecting GPU Spark permanently ignores that the tradeoff can change, while revisiting constantly wastes effort. A trigger such as transfer time falling below compute savings ties the revisit to the exact term that decided the current outcome.",
        "Write the trigger as a measurable condition and record where its value is monitored. Include who receives the alert when the condition is met.",
    ),
    (
        "Write an evidence-based recommendation: choose the simplest option that meets the requirements, such as local CPU processing for small data, and state what evidence is still missing.",
        "The simplest qualified option minimizes operational risk. Listing missing evidence keeps the decision open to correction.",
        "Recommending the most powerful technology by default ignores the measured tradeoff and the operational cost. It also skips stating missing evidence, so the decision cannot be corrected when new data arrives.",
        "Check that each statement in the recommendation cites a measurement or is labeled as an assumption.",
    ),
]
