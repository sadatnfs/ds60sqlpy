"""Per-chapter study notes for the CUDA C++ route.

Each entry explains why the chapter's tempting mistake fails and gives three
retrieval questions with short answers. The guide shows the questions and the
explanations file shows the answers.
"""

STUDY_NOTES: dict[int, dict] = {}

STUDY_NOTES[1] = {
    "mistake_fix": "Cores only help the fraction of time spent on independent work. In worked example 1 the 20 seconds of parsing and 4 seconds of transfers stay put, so a tenfold kernel gives only a 3.125 times application speedup. A dependent chain, such as a running balance, cannot use extra cores at all.",
    "self_check": [
        (
            "If parsing in worked example 1 grew to 40 seconds while the transform stayed 80 seconds, what would cap the speedup?",
            "The serial 40 seconds plus transfers. Even an infinitely fast transform leaves at least 44 seconds, so the speedup is under 120/44, about 2.7.",
        ),
        (
            "Why does batching 1,000 tiny requests change the verdict of worked example 2?",
            "The 30 microseconds of submission and transfer overhead is paid once for the batch instead of per request, so the arithmetic finally dominates.",
        ),
        (
            "Name one workload in your own projects that has a dependency chain.",
            "Any answer where each step needs the previous result, such as a cumulative balance, a recurrence or a sequence of dependent network calls.",
        ),
    ],
}

STUDY_NOTES[2] = {
    "mistake_fix": "Threads are a programming abstraction that the hardware schedules in warps onto a limited set of SMs over time. Worked example 2 shows a 100-thread block filling four warps, with 28 idle lanes, and 100 blocks reusing the same execution units in waves rather than claiming 10,000 permanent cores.",
    "self_check": [
        (
            "How many warps does a block of 65 threads occupy, and how many lanes sit idle?",
            "Three warps; the last warp holds one valid thread and 31 unused lanes.",
        ),
        (
            "Why is a block not the same thing as an SM?",
            "A block is a cooperating group in your program; the SM is the hardware that hosts one or more resident blocks as resources allow.",
        ),
        (
            "What does the copy engine add to the hardware picture?",
            "It moves data between host and device memory, so transfers can overlap with kernel execution when streams and pinned memory permit.",
        ),
    ],
}

STUDY_NOTES[3] = {
    "mistake_fix": "Packages and compilers are user-space software. Worked example 2 compiles successfully with nvcc yet `cudaGetDeviceCount` finds no device, because hardware access depends on a physical GPU, the host driver and deliberate container exposure. Installing software can never create the device itself.",
    "self_check": [
        (
            "Which layer must exist on the host and cannot be supplied by a container image?",
            "The NVIDIA kernel driver, together with a physical GPU exposed to the container.",
        ),
        (
            "Why can a framework run GPU tensors on a machine where `nvcc` is missing?",
            "Its wheel ships precompiled kernels and compatible user-space libraries, so no developer compiler is needed to execute them.",
        ),
        (
            "What label would you give a successful nvcc build on a machine with no GPU?",
            "Build evidence only: the source compiled for a target, but nothing about runtime behavior was observed.",
        ),
    ],
}

STUDY_NOTES[4] = {
    "mistake_fix": "Divisible sizes hide tail and boundary handling. Worked example 1 partitions 10 elements into blocks of four and leaves a final range of [8,10); an indexing scheme tested only at 8 or 12 never exercises that tail, so out-of-range writes or skipped elements stay invisible.",
    "self_check": [
        (
            "Write the ownership ranges for 13 elements in blocks of five.",
            "[0,5), [5,10) and [10,13); the last block has only three valid elements.",
        ),
        (
            "Why does a stable filter need a scan rather than a reduction?",
            "Each selected element needs its own output position, which is the count of selected elements before it, a prefix result that a single total cannot supply.",
        ),
        (
            "What extra rule does scatter need that map does not?",
            "A conflict policy for destinations written by more than one worker, such as atomic combination or a guarantee of unique targets.",
        ),
    ],
}

STUDY_NOTES[5] = {
    "mistake_fix": "Shape lists logical extents only; strides and ownership decide where elements live. Worked example 2 builds a transposed view with the same six values but strides (1,3), and writes through it change the original. Two arrays with identical shapes can therefore differ in layout and can even share storage.",
    "self_check": [
        (
            "Give the element offset of (1,1) in a 2-by-3 float32 matrix with row stride 4.",
            "1 times 4 plus 1, which is element 5, or byte offset 20.",
        ),
        (
            "Why must a kernel receive strides, not only a shape, for a view?",
            "Without strides it assumes contiguous rows and reads the wrong storage locations for transposed or padded data.",
        ),
        (
            "What risk does aliasing add when one buffer is both input and output?",
            "A write can change a value that another thread still needs to read, so results depend on execution order.",
        ),
    ],
}

STUDY_NOTES[6] = {
    "mistake_fix": "Parallel reductions legitimately change summation order, so bitwise equality is the wrong default; worked example 1 shows order alone turning 1 into 0. A tolerance must still be justified, because worked example 2 shows 4 against a reference of 3 is a real error, not rounding noise.",
    "self_check": [
        (
            "Why does a relative-only tolerance fail at reference zero?",
            "The allowed error becomes zero, so every tiny nonzero rounding result is rejected.",
        ),
        (
            "What does `math.fsum` demonstrate in worked example 1?",
            "That the exact answer is recoverable with compensated summation, so the 0 came from order and rounding, not from wrong inputs.",
        ),
        (
            "How should a test treat NaN in an output?",
            "Check for it explicitly and fail with a message, because NaN compares false with everything and can slip through comparisons.",
        ),
    ],
}

STUDY_NOTES[7] = {
    "mistake_fix": "Peak arithmetic is only one roof. Worked example 2 shows a kernel at intensity 2 FLOP/byte capped at 1 TFLOP/s by bandwidth on a 10 TFLOP/s device, and launch overhead or transfers can dominate an application even when the kernel itself speeds up.",
    "self_check": [
        (
            "What useful byte count does vector addition of n float32 elements move?",
            "12n bytes: two 4-byte reads and one 4-byte write per element.",
        ),
        (
            "At what intensity does the worked example 2 device switch from bandwidth bound to compute bound?",
            "At 20 FLOP/byte, where 500 GB/s times intensity reaches 10 TFLOP/s.",
        ),
        (
            "Why must kernel time and end-to-end time be reported separately?",
            "Transfers, launch overhead and host work can dominate the end-to-end figure even when the kernel is fast.",
        ),
    ],
}

