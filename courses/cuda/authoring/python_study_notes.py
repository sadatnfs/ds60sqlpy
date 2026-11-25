"""Per-chapter study notes for the CUDA Python and GPU Spark guides.

Each entry holds six progressive hints (hint k belongs to exercise k), the
chapter's most likely mistake with its fix, the limit of the CPU evidence and
three self-check questions whose answers are published in the solution file.
"""

STUDY_NOTES = {
    1: {
        "hints": [
            "List each step of worked example 2 in order and ask, for each one, whose memory holds the value at that moment.",
            "Picture a laptop with no NVIDIA driver. What does a successful import line still let you conclude there?",
            "Ask what `sum` must return when nothing is added, then ask whether a zero-element launch could change that value.",
            "The printed digits must exist in host memory first. Which copy puts them there, and what must finish before it starts?",
            "Start from the reference ledger's three rows and add the columns a GPU run would need to tell two copies apart.",
            "Read the line the reference actually prints and decide which backend that sentence names.",
        ],
        "mistake": "The common mistake is reading a successful `import cupy`, or a GPU package in the environment, as proof that the arithmetic ran on a device. In this chapter the reference sums `[1, 2, 3]` entirely in the Python process. To fix the claim, record four facts per operation: the issuing process, the allocation holding the inputs, the processor running the arithmetic and the event that proves the result is ready. Leave a column blank rather than guess.",
        "limit": "The reference prints `CPU reference: 6` with every ledger row on the CPU. That shows the arithmetic and the ledger format are right; it shows nothing about device residency, transfer cost or kernel completion on any GPU.",
        "self_check": [
            (
                "Why can a statement that creates a CuPy result return before the answer exists?",
                "The host only enqueues the kernel. The Python object holding shape and dtype exists immediately, while the device arithmetic finishes later; a synchronization or a transfer is what proves completion.",
            ),
            (
                "Which events in the five-event GPU sum belong to the host?",
                "Constructing the input list and retrieving the scalar into a Python integer. The copy and the reduction happen in between, and the final value must land in host memory before Python can use it.",
            ),
            (
                "Why can printing a device scalar change what you were trying to observe?",
                "Printing forces a device-to-host copy that waits for the producing kernel. That inserts a synchronization point, so timing or overlap measured around the print no longer reflects the unobserved program.",
            ),
        ],
    },
    2: {
        "hints": [
            "Count how many float32 values precede (1,1) in row-major storage, then convert elements to bytes.",
            "Keep the shape `(2, 3)` fixed and recompute both strides with an 8-byte itemsize before touching any offset.",
            "Swap the axes and ask how far in bytes one step along each new axis moves through the original storage.",
            "Apply `row*width+col` to the column slice of worked example 2 and list which original columns it reads.",
            "Write the address formula with a negative last stride and check which integer type the index arithmetic must use.",
            "Pick one case per assumption: contiguity, the stride formula, launch bounds and dtype. Name what each case would catch.",
        ],
        "mistake": "A frequent mistake is passing a sliced or transposed array to a kernel that assumes contiguous row-major data, so it computes `row*width+col` and silently reads the wrong elements. Worked example 2 shows the trap: the column slice has strides `(12, 8)`, not `(8, 4)`. Fix it by checking strides and dtype at the kernel boundary, then either rejecting the view, packing an explicit contiguous copy whose cost you report, or indexing with the real strides.",
        "limit": "The reference checks byte offsets for three views of one 2 by 3 float32 matrix. Offset arithmetic is exact here, but it does not test device alignment rules, memory coalescing or how a particular library decides to copy a non-contiguous view.",
        "self_check": [
            (
                "What does a stride tell you that a shape does not?",
                "The byte displacement for a one-step move along an axis. Two arrays with shape `(2, 2)` can address storage differently, as the column slice with strides `(12, 8)` shows.",
            ),
            (
                "Why do logical bytes and storage span differ for the column slice?",
                "The slice holds four float32 values, 16 logical bytes, but they are scattered across the original 24-byte allocation because every other column is skipped.",
            ),
            (
                "Why is reinterpreting float64 bytes as float32 wrong even when element counts match?",
                "Dtype decides both width and bit interpretation. Reading 8-byte doubles as 4-byte floats splits each value into two meaningless halves; a conversion must be an explicit cast.",
            ),
        ],
    },
    3: {
        "hints": [
            "Count bytes per iteration in the round-trip version and multiply by ten; then count the upload-once, download-once version.",
            "Hold the 4000-byte payload fixed and ask which part of the transfer model, latency or bandwidth, changes with batching.",
            "Mark when Python regains control after the asynchronous upload and when the copy engine finishes reading the host buffer.",
            "Ask who owns the page-locked buffer while a copy is pending, and what happens if that owner is garbage collected.",
            "Write where the caller's clock starts and stops, then check whether both transfers fall inside that interval.",
            "Compare about 10 microseconds of submission latency with the time a CPU needs for ten float additions.",
        ],
        "mistake": "The mistake this chapter targets is tuning the arithmetic while ignoring how many times data crosses the bus. Copying input and output on every one of K iterations moves 2KB bytes; keeping intermediates resident moves 2B. A second mistake is overwriting or freeing a host buffer while an asynchronous copy still reads it. Fix both by counting transfers before tuning kernels, and by waiting on the copy's event before reusing or releasing the source.",
        "limit": "The 81920 and 8192 byte counts come from the transfer model, not from a timer. Real effective bandwidth, pinned versus pageable behavior and copy and compute overlap must be measured on the target system before you claim a latency saving.",
        "self_check": [
            (
                "In the model latency plus B divided by W, which term does batching reduce?",
                "Only the fixed latency term, because it is paid once instead of once per copy. The bandwidth term depends on total bytes and is unchanged when the same payload is grouped.",
            ),
            (
                "Why is pinning every host array a poor default?",
                "Pinned pages cannot be swapped out and consume host resources. Pin the buffers that feed overlapping copies, and keep their owners alive until each copy completes.",
            ),
            (
                "What must an end-to-end timer include in this chapter?",
                "Preparation, the upload, the computation and the final download to host output. Excluding transfers hides exactly the difference between the round-trip and resident versions.",
            ),
        ],
    },
    4: {
        "hints": [
            "Average each column of `[[1,3],[3,7]]` first, then subtract that row vector from both rows.",
            "Append a column of identical values and compute its mean before subtracting anything.",
            "Subtract coordinates pairwise for `[1,2]` and `[4,6]`, square each difference, then add them.",
            "Repeat the expanded identity with two large, nearly equal vectors and count how many float32 digits survive the subtraction.",
            "Multiply N, M and D for the broadcast difference tensor, then multiply by the float32 itemsize.",
            "Before writing a kernel, list which library calls already compute the centering and the distance with tested edge handling.",
        ],
        "mistake": "A common mistake is trusting the expanded distance formula because it matches the direct form on small integers, as in worked example 2. The identity is exact algebra but not exact floating point: with large nearly equal vectors, subtracting squared norms cancels most significant digits. Fix it by keeping the direct difference form as the reference, and add an adversarial test with large close values before accepting the expanded or fused version.",
        "limit": "The reference verifies centering and one distance with small exact integers. It cannot reveal float32 cancellation, temporary memory pressure from broadcasting, or whether a fused kernel beats a library call; those need adversarial inputs and measured runs.",
        "self_check": [
            (
                "How does broadcasting subtract column means without building a repeated matrix?",
                "A dimension of size one is extended logically, so the length-2 mean vector is reused for every row. No full repeated copy is materialized.",
            ),
            (
                "What property of the centered result checks the computation?",
                "Every centered column sums to zero, as `[-1, 1]` and `[-2, 2]` do here.",
            ),
            (
                "Why is a mature library baseline also a performance competitor?",
                "A custom kernel must match the library's correctness and beat its speed. If the library already optimizes the operation, the custom kernel adds maintenance and testing work with no gain.",
            ),
        ],
    },
    5: {
        "hints": [
            "Create a generator with seed 7 inside a loop body and compare the first draw of each batch.",
            "Keep one generator object alive across both batches and ask where its fifth draw continues from.",
            "Call `getstate` before the batch you want to replay, draw it, then restore that state and draw again.",
            "Choose statistics whose expected values you know for the distribution, and fix a tolerance before you sample.",
            "List what a CPU generator and a GPU generator would have to share for byte equality, and what a statistical contract needs instead.",
            "Walk through one training step and name every component that draws random numbers, including the data sampler and device generators.",
        ],
        "mistake": "The classic mistake is calling the seed function at the start of every batch. Each call restarts the generator, so every batch repeats the same samples and the model sees far less variety than intended. A related mistake is assuming that one seed makes Python, NumPy, CuPy and TensorFlow emit the same numbers. Fix the first by creating one generator per stream and keeping it between batches. Fix the second by stating the reproducibility scope and using a statistical or tolerance contract across backends.",
        "limit": "The reference replays a batch with Python's own `Random` state in one interpreter. It proves save and restore within that library; it says nothing about stream equality across libraries, devices, parallel stream partitioning or a different library revision.",
        "self_check": [
            (
                "Why does a shared seed not guarantee identical numbers across CPU and GPU libraries?",
                "Each library uses its own generator algorithm, stream partitioning and version-specific details. A seed selects a starting state within one generator design, not a cross-library agreement on bytes.",
            ),
            (
                "What is the difference between restoring saved state and reseeding?",
                "Restoring resumes exactly where the stream was when the state was saved, so the replayed batch matches. Reseeding returns to the start of the stream, which repeats earlier draws.",
            ),
            (
                "Name three scopes of reproducibility a report should distinguish.",
                "Same code and environment, same backend and hardware, and cross-backend numerical agreement within a stated tolerance. Each scope needs its own evidence.",
            ),
        ],
    },
    6: {
        "hints": [
            "Follow the ledger step by step: after the array is released, which counter falls and which one stays?",
            "Change one assumption in worked example 2 while preserving the declared contract: reuse a free block.",
            "Find the Python object that still references each step's result, then decide what the loop actually needs to keep.",
            "Ask whether returning the pool's free blocks can release memory that a live array still points to.",
            "Fix a small step count and record live and reserved bytes at the same synchronization point before and after each step.",
            "Separate the limit on host process memory from the limit on device memory, and check whether a container setting reaches both.",
        ],
        "mistake": "The most common mistake is reading a high reserved total in a device memory report as a leak. A caching pool keeps freed blocks for reuse, so reserved bytes can stay at 1024 while live bytes are zero. The opposite mistake is calling `free_all_blocks()` to fix a real leak: if a list still references every step's output, live bytes keep growing to 4096 and beyond. Diagnose by comparing live and reserved counts at fixed points, then remove the unneeded references.",
        "limit": "The allocator ledger is a bounded model with exact byte counts. It does not reproduce context overhead, library workspaces, delayed asynchronous frees or fragmentation, and it deliberately avoids exhausting a shared GPU to show an out-of-memory error.",
        "self_check": [
            (
                "What does a stable reserved total across repeated equal workloads usually mean?",
                "The pool is reusing its cached blocks. That is normal behavior, not a leak, as long as live bytes also return to the same level after each step.",
            ),
            (
                "Which signal suggests retained tensors, outputs or graphs?",
                "Live allocations that grow after every step of an equal workload, like the list of results that reaches 4096 bytes after four steps.",
            ),
            (
                "Why is clearing the cache not a repair for a workload whose live set exceeds memory?",
                "Cache clearing returns only free blocks to the driver. Arrays the model still needs remain live, so the required memory is unchanged.",
            ),
        ],
    },
    7: {
        "hints": [
            "Mark the moment the launch call returns and the moment the output is ready. Which interval contains the arithmetic?",
            "Sort the five synthetic samples and pick the middle one.",
            "Draw the caller's timeline from host input to host output and place both copies on it.",
            "Separate the first call's context, compilation and allocator setup from the later repeated samples.",
            "List what must be identical on both sides before a ratio of times means anything: data, dtype, outputs and tolerance.",
            "Ask where the trace numbers came from. Were they measured on any device, or written into the program?",
        ],
        "mistake": "The mistake this chapter targets is stopping a host timer when an asynchronous launch returns. That measures enqueue latency, 2 microseconds in worked example 1, not the 102 microseconds until the output exists. Another is reporting only the fastest sample, or deleting the 100 ms outlier without explaining it. Fix the boundary with a synchronization or GPU events, report the median with a tail statistic and the sample count, and keep cold-start time in a separate row.",
        "limit": "Every value in this chapter's trace is invented for teaching. The median and maximum arithmetic is exact, but it cannot support any speedup claim; a real comparison needs measured, synchronized samples of equal work on named hardware.",
        "self_check": [
            (
                "Why can a first call be much slower than later ones?",
                "It can include context creation, library initialization, compilation and allocator population. Those are real costs, but they belong in a cold-start report separate from steady-state samples.",
            ),
            (
                "What does the median hide that the maximum reveals?",
                "Tail behavior. For `[10, 11, 10, 12, 100]` the median of 11 ms looks healthy while one request took 100 ms.",
            ),
            (
                "What makes two timings an equal-work comparison?",
                "The same input data, dtype and transfer policy, completed outputs that agree within a stated tolerance, and the same synchronization boundary on both sides.",
            ),
        ],
    },
    8: {
        "hints": [
            "Arrange the claims from weakest to strongest, asking for each what a success at that step still leaves unproven.",
            "Decide whether a missing device is a property of the package, the container runtime or the host, and what you would inspect first.",
            "The program launched and finished. Which claim in the ladder failed when the values came back wrong?",
            "Write the selection rule so that a missing requested backend ends the run with a clear error instead of switching processors.",
            "Ask whether operations queued after a device assertion in the same process can still be trusted.",
            "For each backend name, state what hardware and software it implies, then check that the label matches what actually ran.",
        ],
        "mistake": "A frequent mistake is summarizing a probe as ready because its exit status was zero. In worked example 2 the kernel launched and completed but returned wrong values, which is a correctness failure. Another is letting a GPU evidence run quietly fall back to CPU when no device is visible. Fix both by recording each evidence level separately, failing closed when the requested backend is absent, and restarting the process after a fatal device error.",
        "limit": "The fixture stops at the correctness level on purpose and never touches real hardware. It teaches how to classify failures; it does not diagnose your driver, container runtime exposure or binary architecture, which need checks on the actual host.",
        "self_check": [
            (
                "Why can a successful import not prove a device is usable?",
                "Import only resolves the Python package. Device visibility, allocation, launch, completion and correctness are later claims that each need their own test.",
            ),
            (
                "How do you classify an unsupported architecture binary versus an allocation failure?",
                "The first is a build issue: the compiled code does not target the device. The second is a workload budget issue: the request exceeds the memory available to the job.",
            ),
            (
                "Is MPS or ROCm a way to emulate CUDA?",
                "No. They are separate accelerator backends with their own packages and supported operations, so their results must be labeled by name, not reported as CUDA evidence.",
            ),
        ],
    },
    9: {
        "hints": [
            "Go line by line through the wrapper and the kernel and ask which lines touch Python objects, files or new allocations.",
            "Write the plain Python loop the kernel replaces, element by element, and run it on the supplied input.",
            "Decide where the length comparison belongs so that no launch happens with mismatched buffers.",
            "Ask who should own the output buffer's lifetime: the host wrapper that launches, or each GPU thread.",
            "Compare what the compiler knows about argument types with what an interpreter learns only at run time.",
            "List every layer between your source and the device, from the Python package to the driver, and name what to record for each.",
        ],
        "mistake": "A common mistake is writing a device function as if each GPU thread ran a full Python interpreter, for example opening a file, building a list or calling an unsupported library inside the kernel. Those calls fail to compile or belong to the host. Fix it by splitting the work: the host wrapper validates lengths, reads files, allocates the output and copies data; the kernel computes one index, checks the bound and writes only its own element.",
        "limit": "The CPU oracle doubles `[1, -2, 3]` and accepts an empty input, which defines the expected values. It does not compile anything, so it cannot show which constructs the numba-cuda compiler accepts or how a specialized kernel behaves on a device.",
        "self_check": [
            (
                "Why can the same syntax be legal on the host and illegal in a device function?",
                "Device code is compiled from a restricted typed subset. Arbitrary objects, file access and unsupported library calls exist only in the host interpreter.",
            ),
            (
                "What does a host wrapper do before launching the kernel?",
                "It validates input lengths, allocates the output buffer, converts data to numeric buffers and copies them explicitly, so the kernel only reads fixed buffers and scalars.",
            ),
            (
                "Why does `numba.cuda` in an import line not identify the implementation?",
                "The maintained numba-cuda distribution uses the same namespace, so the spelling alone does not tell you which package and version supplied it. Record the pinned distribution.",
            ),
        ],
    },
    10: {
        "hints": [
            "Divide 17 by the block size and round up, not down, then count the launched lanes.",
            "List the global indices of the last block and mark which ones exceed the valid range.",
            "Ask what the output for an empty input is and whether any launch is needed to produce it.",
            "After handling index i, how far must a thread advance so that no other thread repeats its work?",
            "Compute 17 divided by 4 with floor division and list the indices no block covers.",
            "Decide which tool can observe an out-of-bounds device access that a CPU model never performs.",
        ],
        "mistake": "The most common mistake is sizing the grid with floor division, which silently omits the final partial block, or launching with ceiling division but forgetting the bounds guard so lanes 10 and 11 in worked example 1 touch memory past the buffer. Fix both by using ceiling division for the block count and guarding every load and store with the input length, then test zero, one, block size minus one, block size, block size plus one and a nonmultiple.",
        "limit": "The reference proves the integer mapping visits every valid index exactly once. It cannot prove race freedom, memory safety or correct guards in a real kernel; those need execution under a supported memory checker on a device.",
        "self_check": [
            (
                "How is the global index computed in one-dimensional indexing?",
                "Block index times threads per block plus thread index.",
            ),
            (
                "Why does a grid-stride loop help with large arrays?",
                "A bounded launch can cover any length: each thread processes index i, then advances by the total number of launched threads until it passes the end.",
            ),
            (
                "Which input sizes belong in an indexing test set?",
                "Zero, one, block size minus one, block size, block size plus one and a nonmultiple of the block size, because each exercises a different tail case.",
            ),
        ],
    },
    11: {
        "hints": [
            "Pick a small rectangular tile and list its row indices and column indices as two separate ranges.",
            "Use the row-major formula with the image width, then check the largest offset against the allocation size.",
            "Recompute each border element of `[3,6,9]` with a zero outside the image instead of a repeated edge value.",
            "Update the output in place from left to right and note which neighbor value the second element reads.",
            "With a single column, ask which value clamping supplies for both the left and right neighbors.",
            "Choose an image whose height and width have different tails and test each coordinate's guard separately.",
        ],
        "mistake": "A frequent mistake is writing a stencil's output into its own input. After the first pixel is updated, its neighbor reads the new value instead of the original, so the result depends on thread order. A second mistake is guarding only one coordinate, or using one bound for both, which lets threads in a non-square tail write outside the image. Fix both by reading from an immutable input, writing to a separate output and checking row and column against their own limits.",
        "limit": "The CPU loop reproduces the clamped average `[4, 6, 8]` with visible coordinates. Its run time says nothing about coalescing, tile shape or GPU throughput, and it cannot show races that only appear when threads run concurrently.",
        "self_check": [
            (
                "Why must the boundary policy be stated as part of correctness?",
                "Clamp, zero padding, reflect and valid-only output give different answers at the edges; `[3,6,9]` becomes `[4,6,8]` with clamping but `[3,6,5]` with zero padding.",
            ),
            (
                "What is the flat offset of row 1, column 2 in a row-major 2 by 3 image?",
                "`1 * 3 + 2 = 5`. Swapping row and column would compute a different address that can fall outside the allocation.",
            ),
            (
                "Why does a rectangular launch need two independent guards?",
                "Height and width can each leave a different partial tail, so a thread may be valid in one coordinate and out of range in the other.",
            ),
        ],
    },
    12: {
        "hints": [
            "Ask which value leaves a sum unchanged when it is added to a padded lane.",
            "Zero can be a real minimum. Pick a value no real input can reach, or carry a separate valid flag.",
            "Count the lanes in the block, not the input elements, and ask which must arrive at the barrier.",
            "Move the length check from the top of the kernel to the load, so the lane stays active but reads nothing.",
            "Ask whether one block's shared array is visible to a thread in a different block.",
            "Pick a length one larger than the block size and write the expected padded result before running.",
        ],
        "mistake": "The dangerous mistake is letting a tail lane return early before a block barrier. Other lanes then wait at a synchronization point that not every thread reaches, which can hang or produce undefined behavior. Another mistake is padding with a value that is not the identity, such as zero for a minimum. Fix the first by guarding only the data access while every lane still reaches the barrier, and the second by choosing an algorithm-specific identity or a validity flag.",
        "limit": "The model lists four participating lanes and a padded sum of 12. It is a sequential trace, so it cannot detect a missing barrier, a shared-memory race or a hang; those only appear when a real block runs on a device.",
        "self_check": [
            (
                "What makes a barrier a collective obligation?",
                "Every thread of the block that participates must reach a compatible synchronization point. A thread that returns early can leave the others waiting.",
            ),
            (
                "Why is the identity value algorithm-specific?",
                "Zero is neutral for a sum but not for a minimum, and a weighted average also needs a count. The pad must leave that algorithm's answer unchanged.",
            ),
            (
                "Can shared memory pass data between two blocks?",
                "No. It is local to one block. Cross-block cooperation needs a separate stage, such as writing partials to global memory and combining them in another launch.",
            ),
        ],
    },
    13: {
        "hints": [
            "Pair adjacent values of `[1,2,3,4,5]`, add each pair, and carry the unpaired element to the next level.",
            "Check whether your tree still contains the fifth value after the first level.",
            "Add a very large number, its negative and a small residual, then compare a left-to-right sum with `math.fsum`.",
            "Ask what a purely relative tolerance allows when the expected answer is close to zero.",
            "Compare one global counter that every thread updates with per-block partial sums combined later.",
            "Ask whether repeating a run on the same machine says anything about a different GPU or library version.",
        ],
        "mistake": "A common mistake is treating every mismatch between a parallel sum and a sequential loop as harmless rounding. In worked example 2 a faulty tree returns 10 instead of 15 because it drops the fifth value; that is an indexing bug, not rounding noise. The opposite mistake is demanding bitwise identity across orderings. Fix both by testing odd tails explicitly, comparing with a higher-accuracy CPU sum and setting absolute and relative tolerances from the data's scale.",
        "limit": "The reference uses `math.fsum` and a padded tree on tiny inputs. It shows the expected values; it cannot show the error a real float32 tree or atomic accumulator produces, which depends on the device's grouping and arrival order.",
        "self_check": [
            (
                "Why can a tree reduction differ from a left-to-right loop?",
                "Floating-point addition is not associative, and the tree groups additions differently. Both can be valid implementations with different rounding.",
            ),
            (
                "How do you tell rounding noise from a missing element?",
                "Rounding noise is small relative to the data's scale. A missing element changes the sum by that element's value, like 10 instead of 15.",
            ),
            (
                "Why does a sum near zero need an absolute tolerance?",
                "A relative tolerance scales with the expected value, so it shrinks to almost nothing near zero and rejects acceptable rounding.",
            ),
        ],
    },
    14: {
        "hints": [
            "Interleave two threads' read, add and write steps on one counter that starts at 0 and record the final value.",
            "Route all six inputs to the same bin and ask how many updates that bin's counter must absorb.",
            "Line up the two local histograms bin by bin and add the matching counters.",
            "Multiply the number of partial histograms, the bin count and the bytes per counter.",
            "Ask whether atomic float additions arriving in a different order must give the same rounded total.",
            "Decide what must finish, including the merge, before the host may read the counts.",
        ],
        "mistake": "A common mistake is assuming an atomic makes a whole algorithm safe. Atomic addition protects one counter from lost updates, but it does not order other memory, and a non-atomic reader can still see a half-merged histogram. Another mistake is sending every thread to one shared bin, which serializes the updates. Fix contention with per-block private histograms merged later, and read the result only after every update and merge has completed.",
        "limit": "The reference computes bins `[2, 1, 3]` and merges two partial histograms sequentially. It cannot exhibit a lost update, contention or arrival-order rounding, which only occur when real threads race on a device.",
        "self_check": [
            (
                "What exactly does an atomic addition protect?",
                "One supported memory location against lost updates from competing atomic operations. It does not make a multi-location update transactional.",
            ),
            (
                "What does privatization trade away to reduce contention?",
                "Extra storage for per-block or per-warp histograms and an additional merge step.",
            ),
            (
                "Why can floating-point atomic sums vary between runs?",
                "Atomicity prevents lost updates, but the order of additions follows thread arrival, and floating-point rounding depends on that order.",
            ),
        ],
    },
    15: {
        "hints": [
            "List each lane's byte offset, divide by the 32-byte segment size with floor division and count the distinct results.",
            "Add 4 to every offset of the contiguous case and check whether the last lane now lands in a new segment.",
            "Double the spacing between lanes and recount the segments eight four-byte loads touch.",
            "Ask which side of a naive transpose is contiguous, the reads or the writes, and how a shared tile could swap that.",
            "Ask what extra resident warps need from registers and shared memory, and whether they still wait on the same memory traffic.",
            "List what to hold fixed between the two kernels and which real profiler counters would confirm a traffic difference.",
        ],
        "mistake": "A common mistake is crediting a speedup to one mechanism, such as higher occupancy or a padded shared tile, without measuring. Occupancy only helps hide latency; more resident warps can still compete for the same bandwidth or shared capacity. Another mistake is treating this chapter's segment counts as hardware facts. Fix both by holding dtype, shape and output fixed, timing the entire kernel, and checking profiler counters for memory transactions before naming a cause.",
        "limit": "The segment counts 1 and 8 come from a simplified 32-byte model. Real alignment, transaction granularity, caching and bank conflicts depend on the GPU architecture, so the model teaches the access pattern, not measured traffic.",
        "self_check": [
            (
                "Why can neighboring lanes reading neighboring elements be cheaper?",
                "Their bytes fall in few aligned segments, so the hardware serves them with fewer memory transactions than widely strided accesses.",
            ),
            (
                "What problem does a tiled transpose address?",
                "A naive transpose has contiguous reads but strided writes. Staging a tile in shared memory lets both the reads and the writes stay contiguous.",
            ),
            (
                "Why can padding a shared tile have a cost?",
                "Padding may reduce bank conflicts for one layout, but it consumes shared capacity that could otherwise hold more data or more resident blocks.",
            ),
        ],
    },
    16: {
        "hints": [
            "Name the processor that executed the loop and pick the evidence label that matches it.",
            "Let two simulated threads both read count 0 before either writes, and record the final value.",
            "Look up the pinned simulator's documented support before assuming a feature behaves as it would on hardware.",
            "Order the stages from mathematical reference to stress cases, and say what each stage adds that the earlier one could not.",
            "Choose an input length that is not a multiple of the block size but is still small enough to trace by hand.",
            "Write a label that names what ran and what remains pending, without any device name, bandwidth or throughput.",
        ],
        "mistake": "The central mistake is treating a passing simulator run as GPU correctness. A simulator usually serializes threads, so a shared counter incremented without an atomic still reaches 2, while real concurrent threads can lose an update and report 1. Another mistake is quietly rewriting the algorithm when a feature is unsupported by the simulator. Fix both by keeping the validation ladder stages separate, labeling simulator output as such, and recording unsupported features instead of working around them.",
        "limit": "The reference contrasts a serial count of 2 with a possible lost-update count of 1 by construction. It does not run a simulator or a GPU, so it cannot show which races your actual simulator hides or exposes.",
        "self_check": [
            (
                "Name three behaviors a simulator usually does not reproduce.",
                "Warp scheduling, memory transactions and concurrent timing; occupancy and some synchronization defects are also typically absent.",
            ),
            (
                "Why can a serialized run hide a race?",
                "Each update finishes before the next begins, so no two threads read the same old value. Real concurrent threads can interleave and lose a write.",
            ),
            (
                "Where does the simulator belong in the validation ladder?",
                "Early, after the mathematical reference and CPU mapping model, for inspecting small inputs by hand. Real-device output and diagnostic tools come later.",
            ),
        ],
    },
    17: {
        "hints": [
            "Mutate the original list and check which of the two names reports the new value.",
            "Ask what happens to the consumer's view if the producer's owning object is released first.",
            "List every field a consumer needs to locate element (i, j) on the correct device.",
            "Ask whether passing bytes to another library also passes the record of how they were computed.",
            "Ask how the consumer knows the producer's writes have finished before it reads.",
            "Change one view while nothing else writes, then inspect the other, and decide which outcome proves aliasing.",
        ],
        "mistake": "A common mistake is assuming DLPack exchange keeps autograd working across frameworks. The protocol shares storage and metadata, not the originating computation graph, so gradients can silently stop at the boundary. Another is letting the producer's owner be freed while the consumer still holds the buffer. Fix both by running a numerical forward check and a separate gradient check after exchange, and by keeping the producer alive according to the pinned API's ownership rules.",
        "limit": "The reference uses Python lists to show aliasing, where the alias changes to 9 and the copy stays 1. It does not exchange device buffers, so stream readiness, lifetime rules and autograd behavior across real frameworks remain untested.",
        "self_check": [
            (
                "Why is a zero-copy exchange not the same as two independent values?",
                "Both views share one allocation, so a mutation through one is visible through the other, and the consumer depends on the owner's lifetime.",
            ),
            (
                "Does sharing a physical GPU let two separate workers share a buffer?",
                "No. Zero-copy exchange here happens inside one process. Separate workers or containers cannot simply pass a live pointer.",
            ),
            (
                "What does the modern exchange interface add over legacy capsules?",
                "It can negotiate stream readiness between producer and consumer. Legacy capsules have their own ownership rules and must be followed exactly.",
            ),
        ],
    },
    18: {
        "hints": [
            "Draw one node per operation and an edge only where one operation reads what another wrote.",
            "Find the read of a buffer whose producer has no recorded event that the consumer waits on.",
            "Ask which call stops Python and which only tells the device queue to wait.",
            "Follow buffer X after its last consumer is enqueued and ask when the allocator may hand it out again.",
            "Use two streams and inputs with known outputs, so a missing wait shows up as a wrong value.",
            "Ask which dependency a device-wide synchronization adds that your intended graph never declared.",
        ],
        "mistake": "A frequent mistake is assuming that operations on two streams run in the order they were written in Python. Without an event and a wait, a consumer on stream B may read buffer X before the producer on stream A finishes. Another mistake is adding a device-wide synchronization to make a bug vanish, which hides the missing edge and removes overlap. Fix both by drawing the dependency graph, recording an event after each producer and making each consumer wait on it.",
        "limit": "The reference accepts a valid dependency order and rejects a premature download in a sequential model. It cannot reproduce real stream timing, library current-stream conventions or allocator reuse while a kernel is still running.",
        "self_check": [
            (
                "What does an event record?",
                "A point in one stream. Another stream can wait on it, adding a dependency without necessarily blocking the host.",
            ),
            (
                "Why is a correct pointer not enough for interop?",
                "The write may still be in flight, or the storage may be recycled before the consumer finishes. Readiness and lifetime are separate from the address.",
            ),
            (
                "Why test with a non-default stream?",
                "Default-stream execution can serialize work and hide missing dependencies that appear once operations run on independent streams.",
            ),
        ],
    },
    19: {
        "hints": [
            "For each kernel parameter, write the element type behind the pointer and the exact width of each scalar.",
            "Multiply the element count by the itemsize of the declared dtype and compare it with the allocated bytes.",
            "Ask what each stage needs: compiling only needs source and target, while launching needs a compatible device.",
            "List the resources in creation order, then ask what must complete before each one is released.",
            "Pass a float64 buffer where float32 is expected and write down how the kernel would read the first element.",
            "List every independently versioned component between your source and the device, and the target architecture.",
        ],
        "mistake": "The chapter's key mistake is passing arguments that do not match the compiled signature, such as a float64 allocation where the kernel expects float32, or a pointer where a 32-bit length belongs. The launch may not fail; it reads wrong bytes. Another mistake is checking only the launch status, which misses errors reported at completion. Fix both by validating dtype, size and argument layout in a small host wrapper, and by checking errors at submission and again after synchronization.",
        "limit": "The reference rejects storage too small for five float64 values in a CPU contract check. It does not load a driver, compile a module or launch anything, so binding behavior and release-specific API details need a prepared CUDA Python environment.",
        "self_check": [
            (
                "Why must compile success be recorded separately from launch success?",
                "Code can compile for an architecture that the current device does not have, so it builds cleanly and still fails or misbehaves at launch.",
            ),
            (
                "What does a launch need besides the compiled function?",
                "Arguments in the correct binary layout, grid and block geometry and a stream, all matched to the function signature.",
            ),
            (
                "Why use release-matched examples for CUDA Python?",
                "Its components are versioned independently, so code copied from a moving development branch may use APIs your installed release does not have.",
            ),
        ],
    },
    20: {
        "hints": [
            "Apply `2*x + 1` to each of `-1`, `0` and `3`.",
            "Divide 257 by 128 and round up, then count how many lanes the last block holds beyond the data.",
            "Ask what name the compiled module exports for the entry point and what `extern C` changes about it.",
            "Decide whether the kernel will index with real strides or reject any input that is not contiguous.",
            "Run the same kernel once before timing, then time repeated warm calls separately.",
            "Compute the same affine result with a CuPy expression and compare outputs under one tolerance.",
        ],
        "mistake": "A common mistake is expecting a raw kernel to behave like a CuPy expression. The CUDA C++ inside the string has no broadcasting, dtype promotion or stride support; a float64 or sliced input is simply read as raw bytes. Another mistake is timing the first call, which includes compilation. Fix both by validating dtype, contiguity and length in Python before launching, guarding the tail in the kernel, and warming up before collecting steady-state samples.",
        "limit": "The reference checks the affine values `[-1, 1, 7]` and the three-block launch count with plain Python. It never compiles CUDA C++, so symbol lookup, compiler flags and warm execution time remain unverified.",
        "self_check": [
            (
                "Which side controls what in a raw kernel?",
                "Python controls allocation, validation and launch geometry. CUDA C++ in the string controls each thread's arithmetic and its tail guard.",
            ),
            (
                "Why is a high-level CuPy expression still a strong baseline?",
                "It already handles dtype, broadcasting and strides with tested code. A raw kernel must match it and show a measured benefit, such as fusing operations.",
            ),
            (
                "What happens on the first invocation of a raw kernel?",
                "The source may be compiled and cached, so the first call includes compilation latency that later warm calls do not.",
            ),
        ],
    },
    21: {
        "hints": [
            "Add every stage a request pays for, not only the kernel time, for both the library and the custom path.",
            "Write the shapes, dtypes, tolerance and edge inputs both implementations must accept before comparing them.",
            "Find the moment when the most buffers are alive together and add their sizes.",
            "Ask who requalifies the custom kernel when the GPU architecture or the compiler version changes.",
            "Pick one size where launch overhead dominates and one representative size where useful work dominates.",
            "State the measured benefit the custom path would need before its extra obligations are worth accepting.",
        ],
        "mistake": "A common mistake is comparing only kernel times. In worked example 1 the custom kernel saves 2 ms but adds 3 ms of packing, so complete latency worsens from 10 to 11 ms. Another mistake is presenting a slower teaching kernel as a production improvement. Fix both with a ledger that covers supported dtypes and layouts, temporary memory, numerical behavior, warmup, packaging and fallback, measured at a tiny and a representative size, and keep the library unless the full measurement favors the replacement.",
        "limit": "The reference adds modeled milliseconds, 10 for the library and 11 for the custom path. These are illustrative numbers, not timings; a real decision needs both implementations measured on the target device with the same inputs and checked outputs.",
        "self_check": [
            (
                "When can a custom kernel be justified over a library call?",
                "When it delivers a measured end-to-end benefit, such as fusing launches or handling an unusual layout, that survives correctness checks and outweighs its maintenance cost.",
            ),
            (
                "Why include tiny inputs in the comparison?",
                "At tiny sizes launch overhead and first-call compilation dominate, so a fused or custom kernel that wins on large inputs can lose there.",
            ),
            (
                "What is an educational kernel's honest success claim?",
                "It is learning evidence that the student understands the mechanism. It is not evidence of a production improvement unless measurements show one.",
            ),
        ],
    },
    22: {
        "hints": [
            "Average each column of the two training rows separately.",
            "Subtract the fitted means from each row, then take the dot product with `[2, -1]`.",
            "Ask what a zero standard deviation does to division, and what scale value the schema should declare instead.",
            "For each array, name the library that allocated it, whether each handoff copies or aliases, and who reads it last.",
            "Ask which statistics a validation row may use, and where they must come from.",
            "List what a reviewer needs to accept the run: values, tolerances, timing boundaries and unsupported cases.",
        ],
        "mistake": "The typical capstone mistake is refitting preprocessing on validation data. Recomputing means independently changes the transformation and leaks evaluation information, so scores are no longer comparable. Another mistake is mixing libraries without a reason, which adds copies, ownership questions and waits. Fix both by fitting means and scales once on the training fixture, saving that state and reusing it, keeping the pipeline on one backend where practical, and documenting every allocation owner and handoff.",
        "limit": "The reference fits means `[2, 3]` and scores `[-1, 1]` on a two-row fixture with plain Python. It establishes expected values, not interchange behavior or latency, which require running the pipeline on a supported backend.",
        "self_check": [
            (
                "Why establish a CPU oracle before optimizing the pipeline?",
                "It fixes the expected values, so every later backend or optimization can be checked against the same answers and tolerances.",
            ),
            (
                "How should a constant feature be handled?",
                "Center it to zero and follow a declared scale policy instead of dividing by a zero standard deviation.",
            ),
            (
                "Why report preparation, transfer and computation separately?",
                "Complete latency hides where time goes. Separate stages show whether an optimization helped the computation or merely moved cost elsewhere.",
            ),
        ],
    },
    23: {
        "hints": [
            "Differentiate the mean of `(w*x - y)**2` with respect to `w` and evaluate it at `w = 0` for the batch.",
            "Subtract the learning rate times the gradient from the current weight.",
            "Replace the mean with a sum and ask how the gradient changes with batch size.",
            "Check parameters, inputs, targets and optimizer state, not just the batch you moved.",
            "List each value both frameworks must share: data, initial weight, loss reduction and learning rate.",
            "Ask what must already agree before any timing number means anything.",
        ],
        "mistake": "A common mistake is moving only the inputs to the GPU while parameters, targets or optimizer state stay on the CPU, which raises a device mismatch error or forces hidden copies. Another is comparing frameworks whose loss reductions differ: a sum loss doubles this batch's gradient and changes the update. Fix both by inspecting every tensor's device, failing clearly when an explicitly requested GPU is missing, and keeping data, initialization, reduction and learning rate identical.",
        "limit": "The reference reproduces loss 10, gradient -10 and new weight 1 with CPU arithmetic. It does not run PyTorch or TensorFlow, so actual device placement and autograd results need the framework lanes.",
        "self_check": [
            (
                "Why derive the gradient by hand before trusting autograd?",
                "A hand derivation gives an independent expected value, so a wrong loss, shape or placement shows up as a mismatch instead of a plausible number.",
            ),
            (
                "How do PyTorch and TensorFlow differ in placement idiom?",
                "PyTorch moves tensors and modules to a device explicitly. TensorFlow relies on device scopes, placement rules and tracked variables.",
            ),
            (
                "What does a correct one-step update establish?",
                "Bounded correct behavior for that step. It says nothing about model quality or GPU performance.",
            ),
        ],
    },
    24: {
        "hints": [
            "Add the preparation time and the compute time for one batch.",
            "Once stages overlap, find the slowest stage, because it sets the steady-state interval.",
            "Multiply the payload of one batch by the number of batches waiting in the queue.",
            "Ask what page-locked host memory changes for transfers and what it costs the host.",
            "Ask what a resident-tensor run removes from the pipeline and what it therefore cannot measure.",
            "Change one worker or queue setting per run and keep an upper bound on each.",
        ],
        "mistake": "A common mistake is blaming the model kernel when the GPU is idle because the next batch is not ready. Another is assuming more workers or a deeper prefetch queue always helps; once the bottleneck stops parallelizing, they only add memory and I/O pressure. Fix both by timing complete steps, checking whether preparation or computation is the slowest stage, and varying one bounded worker or queue setting at a time, shutting workers down cleanly afterward.",
        "limit": "The reference computes a 10 ms serial step, a 6 ms ideal steady state and 25165824 queued bytes from given stage times. Real overlap, decoder cost and framework overhead must be measured with the actual pipeline.",
        "self_check": [
            (
                "Why is ideal overlap 6 ms per batch rather than 4 ms?",
                "Preparation takes 6 ms, so even with perfect overlap a new batch cannot arrive faster than the slowest stage.",
            ),
            (
                "What does a prefetch queue cost?",
                "Memory for every queued batch, at least depth times payload, plus decoder state and framework overhead.",
            ),
            (
                "Why bound and clean up workers in a small lesson?",
                "Unbounded workers can leave a large background process tree and exhaust host memory or I/O on a shared machine.",
            ),
        ],
    },
    25: {
        "hints": [
            "Count every array the optimizer keeps per parameter and multiply by the dtype's bytes.",
            "Multiply batch size, saved elements per example and itemsize.",
            "Ask which number includes storage the allocator holds for reuse but no live tensor uses.",
            "Look for a loss or output kept in a list across steps that still carries its graph.",
            "Ask whether changing how memory is reserved changes how many bytes the step needs live.",
            "Fix small upper bounds before running and decide when you will stop without exhausting the device.",
        ],
        "mistake": "A common mistake is applying a universal bytes-per-parameter rule and ignoring activations, workspaces and allocator reserve. Another is keeping every step's loss tensor in a list, which retains autograd graphs and grows memory regardless of batch size. A third is reading reserved memory as live usage. Fix these by building a ledger from the actual arrays and dtypes, storing detached scalar summaries and comparing allocated with reserved memory in small, bounded batch experiments.",
        "limit": "The reference totals 16000 bytes of optimizer state and 4096 activation bytes for an illustrative ledger. Real usage also includes workspaces, allocator reserve and framework internals, so it does not predict an out-of-memory threshold on a device.",
        "self_check": [
            (
                "Why does Adam need more memory than plain SGD?",
                "Adam typically keeps two moment tensors per parameter in addition to the parameters and gradients.",
            ),
            (
                "What does TensorFlow memory growth change?",
                "How memory is reserved over time. It does not make a workload whose live bytes exceed the device fit.",
            ),
            (
                "Does a container memory limit cap GPU memory?",
                "Not generally. Host container limits do not impose a per-process GPU memory quota, so plan bounded experiments explicitly.",
            ),
        ],
    },
    26: {
        "hints": [
            "Multiply the gradient by the scale before the backward pass, then divide by the same scale once.",
            "Ask what a supported scaler does when the scaled gradient becomes infinite or not a number.",
            "Decide which representation the clipping threshold refers to, scaled or original.",
            "Compare how many bits fp16 and bf16 spend on the exponent and on the fraction.",
            "Run the same initialization, batch and loss at full precision as your reference.",
            "Report accuracy and gradient checks separately from memory and speed.",
        ],
        "mistake": "A common mistake is clipping gradients while they are still scaled. In worked example 2 a scaled gradient of 512 clipped at threshold 1 and then unscaled becomes 0.0009765625 instead of the intended 0.5. Another mistake is converting every tensor to half precision and calling it mixed precision, which can break reductions and normalization. Fix both by unscaling before clipping and by letting the framework's autocast or policy choose operation dtypes.",
        "limit": "The reference reproduces 0.5 for the correct order and 0.0009765625 for the wrong one with ordinary Python floats. It does not run autocast, a gradient scaler or a Keras policy, so dtype choices and overflow handling need the pinned framework.",
        "self_check": [
            (
                "Why scale the loss in fp16 training?",
                "Small gradients can underflow to zero in fp16. Scaling keeps them representable, and dividing afterward restores the intended update.",
            ),
            (
                "How do fp16 and bf16 differ although both use 16 bits?",
                "bf16 has more exponent bits and therefore more range, while fp16 has more fraction bits and therefore more precision within its smaller range.",
            ),
            (
                "Can a speedup excuse a numerical failure?",
                "No. Validate finite gradients and held-out behavior first; speed and memory are compared only after quality matches the baseline.",
            ),
        ],
    },
    27: {
        "hints": [
            "Write output index i as a sum over kernel index k of input times kernel, without flipping the kernel.",
            "Count how many positions a length-2 kernel can occupy fully inside a length-4 input.",
            "Charge the conversion once per call that needs it, then ask how many convolutions must reuse the converted data.",
            "Ask which pass training runs after the forward pass and whether it uses the same layout and algorithm.",
            "Ask what the library may do on the first call for a new shape before it settles on an algorithm.",
            "Keep the mathematical operation fixed and change only the batch size between the two cases.",
        ],
        "mistake": "A common mistake is assuming one layout is always faster. NCHW and NHWC store the same axes in different orders, and a conversion is real work unless the consumer can use a view. Another mistake is timing only the forward pass or treating a profiler's kernel name as proof that results match. Fix both by checking outputs and gradients first, then timing complete latency with conversion, algorithm search and workspace included, across at least two shapes.",
        "limit": "The reference computes the valid cross-correlation `[-1, -1, -1]` and a conversion amortization in plain Python. It cannot show which algorithm a library picks, the workspace it needs or real layout costs, which depend on shape, dtype and hardware.",
        "self_check": [
            (
                "How does a deep learning convolution usually differ from the textbook definition?",
                "Frameworks typically compute cross-correlation, which does not flip the kernel. Flipping it changes the sign in worked example 1.",
            ),
            (
                "When does a layout conversion pay off?",
                "When the converted data is reused across enough operations that the per-call savings exceed the one-time conversion cost.",
            ),
            (
                "Why might the fastest algorithm for one shape lose on another?",
                "Library implementations choose algorithms by shape, dtype, workspace and determinism settings, and each choice has different strengths.",
            ),
        ],
    },
    28: {
        "hints": [
            "Take the latest end time and subtract the earliest start time.",
            "List the time ranges where both the CPU and GPU intervals are active.",
            "Look for a host line that turns a device value into a Python number between kernels.",
            "Ask what recording shapes, stacks and memory adds to every event.",
            "Pick the single bottleneck the timeline suggests and change only that.",
            "Rerun without the profiler, synchronize before reading the clock and check the outputs still match.",
        ],
        "mistake": "A frequent mistake is adding up operator durations from a profiler table and calling the result step time. When CPU preparation and GPU kernels overlap, the sum exceeds wall time: 14 ms instead of 10 ms in worked example 1. Another mistake is trusting GPU utilization, since a busy device can be running redundant copies. Fix both by reading the timeline for the critical path, testing one hypothesis at a time and confirming with uninstrumented, synchronized timing.",
        "limit": "The reference computes a 14 ms event sum against a 10 ms interval from given timestamps. It does not capture a trace, so real overlap, synchronization points and profiler overhead must come from a bounded profile on the target system.",
        "self_check": [
            (
                "Why can summed event durations exceed wall time?",
                "Events on the CPU and the GPU can run at the same time, so their durations overlap rather than add.",
            ),
            (
                "Why is high GPU utilization not proof of useful work?",
                "The device can be busy with wasteful copies or redundant kernels; utilization measures activity, not progress toward the result.",
            ),
            (
                "What context must be kept with a saved trace?",
                "The hardware, software versions and workload, because the same code can produce a very different trace elsewhere.",
            ),
        ],
    },
    29: {
        "hints": [
            "List the shape signatures in order and count how many are new when they arrive.",
            "Divide the compile time by the per-call saving, then check the calls just below and above that number.",
            "Ask what happens when compiled code meets a Python side effect or a data-dependent branch it cannot capture.",
            "Write the dimensions and dtypes the compiled path must accept, with explicit bounds.",
            "Ask whether matching forward outputs guarantees that the backward pass matches too.",
            "Ask which step generates code and which step only reuses a recorded execution schedule.",
        ],
        "mistake": "A common mistake is enabling compilation for a short job and reporting a speedup from warm calls only. With a 500 ms compile and a 1 ms saving per call, the first 500 calls are slower in total. Another mistake is feeding many distinct shapes, which triggers new specializations or graph breaks. Fix both by stating an accepted shape set, measuring compile time separately and comparing eager and compiled outputs and gradients across that set.",
        "limit": "The reference counts two specializations and a 500-call break-even with a simplified cache. Real frameworks use guards, graph breaks and recompilation limits of their own, so actual behavior must be observed with the pinned PyTorch or TensorFlow release.",
        "self_check": [
            (
                "How do tracing, compilation and replay differ?",
                "Tracing records operations, compilation transforms that record into code and replay reuses prepared work without rebuilding it.",
            ),
            (
                "Why can changing shapes slow a compiled model?",
                "New shapes can fail the guards and trigger another specialization, paying compile time again.",
            ),
            (
                "Is using a generic graph API proof that CUDA Graph replay happened?",
                "No. CUDA Graph replay has its own restrictions on allocations and stable execution, so it needs separate evidence.",
            ),
        ],
    },
    30: {
        "hints": [
            "List every quantity the next optimizer step reads, not only the weights.",
            "Apply the velocity update with the saved velocity, then update the weight.",
            "Repeat the step with the velocity reset to zero and compare the two new weights.",
            "Ask which batch must come next after restore, and what state lets the sampler produce it.",
            "Ask what is ambiguous about saving in the middle of gradient accumulation.",
            "Decide how close two runs on different hardware must be, and write that tolerance down.",
        ],
        "mistake": "The most common mistake is checkpointing only model weights. Optimizer moments, the learning-rate schedule, the gradient scaler, random states and the sampler position all affect the next step; resetting momentum alone changes the next weight from 0.935 to 0.98 in the reference. Another mistake is expecting byte-identical results on different hardware. Fix both by saving complete state at an update boundary and testing an interrupted run against an uninterrupted one under a declared tolerance.",
        "limit": "The reference compares a restored momentum update with a weights-only restart in plain Python. It does not save or load a PyTorch or TensorFlow checkpoint, so format details and GPU algorithm differences remain untested.",
        "self_check": [
            (
                "Why save at an update boundary?",
                "Partially accumulated gradients are ambiguous to restore unless the format explicitly handles them, while a completed step is consistent.",
            ),
            (
                "Does a checkpoint restore a running GPU context?",
                "No. It restores numerical training state, not a live context, an in-flight stream or allocator contents.",
            ),
            (
                "Why must checkpoint storage outlive the training process?",
                "The process is disposable; a restart can only continue if the saved state survives the process that wrote it.",
            ),
        ],
    },
    31: {
        "hints": [
            "Divide the batch size by the completed batch time in seconds.",
            "Ask how long a single request in that batch waits from arrival to answer.",
            "Name what `eval` changes in module behavior and what `inference_mode` changes in autograd bookkeeping.",
            "Find the layers whose call signature accepts a training flag and decide what to pass.",
            "Time model loading and the first execution separately from warm requests.",
            "Send a shape or dtype the exported signature does not accept and decide what should happen.",
        ],
        "mistake": "A common mistake is treating amortized cost per item as request latency. A batch of 32 that takes 8 ms gives 4000 items per second, but each request still waits the whole 8 ms, not 0.25 ms. Another mistake is disabling gradients and assuming dropout and normalization switched to inference behavior. Fix both by reporting latency, throughput, tail latency, cold start and memory separately, and by setting the framework's evaluation mode explicitly.",
        "limit": "The reference computes 4000 items per second and an 8 ms batch latency from given numbers. It runs no model, so queueing, output materialization and cold start must be measured on the serving path.",
        "self_check": [
            (
                "Why can a larger batch hurt an interactive service?",
                "It raises throughput but makes each request wait for the whole batch, increasing latency.",
            ),
            (
                "Why measure cold start separately?",
                "Loading and compiling the model happen once and would distort warm request timings if hidden in warmup.",
            ),
            (
                "Why include output materialization in latency?",
                "A response for a CPU client is not finished until results are copied back and serialized.",
            ),
        ],
    },
    32: {
        "hints": [
            "Square the error for each prediction and target pair, then average.",
            "Count examples assigned to training and validation and how many each step consumed.",
            "List weights, optimizer state, activations and allocator reserve as separate entries.",
            "Compare an uninterrupted run with one that stops, restores and continues over the same steps.",
            "Choose the change that targets the bottleneck your measurements identified, and only that one.",
            "Write which results came from the CPU and which GPU checks have not run yet.",
        ],
        "mistake": "A common capstone mistake is reporting a faster candidate that quietly evaluates fewer held-out examples or changes the effective batch size. Its metric is no longer comparable with the baseline. Another mistake is merging CPU results and pending GPU evidence into one claim. Fix both by preserving the split and sample accounting, labeling any change in objective or examples as a new experiment, and marking CPU verification and GPU verification as separate fields in the report.",
        "limit": "The reference checks three examples with MSE 2/3 and records GPU verification as false. It shows the report structure, not learning quality, device placement or throughput, which require running a framework lane on a supported device.",
        "self_check": [
            (
                "Why define the held-out split before tuning?",
                "Choosing it afterward lets tuning decisions see evaluation data, so the reported metric becomes optimistic.",
            ),
            (
                "Why keep a failed hypothesis in the report?",
                "It records what evidence rejected the idea and prevents repeating the experiment or overstating what was tried.",
            ),
            (
                "What does a capstone completion marker certify?",
                "Completed learning work. It is not a production certification of the model or its performance.",
            ),
        ],
    },
    33: {
        "hints": [
            "List each tensor input, each scalar parameter and the output, with dtype, shape and device for every one.",
            "Compute `2*x + 1` for each input, then replace any negative result with zero.",
            "Decide whether the output gets new storage or writes into an input, and say so in the schema.",
            "Ask what a raw pointer kernel reads when it receives a transposed view, and where the wrapper should catch that.",
            "Ask whether registering the operator in one framework makes it callable from the other.",
            "List what a reviewer needs to reproduce the build and to trust that the forward pass matches.",
        ],
        "mistake": "A common mistake is treating a working kernel as a finished operator. The kernel may return `[0, 1, 7]` for a contiguous tensor yet silently read wrong values from a transposed view, a different dtype or another device. Fix it by writing the full schema first, including aliasing and mutation, validating dtype, device and layout in the host wrapper before launch, and either implementing strides or packing the input deliberately and reporting the copy cost.",
        "limit": "The reference computes the fused affine-ReLU values `[0, 1, 7]` in Python. It builds no extension, so registration, dispatch, ABI compatibility and non-default stream behavior need a fixed, prepared project with a pinned toolkit and framework.",
        "self_check": [
            (
                "What belongs in an operator contract besides argument types?",
                "Dtype, shape, device, layout, aliasing and mutation, plus how output structure is derived for compilation systems.",
            ),
            (
                "Why can a Python pad accepting a source string not stand in for a registered operator?",
                "Framework registration needs a separately built project with a matching compiler, toolkit and framework ABI.",
            ),
            (
                "Why is backward treated as a separate contract?",
                "A correct forward pass does not imply correct gradients; backward has its own mathematics and tests.",
            ),
        ],
    },
    34: {
        "hints": [
            "Multiply the upstream gradient by `a` wherever the preactivation is positive, and use the boundary rule elsewhere.",
            "The bias is shared by every element, so collect each element's masked upstream contribution into one number.",
            "Perturb `x` by the same small step in both directions and divide the difference by twice the step.",
            "Evaluate the preactivation at the failing point and ask whether the derivative is unique there.",
            "Ask what a first-order check says about differentiating the gradient itself.",
            "Compare forward results first, then compare backward results separately against each framework's native expression.",
        ],
        "mistake": "A common mistake is returning the gradient of a shared parameter with the shape of the input. The bias gradient is a sum of masked upstream values, a scalar here, not an elementwise array. Another mistake is running finite differences at the ReLU kink and treating the mismatch as a bug. Fix both by deriving each vector-Jacobian product by hand, reducing over elements for shared parameters and testing points away from the kink separately from the documented boundary behavior.",
        "limit": "The reference checks a finite-difference derivative near 2 and a bias VJP of 3 in double precision. It does not register a gradient in PyTorch or TensorFlow, so integration, higher-order gradients and unusual layouts remain untested.",
        "self_check": [
            (
                "What does a backward function compute?",
                "A vector-Jacobian product: each output's upstream gradient weighted by how that output depends on each input.",
            ),
            (
                "Why can a central difference disagree at the kink?",
                "It straddles the boundary, where the derivative is not unique, so it need not equal the framework's chosen subgradient.",
            ),
            (
                "What do framework registration checks validate?",
                "Integration properties of the operator, not the correctness of every derivative formula.",
            ),
        ],
    },
    35: {
        "hints": [
            "Weight each microbatch mean by its example count, add the products and divide by the total count.",
            "Average the two microbatch means without weights and compare the result with the full-batch mean gradient.",
            "Count the microbatches in one effective batch and place exactly one optimizer step after the last.",
            "Ask which intermediates backward needs, which were discarded and what must run again to recreate them.",
            "Ask whether a parameter with no gradient still has to be stored on the device.",
            "List everything that must match between the accumulated and full-batch runs: data order, reduction, state and randomness.",
        ],
        "mistake": "The classic mistake is averaging microbatch mean gradients equally when microbatch sizes differ. Means 2 and 8 over sizes 3 and 1 give 5 that way, but the correct effective-batch gradient is 3.5. Another mistake is stepping the optimizer after every microbatch. Fix both by weighting each microbatch by its share of examples and stepping once per effective batch, then confirming equal updates against a full batch before comparing memory or time.",
        "limit": "The reference computes 3.5 against 5 with ordinary arithmetic. It does not run accumulation or activation checkpointing in a framework, so batch-dependent layers, random state and real peak memory must be checked with the pinned PyTorch or TensorFlow lane.",
        "self_check": [
            (
                "When is dividing by the microbatch count correct?",
                "Only when every microbatch has the same number of examples; otherwise weights must follow example counts.",
            ),
            (
                "What does activation checkpointing trade?",
                "Memory for compute: discarded intermediates are recomputed during backward, so arithmetic increases.",
            ),
            (
                "Can accumulation still differ from a full batch when weights are right?",
                "Yes. Batch-dependent layers such as batch normalization, random state and optimizer timing can break the equivalence.",
            ),
        ],
    },
    36: {
        "hints": [
            "Subtract the row's largest score from every score before exponentiating, then normalize.",
            "For each query position, mark which key positions are at or before it.",
            "Multiply batch, heads, sequence length squared and the bytes per element.",
            "Decide what a row with no valid key should return, and make it an explicit rule instead of a NaN.",
            "Compare masked outputs and gradients from the fused path and a plain reference at a stated tolerance.",
            "Ask what runtime evidence would show which backend actually executed.",
        ],
        "mistake": "A common mistake is exponentiating raw scores; values like 1000 overflow and produce infinities or NaNs. Another is masking after softmax, which leaves probability on forbidden positions, or leaving a fully masked row to return NaNs by accident. Fix these by subtracting the row maximum, applying causal and padding masks before normalization and defining behavior for fully masked rows, then comparing a fused path with a reference in both forward and backward.",
        "limit": "The reference computes stable probabilities that sum to 1 and a lower-triangular causal mask in Python. It cannot show which fused kernel a framework selects, since that depends on backend, dtype, head size and mask.",
        "self_check": [
            (
                "Why does attention create a quadratic intermediate?",
                "The full score matrix has one entry per query and key pair, so its size grows with sequence length squared.",
            ),
            (
                "Does subtracting the row maximum change the softmax result?",
                "No. It cancels in the normalization, but it keeps exponentials in range.",
            ),
            (
                "Does calling a scaled-dot-product attention API prove a fused kernel ran?",
                "No. Backend selection depends on dtype, head size and mask, so it must be confirmed from runtime evidence.",
            ),
        ],
    },
    37: {
        "hints": [
            "Multiply the rank by the sum of the matrix's two dimensions.",
            "Add the frozen base matrix to the adapter parameters when estimating storage.",
            "List the tensors the optimizer holds and compare that list with the ones you meant to train.",
            "Ask how attention intermediates and caches grow when sequence length doubles.",
            "Generate synthetic tokens locally and bound the number of steps before training anything.",
            "Set aside validation data before fitting and keep it out of tuning decisions.",
        ],
        "mistake": "A common mistake is assuming a parameter-efficient method uses little memory. A rank 8 adapter on a 1024 by 1024 matrix trains 16,384 parameters, but the 1,048,576 base parameters stay in memory and activations still flow through them. Another mistake is building the optimizer over all parameters, which adds state for frozen weights. Fix both by counting the variables and optimizer state each framework actually holds and comparing methods on the same held-out synthetic task.",
        "limit": "The reference counts 1,048,576 base and 16,384 adapter parameters. It trains no model, so real memory, quality and runtime differences between full and adapter fine-tuning need the framework lanes on a bounded synthetic task.",
        "self_check": [
            (
                "How does a low-rank update reduce trainable parameters?",
                "It factors the update into two thin matrices whose total size is rank times the sum of the dimensions.",
            ),
            (
                "Does freezing the base remove its memory cost?",
                "No. It removes gradients and optimizer updates for it, but the weights still occupy storage and activations can still be needed.",
            ),
            (
                "Why build a tiny transformer with synthetic tokens first?",
                "It allows bounded, offline experiments that check training mechanics without downloading a large model.",
            ),
        ],
    },
    38: {
        "hints": [
            "Multiply 2 for keys and values by layers, batch, sequence, KV heads, head dimension and bytes per element.",
            "Change only the sequence length and recompute.",
            "Look up the model's key-value head count instead of assuming it equals the query head count.",
            "Generate a few tokens with and without the cache and compare logits at every step.",
            "Time prefill over the prompt separately from each decode step.",
            "Ask whether rounding values in Python shows that a packed low-bit kernel ran.",
        ],
        "mistake": "A common mistake is estimating KV cache size with the query head count. Grouped-query models store fewer key-value heads, so the estimate is too large. Another mistake is assuming weight quantization also shrinks the cache. It does not: doubling sequence length doubles the cache even when weights are smaller. Fix both by using the model's actual KV layout, accounting for weights and cache separately and testing cached against uncached logits over bounded steps.",
        "limit": "The reference computes 4096 cache bytes, doubling to 8192, in a dense model. Real caches may use paging, padding or other layouts, and Python rounding does not demonstrate quantized execution, so serving memory must be measured on the deployed stack.",
        "self_check": [
            (
                "How do prefill and decode differ?",
                "Prefill processes the whole input sequence at once, while decode adds one token at a time and reuses cached keys and values.",
            ),
            (
                "Which factors grow the KV cache?",
                "Layers, batch, sequence length, KV head count, head dimension and element width.",
            ),
            (
                "Why state positional-encoding and mask conventions when testing cache equivalence?",
                "Cached and uncached paths must apply the same positions and masks, or matching logits cannot be expected.",
            ),
        ],
    },
    39: {
        "hints": [
            "With equal replica sizes, add the two mean gradients and divide by the replica count.",
            "Weight each replica's mean gradient by its example count, or state a documented equal-batch policy instead.",
            "Write which process owns which device, and how each process learns its rank.",
            "List the examples each rank received and check that every example appears exactly once.",
            "Ask what the healthy ranks do while one rank never joins a collective, and how long they should wait.",
            "Ask whether passing a PyTorch distributed test says anything about a TensorFlow strategy.",
        ],
        "mistake": "A common mistake is averaging replica gradients equally when replicas processed different numbers of examples. Counts 3 and 1 with gradients 2 and 4 give a global example mean of 2.5, not 3. Another is padding the last batch with repeated examples and counting them twice. Fix both by deciding the normalization from the intended data accounting, checking complete sample coverage and comparing against a single-device reference with the same effective batch.",
        "limit": "The reference computes weighted means on the CPU, giving 3 for equal replicas and 2.5 for counts 3 and 1. It launches no processes, so NCCL behavior, GPU peer access and communication cost need a prepared multi-GPU host.",
        "self_check": [
            (
                "What does data parallelism give each replica?",
                "Different examples. Each replica computes gradients, and the gradients are combined before a consistent update.",
            ),
            (
                "Why does adding replicas change the optimization problem?",
                "It changes the effective batch size, which changes gradient noise and can require different learning rates.",
            ),
            (
                "What is the usual PyTorch arrangement for DistributedDataParallel?",
                "One process per device, each with its own rank, joined through a suitable collective backend.",
            ),
        ],
    },
    40: {
        "hints": [
            "Write each constraint as a number with a unit, such as a memory ceiling, a latency target and a quality floor.",
            "Check memory and quality against their limits first and drop any candidate that fails either one before comparing speed.",
            "Point to the part of a measured trace that shows where time goes, then pick the change that targets it.",
            "Ask how you would return to the baseline tomorrow if the new version fails in use.",
            "Send an unsupported shape and a request beyond the resource limit and describe the correct refusal.",
            "Mark each claim as measured live, measured on the CPU only or still a hypothesis.",
        ],
        "mistake": "A common mistake is ranking candidates by kernel speed before checking feasibility. Candidate B in worked example 1 needs 12 GiB on an 8 GiB device, so its timing is irrelevant, and candidate C misses the accuracy threshold. Another mistake is adding a custom kernel or more GPUs because they sound advanced. Fix both by filtering on every stated constraint first and choosing one optimization tied to a measured bottleneck, with the unchanged baseline kept runnable for rollback.",
        "limit": "The reference filters three described candidates and accepts only candidate A. Its memory, latency and accuracy figures are given, not measured, so a real decision needs live evidence for each claim in the acceptance matrix.",
        "self_check": [
            (
                "Why must quality be part of acceptance?",
                "A candidate that meets latency but drops held-out accuracy below the threshold fails the task it was built for.",
            ),
            (
                "Which bottlenecks can an optimization target?",
                "Input preparation, transfer, arithmetic, memory traffic or communication, as shown by measurement.",
            ),
            (
                "What can CPU-only work honestly deliver?",
                "A working model and a decision report, with GPU execution and deployment qualification explicitly left open.",
            ),
        ],
    },
    41: {
        "hints": [
            "Find the latest rank to reach the barrier; every rank waits until it arrives.",
            "For each strategy, ask what is copied to every rank and what is split, whether parameters, operations, layers or optimizer state.",
            "Ask what the remaining ranks do in a collective if one never arrives, and who stops the job.",
            "Ask which update step every rank's saved state must share before the files form one checkpoint.",
            "For each collective, write the bytes exchanged and how often it runs per training step.",
            "List the resources your job created and release only those, leaving checkpoints in place.",
        ],
        "mistake": "A common mistake is restarting one failed rank on its own. The surviving ranks are already waiting inside a collective, so the restarted rank joins a different step and the job hangs or silently diverges. Another mistake is building a checkpoint from rank files saved at different steps. Fix both by using bounded waits, stopping the whole owned job when a rank fails and recovering from a checkpoint taken at one documented global update boundary, with the data position recorded for every rank. Report the slowest rank, not the average, when reasoning about synchronized steps.",
        "limit": "The reference computes a 30 ms barrier time and rejects a mixed-step checkpoint from synthetic numbers. It contacts no hosts, so rendezvous, network bandwidth, straggler causes and recovery behavior need explicitly owned machines and separate qualification for each framework.",
        "self_check": [
            (
                "Why does the slowest rank set a synchronized step's time?",
                "Every rank must reach the barrier or collective before any can continue, so the 30 ms rank sets the time even though the average is 17.3 ms.",
            ),
            (
                "How do tensor and pipeline parallelism differ?",
                "Tensor parallelism splits individual operations across devices; pipeline parallelism assigns different layers to different devices.",
            ),
            (
                "Why can a browser lesson not create a cluster?",
                "Multi-host training needs owned hosts, network access and prepared software, none of which a lesson page provides.",
            ),
        ],
    },
    42: {
        "hints": [
            "Start each tile at a multiple of the tile size and end it before the next start or at the vector length.",
            "In the last tile, compute which lane offsets fall beyond the length and guard both their loads and their stores.",
            "Ask which decisions the programmer writes in a thread-level kernel that a tile compiler makes instead.",
            "Record the DSL release, the compiler and the device architectures that release supports.",
            "Use the same shape, dtype and timing boundary for the library call, the thread reference and the tile kernel.",
            "Ask what a larger tile keeps live per program and what that does to how many programs can run together.",
        ],
        "mistake": "A common mistake is masking the final tile's loads but not its stores, or the reverse, so the two invalid lanes of the third tile read or write past the vector. Another is assuming a larger tile is faster because it improves reuse; it can raise register pressure and lower concurrency. Fix both by applying one mask to every boundary load and store, and by letting measurements on a supported device, not tile size alone, decide the direction of a performance change.",
        "limit": "The reference partitions 10 elements into three tiles, each element covered once. It does not compile Triton or a CUDA tile kernel, so masking in generated code, supported operations and performance need a prepared DSL release on a compatible device.",
        "self_check": [
            (
                "What does a tile-level language change for the programmer?",
                "The programmer describes operations on blocks of data, and the compiler chooses how to distribute them over threads and instructions.",
            ),
            (
                "Why use half-open tile intervals?",
                "Each tile ends where the next begins, so every element is covered exactly once without overlap.",
            ),
            (
                "Does opening this lesson give the Python worker a DSL compiler?",
                "No. It provides a CPU tiling model only; a DSL needs a prepared environment with a supported device.",
            ),
        ],
    },
    43: {
        "hints": [
            "Sort the records by key and keep the original order among records whose keys are equal.",
            "Ask whether the library documents a guaranteed order among duplicates, and what you may assume if it does not.",
            "Drop the contracted inner dimension and keep the two outer dimensions.",
            "Add the workspace the library requests to the inputs and outputs that are live at the same time.",
            "Time creating the plan separately from running it repeatedly.",
            "Read the documentation for the exact installed release rather than the newest online version.",
        ],
        "mistake": "A common mistake is assuming every sort is stable. An unstable sort may legally put record C before A when both have key 2, which breaks code that relies on input order. Another is reusing a plan built for a different shape or dtype, or forgetting the workspace it allocates. Fix both by stating duplicate semantics in the contract, testing duplicates and empty inputs on tiny fixtures and keeping plan creation, workspace and stream association explicit in the ledger.",
        "limit": "The reference traces a stable sort and a `(2, 4)` output shape in Python. It calls no CUDA library, so plan lifetime, workspace size and release-specific behavior require the prepared library package.",
        "self_check": [
            (
                "What does an FFT contract need besides the input array?",
                "The normalization and transform conventions, because libraries differ in where they scale the result.",
            ),
            (
                "Why does a plan have a shape and dtype contract?",
                "It is prepared for specific sizes and types, so reusing it outside that contract can give wrong results or fail.",
            ),
            (
                "Why choose a small release-pinned library family?",
                "Each package carries CUDA compatibility requirements, and pinning keeps behavior and documentation matched.",
            ),
        ],
    },
    44: {
        "hints": [
            "Group rows by category and add only the non-null values under the declared rule.",
            "Compare how a zero and a missing value affect a sum and a count.",
            "Fit the category-to-integer mapping on training data once, and decide where an unseen category goes.",
            "Carry a stable key column through every step, so each output row can be traced to its input.",
            "Add the value bytes, the validity masks and every host-device copy made during conversion.",
            "Ask which one schedules distributed work and which one runs dataframe operations in one process.",
        ],
        "mistake": "A common mistake is turning a missing value into zero or NaN without stating the rule. Zero changes sums and means, and a nullable integer column cannot hold NaN without a type change. Another is fitting category codes separately per partition, so the same category gets different features. Fix both by keeping validity masks, fitting encoders once on training data with an explicit unknown category and checking results against a CPU dataframe before measuring.",
        "limit": "The reference computes sums A 2 and B 5 and a row count of 2 for A in Python. It does not run cuDF or the Spark plugin, so GPU null handling, conversion cost and supported operators need compatible NVIDIA execution.",
        "self_check": [
            (
                "How does cuDF differ from the Spark RAPIDS plugin?",
                "cuDF is a single-process GPU dataframe library; the plugin replaces supported Spark physical operators inside Spark's scheduler.",
            ),
            (
                "Why are counting rows and counting non-null values different?",
                "Category A has two rows but only one non-null value, so the two counts answer different questions.",
            ),
            (
                "Why carry row identity through conversion to tensors?",
                "Without a stable key you cannot join predictions back to inputs or verify that no rows were dropped or reordered.",
            ),
        ],
    },
    45: {
        "hints": [
            "Write the allowed range for every dimension, batch and sequence length included, together with the accepted dtypes.",
            "Check a batch of 9 against the envelope before any execution and decide what message the caller should receive.",
            "Ask what each step proves on its own: that the model exported, that an engine was built and that the engine produced correct outputs.",
            "Ask which data split calibration may read, and why it must not overlap the examples used for evaluation.",
            "List what a cached engine depends on, such as the device, toolkit and runtime versions, and record each one with the cache.",
            "Run the source model and the engine on the same held-out examples with the same metric, not only a shape check.",
        ],
        "mistake": "A common mistake is treating a successful export or engine build as proof that deployment works. Export can succeed while execution fails, and an engine can execute while a lower precision quietly degrades classification quality beyond tolerance. Another mistake is silently truncating a request outside the declared shapes, such as batch 9 when the envelope stops at 8. Fix both by enforcing the shape envelope with a clear error, keeping the source model and build recipe and comparing task quality on held-out data at every precision you ship.",
        "limit": "The reference enforces a declared shape envelope in Python and rejects an out-of-range request. It does not export a model or build a TensorRT engine, so operator support, calibration effects, cache compatibility and timing need a prepared runtime on the target hardware, measured separately for build, cold start and warm inference.",
        "self_check": [
            (
                "Why is one successful shape weak evidence for an engine?",
                "Implementations are chosen per shape, precision and hardware, so other shapes in the contract can fail or behave differently.",
            ),
            (
                "Why keep calibration data separate from evaluation data?",
                "Calibrating on evaluation examples tunes the engine to them and makes reported quality optimistic.",
            ),
            (
                "Can an engine cache be copied to another machine safely?",
                "Not by assumption. It can depend on the hardware, toolkit and runtime versions, so record them and rebuild or requalify when they differ.",
            ),
        ],
    },
    46: {
        "hints": [
            "List every axis a native extension depends on, from the Python version to the driver on the host.",
            "Ask what loads when the package imports and what is only exercised when the first kernel actually runs.",
            "Compare code compiled for specific GPU architectures with intermediate code that a driver can compile later.",
            "Write what a reviewer needs to rebuild the same artifact: input versions, hashes and compiler flags.",
            "Call the operator with a dtype it does not support and describe the error the user should see.",
            "For each environment you claim to support, list the tests that must pass before release.",
        ],
        "mistake": "A common mistake is treating a successful import as proof that the package works on a machine. The host shared library can load while the first kernel fails because the wheel has no compatible device code for that GPU. Another mistake is claiming universal portability from one build; two environments with the same Python version but a different framework ABI or CUDA assumption may need separate builds. Fix both by maintaining a tested compatibility matrix and running import, registration, forward, backward and unsupported-input tests in every declared environment.",
        "limit": "The reference checks that a build ledger is complete. A complete ledger does not show that a driver accepts the binaries or that a GPU runs the kernels; that requires executing real kernel work in each declared environment, which this lesson cannot do on a classroom worker.",
        "self_check": [
            (
                "Why does a wheel filename not guarantee GPU support?",
                "It encodes Python and platform tags, not every device architecture the embedded code was compiled for.",
            ),
            (
                "When can intermediate device code help portability?",
                "It can be compiled by a driver for a newer device, but only within the documented compatibility rules.",
            ),
            (
                "Is publishing a package part of this lesson's workflow?",
                "No. Publishing or using external registries is a separately authorized workflow, kept apart from classroom reading.",
            ),
        ],
    },
    47: {
        "hints": [
            "Divide the operation count by the bytes moved.",
            "Count the intermediate's bytes once for the write you avoid and once more for the read you avoid.",
            "Pick a counter that measures memory traffic or the stall reason your hypothesis predicts.",
            "Change one mechanism and keep the shapes, dtype, inputs and timing method identical.",
            "Use a size that is not a multiple of the tile or block, plus a very small case.",
            "Relate the measured resource use, such as registers or active blocks, to why the timing did not improve.",
        ],
        "mistake": "A common mistake is accepting a traffic model's prediction as a result. Fusion removes an intermediate write and read in the model, but extra register pressure or fewer active blocks can make it slower for some shapes. Another is changing several things at once, so no single cause can be credited. Fix both by changing one mechanism at a time against an unchanged library baseline, checking numerical results and boundary shapes after every change and keeping failed optimizations in the record with the evidence that rejected them.",
        "limit": "The reference computes an intensity of 0.5 operations per byte and 8192 removable bytes from a simplified model. Whether the kernel is really bandwidth or compute limited, and whether fusion helps, requires profiler counters on the target device and shape.",
        "self_check": [
            (
                "What does a low arithmetic intensity suggest?",
                "The operation moves many bytes per arithmetic operation, so reducing memory traffic is a reasonable first hypothesis.",
            ),
            (
                "Why can a fused kernel be slower?",
                "It can use more registers or shared memory per block, reducing active blocks and the device's ability to hide latency.",
            ),
            (
                "Why include a failed optimization in the case study?",
                "Explaining why a hypothesis failed shows the reasoning and measurements behind the final choice.",
            ),
        ],
    },
    48: {
        "hints": [
            "Find the median of each sample list, then divide the baseline median by the candidate median.",
            "Keep every timing sample with the conditions under which it was taken, not just the best one.",
            "Compare outputs against the declared tolerance before looking at any speed number.",
            "Report the first run, with setup and compilation, separately from the warm runs.",
            "Name the exact hardware and software you tested on and nothing beyond it.",
            "List what another person needs to rerun the comparison and get the same answer.",
        ],
        "mistake": "A common mistake is reporting only the best timing and a single speedup number. That hides variation and conditions, and three samples cannot support a confident ratio. Another is quoting a speedup when the candidate's output differs beyond tolerance, which measures different behavior. Fix both by checking correctness first, keeping raw bounded samples with the source revision, hardware, driver, versions and load conditions, and stating the 1.25 median ratio with its limited confidence.",
        "limit": "The reference computes a median ratio of 1.25 from synthetic samples. It is explicitly not a GPU benchmark; a real review needs repeated synchronized measurements on named hardware and software, and its results apply only to that device.",
        "self_check": [
            (
                "Why prefer the median of raw samples over the best time?",
                "The median resists outliers and the raw samples show variation, while the best time hides how often it occurs.",
            ),
            (
                "Which costs should be reported separately?",
                "Kernel-only time, transfers, preprocessing, compilation and end-to-end latency.",
            ),
            (
                "Does one device's result rank architectures in general?",
                "No. It is a result from that device with that software and workload, not a universal ranking.",
            ),
        ],
    },
    49: {
        "hints": [
            "For each piece of work, ask whether it runs in one dataframe process, in Spark SQL operators, in a UDF process or in a training job.",
            "Ask which product is the dataframe library and which one hooks into Spark planning and execution.",
            "Ask whether Spark's optimizer can see inside the function body, or only its inputs and outputs.",
            "Use the same schema, null policy and aggregation in both languages and compare the output rows.",
            "List the checks you can complete today on a CPU worker, such as semantic references and plan reading.",
            "Write the evidence a GPU run must produce: runtime, executed operator plan, metrics and equal results.",
        ],
        "mistake": "A common mistake is expecting the Spark plugin to accelerate everything in an application. A Python loop inside an ordinary UDF stays opaque to the optimizer and runs as host code even with the plugin enabled. Another is treating equal outputs from Scala and PySpark as proof that GPU operators ran. Fix both by keeping work in declarative DataFrame operations where possible and reading the executed physical plan on a prepared GPU environment before claiming acceleration.",
        "limit": "The reference computes grouped totals A 6 and B 14 with no GPU execution claimed. It cannot show which operators the plugin replaces; that requires an executed plan from a compatible Spark and GPU environment.",
        "self_check": [
            (
                "What was the plugin formerly called?",
                "The RAPIDS Accelerator for Apache Spark; it is now the NVIDIA cuDF plugin for Apache Spark.",
            ),
            (
                "Why can Scala and PySpark reach the same physical plan?",
                "Both build DataFrame expressions that the same Catalyst optimizer plans and executes.",
            ),
            (
                "Do GPU-aware UDF and machine learning integrations come with the plugin?",
                "They have their own package and execution contracts and must be set up and verified separately.",
            ),
        ],
    },
    50: {
        "hints": [
            "Name every component that must line up, from the Spark line and Scala version to the GPU and operating system.",
            "Read the Scala suffix on the jar and compare it with the Scala binary version of the Spark distribution.",
            "Ask which one ships inside a package and which one must already be installed on the host.",
            "Record each artifact's release version, checksum and the primary source you took it from.",
            "Keep an ordinary CPU Spark environment and a query whose expected result is known.",
            "Write the steps a selected host must pass: import, startup, a bounded query and the expected result.",
        ],
        "mistake": "A common mistake is choosing jars by name, for example a plugin built for Scala 2.12 on a Scala 2.13 distribution, which can fail with a NoSuchMethodError before any GPU work. Another is copying a development SNAPSHOT from a documentation example, or assuming the CUDA classifier replaces a compatible host driver. Fix these by checking the published support matrix for the exact release, recording versions and checksums and running a bounded smoke query on the selected host with a CPU rollback ready.",
        "limit": "The reference applies an illustrative predicate that rejects a Scala or host-architecture mismatch. It is not a full compatibility probe; driver, GPU architecture, vendor Spark patches and native library initialization can only be confirmed by a smoke run on the selected host.",
        "self_check": [
            (
                "Why is a nominal Spark version not enough to establish compatibility?",
                "Distributions can carry vendor patches, so binary compatibility must be checked against the exact distribution and release.",
            ),
            (
                "What does the CUDA classifier on a plugin jar select?",
                "The native library packaging. It does not supply or replace a compatible NVIDIA driver on the host.",
            ),
            (
                "Are a local ARM Mac image and an NVIDIA Linux host the same concern?",
                "No. Image architecture and the GPU host's architecture are separate axes in the matrix.",
            ),
        ],
    },
    51: {
        "hints": [
            "Write the query's intent as logical nodes, then write how each node would actually be executed.",
            "Find the operator names the selected plugin release uses for GPU nodes, instead of guessing from the query text.",
            "Mark every place where data moves between a CPU node and a GPU node.",
            "Ask which call in your code actually makes Spark run the job.",
            "Compare the plan printed before the action with the one shown in the completed SQL execution view.",
            "Choose metrics that together describe rows, batches, time, spill and device activity for each operator.",
        ],
        "mistake": "A common mistake is reading a plan printed before any action as evidence of what ran. Adaptive Query Execution can change the physical plan at run time, and nothing executes until an action such as count. Another is labeling a whole job GPU accelerated because one GPU node appears. Fix both by inspecting the final executed plan and its metrics after an action, operator by operator, and counting the transitions where data changes representation.",
        "limit": "The reference counts two GPU nodes and two backend transitions in a synthetic plan. It does not run Spark, so actual plugin operator names, AQE changes and metrics require an executed query on a prepared GPU environment.",
        "self_check": [
            (
                "What is the difference between explain output and the executed SQL view?",
                "Explain shows what Spark planned; the executed view and its metrics show what happened for a completed action.",
            ),
            (
                "Can a CPU node coexist with useful GPU computation?",
                "Yes. Metadata or coordination nodes can stay on the CPU while the heavy operators run on the GPU.",
            ),
            (
                "Why count transitions in a mixed plan?",
                "Each transition may copy data or change its representation, and that cost belongs in the measurement.",
            ),
        ],
    },
    52: {
        "hints": [
            "Ask whether the plugin environment is valid and chose the CPU for one operator, or whether no usable GPU exists at all.",
            "Check the operator, the expression and the data type against the release's supported-operator documentation.",
            "Count each crossing between columnar GPU execution and row-based CPU execution, both into and out of the UDF.",
            "Find a built-in expression with the same meaning as the UDF, and prove equivalence before replacing it.",
            "Include nulls, overflow, strings and timestamps in the parity tests for any rewrite.",
            "For each operator that stayed on the CPU, record the diagnostic reason and the transitions it caused.",
        ],
        "mistake": "A common mistake is assuming CPU fallback means a machine without a GPU can run with the plugin enabled. Fallback is a per-operator choice inside a valid plugin environment; a machine with no GPU should use the plain CPU baseline. Another mistake is forcing an incompatible operator onto the GPU to raise coverage. Fix both by keeping the two cases separate, preserving semantics with parity tests and measuring the whole query, transitions included.",
        "limit": "The reference models a CPU-only baseline and per-operator fallback as separate cases. It cannot produce NOT_ON_GPU diagnostics or measure conversion costs, which need the selected plugin release on a GPU host.",
        "self_check": [
            (
                "What does support depend on in the plugin?",
                "The operator, the expression, the data type and the configuration, so one aggregate can be supported for some types and not others.",
            ),
            (
                "Why can a mixed plan be slower than expected?",
                "It may pay row to columnar conversions and device transfers repeatedly around unsupported parts.",
            ),
            (
                "How should CPU-only learners run Spark in this course?",
                "Ordinary Spark with the GPU plugin disabled or absent.",
            ),
        ],
    },
    53: {
        "hints": [
            "Count all rows for one answer and only the rows where the value is present for the other.",
            "Look up what Spark SQL returns for a sum over values that are all null, then compare it with a Python sum starting at zero.",
            "Represent both operands as decimals with the declared scale and compare the result exactly.",
            "Set the session timezone explicitly and include values near a day or offset boundary.",
            "Base the tolerance on the dtype, the reduction algorithm and the magnitude of the values.",
            "Sort both result sets by stable keys before comparing, and keep duplicate rows instead of removing them.",
        ],
        "mistake": "A common mistake is comparing CPU and GPU results as if every column were a float array. Decimal and integer results usually need exact equality, an all-null sum is null rather than zero, and timestamps depend on the session timezone. Another is widening a tolerance until a semantic mismatch passes. Fix both by using explicit schemas, deterministic ordering and exact comparison for decimals, reserving justified tolerances for floating aggregates whose reduction order can change.",
        "limit": "The reference computes row count 3, non-null count 2, sum 7 and the exact decimal 3.30 in Python. It does not run Spark SQL, so null, overflow and timezone behavior must be confirmed against the selected Spark mode and plugin release.",
        "self_check": [
            (
                "How do COUNT(*) and COUNT(value) differ?",
                "COUNT(*) counts rows, including those whose value is null; COUNT(value) counts only non-null values.",
            ),
            (
                "Why can a binary float not stand in for a decimal test?",
                "Values like 1.10 have no exact binary representation, so the float result cannot verify the decimal's precision and scale.",
            ),
            (
                "Why name the timezone in a timestamp test?",
                "The same stored instant can format or compare differently under different session timezones.",
            ),
        ],
    },
    54: {
        "hints": [
            "Multiply the number of rows by the width of one value.",
            "Divide the row count by eight and round up.",
            "Ask how a reader finds where the second string starts and ends in one shared character buffer.",
            "Read the physical plan and mark each row to columnar and columnar to row node.",
            "Add values, masks, offsets and any temporary decoded copies made for the transfer.",
            "Convert a batch with nulls and strings and back, then compare schema, row identity, nulls and values.",
        ],
        "mistake": "A common mistake is sizing batches by row count alone. A thousand float64 values occupy 8000 payload bytes, but a thousand strings can occupy far more depending on their lengths. Another is treating null as zero during conversion, which erases information. Fix both by planning batches by bytes, including masks, offsets and temporary copies, and by testing that every conversion preserves schema, nulls and row identity.",
        "limit": "The reference counts 8000 payload bytes, a 2-byte mask for nine rows and 7 string bytes. It moves no data, so Arrow conversion, device transfers and spill behavior need measurement in the actual pipeline.",
        "self_check": [
            (
                "Does using Arrow guarantee zero-copy GPU residency?",
                "No. Arrow defines interoperable columnar formats; residency and copying depend on each process and device boundary.",
            ),
            (
                "Why can a larger batch raise spill risk?",
                "It improves amortization but increases peak memory, which can push data to a slower tier.",
            ),
            (
                "What structures does a nullable string column need?",
                "Offsets to mark string boundaries, character storage and a validity mask for nulls.",
            ),
        ],
    },
    55: {
        "hints": [
            "Divide one assigned GPU by the per-task resource amount.",
            "Find every limit that applies, such as CPU task slots, resource shares and plugin admission, and take the smallest.",
            "Ask whether the scheduler reserves any memory on the device when it admits a task with a fractional amount.",
            "Inspect which GPU addresses discovery reported and which ones each executor was assigned.",
            "Change one concurrency setting and keep the query, partitions and data fixed.",
            "Describe what happens to live batches and memory when too many tasks use the GPU at once.",
        ],
        "mistake": "A common mistake is reading a fractional GPU request such as 0.25 as a quarter of the device's memory. It is only a scheduling share; four admitted tasks still compete for the same VRAM. Another is assuming Spark's runnable task slots decide GPU concurrency, when the plugin's admission limit can be lower. Fix both by recording every resource control, verifying assigned device addresses and changing one concurrency setting at a time while observing throughput and memory.",
        "limit": "The reference computes four scheduling shares with a two-task admission bound. It does not run discovery or tasks, so actual assignment, memory pressure and throughput require a prepared GPU Spark cluster.",
        "self_check": [
            (
                "Which controls limit GPU task concurrency?",
                "CPU task slots, fractional GPU resource requests and the plugin's GPU admission concurrency, which together set the effective bound.",
            ),
            (
                "Why can raising concurrency fail without any syntax error?",
                "More active tasks multiply live batches, so memory pressure can cause spills or failures at run time.",
            ),
            (
                "What should resource discovery evidence show?",
                "The GPU addresses that were discovered and the address assigned to each executor.",
            ),
        ],
    },
    56: {
        "hints": [
            "Add each active task's live set and the shared workspace once.",
            "Recompute the total with one task fewer and compare it with the budget.",
            "Ask whether shrinking the JVM heap frees anything on the GPU.",
            "Choose an explicit disposable path for spill files and set a capacity limit for it.",
            "Fix row and byte bounds for a batch before launching the run.",
            "Ask what a completed but spilling run proves and what it still needs reported.",
        ],
        "mistake": "A common mistake is tuning the JVM heap to fix GPU memory pressure. They are separate allocators, so reducing heap creates no VRAM. Another mistake is raising GPU task concurrency because each task fits alone; three tasks fit a modeled 8 GiB budget, but four need 9 GiB. A third is treating spill as failure or as free capacity. Fix these by budgeting device, pinned host, pageable host and spill disk separately and lowering concurrency when live demand exceeds the budget.",
        "limit": "The reference fits one to three tasks into an illustrative 8 GiB budget and rejects four. Real live sets, workspaces and spill thresholds depend on the query and the plugin release, so they must be observed on a prepared host with bounded data.",
        "self_check": [
            (
                "What does a spill do?",
                "It moves data to a slower tier so the query can progress under memory pressure, adding serialization and I/O cost.",
            ),
            (
                "Why is comparing only kernel time misleading when spills occur?",
                "Spills add end-to-end time outside the kernels, so the slowdown is invisible in kernel measurements.",
            ),
            (
                "Why must memory experiments use bounded data?",
                "Deliberately filling a shared device or disk can disrupt other users, so limits are set before running.",
            ),
        ],
    },
    57: {
        "hints": [
            "Multiply how many times a key appears on the left by how many times it appears on the right.",
            "Decide what each join type does with a key that appears on only one side.",
            "Compare the largest partition with the typical ones, not only the average size.",
            "Ask which strategy copies one side to every worker and which redistributes records by key.",
            "Check that a salted or repartitioned version returns the same duplicates and null-key rows as the CPU oracle.",
            "Run an action and read the final adaptive plan to see which join strategy actually ran.",
        ],
        "mistake": "A common mistake is expecting a join's output to be at most as large as its inputs. Duplicate keys multiply: two A rows on each side produce four matches. Another is broadcasting a side that looks small only because statistics are stale, or salting skewed keys in a way that changes multiplicity or outer-join rows. Fix both by checking cardinality against a CPU oracle with duplicate and missing keys, and by inspecting partition sizes and the final executed plan.",
        "limit": "The reference counts four A matches from two-by-two duplicate keys. It does not execute Spark joins, so broadcast choices, skew handling and memory pressure need the final adaptive plan from a real run.",
        "self_check": [
            (
                "Can GPU acceleration reduce a join's output rows?",
                "No. The semantic expansion from duplicate keys is the same on any backend.",
            ),
            (
                "Why does skew lengthen a stage?",
                "One large partition creates a long task, and the stage cannot finish until that task does.",
            ),
            (
                "Why keep a simple CPU oracle for joins?",
                "It catches fast but incorrect rewrites that drop duplicates or mishandle missing and null keys.",
            ),
        ],
    },
    58: {
        "hints": [
            "Divide the payload size by the effective bandwidth, keeping the units consistent.",
            "Time the complete stage, then separate the time spent in local operators from the time spent moving data.",
            "Ask whether partial results can be combined before the shuffle without changing the aggregate's meaning.",
            "List the hardware, topology, libraries and real traffic test an accelerated transport needs before you trust it.",
            "Ask which shuffle settings can change in a running session and which need fresh executors.",
            "Use identical partitioned fixtures for both shuffle paths and record bytes, spills and the output rows.",
        ],
        "mistake": "A common mistake is optimizing a local kernel when the stage is limited by moving data. Moving 10 GiB over an effective 1 GiB/s path takes at least 10 seconds, so saving 50 ms in a kernel changes almost nothing. Another is assuming RDMA or GPUDirect works because a library is installed. Fix both by measuring the complete stage, establishing an ordinary shuffle baseline and qualifying any accelerated transport on real hardware and topology before comparing.",
        "limit": "The reference computes a ten-second payload lower bound and a 50 ms kernel saving. It sends no network traffic, so real bandwidth, retries, spill and transport compatibility must be measured on owned hosts with a bounded fixture.",
        "self_check": [
            (
                "What costs make up a shuffle?",
                "Serialization or columnar handling, buffering, transport, disk and downstream processing.",
            ),
            (
                "When is pre-aggregation a valid rewrite?",
                "When combining partial results first gives the same final answer, which fails for nonassociative or stateful operations.",
            ),
            (
                "Why should a lesson pad not change cluster settings?",
                "Network services and cluster-wide settings affect other users and require owned, authorized environments.",
            ),
        ],
    },
    59: {
        "hints": [
            "Divide the row count by the partition count for both settings.",
            "Ask what an average hides when one partition is much larger than the rest, and which numbers reveal it.",
            "Trigger an action first, then read the plan the completed query actually used.",
            "Decide whether both runs start with cold caches or warm caches, and record which.",
            "Use a tiny fixture to check correctness and a separate representative dataset to measure speed.",
            "Ask whether a qualification tool's estimate has been confirmed by running the workload on your hardware.",
        ],
        "mistake": "A common mistake is comparing a warm GPU run on cached data with a cold CPU run that downloads its inputs, then reporting the ratio as a speedup. Another is timing tiny correctness fixtures, where startup dominates, or citing a qualification estimate as a measured result. Fix these by using the same input snapshot, query, output materialization, cache state and warmup policy on both backends, reporting cold and warm distributions separately and recording the executed plan and partition sizes for every measured run.",
        "limit": "The reference computes partition averages of 10000 and 100000 and rejects unmatched cache states. It runs no queries, so AQE decisions, per-task memory and actual speedups must be observed with representative data on the target cluster.",
        "self_check": [
            (
                "What can Adaptive Query Execution change at run time?",
                "It can coalesce partitions, switch join strategy and split skewed partitions based on runtime statistics.",
            ),
            (
                "Is there a best partition count for all workloads?",
                "No. Partition count trades task overhead against memory per task and concurrency, which depend on data and device.",
            ),
            (
                "Why keep semantic fixtures separate from performance datasets?",
                "Tiny fixtures are ideal for exact correctness checks but their timings are dominated by startup, not by the work.",
            ),
        ],
    },
    60: {
        "hints": [
            "List the execution surfaces and say for each whether the work runs as Spark operators, a Python process or a local library.",
            "Check that the built-in expression returns null for a null input and keeps the same result type as the UDF.",
            "Ask what Arrow changes about moving data into a pandas UDF and what it leaves unchanged about where the body runs.",
            "Write down which device a GPU-aware UDF uses, how large each batch is and how memory is released afterward.",
            "Ask whether enabling SQL operator acceleration also accelerates a machine learning estimator.",
            "Use the same split, target, metric and preprocessing for both training paths before comparing time.",
        ],
        "mistake": "A common mistake is wrapping simple algebra such as `x*2` in a Python UDF. The expression disappears behind a process boundary and blocks optimization that a built-in expression would allow. Another is calling a GPU library from every partition without a resource contract, which can oversubscribe a device. Fix both by preferring built-in expressions whose null and type semantics match, and by giving GPU-aware UDFs an explicit device share, batch size and cleanup plan.",
        "limit": "The reference produces the null-preserving result `[2, None, 6]` in Python. It does not run pandas UDFs, Spark RAPIDS ML or a GPU library, so their execution surfaces and compatibility must be validated separately.",
        "self_check": [
            (
                "Does Arrow make a pandas UDF's body run on the GPU?",
                "No. Arrow improves interchange; the function body still runs wherever its code runs.",
            ),
            (
                "Why are SQL and ML acceleration validated separately?",
                "They are separate integrations with their own estimator support, semantics and release compatibility.",
            ),
            (
                "Why compare model quality as well as elapsed time?",
                "A faster training path is not acceptable if it changes results on the same split and metric.",
            ),
        ],
    },
    61: {
        "hints": [
            "Draw Kubernetes placing pods on nodes and Spark placing tasks on executors as two separate layers.",
            "Name the exact cluster, namespace, labels and job identity that this lab may touch.",
            "Read the pod events and compare the requested resources with what eligible nodes advertise.",
            "Run a small probe inside an owned executor container to see which devices it can actually access.",
            "Ask which services must stay internal and how you would reach them without exposing them publicly.",
            "List only the resources this lab created and delete those, keeping any logs you were asked to preserve.",
        ],
        "mistake": "A common mistake is treating a running driver pod as proof that GPU Spark works. If executors stay Pending, only submission succeeded. Another is using an ambient kubeconfig or exposing the driver service publicly for convenience. Fix both by working only in a named disposable cluster and namespace, reading events and resource requests for Pending pods, confirming device visibility inside an executor and cleaning up only resources this lab created.",
        "limit": "The reference marks the single illustrative GPU node as eligible and performs no cluster operation. Device plugins, image provenance, scheduling and real device visibility can only be checked in an explicitly owned Kubernetes cluster.",
        "self_check": [
            (
                "Does a pod's GPU resource limit prove the plugin can run?",
                "No. The image, driver and native libraries must also support Spark GPU execution inside the container.",
            ),
            (
                "Can Docker Desktop on a Mac provide an NVIDIA GPU to Kubernetes?",
                "No. It is useful for the CPU classroom but does not create an NVIDIA GPU.",
            ),
            (
                "What advertises GPU resources to the Kubernetes scheduler?",
                "An installed and configured device plugin on the nodes that have GPUs.",
            ),
        ],
    },
    62: {
        "hints": [
            "Find the first error in the logs and decide which layer produced it, before reading any later retries.",
            "Link the application, executor, stage, task and SQL execution identifiers that belong to the same failure.",
            "Count the actual live set and spill categories before changing any memory setting.",
            "Ask what happens to an external write when the same task runs a second time.",
            "List the processes your job started and stop only those, leaving any shared device untouched.",
            "Gather sanitized configuration, plans, logs, metrics and the input identity into one packet.",
        ],
        "mistake": "A common mistake is raising memory settings until an error disappears. A device out-of-memory error with JVM heap below its limit is a GPU live-set problem, so more heap changes nothing, and unbudgeted increases only move pressure between tiers. Another is resetting a shared GPU to recover, which can break unrelated jobs. Fix both by preserving the first relevant error, correlating it with executor, task and SQL identities, budgeting each memory category and stopping only processes the job owns. Treat retries as at-least-once execution, so external writes need idempotency.",
        "limit": "The reference shows two attempts targeting one logical output key. It does not produce real failures, so native library errors, device context poisoning and recovery behavior must be studied from preserved logs of an owned job, never by causing failures on shared hardware.",
        "self_check": [
            (
                "Why preserve the first relevant error?",
                "Later generic task retries can hide the original native failure that explains the incident.",
            ),
            (
                "Why can task retries duplicate side effects?",
                "Spark may run a task again after it already wrote externally, so writes inside a UDF can happen twice.",
            ),
            (
                "Who may reset a device?",
                "An administrator, because a device-wide reset can affect unrelated jobs; the classroom never does it automatically.",
            ),
        ],
    },
    63: {
        "hints": [
            "Multiply each product's quantities by its price, sum per product and check both totals.",
            "Read the input with an explicit schema, join on product, derive revenue and group by product in Scala.",
            "Apply the same operations in PySpark and sort the output so the two results can be compared row by row.",
            "Add a second price for product A and decide whether your contract rejects it or accepts the multiplied rows.",
            "List the plans, metrics and equality checks that must come from actual GPU hardware.",
            "Report the CPU results and the pending GPU limitations in separate sections.",
        ],
        "mistake": "A common capstone mistake is treating a correct result table as proof of acceleration, or a GPU plan as proof of correctness. Each answers a different question. Another is letting a duplicate dimension key silently double revenue. Fix both by checking exact output against a CPU oracle, enforcing or explicitly accepting key uniqueness and keeping query text and inputs unchanged across backends while collecting plans and metrics separately.",
        "limit": "The reference produces sorted revenue `[(A, 60), (B, 60)]` with exact integers. It runs neither Spark implementation, so equivalent Scala and PySpark plans and any GPU evidence must come from executed jobs.",
        "self_check": [
            (
                "Why run both ordinary Spark implementations before any GPU comparison?",
                "Semantic agreement must be established first, so later differences point to the backend rather than the query.",
            ),
            (
                "What does a GPU report need besides timing?",
                "The compatibility matrix, initial and executed plans, unsupported reasons, resource assignment, concurrency and memory observations.",
            ),
            (
                "When may the query text change across backends?",
                "Only as a separately named rewrite that is revalidated against the oracle.",
            ),
        ],
    },
    64: {
        "hints": [
            "Add every cost that changes, including transfers and conversions, not only compute time.",
            "Compare the job's run time with the startup cost of a distributed engine.",
            "Ask how often a user pays startup and how much of the workflow is steady-state work.",
            "Include maintenance, compatibility tracking and resource ownership in the comparison.",
            "Name a data size or workload change that would make you repeat this evaluation.",
            "Recommend the simplest option that meets the constraints and say what evidence is still missing.",
        ],
        "mistake": "A common mistake is treating GPU acceleration as the goal instead of a candidate. In worked example 2 a GPU query saves 30 seconds of compute but adds 40 seconds of transfers and conversions, so the application loses 10 seconds. Another mistake is choosing Spark for tiny data where startup outweighs the work. Fix both by comparing total completion time, resource cost, operational complexity and quality, and by keeping a CPU fallback installation alongside any plugin deployment.",
        "limit": "The reference computes a 10-second end-to-end loss from modeled costs. It measures nothing, so a real recommendation needs timings, costs and quality checks under the actual data size, workload mix and hardware.",
        "self_check": [
            (
                "Name three conditions that can make GPU Spark the wrong choice.",
                "Tiny data, unsupported expressions, expensive transfers, external I/O, severe skew or a memory-constrained device.",
            ),
            (
                "How does a CPU fallback installation differ from plugin operator fallback?",
                "It is a separate ordinary Spark environment, while operator fallback happens inside a running plugin job.",
            ),
            (
                "Why is a no-change outcome a valid result?",
                "A good decision identifies the smallest system that solves the problem, and that can be the current one.",
            ),
        ],
    },
}