STUDY_NOTES[8] = {
    "mistake_fix": "A screenshot cannot show the input, timing scope, warm-up policy or correctness check behind a number. Worked example 1 contrasts a bare 0.2 ms claim with a record of shape, seed, warm-ups, samples, versions and an error bound; only the second can be checked or reproduced by someone else.",
    "self_check": [
        (
            "Which four observations must stay separate in a receipt?",
            "Hardware access, successful compilation, successful execution and acceptable numerical output.",
        ),
        (
            "Why does a seed alone not reproduce an input?",
            "The generator, dtype, shape and distribution must also be recorded to regenerate the same values.",
        ),
        (
            "Why add a 33-element fixture to the vector-add oracle?",
            "It crosses a 32-thread boundary, exposing tail and bounds assumptions that a three-element case cannot.",
        ),
    ],
}

STUDY_NOTES[9] = {
    "mistake_fix": "A pointer copy duplicates an address, not the storage, so both copies see the same bytes and the same lifetime. Worked example 2 returns a pointer whose vector is already destroyed. Host containers also live in host memory, so device code needs an explicit device allocation and transfer.",
    "self_check": [
        (
            "What two values should travel together whenever a buffer crosses a function boundary?",
            "The pointer and the element count, or an equivalent range.",
        ),
        (
            "What does `const float*` guarantee and what does it not?",
            "It forbids writes through that pointer; it does not prove unique ownership or stop another alias from changing the data.",
        ),
        (
            "Why is `size_t` preferred for element counts?",
            "It is unsigned and wide enough to index any object, avoiding overflow and sign errors for large buffers.",
        ),
    ],
}

STUDY_NOTES[10] = {
    "mistake_fix": "A destructor releases what its owner holds, but an allowed copy creates two owners of one handle. Worked example 2 shows that a default copy leads to two releases of the same allocation. Ownership needs copying disabled and moves that leave the source empty. Worked example 1 adds the failure path: an automatic owner releases A when acquiring B fails, while a raw pointer leaks it.",
    "self_check": [
        (
            "What should a moved-from device buffer owner hold?",
            "An empty handle, so its destructor releases nothing.",
        ),
        (
            "In worked example 1, what releases buffer A when acquiring B fails?",
            "Stack unwinding runs A's owner destructor, giving the trace acquire-A, acquire-B-failed, release-A.",
        ),
        (
            "Why should a destructor report errors rather than throw?",
            "Throwing during unwinding from another exception terminates the program.",
        ),
    ],
}

STUDY_NOTES[11] = {
    "mistake_fix": "Packaging device code shows only what targets were compiled. Worked example 2 lists the loading error 'no kernel image is available', which occurs when the executable lacks a cubin or compatible PTX for the actual GPU. Execution evidence requires a run on the target device.",
    "self_check": [
        (
            "What is the difference between PTX and a cubin?",
            "PTX is a virtual instruction form that can be JIT compiled; a cubin is machine code for one target architecture.",
        ),
        (
            "Which diagnostic class is an undefined host function?",
            "A host link error, not a device or loading problem.",
        ),
        (
            "What should a release record include for a CUDA binary?",
            "Toolkit version, target architectures, host compiler, build flags and the commit, plus later runtime receipts per device.",
        ),
    ],
}

STUDY_NOTES[12] = {
    "mistake_fix": "Launches are asynchronous: the host regains control after submission. Only a synchronizing call, such as a checked `cudaDeviceSynchronize` or a blocking copy, proves the kernel completed and surfaces execution errors. Worked example 2 notes that a launch status alone does not establish the output values.",
    "self_check": [
        (
            "In `fill<<<2,32>>>(out,50)`, how many threads launch and how many write?",
            "64 threads launch; 50 pass the bounds predicate and write.",
        ),
        (
            "Which call reports launch configuration errors and which reports execution errors?",
            "`cudaGetLastError` after the launch catches configuration errors; a checked synchronization reports errors raised while the kernel ran.",
        ),
        (
            "Why keep the ownership mapping fixed when changing the formula in worked example 2?",
            "It isolates the arithmetic change, so any mismatch points at the expression rather than at scheduling.",
        ),
    ],
}

STUDY_NOTES[13] = {
    "mistake_fix": "Host and device pointers live in different address spaces, so a matching numerical value means nothing. Pass device pointers only to kernels and device APIs, move data with an explicit `cudaMemcpy` direction, and validate the full round trip as worked example 1 does with distinct nonzero values. Four float32 values need 16 bytes, so a request for 4 bytes copies only the first element.",
    "self_check": [
        (
            "Why does worked example 1 use distinct nonzero values?",
            "Zero-initialized data can hide a short copy, while distinct values reveal exactly which elements arrived.",
        ),
        (
            "What do the sentinel values in worked example 2 detect?",
            "Writes beyond the intended range, though they cannot rule out every invalid access.",
        ),
        (
            "When may the host input buffer be freed after a copy to the device?",
            "Only after the transfer has completed, which a blocking `cudaMemcpy` guarantees on return.",
        ),
    ],
}

STUDY_NOTES[14] = {
    "mistake_fix": "A demo length is not the contract. Real inputs arrive at sizes such as 19 or 33, and worked example 1 shows the final pass of a grid-stride loop covering only part of the stride. Without `i < n` the extra threads read and write past the allocation, which may corrupt memory silently.",
    "self_check": [
        (
            "In worked example 1, why does thread 3 own only two indices?",
            "Its next index, 19, equals n, so the loop stops after 3 and 11.",
        ),
        (
            "Why cast to a wide integer before multiplying block index by block size?",
            "The product can overflow a 32-bit int for large grids, and widening after the overflow cannot recover the lost value.",
        ),
        (
            "What does a grid-stride loop give you that a one-element mapping does not?",
            "Correct coverage of any n with a fixed grid size, so the launch need not grow with the input.",
        ),
    ],
}

STUDY_NOTES[15] = {
    "mistake_fix": "Axis choice decides which coordinate each thread computes, so swapping x and y on a rectangular image touches different pixels. Worked example 2 shows a 3-by-2 image becoming 2-by-3: unless grid height grows and both coordinates are checked, some rows are skipped or padding is overwritten.",
    "self_check": [
        (
            "For a width-3 image with stride 4, where is pixel (row 1, column 0) stored?",
            "At index 1 times 4 plus 0, which is 4.",
        ),
        (
            "Why must a kernel check row and column separately rather than the flattened offset?",
            "An invalid column can still produce an in-range flat offset that lands in the next row or in padding.",
        ),
        (
            "What should happen to padding sentinels after the transform?",
            "They must stay unchanged, because padding is not image data.",
        ),
    ],
}

STUDY_NOTES[16] = {
    "mistake_fix": "The compiler decides where locals live: large or dynamically indexed arrays and register pressure push values into local memory, which is backed by device memory. Shared memory is private to one block for that block's lifetime, so another block can never read it. Worked example 2 shows how quickly 'local' data grows.",
    "self_check": [
        (
            "Which storage would you choose for three filter coefficients that every thread reads?",
            "Constant or read-only storage, because all threads read the same few values.",
        ),
        (
            "When does shared memory's content disappear?",
            "When the block that owns it finishes executing.",
        ),
        (
            "Why can a per-thread array of 1,024 floats hurt occupancy?",
            "It needs 4 KB per thread, which spills to local memory and inflates per-thread resources.",
        ),
    ],
}

STUDY_NOTES[17] = {
    "mistake_fix": "A fence orders one thread's own memory operations as seen by others; it does not make any thread wait. A barrier such as `__syncthreads()` makes every thread of the block arrive before any proceeds and orders shared memory for them. Worked example 1 needs that waiting so no consumer reads an unloaded tile slot.",
    "self_check": [
        (
            "In worked example 1, which thread produces the value read by thread 0?",
            "Thread 3, which loaded 12 into tile[3].",
        ),
        (
            "Why must tail lanes still reach the barrier?",
            "A block barrier expects every thread of the block; skipping it is undefined and can hang.",
        ),
        (
            "What neutral value suits a max operation in a padded tile?",
            "The lowest representable value, such as negative infinity for floats.",
        ),
    ],
}

STUDY_NOTES[18] = {
    "mistake_fix": "A square all-ones input yields the same output under swapped indices or transposed layouts, so layout mistakes cannot appear. Worked example 2 recommends a 3-by-5 times 5-by-2 product with distinct values, which makes swapped m and n or wrong offsets produce visibly wrong entries.",
    "self_check": [
        (
            "Give the flat offset of A(1,2) when A is 2-by-3 row-major.",
            "1 times 3 plus 2, which is 5.",
        ),
        ("How many multiply-adds does an m-by-k times k-by-n product need?", "m times n times k."),
        (
            "Why record the accumulation type with the test?",
            "It sets how much rounding error is expected, which determines a fair tolerance.",
        ),
    ],
}

STUDY_NOTES[19] = {
    "mistake_fix": "Shared memory only helps when values are reused enough to repay loading and synchronizing. Tiling adds barriers and uses shared storage that can lower occupancy, and on tiny matrices the overhead dominates. Worked example 1 counts the saved reads; whether that saves time must still be measured.",
    "self_check": [
        (
            "How many phases does k equal 7 need with tile width 4?",
            "Two, using ceiling division of 7 by 4.",
        ),
        (
            "Why are invalid tile entries filled with zero?",
            "Zero adds nothing to the dot product, so tail phases keep the sum correct.",
        ),
        (
            "Why is a second barrier needed at the end of each phase?",
            "It stops fast threads from overwriting the tile while slower threads are still reading it.",
        ),
    ],
}

STUDY_NOTES[20] = {
    "mistake_fix": "Floating-point addition rounds at each step, so different trees give different answers, as worked example 2 shows. Blocks also have no guaranteed co-residency, so a block spinning on a counter can wait forever for a block that never starts. Combine block partials in a second launch.",
    "self_check": [
        ("Trace the halving tree for [3,1,4,1].", "[7,2], then [9]."),
        (
            "What identity does a product reduction use for tail threads?",
            "One, so padding leaves the product unchanged.",
        ),
        (
            "Why compare a float reduction against a compensated reference instead of a plain CPU loop?",
            "The CPU loop is just another association order; a compensated reference shows the true error.",
        ),
    ],
}

STUDY_NOTES[21] = {
    "mistake_fix": "A sum gives one total, but compaction needs a different position for each selected element: the count of selected elements before it. That is an exclusive scan of the flags, as worked example 1 shows with positions [0,1,1,2,2]. The total count still needs the last prefix plus the last flag.",
    "self_check": [
        ("Give the exclusive scan of flags [0,1,1,0,1].", "[0,0,1,2,2], with total count 3."),
        (
            "What does stability mean for compaction?",
            "Selected elements keep their original relative order in the output.",
        ),
        (
            "What extra stage do multiple blocks need for a scan?",
            "Scan the block totals and add each block's offset to its local results.",
        ),
    ],
}

STUDY_NOTES[22] = {
    "mistake_fix": "Atomic cost depends on contention. Values spread over many bins rarely collide, while a skewed input that sends most values to one bin serializes updates. Worked example 2 shows block privatization, which reduces global contention but adds initialization and merging, so measure both input shapes before choosing.",
    "self_check": [
        (
            "Why must the bin counts in worked example 1 sum to six?",
            "Every input value lands in exactly one bin, so the total equals the input count.",
        ),
        (
            "What does an atomic add guarantee and what does it not?",
            "Each single update is indivisible; it does not make a multi-step algorithm atomic or order other writes.",
        ),
        (
            "When might a private histogram be slower?",
            "On small inputs or with many bins, where initializing and merging private copies costs more than it saves.",
        ),
    ],
}

STUDY_NOTES[23] = {
    "mistake_fix": "Smooth-looking output can hide wrong boundaries or in-place updates that read already-updated neighbors. Worked example 1 shows two valid boundary policies giving different numbers, and worked example 2 shows in-place updates adding bias. Compare exact values against a reference with the chosen policy instead.",
    "self_check": [
        (
            "What is the clamped three-point mean of the last element of [2,4,8]?",
            "(4 + 8 + 8) / 3, which is 20/3.",
        ),
        (
            "Why use two buffers per time step?",
            "Every output must read the old values; writing in place lets later outputs read new ones.",
        ),
        (
            "What is a halo in a tiled stencil?",
            "Extra cells around the tile loaded so edge outputs have all their neighbors.",
        ),
    ],
}

STUDY_NOTES[24] = {
    "mistake_fix": "Composition adds contracts that each kernel alone never checked: valid counts, shapes and ownership must match between stages. Worked example 1 passes count three, not capacity, to the mean and histogram, and worked example 2 defines what an empty selection returns instead of dividing by zero.",
    "self_check": [
        (
            "What must travel with a compacted buffer to the next stage?",
            "Its valid count, not its allocated capacity.",
        ),
        (
            "What does the pipeline return for an empty selection?",
            "Count zero, sum zero, a named empty status instead of a mean, and an all-zero histogram.",
        ),
        (
            "Why introduce GPU stages one at a time?",
            "Each stage can then be compared against the CPU oracle, so a mismatch points at one stage.",
        ),
    ],
}