# A second, lesson-specific misconception and its correction, distinct from the
# mistake above. Rendered after the mistake paragraph when present.
MISCONCEPTIONS = {
    5: (
        "Setting the same seed in two runs guarantees the same results everywhere.",
        "A seed fixes one generator's starting state in one implementation. Parallel stream partitioning, nondeterministic GPU reductions and library revisions can still change results, so state the scope of reproducibility, such as the same code, environment and backend, and test it at that scope.",
    ),
    14: (
        "Floating-point atomic addition always produces the same total because no update is lost.",
        "Atomics prevent lost updates, but they do not fix the order in which updates arrive. Floating-point addition is not associative, so a float sum accumulated with atomics can differ in its last bits between runs. Integer counts such as histogram bins are exact; for float totals, state a tolerance or use a deterministic reduction order when bitwise repeatability is required.",
    ),
    16: (
        "If the simulator and the CPU reference agree, the kernel only needs a quick hardware run to measure its speed.",
        "Agreement on the early rungs of the validation ladder says nothing about concurrency, memory transactions or compiler output for the target architecture. Real-device output must be checked for correctness, not just timed, and repeated stress runs with varied sizes are needed because a race can pass many times before it fails. Memory and race checking tools belong on the ladder as well.",
    ),
    19: (
        "Once a kernel compiles and the launch call returns without an error, the device has finished the computation correctly.",
        "A kernel launch is asynchronous: the call queues work on a stream and returns before the device runs it. Errors from an invalid memory access or a bad configuration can surface only at a later synchronization or copy, sometimes reported by an unrelated call. Compilation proves only that source was translated, possibly for an architecture this machine lacks. Treat compilation, submission, completion and readback equality as four separate checks, and synchronize before reading results on the host.",
    ),
    21: (
        "Writing a custom kernel is the more serious engineering choice, so a library call is only a stepping stone.",
        "A tuned library usually covers more shapes, dtypes and architectures, and its maintainers carry the testing and packaging burden. A custom kernel is justified only by a specific need such as fusion or an unusual layout, and it then becomes code you must test, package and maintain for every target you support.",
    ),
    22: (
        "If the pipeline's final scores match the CPU oracle, the capstone is complete.",
        "Matching scores show the arithmetic is right for this fixture, but the capstone also asks which library owns each allocation, whether each handoff aliases or copies and when the consumer may read. A pipeline can produce correct scores while copying the data three times, or while reading a buffer before its producer finished on another stream. Report the ownership diagram and separate preparation, transfer and compute timings alongside the equality check.",
    ),
    24: (
        "Feeding the model synthetic tensors that already live on the device shows the speed the real pipeline will reach.",
        "Resident synthetic data removes decoding, transforms and transfers, so it measures only the compute side. Use it to bound what the model could do, then time the real pipeline and compare the two.",
    ),
    25: (
        "Turning on TensorFlow memory growth or clearing an allocator cache will make an oversized workload fit.",
        "Memory growth only changes when TensorFlow reserves device memory, and clearing a cache releases memory that is reserved but unused. Neither shrinks the live set of parameters, gradients, optimizer state and activations. If the live set exceeds the device, reduce the batch size or precision, or change the model.",
    ),
    29: (
        "A compiled function always computes exactly the same values as its eager version.",
        "Compilation can fuse operations and reorder floating-point arithmetic, and Python side effects in traced code may run once at trace time rather than on every call. Compare compiled and eager outputs and gradients with a stated tolerance over the accepted shape set, and keep side effects outside compiled regions.",
    ),
    40: (
        "A capstone decision must recommend some optimization, or the project has failed.",
        "Keeping the reproducible baseline is a valid outcome when no candidate meets every constraint. The acceptance matrix should show which claims have live evidence and which remain hypotheses, so a reviewer can see why the baseline was kept.",
    ),
    41: (
        "Data, tensor and pipeline parallelism are interchangeable ways to add GPUs, so any of them will scale a model across hosts.",
        "Each partitions something different and communicates differently. Data parallelism replicates parameters and reduces gradients every step; tensor parallelism splits operations and exchanges activations inside layers, which needs fast links; pipeline parallelism splits layers and passes activations between stages, leaving idle bubbles unless microbatches fill them. Choose by model size, memory and the network between hosts, and model the communication before scaling out.",
    ),
    42: (
        "A tile language makes memory layout someone else's problem because the compiler chooses the instructions.",
        "The compiler distributes work inside a tile, but the program still decides tile shapes, the order of loads and how data is laid out in memory. A strided or misaligned layout can still waste bandwidth, so compare against a library and the thread-level reference on the same operation.",
    ),
    43: (
        "A library sum or FFT returns the same answer as NumPy as long as the inputs match.",
        "Library conventions differ. A reduction may accumulate in a different dtype or order, so a float32 sum can differ in its last digits, and an integer sum may overflow its type. Some FFT libraries leave both directions unnormalized, so a forward then inverse transform returns values n times larger than the input, while NumPy scales the inverse by 1/n by default. Read each function's dtype, identity and normalization rules and compare on tiny fixtures with stated tolerances.",
    ),
    44: (
        "Using cuDF in a single process is the same as running the Spark plugin, just without a cluster.",
        "cuDF is a dataframe library that executes operations directly in one process. The Spark plugin replaces supported physical operators inside Spark's scheduler, with Spark's planning, partitioning, shuffles and fallback rules. Results, supported operations and performance must be checked separately for each path against the same CPU dataframe oracle.",
    ),
    45: (
        "An engine built and cached on one machine can be copied to any other deployment host.",
        "Engine caches can depend on the GPU model, toolkit and runtime versions used at build time. Treat a cached engine as tied to its build environment: record that environment, rebuild from the preserved source model and recipe for each target, and recheck outputs and quality after every rebuild.",
    ),
    46: (
        "Embedding PTX in a wheel means the operator will run on every current and future GPU.",
        "The driver can compile intermediate PTX at load time only within compatibility rules. The driver must understand that PTX version, and PTX targets a minimum architecture, so it can run on that architecture and newer ones but not on older ones. Just-in-time compilation also adds a first-launch delay that depends on the installed driver. Record which native architectures and PTX targets the build contains, test the first kernel launch on each declared GPU and mark untested devices as untested.",
    ),
    47: (
        "If the arithmetic intensity model says an operation is memory bound, reducing bytes will make it faster.",
        "The model is a hypothesis built from counted operations and bytes; real behavior also depends on caching, coalescing, occupancy and launch overhead, which the model ignores. Use the profiler to check achieved bandwidth and compute utilization for the target shape. If achieved bandwidth is already far below the device's capability, the bottleneck may be latency or the access pattern rather than total bytes, and cutting bytes alone may not help.",
    ),
    48: (
        "Results from one GPU let a reviewer predict the speedup on another GPU.",
        "Bandwidth, cache sizes, clocks, driver and library versions all differ between devices. A review should state which device produced each number and treat other devices as untested until they are measured.",
    ),
    50: (
        "If the plugin jar loads and the Spark session starts, the installation is compatible.",
        "Session startup on the driver proves little about executors. Native libraries and the device are initialized on each executor, where a driver, CUDA variant or CPU architecture mismatch can still fail. Count the installation as compatible only after a bounded smoke query runs operators on the GPU and the executed plan confirms it.",
    ),
    53: (
        "Results from CPU Spark and the GPU plugin can always be compared exactly.",
        "The plugin documents operations whose GPU results can differ from CPU Spark, such as floating aggregations whose order varies, and some of them are disabled by default for that reason. Read the compatibility notes for each operation in the query, compare decimals and integers exactly and compare floats with a justified tolerance.",
    ),
    54: (
        "Arrow conversion between Spark and Python is free because both sides are columnar.",
        "Spark's internal CPU rows and the plugin's GPU columns are not Arrow buffers by default, so each boundary can serialize, copy or rebuild validity masks and offsets. A pandas UDF, for example, converts batches to Arrow, sends them to a Python worker and converts the result back. Measure that conversion separately and count every row to columnar transition in the plan.",
    ),
    56: (
        "Pinned host memory is an unlimited fast staging area, so a larger pinned pool is always better.",
        "Pinned memory is page-locked host memory that the operating system cannot swap out, so a large pool takes RAM away from the JVM, Python workers and other processes on the host. It speeds transfers and spills to host memory, but it is a fixed budget like device memory. Size it in the same ledger as the heap, the device pool and spill disk, and change it in bounded steps.",
    ),
    58: (
        "Adding more shuffle partitions always spreads the network load and speeds up the stage.",
        "More partitions create more, smaller blocks. Each block needs metadata, requests and buffer space, and many tiny blocks can be slower to fetch and process than fewer large ones. The bytes crossing the network stay the same unless the query changes. Measure total shuffle bytes, block counts and fetch wait time, and change the partition count in bounded steps alongside the semantic checks.",
    ),
    59: (
        "The configured partition count is the number of partitions the stage runs with.",
        "With AQE enabled, Spark can coalesce small shuffle partitions after a stage completes and split skewed ones in joins, so the executed partition count can differ from the configured value. Per-task memory and concurrency follow the executed partitions. Read partition counts and sizes from the completed query's stage metrics and report them with the timing, and confirm that CPU and GPU runs used comparable plans.",
    ),
    61: (
        "If Spark requests a GPU for each executor, Kubernetes will find a GPU node automatically.",
        "The scheduler can place the pod only on a node whose device plugin advertises enough GPUs and whose taints, selectors and other resource limits allow it. Spark must also be given a discovery script or an equivalent so the executor reports the device address it received. Check node capacity, pod events and the executor's discovered address.",
    ),
    62: (
        "Raising the task retry count makes a failing GPU job more reliable.",
        "Retries help with transient faults such as a lost executor, but a deterministic failure, like a device out-of-memory error on the same skewed partition or a native library mismatch, fails the same way on every attempt. Extra retries then delay the report, repeat external side effects and can bury the first error under many copies. Classify the failure first; retry only transient causes, and fix deterministic ones by changing the data split, memory budget or environment.",
    ),
    64: (
        "If a cluster has GPUs, every Spark job on it should run with the plugin enabled.",
        "The hardware may already be paid for, but enabling the plugin for every job adds compatibility tracking, release upgrades, fallback diagnosis and memory tuning to all of them, and jobs with tiny data or unsupported operators can get slower. Enable it per workload where measured end-to-end results improve, and keep the remaining jobs on ordinary CPU Spark with a recorded reason.",
    ),
}