STUDY_NOTES[25] = {
    "mistake_fix": "Reinstalling only changes the toolkit and driver, which matters for loading or version failures but not for code faults. A compile error needs a source fix, an illegal access needs bounds or ownership repair, and a wrong answer after a clean run needs arithmetic or layout review. Classifying the phase first, as worked examples 1 and 2 do, tells you which repair applies and avoids hours of unrelated rebuilds.",
    "self_check": [
        (
            "Why can an error appear at a line far from the faulty kernel?",
            "Asynchronous execution errors surface at the next synchronizing call, which may be later in the program.",
        ),
        (
            "What is a sticky error?",
            "An error that corrupts the context so later calls keep failing until the process ends.",
        ),
        (
            "What should a minimal reproducer contain?",
            "The smallest input and build command that still fails, the observed and expected output, and the versions used.",
        ),
    ],
}

STUDY_NOTES[26] = {
    "mistake_fix": "A sanitizer reports only problems that occurred in the inputs you ran, and it changes timing, so it says nothing about speed. It also checks access and hazard rules, not whether the arithmetic is correct. Worked example 1 pairs memcheck with a CPU bounds test because each covers what the other misses; worked example 2 still validates values after the race is repaired.",
    "self_check": [
        ("Which checker targets shared-memory hazards?", "Racecheck."),
        (
            "Why are sanitizer runs not performance evidence?",
            "Instrumentation slows execution and changes timing.",
        ),
        (
            "Why is a host sleep not a repair for a missing barrier?",
            "It creates no ordering between device threads, so the race remains.",
        ),
    ],
}

STUDY_NOTES[27] = {
    "mistake_fix": "The mask must name exactly the lanes that reach the collective. If a branch admits only half the warp, a full mask promises 16 lanes that never arrive, which is undefined behavior. Worked example 1 avoids this by letting all 32 lanes execute the collective while unselected lanes contribute zero.",
    "self_check": [
        ("What ballot mask do predicates true at lanes 0 and 3 produce?", "1 plus 8, which is 9."),
        (
            "Why may a shuffle not read from lane seven in worked example 2?",
            "Lane seven is outside the participating group, so its value is not defined for that collective.",
        ),
        (
            "Why is source order not a synchronization guarantee within a warp?",
            "Independent thread scheduling lets lanes progress separately, so ordering needs explicit synchronization.",
        ),
    ],
}

STUDY_NOTES[28] = {
    "mistake_fix": "Atomicity covers one operation on one location. Publishing a payload needs ordering: the producer's payload write must happen before a release on the flag, and the consumer must acquire the flag before reading the payload, at a scope that covers both parties. Worked example 2 shows a correct atomic count alongside an incomplete payload protocol, which is exactly the gap this mistake ignores.",
    "self_check": [
        (
            "What are the four events in worked example 1's publication chain?",
            "Payload write, release of the flag, acquire of the flag, then payload read.",
        ),
        (
            "Why can block scope be too narrow?",
            "If producer and consumer sit in different blocks, block-scope ordering does not reach the consumer; device scope is needed.",
        ),
        (
            "What is the difference between visibility and atomicity?",
            "Atomicity makes one operation indivisible; visibility concerns when other observers can see a write.",
        ),
    ],
}

STUDY_NOTES[29] = {
    "mistake_fix": "Fast-math and reassociation change rounding, special values and sometimes accuracy by large factors, as the cancellation in worked example 1 shows. Whether that is acceptable depends on an error budget for the application, so a faster mode must be measured against a higher-precision reference before it replaces the original.",
    "self_check": [
        (
            "Why does centering around the mean help in worked example 1?",
            "It subtracts close values first, keeping deviations small, so no huge nearly equal quantities are subtracted.",
        ),
        (
            "What does FMA change compared with a separate multiply and add?",
            "It rounds once instead of twice, which usually improves accuracy but changes bit patterns.",
        ),
        (
            "When is exact equality an appropriate test for floating point?",
            "Only when the algorithm and order are fixed and the result is known to be exactly representable.",
        ),
    ],
}

STUDY_NOTES[30] = {
    "mistake_fix": "A sleep changes timing, which can hide a race without creating any ordering, so the defect returns on a different machine or load. Resetting a shared GPU destroys other users' work and the evidence of your own fault. Worked example 1 shows the better path: shrink the failure to the smallest input, here length one, and turn it into a regression test before changing code. Keep the failing command and its exact error text with the fixture.",
    "self_check": [
        (
            "Why does length one expose the `i <= n` bug in worked example 1?",
            "Index one is already out of range for a one-element buffer, so the extra iteration is the first write.",
        ),
        (
            "How should a timeout with no completion be classified?",
            "As incomplete execution; inspect boundedness and dependencies rather than reporting a result.",
        ),
        (
            "What does it mean if a bug disappears in a debug build?",
            "It is a clue that timing or optimization matters, not proof the defect is fixed.",
        ),
    ],
}

STUDY_NOTES[31] = {
    "mistake_fix": "A host clock around a launch measures submission, not execution, as worked example 1 shows with 5 microseconds reported for 80 microseconds of work. Excluding transfers is representative only when the data truly stays resident; a request-response service pays the upload and download on every call, so its timing must include them.",
    "self_check": [
        (
            "What must happen before reading an elapsed time between two events?",
            "The end event must complete, typically by synchronizing on it.",
        ),
        (
            "Why keep the 9.0 ms sample in worked example 2?",
            "It may reveal interference or cold behavior that real users would also see.",
        ),
        (
            "What does warm-up separate from repeated work?",
            "One-time costs such as context creation, module loading and JIT compilation.",
        ),
    ],
}

STUDY_NOTES[32] = {
    "mistake_fix": "The end-to-end time depends on the critical path, not on the most prominent bar. Worked example 1 halves a 2 ms kernel and saves only 1 of 10 ms, because 6 ms are transfers and 2 ms are host work. Worked example 2 shows a 6 ms idle gap that no kernel tuning removes. Start with the timeline, find the largest serial cost on the path, and change that first. Removing an unneeded round trip could save up to the 6 ms of transfers, six times the kernel gain, if the data may stay resident on the device.",
    "self_check": [
        (
            "In worked example 1, what saving would removing one 3 ms transfer give?",
            "3 of 10 ms, three times more than halving the kernel.",
        ),
        (
            "What does an idle gap on the GPU row usually point to?",
            "Host preparation, synchronization or missing batching that leaves the device waiting.",
        ),
        (
            "Why must NVTX ranges match real code boundaries?",
            "Misplaced ranges attribute time to the wrong phase and mislead the analysis.",
        ),
        (
            "Why can two overlapping bars fail to speed up the application?",
            "The overlap may lie off the critical path, or the overlapped work may contend for the same resource.",
        ),
    ],
}

STUDY_NOTES[33] = {
    "mistake_fix": "A utilization percentage measures how busy a unit is, not whether the work is useful. Worked example 1 shows high DRAM traffic where only a quarter of the bytes are used, and worked example 2 shows higher occupancy with a slower kernel. Each counter answers a narrow question, so combine several counters with correctness checks and timing before naming a bottleneck, and label untested explanations as hypotheses. Here the counter points at the access pattern: a layout that transfers close to the 400 useful bytes could cut DRAM traffic by up to four times, while faster arithmetic would leave the 0.25 ratio unchanged.",
    "self_check": [
        (
            "What fraction of transferred bytes is useful in worked example 1?",
            "0.25, since 400 of 1,600 bytes are used.",
        ),
        (
            "Why can a profiled kernel run slower than in a normal timing run?",
            "Collecting many counters often replays the kernel and adds instrumentation overhead.",
        ),
        (
            "What does achieved occupancy measure?",
            "The average ratio of active warps to the maximum an SM supports, a residency figure, not speed.",
        ),
        (
            "What should you report if counter access is not permitted?",
            "That counters are unavailable, plus timing and correctness evidence, without invented counter values.",
        ),
    ],
}

STUDY_NOTES[34] = {
    "mistake_fix": "Coalescing depends on the addresses neighboring lanes touch at the same instruction, not on how the source loop reads. A loop over records that reads one field advances 16 bytes per lane in worked example 2. Write each lane's address first, then judge the layout.",
    "self_check": [
        (
            "What span do 32 float32 lanes cover at stride one?",
            "128 bytes: byte offsets 0 through 124, each element 4 bytes wide.",
        ),
        (
            "Why is address span not the same as bytes transferred?",
            "Transfers happen in fixed-size sectors, so gaps may or may not be fetched depending on alignment and caching.",
        ),
        (
            "When can array-of-structures be the better layout?",
            "When the consumer needs every field of each record together.",
        ),
    ],
}

STUDY_NOTES[35] = {
    "mistake_fix": "Padding changes the shared bank mapping only; worked example 1 shows width 33 spreading a column across banks. It does nothing for global coalescing, and on patterns without conflicts it only wastes shared memory. Treat banks and coalescing as separate layers and measure each.",
    "self_check": [
        (
            "In the 32-bank model, which bank does row 5 of a column use at width 33?",
            "Bank 5, since 5 times 33 mod 32 is 5.",
        ),
        (
            "Why can a same-address read avoid a conflict?",
            "Lanes reading the identical word can receive it by broadcast.",
        ),
        (
            "What must a padded transpose never output?",
            "The padding column; it is internal storage, not data.",
        ),
    ],
}

STUDY_NOTES[36] = {
    "mistake_fix": "Occupancy is a means of hiding latency, not the goal. Worked example 2 shows a 50% configuration beating a 75% one, because more work per thread can give reuse and instruction-level parallelism. Forcing fewer registers to raise occupancy can also cause spills that cost more than they save.",
    "self_check": [
        (
            "How many 256-thread blocks fit by registers at 32 registers per thread with 65,536 registers?",
            "Eight, since each block needs 8,192 registers.",
        ),
        (
            "What is the difference between a resident warp and an eligible warp?",
            "A resident warp has resources on the SM; an eligible warp also has its next instruction ready to issue.",
        ),
        (
            "What does a register spill cost?",
            "Extra local memory traffic, which is backed by device memory.",
        ),
    ],
}

STUDY_NOTES[37] = {
    "mistake_fix": "Branches are allowed and often useful: a warp-uniform branch costs little, and a branch that skips expensive work saves time. Removing branches by computing both sides doubles work and can raise errors on the unused side. Worked example 2 also shows that regrouping divergent work costs a compaction pass, which pays off only when the saved kernel time exceeds it or the grouping is reused.",
    "self_check": [
        (
            "What utilization does the lockstep model give for workloads [2,2,2,8]?",
            "14 useful lane-rounds out of 32, about 0.44.",
        ),
        (
            "When is a branch warp-uniform?",
            "When every lane of the warp takes the same path, so no divergence occurs.",
        ),
        (
            "Why might reordering work change results?",
            "It can change output order or arithmetic order unless order is restored or proven irrelevant.",
        ),
    ],
}

STUDY_NOTES[38] = {
    "mistake_fix": "One fast run can reflect a lucky clock state, a warm cache or a different accuracy target. Worked example 1 compares medians of five samples each and still limits the claim to that fixture, and worked example 2 shows float16 against float64 is not like for like. A defensible claim keeps raw samples, a competent baseline and the same error contract.",
    "self_check": [
        (
            "Why compare medians rather than the fastest run of each version?",
            "The median resists outliers and reflects typical behavior; the minimum rewards luck.",
        ),
        (
            "What makes a CPU baseline competent?",
            "It uses a reasonable algorithm, optimization flags and threading for the same problem contract.",
        ),
        (
            "Why record thermal state and device sharing?",
            "Clocks drop when hot and shared devices add interference, so timings may not repeat elsewhere.",
        ),
    ],
}

STUDY_NOTES[39] = {
    "mistake_fix": "Streams express permitted concurrency, not a schedule, and the hardware may still run their work one after another. They also share the same device memory, so two streams touching one buffer need an event dependency. Worked example 2 stays correct because its vectors share no mutable storage, not because overlap was observed.",
    "self_check": [
        (
            "In worked example 1, what does stream B wait for?",
            "The event recorded in stream A after the doubling kernel.",
        ),
        (
            "What is guaranteed about two operations in the same stream?",
            "They run in issue order; the second starts after the first completes.",
        ),
        (
            "Why must correctness not depend on observed overlap?",
            "Overlap is optional for the hardware, so a design that needs it can fail on another device or load.",
        ),
    ],
}

STUDY_NOTES[40] = {
    "mistake_fix": "The `Async` suffix means the call returns before the copy finishes. Real overlap also needs pinned host memory, a free copy engine, independent work in another stream and correct dependencies. With pageable memory the copy may block. Worked example 1 computes the ideal 13 ms only under all of those assumptions.",
    "self_check": [
        (
            "What is the ideal time for four chunks with stage costs 2, 3 and 2 ms?",
            "7 ms for the first result plus three 3 ms intervals, which is 16 ms.",
        ),
        (
            "Why reuse pinned buffers instead of pinning in every iteration?",
            "Pinning is expensive and consumes host memory that the operating system cannot page.",
        ),
        (
            "When may a double-buffering slot be refilled?",
            "Only after its download and any host consumption have completed.",
        ),
    ],
}

STUDY_NOTES[41] = {
    "mistake_fix": "A pool keeps freed memory reserved so later allocations are fast, so the device report can stay high while live usage is zero. Worked example 2 shows a 64 MiB reservation with nothing live, which is a retention policy, not a leak. Confirm a leak by tracking live allocations and their owners, and use the release threshold if the reserved memory must return to the system sooner. Report reserved and live bytes separately, since worked example 2 ends with 64 MiB reserved and nothing live.",
    "self_check": [
        (
            "Which two edges make the cross-stream allocation in worked example 1 safe?",
            "Producer to consumer through the ready event, and consumer to free through the done event.",
        ),
        (
            "Why is freeing right after enqueuing work in another stream unsafe?",
            "The free is ordered only in its own stream, so the other stream may still read the buffer.",
        ),
        (
            "What does a stream-ordered free promise?",
            "The memory becomes reusable after prior work in that stream completes, not immediately.",
        ),
    ],
}

STUDY_NOTES[42] = {
    "mistake_fix": "A single pointer hides where the data currently lives. Managed memory still moves pages between host and device, so first touch, alternating access and oversubscription cost real transfers, as worked example 2 shows with twenty transitions. Prefetching and batching each side's work reduce that movement, but only measurement on the target platform confirms the saving. In worked example 2, ten alternating rounds cause twenty ownership transitions, while batching all CPU work and then all GPU work needs only one transfer to each side.",
    "self_check": [
        (
            "Why report the first GPU pass of worked example 1 separately?",
            "It includes migration from host to device that later resident passes do not pay.",
        ),
        (
            "What does unified virtual addressing promise?",
            "One address space for host and device pointers, not uniform access cost or residency.",
        ),
        (
            "What is prefetch?",
            "A placement hint that moves data ahead of use; it must still be ordered with the work that uses it.",
        ),
    ],
}

STUDY_NOTES[43] = {
    "mistake_fix": "A graph replays the nodes you captured or defined, kernel by kernel; it does not merge them into one kernel. Its structure is fixed at instantiation, so data-dependent control flow or a shape beyond the allocation needs a supported update or a rebuild, as worked example 2 explains.",
    "self_check": [
        (
            "Where is break-even in worked example 1?",
            "Setup 300 microseconds divided by a 15 microsecond saving per replay is 20 replays; more than twenty gives a net gain.",
        ),
        (
            "What must stay valid across graph replays?",
            "Every buffer and resource referenced by graph nodes.",
        ),
        (
            "Why can a graph lose for a pipeline that runs once?",
            "Capture and instantiation cost more than the submission overhead saved.",
        ),
    ],
}

STUDY_NOTES[44] = {
    "mistake_fix": "Larger batches raise throughput but make each request wait longer for its batch to fill and finish. Worked example 2 separates first-result latency, about 7 ms, from the 3 ms interval between later results. An interactive service needs a latency target and backpressure, not the largest batch that fits.",
    "self_check": [
        (
            "When is a slot free in worked example 1?",
            "Only after its output download and final consumer complete, not when compute ends.",
        ),
        (
            "What does backpressure do?",
            "It makes producers wait or reject work when no slot can safely accept another item.",
        ),
        (
            "What must cancellation do before freeing device buffers?",
            "Stop admission and wait for in-flight work that still uses them to complete.",
        ),
    ],
}

STUDY_NOTES[45] = {
    "mistake_fix": "Libraries implement the algorithm, but the caller still owns inputs, outputs, temporary storage, stream choice and layout. CUB primitives ask you to query and allocate temporary storage, Thrust policies decide where work runs, and a call on the wrong stream races with other work. Worked example 2 shows semantics matter too: sorting before filtering changes order, so pick the primitive that matches the contract. Worked example 1 makes the memory point concrete: a fused transform-reduce sums the squares of [1,2,3,4] to 30 without storing the intermediate array [1,4,9,16] in device memory.",
    "self_check": [
        (
            "Why can transform-reduce use less memory than transform followed by reduce?",
            "It fuses the steps and avoids storing the intermediate squared array.",
        ),
        ("What is the sum of squares of an empty input?", "Zero, the identity of addition."),
        (
            "Why is a library stream argument a correctness choice?",
            "Work on the wrong stream is not ordered with the producers and consumers of its data.",
        ),
    ],
}

STUDY_NOTES[46] = {
    "mistake_fix": "Swapping dimensions until one test passes can coincide with a transposed or wrongly strided interpretation that fails on other shapes. Worked example 2 shows the same values flattened differently in column-major and row-major order. Write the layout, leading dimension and transpose flags for each operand first, then test rectangular shapes.",
    "self_check": [
        (
            "What is the leading dimension of a column-major 3-by-4 matrix without padding?",
            "3, the number of rows.",
        ),
        (
            "Why does worked example 1 use beta equal to 3 with C initialized to ones?",
            "It catches code that ignores beta or assumes C starts at zero.",
        ),
        (
            "What should beta equal to 0 mean?",
            "The old C does not contribute, so even NaN values in C must not affect the result.",
        ),
    ],
}

STUDY_NOTES[47] = {
    "mistake_fix": "A spectrum can have the right shape and the wrong scale, because conventions differ on where the 1/N factor goes. Frequency-space multiplication gives circular convolution, which wraps results, as worked example 2 shows with [11,10]. Check a round trip and zero-pad to the linear length before trusting it.",
    "self_check": [
        (
            "What length avoids wraparound when convolving lengths 4 and 3?",
            "6, which is 4 plus 3 minus 1.",
        ),
        (
            "A round trip returns N times the input. What is missing?",
            "The 1/N normalization on the inverse transform.",
        ),
        (
            "Why is plan creation kept outside timing loops?",
            "Planning is a one-time setup cost separate from executing transforms.",
        ),
    ],
}

STUDY_NOTES[48] = {
    "mistake_fix": "Dense storage keeps every zero; sparse formats must be chosen and built deliberately. Sparse kernels add indirect reads and uneven row work, so moderate sparsity may run slower than a dense routine. Conversion cost also counts unless the sparse form is reused.",
    "self_check": [
        ("What CSR offsets correspond to row lengths [1,0,2]?", "[0,1,1,3]."),
        ("What does the final CSR offset equal?", "The number of stored entries."),
        (
            "Name two inputs that must be rejected before device access.",
            "Descending offsets and column indices outside the matrix width.",
        ),
    ],
}

STUDY_NOTES[49] = {
    "mistake_fix": "A solver returns numbers even when the problem is nearly singular. Check the status, compute the residual and consider conditioning: worked example 2 shows nearly dependent rows where tiny changes in b swing x widely. A small residual then does not mean an accurate x.",
    "self_check": [
        (
            "What is the residual of x = [2,3] in worked example 1?",
            "Zero, because A times x equals b exactly.",
        ),
        (
            "Why prefer factorization over computing the inverse?",
            "It is cheaper and numerically more stable for solving.",
        ),
        (
            "What does an ill-conditioned matrix mean for the answer?",
            "Small input changes can cause large changes in x, so errors in b are amplified.",
        ),
    ],
}

STUDY_NOTES[50] = {
    "mistake_fix": "Identical states give identical draws, so worked example 2 gets eight numbers but only two distinct values, and the true sample size is far smaller. Each worker needs its own stream or subsequence. Conversely, a GPU estimate that differs from a CPU estimate may only reflect sampling error, which shrinks with the square root of the sample count, so compare within standard errors before suspecting a bug.",
    "self_check": [
        (
            "How much does standard error shrink with 100 times more independent samples?",
            "By a factor of 10, the square root of 100.",
        ),
        (
            "What is the exact value targeted in worked example 1?",
            "One third, the integral of x squared from 0 to 1.",
        ),
        (
            "What should a Monte Carlo receipt record besides the seed?",
            "The generator, stream partition, sample count and the estimate with its standard error.",
        ),
    ],
}

STUDY_NOTES[51] = {
    "mistake_fix": "Algebraically equal formulas can round and overflow differently. Exponentiating 1001 directly overflows in common types, while subtracting the row maximum keeps every exponential at one or below and gives the same ratios. Treat any rewrite as a new numerical contract and test it with large logits.",
    "self_check": [
        (
            "What is the softmax of [0,0]?",
            "[0.5,0.5], because equal logits share the weight equally.",
        ),
        (
            "A row sums to one but entries sit in the wrong columns. Why does the sum test miss it?",
            "A permutation preserves the sum, so only an elementwise comparison with a reference catches it.",
        ),
        (
            "Why subtract the maximum rather than any other constant?",
            "Any constant preserves the ratios, but the maximum makes the largest exponent zero so nothing overflows.",
        ),
    ],
}

STUDY_NOTES[52] = {
    "mistake_fix": "Fusion removes intermediate traffic and launches but can raise register pressure or block reuse, so it must be measured. Epsilon conventions are not interchangeable either: adding it inside the square root differs from adding it to the denominator. Match the reference formula exactly and test constant and low variance rows.",
    "self_check": [
        (
            "What does fused bias-plus-ReLU give for x = [-2,1] and bias 1?",
            "[0,2]: the biased values are [-1,2] and ReLU clamps the negative one to zero.",
        ),
        (
            "What variance does sample variance give for [1,3], and what is the effect?",
            "2 instead of the population value 1, so outputs shrink by a factor of the square root of 2.",
        ),
        (
            "What is centered normalization of a single value with positive epsilon?",
            "[0], because the value minus its own mean is zero and epsilon keeps the denominator positive.",
        ),
    ],
}

STUDY_NOTES[53] = {
    "mistake_fix": "Tensor core formats depend on the architecture and library mode, and lower precision changes range and rounding. FP16 has 5 exponent and 10 fraction bits, while BF16 has 8 exponent and 7 fraction bits, so BF16 covers a far wider range with less precision. Worked example 1 shows rounding error accumulating, so record operand and accumulator types and set an accuracy policy before trusting speed.",
    "self_check": [
        (
            "In worked example 1, how far is the rounded sum from the exact sum?",
            "1, because 1,000 inputs of 1.001 rounded to 1.00 sum to 1,000 instead of 1,001.",
        ),
        (
            "A float16 GEMM ran successfully. Does that prove tensor core use?",
            "No; only profiler or library mode evidence shows which instructions ran.",
        ),
        (
            "Why test extreme magnitudes?",
            "Low precision formats overflow or underflow earlier, and well scaled inputs hide those failures.",
        ),
    ],
}

STUDY_NOTES[54] = {
    "mistake_fix": "A short teaching kernel proves one small contract, not a production attention library or a working Transformer. Production versions handle scaling, masking, numerically stable online softmax, many shapes and dtypes, and backward passes. Claim only what your fixtures and reference cover.",
    "self_check": [
        (
            "With a causal mask that keeps only the first key, what output does worked example 1 give?",
            "[2,0], the first value row, because its weight becomes one.",
        ),
        (
            "How large is a 2,048 token score matrix at four bytes per element?",
            "2,048 squared is 4,194,304 elements, which is 16 MiB per head and batch item.",
        ),
        (
            "Why must online accumulators rescale when the maximum increases?",
            "Earlier terms were computed against the old maximum, so they must be multiplied by the exponential of old maximum minus new maximum.",
        ),
    ],
}

STUDY_NOTES[55] = {
    "mistake_fix": "A grid barrier is safe only under a supported cooperative launch, where every block is resident at the same time. In an ordinary launch some blocks may wait for others that cannot start until the waiting ones finish, so the program can hang. Worked example 2 shows twelve blocks exceeding an eight block capacity. Query the real limit for the kernel and device, or split the work into separate kernel launches whose boundary provides the global synchronization. Keep a CPU model of the group membership, as worked example 1 does, so each partial sum can be checked before the final combination.",
    "self_check": [
        (
            "What are the group results and final total in worked example 1?",
            "10 and 26, combined by a separate valid step into 36.",
        ),
        (
            "What is the assumed cooperative capacity in worked example 2?",
            "Four SMs times two resident blocks, which is eight blocks.",
        ),
        (
            "What should a reduction do if cooperative launch is unavailable?",
            "Use two ordinary launches: one writes partial sums, and the next combines them.",
        ),
        (
            "Why does group-local synchronization not combine the two groups?",
            "It orders only the members of one group; the other group's writes need a block level step.",
        ),
    ],
}

STUDY_NOTES[56] = {
    "mistake_fix": "Issuing an asynchronous copy only starts the transfer, so the consumer must wait on its completion token or barrier before reading the destination. A second milestone governs reuse: a slot may be refilled only after the consumer has finished with it. Worked example 1 separates the two milestones for three tiles in two slots, and worked example 2 shows that alignment must be real, not cast into existence. Double buffering adds overlap but not correctness: with two slots, every refill still waits for the consumer of the tile that last used that slot.",
    "self_check": [
        (
            "List the lifetime states of one tile slot.",
            "Free, loading after the copy is issued, ready after completion, consuming, then free again when the consumer finishes.",
        ),
        (
            "When may tile 2 reuse slot A in worked example 1?",
            "Only after the computation using tile 0 has finished.",
        ),
        (
            "Is an address four bytes past a 16-byte aligned base valid for a 16-byte contract?",
            "No; only offsets that are multiples of 16 keep that alignment.",
        ),
        (
            "How should a partial final tile be handled?",
            "Guard loads by bounds or use a supported fallback, so no read passes the end of the input.",
        ),
    ],
}

STUDY_NOTES[57] = {
    "mistake_fix": "Instruction variants are tied to specific architectures, toolkit versions and compile targets, not to how new a product name sounds. Detect the feature with a real probe and record the result. Worked example 2 dispatches the baseline when cluster launch is unavailable instead of trying an unsupported instruction.",
    "self_check": [
        (
            "Name four fields of a capability record.",
            "Device and compute capability, toolkit and driver versions, the feature probed and the probe result.",
        ),
        (
            "What should an unavailable cluster feature do to reading progress?",
            "Nothing; the lesson remains complete, and only the optional lab stays unqualified.",
        ),
        (
            "When may a block read another block's distributed shared memory?",
            "After the producer initialized it, within the required cluster synchronization, while that block is still alive.",
        ),
    ],
}

STUDY_NOTES[58] = {
    "mistake_fix": "Templates encode tile and layout choices but do not check that they match your data or device. A wrong stride compiles and silently computes the wrong offsets, and an instantiation can target instructions the device lacks. Trace a tiny layout by hand, as worked example 1 does, and confirm architecture support.",
    "self_check": [
        (
            "What offset does (1,1) map to under shape (2,3) and strides (3,1)?",
            "4, because 1 times 3 plus 1 times 1 is 4.",
        ),
        (
            "What does worked example 2 produce when bias comes after ReLU?",
            "[1,2,5] instead of [0,2,5], so the order changes semantics.",
        ),
        (
            "An instantiation compiles but fails on the device. What is missing?",
            "A check that the device supports the selected architecture target and instructions.",
        ),
    ],
}

STUDY_NOTES[59] = {
    "mistake_fix": "PTX is virtual code that the driver or assembler translates, so its instruction count does not equal executed SASS instructions. Fewer instructions can still be slower if they cause stalls, spills or poor memory behavior. Worked example 1 keeps the numerical test because a fused multiply-add rounds once instead of twice. Judge changes by uninstrumented timing plus correctness. Keep the compiler resource report from each build next to its timing so changes in registers and spills can be traced.",
    "self_check": [
        (
            "How do native image and PTX JIT compatibility differ?",
            "A native image runs only on matching architectures; PTX can be compiled by the driver for newer ones at startup.",
        ),
        (
            "What should a cold-start experiment measure?",
            "First launch time in a fresh process with and without a warm JIT cache, separate from steady state.",
        ),
        (
            "Why can removing spills in worked example 2 fail to speed things up?",
            "Shorter live ranges may add recomputation that costs more than the saved local memory traffic.",
        ),
    ],
}

STUDY_NOTES[60] = {
    "mistake_fix": "Each GPU has its own memory and context, and peer access must be supported and enabled per pair. Multi-node work adds networking, process launch and failure handling that a single machine never tests. State which topology was actually used for every claim.",
    "self_check": [
        (
            "What is strong-scaling efficiency for speedup 1.6 on two GPUs?",
            "0.8, or 80 percent, because 1.6 divided by 2 is 0.8.",
        ),
        (
            "Rank zero calls all-reduce while rank one calls broadcast. What happens?",
            "The collectives do not match, so the ranks usually hang waiting for each other.",
        ),
        (
            "What does all-reduce give in worked example 1 that a gather does not?",
            "The total 15 on both devices instead of one destination.",
        ),
    ],
}

STUDY_NOTES[61] = {
    "mistake_fix": "The pad compiles one source file through a fixed command, so it cannot run a build system. A real project lives in its own repository with an out-of-source build directory, explicit targets and an architecture policy. Worked example 1 sketches the three-file layout to create there, not inside the pad. Split tests into fast CPU reference checks and optional GPU checks that run only where a device exists.",
    "self_check": [
        (
            "What are typical source and build directories for a clean project?",
            "The repository root holds sources, and a separate build directory such as build holds generated files.",
        ),
        (
            "Why should architecture targets not come from lesson metadata argv?",
            "They are a build policy, so they belong in the project's CMake settings.",
        ),
        (
            "What does a successful CMake configure prove?",
            "That the toolchain was found and the project parsed, not that it compiles, links or runs correctly.",
        ),
    ],
}

STUDY_NOTES[62] = {
    "mistake_fix": "A container fixes user space software, but the driver, device architecture and memory come from the host. Worked example 2 shows the same tag fitting a 24 GiB device and failing on an 8 GiB one. Dispatch on detected capability and a small numerical probe, and record which path actually ran. A smaller device may need a reduced workload, but report the reduction and keep the original memory error, so a fit on 8 GiB is not mistaken for the full model.",
    "self_check": [
        (
            "Why is an operating-system check insufficient for dispatch?",
            "Linux does not guarantee a visible device, a compatible driver or enough memory.",
        ),
        (
            "What should a device fault preserve?",
            "The original error, the learner's source and the path that ran.",
        ),
        (
            "In worked example 1, when does the CUDA path run?",
            "Only after visibility, allocation and a small numerical probe succeed.",
        ),
    ],
}

STUDY_NOTES[63] = {
    "mistake_fix": "A demo without its assumptions cannot be rerun, checked or extended by anyone else. A deliverable states its input contract, precision, resource budget, failure behavior and reference, and keeps source, generators, commands and raw measurements. Report end-to-end time, including conversions such as building CSR, beside kernel time. For Project A the reference is concrete: input [2,4,8] gives stencil output [2, 14/3, 4] and energy 376/9, so any GPU path must match both.",
    "self_check": [
        (
            "What energy does Project A give for the stencil output [2, 14/3, 4]?",
            "4 plus 196/9 plus 16, which is 376/9, about 41.78.",
        ),
        (
            "A speedup claim omits graph conversion. Why does that matter?",
            "If conversion runs each time, it belongs in end-to-end cost and may erase the gain.",
        ),
        (
            "Name three adversarial fixtures for Project B.",
            "An isolated node, duplicate edges and one very long row next to short rows.",
        ),
    ],
}

STUDY_NOTES[64] = {
    "mistake_fix": "A faster forward pass says nothing about gradients, strides, dtypes or stream rules. Worked example 1 shows correct outputs paired with a wrong gradient of one. Accept the operator only after forward and backward checks pass and unsupported tensors are rejected.",
    "self_check": [
        ("What are the input gradients for loss = sum(3x+1)?", "3 for every element."),
        (
            "A kernel assumes contiguous tensors but accepts transposed views. What is wrong?",
            "It reads with the wrong strides; it must check strides and reject or convert noncontiguous input.",
        ),
        ("What should an unsupported dtype do?", "Raise a clear error before any device access."),
    ],
}
