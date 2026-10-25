"""Durable, original CUDA Python teaching material. No GPU execution at generation."""

from __future__ import annotations

LESSONS = []


def add(n, title, mechanism, example_a, example_b, exercise, answer, code, expected):
    LESSONS.append(
        dict(
            n=n,
            title=title,
            mechanism=mechanism,
            examples=[example_a, example_b],
            exercise=exercise,
            answer=answer,
            code=code.strip() + "\n",
            expected=expected,
        )
    )


add(
    1,
    "Which processor ran this line?",
    """Python is a host language in this lesson: its interpreter evaluates names, calls library functions and schedules work. A NumPy array owns CPU-accessible storage. A CuPy array normally owns device storage while its Python object keeps shape, dtype and ownership information on the host. The statement that creates a result may return before its GPU kernel completes. Printing a scalar can force a transfer and a wait, so observation can change the schedule you are observing.

Use four separate questions: which process issued the operation, which allocation contains its inputs, which processor executes the arithmetic, and which event proves the output is ready. A package import answers none of the last three. A GPU-enabled framework can also place unsupported or deliberately selected work on the CPU. Record actual tensor residency and synchronization instead of inferring placement from the package name.""",
    "A CPU list [1, 2, 3] is reduced by the Python process to 6. No driver, GPU allocation or kernel is involved. The host result is immediately available after sum returns.",
    "For a GPU sum, identify host construction, host-to-device copy, reduction launch, completion and device-to-host scalar retrieval as five events. A returned device scalar is not yet a host integer.",
    "Trace the five events;Explain why import is insufficient;Change the input to an empty list;Find the hidden transfer in scalar printing;Design a residency ledger;Explain how a CPU fallback must be labeled",
    "Construction and retrieval belong to the host;Import proves only Python resolution;The additive identity is zero;Scalar materialization transfers and may synchronize;Record object, backend, allocation and completion;Report CPU reference rather than GPU success",
    """values = [1, 2, 3]
result = sum(values)
assert result == 6
assert sum([]) == 0
ledger = [("input", "CPU"), ("sum", "CPU"), ("result", "CPU")]
assert all(device == "CPU" for _, device in ledger)
print("CPU reference:", result, ledger)""",
    "CPU reference: 6; every ledger event is CPU.",
)

add(
    2,
    "Shape, dtype, stride and layout are a contract",
    """Shape describes logical coordinates; strides describe the byte displacement when one coordinate increases by one. A contiguous row-major matrix with three float32 columns has strides (12, 4). A slice selecting alternate columns changes the last stride without necessarily copying storage. Its shape alone cannot tell a raw kernel how to find the next element.

An address is the allocation base plus view offset plus the sum of index times stride. Dtype determines interpretation and element width, not just a display label. A kernel accepting only contiguous float32 data should validate those conditions or explicitly pack a copy and account for it. Supporting arbitrary strides requires a different indexing contract. Never reinterpret float64 bytes as float32 because the element count happens to match.""",
    "For a 2 by 3 float32 array, coordinate (1, 2) is \\(1\\times12+2\\times4=20\\) bytes from the base. The allocation occupies 24 bytes.",
    "A column slice choosing columns 0 and 2 has shape (2, 2), strides (12, 8) and a 16-byte logical payload. Its covered storage spans 24 bytes; logical bytes and storage span differ.",
    "Calculate offset (1,1);Change dtype to float64;Describe a transposed view;Find the contiguous-only bug;Specify negative-stride support;Design layout contract tests",
    "Offset is 16 bytes in the original matrix;Element width and strides double;Transpose exchanges shape axes and strides;Using row*width+col ignores actual strides;Reject or implement negative strides explicitly;Include contiguous, sliced, transposed, empty and wrong dtype",
    """def offset(indices, strides):
    return sum(i*s for i, s in zip(indices, strides, strict=True))
assert offset((1, 2), (12, 4)) == 20
assert offset((1, 1), (12, 8)) == 20
assert offset((2, 1), (4, 12)) == 20
print("CPU layout model:", offset((1, 2), (12, 4)), "bytes")""",
    "All three views address byte offset 20.",
)

add(
    3,
    "Transfers have cost and lifetime",
    "A transfer pays fixed submission latency plus a size-dependent term. With payload B bytes and effective bandwidth W bytes per second, a useful first model is \\(T=\\ell+B/W\\), where \\(\\ell\\) is submission latency. This is a hypothesis for planning, not a benchmark. Small transfers often pay the fixed term repeatedly. Keeping intermediate arrays on device can save round trips even when the arithmetic expression does not change.\n\nAsynchronous copying also creates an ownership obligation. The source must remain valid and unchanged until the copy finishes; the destination cannot be consumed before its dependency is satisfied. Pinned host memory can enable useful transfer overlap under supported conditions, but pinning every object consumes host resources. Count transfers before optimizing them and include serialization, packing and final output retrieval in end-to-end latency.",
    "Copying 100 rows separately at 10 microseconds submission cost spends at least 1 millisecond on submissions. One contiguous batch pays the submission term once.",
    "Over K iterations, a transformation that copies input and output every iteration moves \\(2KB\\) bytes. Uploading once and downloading once moves \\(2B\\) bytes if all intermediates stay device-resident.",
    "Count bytes for ten iterations;Model a batched transfer;Find premature source reuse;Explain pinned-memory lifetime;Design an end-to-end timer;Identify an intentionally CPU-friendly workload",
    "The round-trip version moves 20 B;Batch submission reduces fixed cost not payload;Wait on the copy event before overwrite;Keep owner alive until completion;Start before preparation and stop after host output;Tiny one-off arrays can favor CPU",
    """size = 4096
iterations = 10
round_trip = 2 * size * iterations
resident = 2 * size
assert round_trip == 81920
assert resident == 8192
latency = 10e-6
bandwidth = 1e9
many = 100 * (latency + 40 / bandwidth)
one = latency + 4000 / bandwidth
assert many > one
print("CPU cost model:", round_trip, resident, "bytes")""",
    "81920 versus 8192 modeled bytes; these are not measured timings.",
)

add(
    4,
    "Array operations before custom kernels",
    "Broadcasting extends dimensions of size one logically, so a column mean can be subtracted from every row without constructing a full repeated matrix. A reduction consumes an axis; matrix multiplication combines contracted dimensions. These shape rules matter before choosing a backend. Express a correct reference using clear operations, then inspect whether intermediates and repeated launches dominate the useful work.\n\nFor squared distances, expanding \\((x-y)^2\\) gives \\(x^2+y^2-2xy\\). The expanded form avoids a full pairwise difference tensor but can lose relative accuracy when large nearly equal vectors cancel. A custom fused kernel can reduce temporary traffic, yet it creates maintenance, numerical and testing obligations. A mature library baseline is therefore both a correctness comparison and a performance competitor.",
    "Center rows [[1,3],[3,7]] by column means [2,5], producing [[-1,-2],[1,2]]. Each centered column sums to zero.",
    "Distance between [1,2] and [4,6] is 25. Both direct differences and the expanded identity yield 25 for this small exact case; cancellation needs an additional adversarial test.",
    "Compute centered columns;Add a constant feature;Implement distance directly;Explain expanded-form cancellation;Count a pairwise temporary;Choose a library baseline",
    "The means are two and five;A constant feature centers to zero;Sum squared coordinate differences;Subtracting nearly equal large terms loses significant digits;N by M by D elements can dominate memory;Use supported array operations before owning a kernel",
    """rows = [[1.0, 3.0], [3.0, 7.0]]
means = [sum(row[c] for row in rows)/len(rows) for c in range(2)]
centered = [[x-m for x, m in zip(row, means, strict=True)] for row in rows]
assert centered == [[-1.0, -2.0], [1.0, 2.0]]
x, y = [1, 2], [4, 6]
distance = sum((a-b)**2 for a,b in zip(x,y,strict=True))
assert distance == 25
print("CPU array reference:", centered, distance)""",
    "Centered columns and distance 25.",
)

add(
    5,
    "Randomness and reproducible experiments",
    """A pseudorandom generator is a deterministic state machine. A seed selects an initial state, while each draw advances it. Seeding inside every batch restarts that state and repeats samples. Separate generators give independent bookkeeping, although their statistical independence still depends on the generator design. Save the data-generation recipe and state when exact continuation matters.

A common seed is not a cross-library agreement on generated bytes. CPU and GPU algorithms, stream partitioning and library revisions can differ. Compare distributions and model behavior when exact streams are not promised. Reproducibility has scope: same code and environment, same backend and hardware, or cross-backend numerical agreement under tolerance. State the scope before claiming two runs reproduce one another.""",
    "Two fresh Python Random objects seeded with 7 produce the same first four draws. Drawing four more values from one object continues its stream instead of repeating it.",
    "Saving getstate before a batch and restoring it later reproduces that batch in the same Python implementation. This does not promise CuPy or TensorFlow will generate those values.",
    "Predict repeated seeding;Continue a stream;Restore generator state;Design a distribution check;Separate backend equality from exact bytes;List checkpoint randomness",
    "Repeated initialization repeats the sequence;Retain the generator between batches;Save state before drawing;Check sample mean and variance with tolerances;Use numeric or statistical contracts;Include Python, NumPy, framework, device and sampler state",
    """import random
rng = random.Random(7)
state = rng.getstate()
first = [rng.random() for _ in range(4)]
second = [rng.random() for _ in range(4)]
rng.setstate(state)
assert first == [rng.random() for _ in range(4)]
assert first != second
print("CPU RNG reference: restored batch matches; continued batch differs")""",
    "Restored batch matches and continued batch differs.",
)

add(
    6,
    "Memory pools, references and apparent leaks",
    """A caching allocator distinguishes live allocations from reserved blocks. Releasing the last array reference can make a block reusable by the pool without returning it to the driver. Device-context overhead and library workspaces add further categories. A stable reserved total after repeated equal workloads can be normal. Growing live allocations after every step suggests retained tensors, outputs or computation graphs.

A pool can reduce allocation latency and fragmentation but cannot shrink the set of live tensors required by a model. Clearing unused cache blocks is not a repair for a workload whose live set exceeds memory. Measure at consistent synchronization points, account for delayed asynchronous frees, and avoid intentionally exhausting a shared GPU to demonstrate an OOM. A bounded allocation ledger teaches the same ownership distinction safely.""",
    "An allocator reserves 1024 bytes, lends all 1024 to an array, then returns the array to its free list. Live bytes become zero while reserved bytes remain 1024.",
    "Appending a fresh 1024-byte result to a Python list each step leaves every result live. After four steps live bytes are 4096; this is different from harmless pool reuse.",
    "Compute live and reserved totals;Reuse a free block;Diagnose a retained-output list;Explain why cache clearing is insufficient;Design bounded snapshots;Separate host RAM and VRAM",
    "Free pool blocks are reserved but not live;Equal-sized reuse need not grow reserve;Drop unneeded owners and detached summaries;Live objects still require storage;Record before and after fixed small steps;Container host-memory limits do not generally cap VRAM",
    """reserved = 1024
live = 1024
live -= 1024
assert live == 0 and reserved == 1024
live += 1024
assert live <= reserved
retained = [1024 for _ in range(4)]
assert sum(retained) == 4096
print("CPU allocator model:", live, reserved, sum(retained))""",
    "Live 1024, reserved 1024, retained-output example 4096 bytes.",
)

add(
    7,
    "A timing experiment that measures the right thing",
    """A host timer around an asynchronous launch may measure enqueue latency rather than completed arithmetic. GPU events delimit work in a stream; host end-to-end timing must wait for all work needed by the output. These boundaries answer different questions. Warmup can include context creation, library initialization, compilation and allocator population, so report cold-start cost separately from repeated steady-state samples.

Use a distribution rather than one flattering minimum. Median summarizes the middle observation, while a tail statistic describes slow requests. Record sample count, workload size, dtype, transfer policy, synchronization and competing load. A speedup should compare equal outputs and equally complete work. This chapter's CPU trace arithmetic is deliberately a model: it cannot establish a GPU speedup.""",
    "A launch returns at 2 microseconds but the output finishes at 102 microseconds. A host timer stopped at return undercounts the operation by a factor of 51.",
    "For completed times [10,11,10,12,100] milliseconds, the median is 11 while the maximum is 100. Removing the last sample without explaining its cause hides tail behavior.",
    "Identify the timing boundary;Compute the median;Add transfer cost;Separate first-call compile time;Design equal-work comparison;Explain why CPU trace is not a benchmark",
    "Completion must be inside the interval when timing finished work;Median is eleven;Include both transfers for end-to-end latency;Report cold and warm distributions separately;Use same data and tolerances;The supplied times are invented teaching observations",
    """import statistics
samples = [10, 11, 10, 12, 100]
assert statistics.median(samples) == 11
submit_us, finish_us = 2, 102
assert finish_us / submit_us == 51
print("CPU trace analysis: median", statistics.median(samples), "ms; tail", max(samples))""",
    "Median 11 ms and maximum 100 ms, from synthetic trace data.",
)

add(
    8,
    "Capability and failure diagnosis",
    """Readiness is a sequence of increasingly strong claims: the package imports, the device is visible, allocation works, a compatible binary launches, execution completes, and the answer is correct. A successful earlier step cannot prove a later one. A missing device in a container may be a host/runtime exposure issue; an unsupported architecture binary is a build issue; an allocation failure may be a workload budget issue.

Fail clearly instead of silently substituting CPU execution in a GPU evidence run. A CUDA device assertion can poison later operations in that process, so the first failure and process boundary matter. Stop and report a bounded failed job rather than repeatedly retrying allocations. On unsupported hosts, use the portable reference route and keep real-device evidence pending. MPS, ROCm and other accelerator backends are alternatives with different contracts, not CUDA emulation.""",
    "A probe that imports CuPy but reports no device establishes package installation only. Mark allocation and kernel tests as not attempted.",
    "A probe that launches but returns wrong values establishes execution, then fails correctness. It must not be summarized as ready simply because the exit status was zero.",
    "Order the evidence levels;Classify missing device;Classify wrong output;Design fail-closed device selection;Explain process restart after fatal device error;Compare alternative backend labels",
    "Import, visibility, allocation, launch, completion and correctness;Inspect explicit runtime exposure and host capability;Correctness failure after execution;Require requested backend and visible device;Discard unhealthy execution context;Name CUDA, ROCm, MPS or CPU truthfully",
    """stages = ["import", "visibility", "allocation", "launch", "completion", "correctness"]
observed = {name: True for name in stages}
observed["correctness"] = False
assert not all(observed.values())
failed = next(name for name in stages if not observed[name])
assert failed == "correctness"
print("CPU diagnostic fixture: failed at", failed)""",
    "Fixture fails at correctness, not readiness success.",
)

add(
    9,
    "A kernel is a restricted parallel program",
    """A Python GPU kernel is compiled from a restricted typed subset; the Python interpreter does not run independently on every GPU thread. Host-side allocation, file access, arbitrary objects and unsupported library calls stay outside the device function. Compilation specializes supported argument types and shapes or layouts according to the selected toolchain. The same syntax can therefore have different legality on host and device.

Keep allocation and validation in a host wrapper. The kernel receives fixed buffers and scalar parameters, calculates its index, checks bounds and writes only its assigned output. That separation makes errors easier to locate. The maintained numba-cuda distribution uses the numba.cuda namespace, so the import spelling alone does not identify which package supplied the implementation. Pin and record the distribution in a prepared environment.""",
    "A host wrapper allocates an output and checks equal input lengths. A device kernel writes `y[i] = 2*x[i]` only when i is in range.",
    "A kernel that tries to open a text file violates the execution model. Move file reading to the host, convert values into a numeric buffer, then copy explicitly.",
    "Separate host and device statements;Implement the CPU oracle;Reject mismatched lengths;Move an allocation out of a kernel;Explain type specialization;List a prepared toolchain ledger",
    "Validation and allocation are host work;Map each input to twice its value;Validate before launch;Pass a preallocated buffer;Typed compiled code is not arbitrary interpreter execution;Record distribution, Python, toolkit, driver and device",
    """def affine_reference(values, scale):
    return [scale*x for x in values]
assert affine_reference([1, -2, 3], 2) == [2, -4, 6]
assert affine_reference([], 2) == []
print("CPU kernel oracle:", affine_reference([1, -2, 3], 2))""",
    "[2, -4, 6], with empty input accepted by the oracle.",
)

add(
    10,
    "One-dimensional indexing and tails",
    """A launch creates blocks containing threads. For one-dimensional indexing, global index equals block index times threads per block plus thread index. The last block often contains lanes beyond the input length. Guard every load and store that would otherwise access those lanes. Ceiling division creates enough blocks, while floor division silently omits a tail.

A grid-stride loop lets a bounded launch cover larger arrays: after processing index i, advance by the total number of launched threads. Every valid index should be visited exactly once for an elementwise operation. Test zero, one, block size minus one, block size, block size plus one and a nonmultiple. CPU scheduling models can prove the intended integer mapping, but cannot prove race freedom or GPU memory safety.""",
    "For n=10 and block size 4, three blocks launch 12 lanes. Indices 0 through 9 are valid, while 10 and 11 must not access the buffer.",
    "With six total threads and n=14, thread zero visits 0,6,12 and thread one visits 1,7,13. The union contains every valid index exactly once.",
    "Compute launch size for n=17;Trace the last block;Test zero without launching;Implement grid-stride coverage;Find floor-division data loss;Specify a sanitizer check",
    "Five blocks of four are enough;Indices 17..19 are out of range;Return empty before launch;Advance by grid size times block size;Floor division omits the final partial block;Run real kernels under supported memory checking separately",
    """n, block = 10, 4
blocks = (n + block - 1) // block
visits = [b*block+t for b in range(blocks) for t in range(block) if b*block+t<n]
assert visits == list(range(n))
strided = [i for t in range(6) for i in range(t,14,6)]
assert sorted(strided) == list(range(14))
print("CPU indexing model:", visits)""",
    "Every valid index appears exactly once.",
)

add(
    11,
    "Two-dimensional indexing and images",
    "An image has coordinates, channel conventions and storage layout. Map thread x to columns and thread y to rows only after defining that contract. A row-major scalar image uses offset `row * width + column`. A rectangular block launch requires independent checks for row and column, because the input dimensions may have different tails. Multiplying both dimensions by the same bound accidentally accepts invalid coordinates.\n\nStencil operations read neighbors, so boundary policy is part of correctness: zero padding, clamp, reflect and valid-only output produce different results. Read from an immutable input and write to a separate output unless a proven algorithm allows in-place updates. A CPU loop is useful because its coordinate meanings are visible. Do not infer coalescing or performance from that loop's execution time.",
    "For a 2 by 3 image, row 1 column 2 maps to flat offset 5. Swapping row and column changes the address and can escape the allocation.",
    "A horizontal three-point average with clamped borders maps [3,6,9] to [4,6,8]. Zero padding would produce [3,6,5], a different documented operation.",
    "Trace a rectangular tile;Calculate flat offsets;Change clamp to zero padding;Find in-place stencil contamination;Test width one;Explain row and column tail guards",
    "List rows and columns independently;Use `row * width + column`;State the changed edge semantics;Earlier writes alter later reads;Clamping repeats the only element;Both coordinates need their own upper bound",
    """values = [3,6,9]
clamped = [(values[max(0,i-1)]+values[i]+values[min(len(values)-1,i+1)])/3 for i in range(len(values))]
assert clamped == [4,6,8]
assert 1*3+2 == 5
print("CPU image reference:", clamped)""",
    "Clamped horizontal average [4, 6, 8].",
)

add(
    12,
    "Shared memory and collective responsibility",
    """Shared memory is a block-local cooperation area. Threads load assigned pieces, synchronize, then consume data another thread may have produced. A barrier is a collective obligation: all threads that participate in a block must reach compatible synchronization points. Returning early for a tail lane before a required barrier can leave other threads waiting or produce undefined behavior.

For a partial tile, valid lanes load input while invalid lanes write the operation's identity, such as zero for a sum. Every lane still reaches the barrier. The identity is algorithm-specific: minimum needs a suitably large sentinel, and a weighted average needs counts as well as sums. Shared storage does not communicate between arbitrary blocks; cross-block cooperation needs a separate algorithm or explicitly supported launch mechanism.""",
    "A four-lane tile reads [2,4,6] and stores [2,4,6,0]. All four lanes synchronize, then the block computes sum 12.",
    "Replacing the invalid lane with an early return is unsafe when later code has a block barrier. Keeping that lane active with a neutral value preserves collective participation.",
    "Choose a sum identity;Choose a minimum identity;Trace barrier participants;Repair early return;Separate block and grid scope;Design a nonmultiple test",
    "Use zero;Use a sentinel outside the valid domain or carry validity;All block lanes reach the barrier;Guard data access instead of participation;Shared memory is per block;Use n=blocksize+1 with explicit expected output",
    """tile = [2,4,6]
width = 4
shared = [tile[i] if i < len(tile) else 0 for i in range(width)]
participants = list(range(width))
assert participants == [0,1,2,3]
assert sum(shared) == 12
print("CPU cooperative model:", shared, sum(shared))""",
    "All four modeled lanes participate; padded sum is 12.",
)

add(
    13,
    "Reduction, ordering and numerical error",
    """Parallel reduction changes the grouping of additions. Real-number addition is associative; finite-precision addition generally is not. A tree reduction can produce a different result from a left-to-right loop even when both are valid implementations. Test tolerances using scale and conditioning rather than requiring arbitrary bitwise identity. Distinguish a tolerable rounding difference from a missing tail element.

Reduction also changes the parallel ownership pattern. Threads first accumulate local partials, then combine within a block, then combine block results in a later stage. A single global atomic accumulator is simpler but can contend and has nondeterministic addition order. Use a higher-accuracy CPU sum where appropriate, test cancellation-heavy inputs, and document dtype and accumulation precision.""",
    "For [1e16,1,-1e16], a naive left sum loses the one on common binary 64 arithmetic, while math.fsum preserves it. The input is intentionally cancellation-sensitive.",
    "For [1,2,3,4,5], a padded pair tree produces 15. A faulty tree that ignores the fifth value produces 10, which is an indexing bug rather than rounding noise.",
    "Compute a tree by hand;Test the odd tail;Construct cancellation;Choose absolute and relative tolerance;Compare atomics with staged reduction;Explain deterministic settings limits",
    "Combine pairs and carry the leftover value;The fifth value must survive;Use large opposite signs plus a small residual;Near zero needs meaningful absolute tolerance;Atomics trade simplicity for contention and order;Repeatability does not imply cross-hardware identical arithmetic",
    """import math
values = [1e16,1.0,-1e16]
assert math.fsum(values) == 1.0
items = [1,2,3,4,5]
while len(items)>1:
    items=[sum(items[i:i+2]) for i in range(0,len(items),2)]
assert items == [15]
print("CPU reduction reference:", math.fsum(values), items[0])""",
    "Accurate cancellation sum 1 and tail-preserving sum 15.",
)

add(
    14,
    "Atomics and contention",
    "An atomic operation updates one supported location indivisibly with respect to competing atomic operations. It does not make an entire multi-location algorithm transactional. A histogram demonstrates the need: two threads reading count 0 and both writing count 1 lose an increment. Atomic addition prevents that lost update for the counter, but every thread targeting the same bin can serialize.\n\nPrivatization reduces contention by building per-block or per-warp partial histograms and merging them later. The memory footprint grows with bin count and number of partials. Floating-point atomic addition can still vary with arrival order. Explain what is protected, what ordering is required, and whether non-atomic readers can observe partially completed results.",
    "Values [0,0,1,2,2,2] produce bins [2,1,3]. Six updates aimed at one bin would be a deliberately skewed contention case.",
    "Two local histograms [2,1,0] and [0,0,3] merge elementwise to [2,1,3]. Local updates reduce shared contention at the expense of extra storage and a merge.",
    "Trace a lost update;Compute a skewed histogram;Merge partials;Count private storage;Explain floating atomic order;Specify completion before reading",
    "Two readers can overwrite one another;Six zeros yield count 6 in bin 0;Add corresponding bins;Partials times bins times counter width;Atomicity does not fix addition order;Wait for all updates and merges before host retrieval",
    """values=[0,0,1,2,2,2]
bins=[0]*3
for value in values:
    bins[value]+=1
left,right=[2,1,0],[0,0,3]
merged=[a+b for a,b in zip(left,right,strict=True)]
assert bins == merged == [2,1,3]
print("CPU histogram oracle:", bins)""",
    "Histogram bins [2,1,3].",
)

add(
    15,
    "Python kernels meet memory performance",
    """Neighboring lanes accessing neighboring elements can be served by fewer memory transactions than widely strided accesses. Count bytes requested by useful data and compare them with the transactions the layout forces. Alignment, transaction granularity and cache behavior depend on architecture, so a simple segment model is educational rather than a complete GPU simulator.

A transpose illustrates the conflict: contiguous reads can lead to strided writes. Shared-memory tiling can reorganize the data before output. Padding may reduce bank conflicts for specific layouts, but it consumes shared capacity. Measure the entire kernel and inspect profiler counters before attributing speed to one mechanism. Increased occupancy is a means to hide latency, not an unconditional goal.""",
    "Eight four-byte lanes reading offsets 0,4,...,28 fit one aligned 32-byte segment in the simplified model. Offsets 0,32,...,224 touch eight segments.",
    "A tiled transpose first reads rows cooperatively then writes rows in the transposed coordinate system. This changes traffic organization without changing the mathematical transpose.",
    "Count touched segments;Shift the base by four bytes;Model a stride of two;Explain tiled transpose;Separate occupancy from throughput;Propose a matched profiler experiment",
    "Count distinct integer offsets divided by segment size;The shift may cross a boundary;Stride can increase transaction count;Shared storage rearranges cooperative ownership;More resident work can still compete for resources;Hold dtype shape and output fixed and inspect real counters",
    """def segments(offsets, width=32):
    return len({offset//width for offset in offsets})
contiguous=[4*i for i in range(8)]
strided=[32*i for i in range(8)]
assert segments(contiguous)==1 and segments(strided)==8
print("CPU segment model:", segments(contiguous), segments(strided))""",
    "Simplified segment counts 1 and 8, not hardware measurements.",
)

add(
    16,
    "A simulator is a debugging tool",
    """A simulator reproduces selected semantics to help inspect indexing and values without requiring the actual device. It usually does not reproduce warp scheduling, memory transactions, concurrent timing, occupancy or all synchronization defects. A serialized execution can hide a race that real concurrent threads expose. Passing a simulator therefore belongs to a different evidence category from passing hardware execution.

Keep a validation ladder: mathematical reference, CPU mapping model, compiler acceptance, real-device output, diagnostic tooling and repeated stress cases. The simulator is useful early in that ladder, especially for small inputs you can inspect by hand. Do not generate invented GPU names, bandwidth or throughput from simulator output. If a feature is unsupported by the chosen simulator, state that instead of changing the algorithm silently.""",
    "A CPU loop visiting all valid indices proves the intended index formula covers the array. It does not prove the GPU compiler generated a correct program for the target architecture.",
    "A shared counter incremented serially yields the expected count even when the corresponding parallel code lacks an atomic operation. The serial result hides the race.",
    "Classify a CPU result;Construct a race hidden by serialization;Name an unsupported feature;Design the validation ladder;Choose a tiny debugging input;Write an honest evidence label",
    "Call it CPU model or simulator;Two updates sharing a read value lose one write;Consult the pinned simulator contract;Keep stages separate;Use a nonmultiple small enough to hand-trace;GPU correctness remains pending until real execution",
    """serial_counter=0
for _ in range(2):
    serial_counter+=1
parallel_reads=[0,0]
lost_update=max(value+1 for value in parallel_reads)
assert serial_counter==2 and lost_update==1
print("CPU race illustration:", serial_counter, lost_update)""",
    "Serial count 2 versus a possible lost-update count 1.",
)

add(
    17,
    "Sharing a buffer without sharing its meaning",
    """Zero-copy interchange shares an allocation rather than creating independent values. Shape, dtype, strides, device, ownership and readiness remain part of the contract. A consumer must not outlive the allocation owner, and mutation through one view can affect another. A copied tensor has different independence from an alias even when both initially display the same numbers.

DLPack provides an interoperability protocol, not automatic gradient connectivity between arbitrary frameworks. Modern object exchange can negotiate stream readiness, while legacy capsule interfaces have their own ownership rules. Follow the pinned producer and consumer APIs. A CuPy-to-PyTorch exchange inside one process is different from separate workers that merely see the same physical GPU. The ordinary classroom cannot pass a live pointer between containers.""",
    "A Python list alias sees a mutation made through the original name. A list copy retains the old value. This CPU analogy makes the ownership question visible before introducing device buffers.",
    "A tensor passed to another array library may share bytes but not the originating autograd graph. Compute a numerical forward check and a separate gradient check rather than assuming both survive exchange.",
    "Distinguish copy and alias;Trace owner lifetime;Describe metadata requirements;Explain missing autograd edges;Name stream readiness evidence;Design mutation tests",
    "An alias shares storage;Keep the producer owner alive under the API contract;Include dtype shape strides device and offset;Storage protocols do not universally preserve graph semantics;Record the producer event or negotiated stream;Change one view and inspect the other without unsafe concurrent writes",
    """owner=[1,2,3]
alias=owner
copied=list(owner)
alias[0]=9
assert owner==[9,2,3]
assert copied==[1,2,3]
print("CPU alias reference:", owner, copied)""",
    "Alias changes to 9 while copied value remains 1.",
)

add(
    18,
    "Streams and events across library boundaries",
    """A stream orders its submitted operations, but independent streams do not inherit every dependency you intend. A consumer on stream B must wait for the producer on stream A when it reads the produced buffer. An event records a point in one stream; a wait introduces a dependency without necessarily blocking the host. Synchronizing the entire device is a useful diagnostic but may destroy intended overlap.

Interop complicates the picture because libraries can have different current-stream conventions and allocator lifetimes. A correct pointer is insufficient if its write is still in flight or its storage is recycled before a consumer finishes. Draw the dependency graph first. Then use the documented stream-aware interchange and allocation recording mechanisms of the pinned libraries. Test a non-default stream to expose assumptions hidden by default execution.""",
    "Upload precedes transform, which precedes download. Independent preprocessing for the next batch may overlap only when it does not overwrite buffers still in use.",
    "Producer A writes buffer X and records event E. Consumer B waits for E before reading X. The graph has an explicit edge even if host Python already returned from A.",
    "Draw the dependency graph;Locate a missing wait;Separate host wait and stream wait;Trace storage reuse;Design non-default stream test;Explain why global synchronization can mask bugs",
    "Edges encode actual data dependencies;Reading before the producing event is unsafe;One blocks host progress and the other queues device ordering;Do not recycle before final consumer completion;Use two streams and known values;Global waits accidentally add dependencies absent from the intended program",
    """edges=[("upload","transform"),("transform","download")]
order=["upload","transform","download"]
positions={name:i for i,name in enumerate(order)}
assert all(positions[a]<positions[b] for a,b in edges)
bad=["download","upload","transform"]
assert not all(bad.index(a)<bad.index(b) for a,b in edges)
print("CPU dependency model: ordered pipeline accepted; premature download rejected")""",
    "Valid dependency order accepted; premature download rejected.",
)

add(
    19,
    "Python controls, CUDA executes",
    """Python host code can select a device, allocate memory, prepare compiled code and submit a kernel. These are resource-management operations, distinct from device arithmetic. Low-level CUDA bindings expose handles, status values and byte counts that higher-level arrays normally hide. A kernel launch also needs argument layout, grid/block geometry and a stream, all matched to the compiled function signature.

Keep beginners on a small reviewed host wrapper before exposing every binding. The wrapper validates input, owns resources and checks both submission errors and later completion errors. CUDA Python components are independently versioned; use release-matched examples rather than copying a moving development API. For this chapter the CPU contract lab checks argument and lifetime reasoning; a prepared external CUDA Python driver lab requires its own version ledger.""",
    "A kernel expecting float32 input plus a 32-bit length cannot safely receive a float64 allocation plus a pointer where an integer belongs. Values need ABI-correct representation.",
    "Compilation success is recorded separately from launch success and readback equality. A program can compile for a device architecture absent on the current machine.",
    "Specify the kernel signature;Count allocation bytes;Classify compile versus launch errors;Design cleanup order;Explain ABI mismatch;Define release-pinned evidence",
    "Name pointer element types and scalar widths;Elements times itemsize;Compile checks source while launch tests executable compatibility;Wait for users then release resources;Wrong byte interpretation can corrupt arguments;Record component versions target architecture and exact source",
    """def validate_contract(count,itemsize,allocated):
    if count<0 or itemsize<=0 or allocated<count*itemsize:
        raise ValueError("invalid buffer contract")
validate_contract(5,4,20)
try:
    validate_contract(5,8,20)
except ValueError:
    print("CPU ABI model: insufficient float64 storage rejected")
else:
    raise AssertionError("expected rejection")""",
    "Insufficient storage for five float64 values is rejected.",
)

add(
    20,
    "CuPy raw kernels and the language boundary",
    """A raw kernel places CUDA C++ source inside a Python string and compiles it through the selected CuPy toolchain. Python controls allocation and launch; CUDA C++ controls thread-level arithmetic. The string does not gain automatic NumPy broadcasting, dtype promotion or stride support. A pointer signature and explicit length become a contract that the host must validate.

Use extern C to give the entrypoint a predictable symbol when appropriate, choose a narrow dtype contract, and guard the tail. The first invocation may compile and cache code, so separate compilation latency from warm execution. A raw kernel is attractive for a small fused operation, but a high-level CuPy expression remains a strong baseline. Existing single-source pads cannot be assumed to support arbitrary extension projects or external compiler flags.""",
    "A float32 affine kernel computes `y[i] = 2*x[i] + 1`. For [-1,0,3] it returns [-1,1,7], and the host rejects a wrong dtype instead of reinterpreting it.",
    "A launch for 257 elements using 128 threads requires three blocks. The last 127 valid-tail decisions belong in the kernel, even though the source is embedded in Python.",
    "Derive expected affine output;Calculate a nonmultiple launch;Explain symbol lookup;Reject noncontiguous input or support strides;Separate compile timing;Compare raw and library paths",
    "Apply the formula elementwise;Ceiling division gives three blocks;The compiled exported name must match;State one layout contract explicitly;Warm the same code before steady-state samples;Compare outputs and complete work under the same tolerance",
    """def affine(values):
    return [2*x+1 for x in values]
assert affine([-1,0,3])==[-1,1,7]
n,threads=257,128
assert (n+threads-1)//threads==3
assert affine([])==[]
print("CPU raw-kernel oracle:", affine([-1,0,3]))""",
    "Affine result [-1,1,7], with three blocks for 257 elements.",
)

add(
    21,
    "Choose a library before owning a kernel",
    """Library selection is an engineering decision about contracts, algorithm quality, maintenance and deployment. A tuned reduction or matrix library usually handles more shapes and architectures than a teaching kernel. A custom implementation may be justified by fusion, unusual layout or a domain-specific operation, but the benefit must survive correctness checks and end-to-end measurement.

Make a comparison ledger: supported dtypes and layouts, temporary memory, numerical behavior, warmup, concurrency, packaging and fallback. Include input sizes where launch overhead dominates and sizes where useful work dominates. A slower educational kernel can still be successful learning evidence; it should not be presented as a production improvement. Prefer the simplest implementation that satisfies the real acceptance criteria.""",
    "A library pipeline takes 8 ms of kernels and 2 ms of transfer. A custom kernel saves 2 ms but adds 3 ms of packing, so total latency worsens from 10 to 11 ms.",
    "A fused transformation reduces three launches to one and removes a large intermediate. It may win at some sizes while losing at tiny sizes where first-call compilation dominates.",
    "Compute complete latency;List a numerical contract;Add temporary memory;Identify a maintenance cost;Choose two workload sizes;Write a keep-or-replace decision",
    "Include packing and transfer;Specify shape dtype tolerance and edge behavior;Count peak simultaneously live buffers;Architecture and compiler changes need requalification;Use tiny and representative bounded inputs;Keep the library unless measured benefits justify added obligations",
    """library={"kernel":8,"transfer":2,"packing":0}
custom={"kernel":6,"transfer":2,"packing":3}
assert sum(library.values())==10
assert sum(custom.values())==11
print("CPU decision model: library",sum(library.values()),"custom",sum(custom.values()))""",
    "Library 10 and custom 11 modeled milliseconds.",
)

add(
    22,
    "Capstone: an interoperable numerical pipeline",
    """Build a small normalize-and-score pipeline with an explicit schema: rows are observations, columns are features, inputs are finite, and the chosen accumulation dtype is documented. Compute means and scales from the training fixture only, preserve constant-feature behavior and keep transformed arrays on one backend where practical. A CPU oracle establishes expected values before any optimization.

The capstone adds ownership and dependency diagrams. Show which library owns each allocation, whether each interchange aliases or copies, and when the consumer may read it. Report preparation, transfer and computation separately, then report complete latency. One backend can implement the full pipeline; introducing a second library needs a reason. The deliverable includes an unchanged baseline and an explanation of one failed optimization.""",
    "Center training rows [[1,2],[3,4]] to [[-1,-1],[1,1]]. Scoring with weights [2,-1] gives [-1,1]. The same means must be reused for later examples.",
    "If validation means are recomputed independently, the transformation changes and can leak evaluation information. Preserve fitted preprocessing state rather than hiding it in a convenient expression.",
    "Derive fitted means;Score the centered rows;Add a constant column;Draw owners and waits;Design train-validation separation;Write the capstone acceptance report",
    "Means are [2,3];Scores are [-1,1];Center to zero and define scale policy;Include producer and final-consumer lifetimes;Fit only on the training subset;Report values tolerances timing boundaries and unsupported cases",
    """rows=[[1,2],[3,4]]
means=[sum(row[c] for row in rows)/len(rows) for c in range(2)]
centered=[[x-m for x,m in zip(row,means,strict=True)] for row in rows]
scores=[sum(x*w for x,w in zip(row,[2,-1],strict=True)) for row in centered]
assert means==[2,3] and scores==[-1,1]
print("CPU pipeline oracle:",means,scores)""",
    "Fitted means [2,3] and scores [-1,1].",
)

add(
    23,
    "Device placement and one auditable training step",
    "A training step includes forward computation, scalar loss, gradients and an optimizer update. Moving only inputs to a GPU while leaving parameters on CPU violates the intended placement contract. Frameworks differ in idiom: PyTorch explicitly moves tensors and modules to a device; TensorFlow uses device scopes, placement rules and tracked variables. Inspect actual placement and fail clearly if an explicitly requested GPU is unavailable.\n\nFor a one-parameter regressor \\(y=wx\\) with mean squared error, derive the derivative before trusting autograd. Both framework lanes should reproduce this tiny update and compare to the same CPU arithmetic. Keep initialization, examples, loss reduction and learning rate identical. A correct one-step update establishes a bounded behavior, not model quality or GPU performance.",
    "With x=[1,2], target=[2,4], \\(w=0\\), mean loss is 10 and derivative is-10. SGD with learning rate 0.1 updates w to 1.",
    "Using sum loss instead of mean doubles the derivative for this batch and changes the update to 2. A faster run with a different loss normalization is not an equivalent training comparison.",
    "Derive the scalar gradient;Calculate the update;Compare sum and mean;Inspect every tensor device;Write equal PyTorch and TensorFlow contracts;Distinguish correctness and performance",
    "The mean derivative is average of 2*x*(w*x-y);Weight becomes 1;Sum scales by batch size;Include parameters inputs targets and optimizer tensors;Use identical data initial state reduction and rate;Time only after output and gradient agreement",
    """x,y=[1.0,2.0],[2.0,4.0]
w=0.0
loss=sum((w*a-b)**2 for a,b in zip(x,y,strict=True))/len(x)
grad=sum(2*a*(w*a-b) for a,b in zip(x,y,strict=True))/len(x)
w-=0.1*grad
assert loss==10 and grad==-10 and w==1
print("CPU training oracle:",loss,grad,w)""",
    "Loss 10, gradient-10, new weight 1.",
)

add(
    24,
    "Input pipelines and a hungry GPU",
    """Training is a producer-consumer pipeline: obtain examples, decode, transform, batch, transfer and compute. GPU idleness can arise because the next batch is not ready, not because the model kernel is poor. Increasing workers helps only while the bottleneck can parallelize and memory/I/O remain within budget. Prefetch queues hide latency by retaining future batches, so queue depth also consumes resources.

PyTorch's DataLoader and pinned-memory options express one host pipeline; TensorFlow's tf.data map, batch and prefetch express another. Use synthetic resident tensors as a diagnostic comparison, not as a replacement for measuring real preprocessing. Time complete steps and inspect overlap. Bound worker counts and terminate workers cleanly so a tiny lesson cannot leave a large background process tree.""",
    "A serial pipeline spends 6 ms preparing and 4 ms computing each batch, totaling 10 ms. Ideal steady-state overlap approaches 6 ms per batch after startup, not 4 ms.",
    "Prefetching three batches of 8 MiB requires at least 24 MiB for queued payloads, excluding decoder state, copies and framework overhead.",
    "Compute serial time;Compute an ideal bottleneck bound;Budget the queue;Explain pinned versus ordinary host storage;Compare resident-data diagnostic;Choose bounded worker experiments",
    "Sum stage times;The slowest stage limits steady state;Multiply batch payload by queue depth;Pinning affects transfer behavior and host resources;It isolates input cost without proving production throughput;Vary one worker or queue setting at a time",
    """prepare,compute=6,4
serial=prepare+compute
ideal=max(prepare,compute)
queued=3*8*1024*1024
assert serial==10 and ideal==6 and queued==25165824
print("CPU pipeline model:",serial,ideal,queued)""",
    "Serial 10 ms, ideal steady-state 6 ms, queued payload 25165824 bytes.",
)

add(
    25,
    "Allocations and out-of-memory reasoning",
    """Training memory contains parameters, gradients, optimizer state, saved activations, temporary workspaces and allocator reserve. These terms respond differently to batch size and precision. Adam commonly maintains two moment tensors, while mixed-precision implementations may retain additional master state. Count the actual implementation instead of applying one universal bytes-per-parameter rule.

PyTorch distinguishes allocated and reserved memory and can retain autograd graphs when losses or outputs remain attached. TensorFlow memory growth changes reservation behavior but does not make an oversized live workload fit. Both require bounded experiments with the same model and controlled batch changes. Host container limits do not generally impose a per-process GPU-memory quota. Avoid intentional OOM on shared devices and use supplied failure traces instead.""",
    "For 1000 float32 parameters, parameters, gradients and two moment arrays total 16000 bytes before activations and workspaces. This is an illustrative ledger, not a full framework prediction.",
    "Doubling batch size can approximately double saved activation payload while leaving parameter count unchanged. Retaining every step loss tensor can grow a graph independently of batch size.",
    "Build a parameter ledger;Add activation bytes;Separate reserve and live usage;Diagnose a retained graph;Explain memory growth;Design a safe batch-size experiment",
    "Count each actual array and its dtype;Use batch times elements per example times itemsize;Reserved includes reusable storage;Store detached scalar summaries when appropriate;It changes allocation policy not required live bytes;Use small fixed upper bounds and stop before exhausting hardware",
    """params=1000
state_bytes=params*4*4
activations=8*128*4
assert state_bytes==16000 and activations==4096
assert state_bytes+2*activations==24192
print("CPU memory ledger:",state_bytes,activations)""",
    "State 16000 bytes and activation 4096 bytes for the example.",
)

add(
    26,
    "Mixed precision as a numerical experiment",
    "Lower precision trades representable range and significant digits against memory and arithmetic capability. Mixed precision deliberately assigns different operations or accumulations to different dtypes. It is not the same as converting every tensor to half. Reductions, normalization and small gradients often need special care; bf16 and fp16 have different range/precision tradeoffs even though both use 16 bits.\n\nPyTorch autocast selects operation dtypes, and gradient scaling is appropriate for supported fp16 training workflows. Unscale before clipping so the clipping threshold has its intended meaning. TensorFlow mixed-precision policies and loss-scaling optimizers provide the corresponding framework mechanisms, with APIs tied to the pinned Keras release. Validate finite gradients and held-out behavior before comparing memory or speed.",
    "Multiplying a small gradient by scale 1024 before backpropagation can keep intermediate values away from underflow. Dividing the computed gradient by 1024 before the optimizer restores the intended update.",
    "Clipping a scaled gradient of 512 with threshold 1 and then unscaling produces 1/1024, not the intended clipped original gradient 0.5. Operation order changes training.",
    "Calculate scaled and unscaled values;Explain overflow detection;Place clipping correctly;Compare fp16 and bf16 concepts;Design a full-precision baseline;Record quality and throughput separately",
    "Apply inverse scale exactly once;Skip or adjust updates according to the supported scaler when nonfinite;Unscale before clipping;Their exponent and mantissa allocations differ;Use same initialization batch and loss;A speed improvement cannot excuse numerical failure",
    """gradient=0.5
scale=1024
scaled=gradient*scale
correct=min(scaled/scale,1.0)
wrong=min(scaled,1.0)/scale
assert correct==0.5 and wrong==1/1024
print("CPU scaling model:",correct,wrong)""",
    "Correct gradient 0.5; incorrect clipping order yields 0.0009765625.",
)

add(
    27,
    "Layouts, convolutions and library algorithm selection",
    """A convolution's mathematical axes are distinct from its storage order. NCHW and NHWC encode where batch, channel, height and width lie; a layout conversion is real work unless a view is valid for the consuming operator. Framework and library implementations choose algorithms based on shapes, dtype, workspace and deterministic settings. The fastest choice for one shape can lose for another.

PyTorch channels-last memory format and TensorFlow data-format conventions need separate explanations because identical axis names do not imply identical APIs. Compare outputs and gradients before timing. Include input conversion, algorithm search and workspace in the appropriate cost ledger. Do not promise a universal preferred layout or treat a profiler's kernel name as proof of mathematical equivalence.""",
    "A one-dimensional valid convolution of [1,2,3,4] with kernel [1,-1], using cross-correlation convention, gives [-1,-1,-1]. Reversing the kernel changes the sign.",
    "A layout conversion costs 2 ms and saves 1 ms per convolution. It loses for one call but amortizes over repeated calls only if the converted data can be reused correctly.",
    "State cross-correlation convention;Calculate output length;Count layout conversion cost;Compare forward and backward;Explain algorithm warmup;Design two shape cases",
    "Write the exact index formula;Valid length is input minus kernel plus one;Include conversions in complete latency;Both computations matter for training;Algorithm choice may need startup work;Use a narrow and wider batch with unchanged semantics",
    """x,k=[1,2,3,4],[1,-1]
out=[sum(x[i+j]*k[j] for j in range(len(k))) for i in range(len(x)-len(k)+1)]
assert out==[-1,-1,-1]
assert 2+1*1>2*1
assert 2+1*4<2*4
print("CPU convolution oracle:",out)""",
    "Valid cross-correlation [-1,-1,-1]; conversion amortization depends on reuse.",
)

add(
    28,
    "Profiling a complete training step",
    """A profiler records events and dependencies, but a table of operator totals is not itself the critical path. CPU preparation, copies, kernels, synchronization and logging may overlap. Summing all event durations can exceed wall time when events run concurrently. Instrumentation also adds overhead, especially with shapes, stacks or memory capture enabled.

PyTorch profiler activities and named ranges make forward, backward and update visible; TensorFlow Profiler adds graph and input-pipeline views. Capture a short bounded schedule after warmup, inspect a timeline, then test one hypothesis with ordinary timing. Preserve a trace's hardware, software and workload context. A busy GPU can spend time on wasteful copies or redundant kernels, so utilization alone is not useful-work evidence.""",
    "CPU preparation from 0 to 6 ms overlaps GPU work from 2 to 10 ms. The complete interval is 10 ms, not 14 ms obtained by summing durations.",
    "A trace with repeated host scalar reads between kernels can reveal forced synchronization. Replacing per-step logging with bounded aggregated reporting changes the host dependency path.",
    "Compute timeline wall time;Identify an overlap;Find a forced synchronization;Name profiler overhead;Propose one targeted change;Verify outside profiling",
    "Use latest completion minus first start;Intervals sharing time overlap;Materializing a device scalar can wait;Detailed tracing changes work and memory;Change only the suspected bottleneck;Rerun synchronized uninstrumented samples with equal outputs",
    """events=[("prepare",0,6),("gpu",2,10)]
summed=sum(end-start for _,start,end in events)
wall=max(end for _,_,end in events)-min(start for _,start,_ in events)
assert summed==14 and wall==10
print("CPU timeline analysis:",summed,wall)""",
    "Summed event durations 14 ms, complete interval 10 ms.",
)

add(
    29,
    "Graphs, compilation and shape behavior",
    """Tracing records a representation of operations; compilation transforms that representation; replay reuses prepared work. These are related but different. Python side effects, data-dependent control flow and changing shapes may trigger graph breaks or new specializations. A compiled path can spend substantial time before steady-state execution, which matters for short-lived jobs.

PyTorch torch.compile has guards and graph-break behavior; TensorFlow tf.function uses tracing and signatures, with XLA an additional choice. Explain them through each framework's idioms. Compare eager and compiled outputs and gradients over the accepted shape set. CUDA Graph replay has further restrictions around allocations and stable execution, so a generic graph API is not proof of CUDA Graph use.""",
    "A specialization cache sees shapes (4,8),(4,8),(8,8) and compiles twice in a simplified model. Repeating the first shape reuses its entry.",
    "A compiled model saves 1 ms per call after a 500 ms compile. More than 500 equivalent calls are needed to repay that startup cost under this simple model.",
    "Count specializations;Calculate break-even calls;Describe a graph break;Specify an accepted shape set;Compare gradients;Separate compilation and replay",
    "Two distinct shape signatures;At 500 calls costs tie and 501 starts benefiting;Unsupported dynamic behavior can leave compiled regions;List bounded dimensions and dtypes;Forward agreement does not imply backward agreement;Compilation creates code while replay reuses an execution schedule",
    """shapes=[(4,8),(4,8),(8,8)]
assert len(set(shapes))==2
compile_ms,saving_ms=500,1
assert compile_ms/saving_ms==500
print("CPU compilation model:",len(set(shapes)),"specializations; break-even",500)""",
    "Two modeled specializations;500-call break-even.",
)

add(
    30,
    "Reproducible, restartable GPU training",
    """A training checkpoint is a state contract, not simply model weights. It may include optimizer moments, learning-rate schedule, gradient scaler, RNG states, sample position and preprocessing metadata. Saving at an update boundary avoids ambiguous partially accumulated gradients unless the format explicitly handles them. The storage must outlive the disposable execution process.

PyTorch state dictionaries and TensorFlow checkpoints track state differently; both need restore tests. Compare a short uninterrupted run with an interrupted/restored run under a declared tolerance and deterministic configuration. GPU algorithm choices and hardware changes can limit bitwise equality. A model checkpoint restores numerical training state, not an arbitrary live GPU context or in-flight stream.""",
    "Momentum update \\(v=0.9v+g\\) stores v as well as weight w. Restoring w but resetting v changes the next update even with the same gradient.",
    "A checkpoint after batch 2 should resume with batch 3. Replaying batch 2 or skipping batch 3 changes data exposure and invalidates a claimed exact continuation.",
    "List checkpoint fields;Compute momentum continuation;Diagnose weights-only restart;Record sampler position;Choose a safe save boundary;Define cross-hardware tolerance",
    "Include all state affecting the next update;Carry the previous velocity;The optimizer trajectory changes;Persist the next unconsumed example or reproducible sampler state;Save after a completed consistent optimizer step;Document numerical agreement rather than universal byte equality",
    """w,v=1.0,0.5
checkpoint={"w":w,"v":v,"next_batch":3}
grad=0.2
continued=checkpoint["w"]-0.1*(0.9*checkpoint["v"]+grad)
weights_only=w-0.1*grad
assert abs(continued-0.935)<1e-12
assert continued!=weights_only
print("CPU restart model:",continued,weights_only)""",
    "Correct restored update 0.935 differs from weights-only 0.98.",
)

add(
    31,
    "Inference has a different performance contract",
    """Inference evaluates a trained model without performing optimizer updates, but framework mode still matters. Dropout and normalization can change behavior between training and evaluation. PyTorch eval and inference_mode address different concerns: module behavior versus autograd bookkeeping. TensorFlow calls need explicit inference behavior where the layer contract uses training, and exported signatures need shape and dtype definitions.

Latency per request, batch throughput, tail latency, cold start and memory are separate metrics. A large batch can improve items per second while making an interactive request wait longer. Measure output materialization when a response must be sent to a CPU client. Include model loading and compilation in a separate cold-start result instead of hiding them in warmup.""",
    "A batch of 32 completes in 8 ms, giving 4000 items per second. That does not imply a single request has 0.25 ms latency when queueing and execution require the whole 8 ms.",
    "Dropout randomly removes activations during training but should follow the framework's inference contract at evaluation. Disabling gradients alone does not necessarily switch module training behavior.",
    "Compute throughput;Separate per-item cost and request latency;Set both PyTorch inference controls;Specify TensorFlow training behavior;Measure cold start;Test an exported signature boundary",
    "Batch divided by completed seconds;Amortized cost is not latency;Use eval plus inference_mode when appropriate;Pass training=False for relevant calls;Include load and first execution separately;Reject unsupported shape or dtype explicitly",
    """batch,seconds=32,0.008
throughput=batch/seconds
amortized=seconds/batch
assert throughput==4000
assert amortized==0.00025
print("CPU serving model:",throughput,"items/s; batch latency",seconds,"s")""",
    "4000 items/s with 8 ms batch latency, not 0.25 ms request latency.",
)

add(
    32,
    "Capstone: a trustworthy GPU model report",
    """Train a tiny offline regressor or classifier using either complete framework lane. Define a held-out split before tuning. Preserve the CPU baseline, the training objective and the total number of examples. A report should separate numerical agreement, learning quality, device placement, throughput, memory and restart behavior. An optimization that drops hard examples or changes effective batch size needs a new experiment label.

Use a small bounded search over one variable at a time. Retain a failed hypothesis and explain what evidence rejected it. Save the software/hardware ledger, source revision, seeds, split, timing boundary and checkpoint test. CPU-only learners can complete the mathematical and reporting sections now, while GPU timings and placement remain pending. A capstone completion marker records learning work, not a production certification.""",
    "Predictions [1,2,3] against targets [1,3,2] have MSE 2/3. Record this validation metric separately from the training loss.",
    "A candidate that runs twice as fast but evaluates only half the held-out examples cannot use the original metric denominator. Compare the same examples and preserve sample accounting.",
    "Compute the validation metric;Write the sample ledger;Define a memory budget;Design a restart comparison;Choose one optimization;State pending hardware evidence",
    "Mean squared errors 0,1,1 give 2/3;Track train validation and consumed counts;Include weights state activations and reserve separately;Compare uninterrupted and resumed steps;Tie it to a measured bottleneck;Mark CPU and GPU results independently",
    """predictions,targets=[1,2,3],[1,3,2]
mse=sum((p-t)**2 for p,t in zip(predictions,targets,strict=True))/len(targets)
assert abs(mse-2/3)<1e-12
report={"backend":"CPU reference","examples":len(targets),"mse":mse,"gpu_verified":False}
assert report["examples"]==3 and not report["gpu_verified"]
print(report)""",
    "Three examples, MSE 2/3, GPU verification explicitly false.",
)

add(
    33,
    "A Python API over a CUDA C++ operator",
    """A framework operator is more than a callable function. Its contract includes name, argument and return types, dtype, shape, device, layout, aliasing and mutation. Dispatch chooses an implementation for the backend; compilation systems may also need metadata behavior that predicts output structure without running real data. A host wrapper must validate unsupported cases before handing pointers to a kernel.

PyTorch custom operator registration and TensorFlow REGISTER_OP/OpKernel follow different integration mechanisms and require independently prepared builds. Neither is implied by a Python pad accepting a source string. Use a fixed reviewed project with pinned compiler, toolkit and framework ABI. First compare a fused affine-plus-ReLU forward against the native expression, then verify invalid inputs and non-default stream behavior. Backward is a separate contract taught next.""",
    "For \\(y=\\max(0,2x+1)\\), inputs [-2,0,3] yield [0,1,7]. A custom kernel must match the chosen dtype and define behavior at the activation boundary.",
    "A raw pointer kernel may return correct values for contiguous tensors but fail on a transposed view. Either implement strides or reject/pack the input explicitly and report copy cost.",
    "Write the operator schema;Derive output values;Specify aliasing;Reject unsupported layout;Compare framework registration mechanisms;Define fixed-project build evidence",
    "Name tensor inputs scalar parameters and output;Apply affine then clamp;State whether output shares storage;Check before launch or use deliberate packing;Each framework needs its own registered implementation;Record build ABI architecture and real forward tests",
    """def fused_reference(values,scale=2.0,bias=1.0):
    return [max(0.0,scale*x+bias) for x in values]
assert fused_reference([-2,0,3])==[0,1,7]
assert fused_reference([])==[]
print("CPU custom-op oracle:",fused_reference([-2,0,3]))""",
    "Fused affine-ReLU output [0,1,7].",
)

add(
    34,
    "Backward is part of the operator",
    "A backward implementation computes a vector-Jacobian product: the upstream gradient weights each output's contribution to each input. For an elementwise affine-ReLU \\(y=\\max(0,ax+b)\\), the derivative with respect to x is a where ax+b is positive and the chosen boundary derivative elsewhere. The derivative with respect to shared a or b is a reduction over elements, not an elementwise output of the same shape.\n\nPyTorch autograd registration and TensorFlow custom-gradient or registered-gradient mechanisms differ, but both need mathematical tests. Finite differences approximate derivatives away from nondifferentiable boundaries; double precision and carefully chosen perturbations reduce numerical noise. Framework registration checks validate integration properties, not every derivative. State whether higher-order gradients and unusual layouts are supported.",
    "At x=2 with \\(a=2,b=1\\), y=5 and derivative \\(dy/dx=2\\). A central finite difference around 2 agrees within numerical tolerance.",
    "At \\(x=-0.5\\), the preactivation is zero. A central difference straddles the kink and need not equal the framework-selected subgradient, so test the documented boundary separately.",
    "Derive the input VJP;Derive bias gradient;Run finite differences away from a kink;Explain a failed kink gradcheck;Specify higher-order support;Compare each framework reference",
    "Multiply upstream by a and the positive mask;Sum masked upstream values;Use symmetric perturbations and a suitable epsilon;The derivative is not unique at the boundary;Do not imply it from first-order success;Compare native forward and backward independently",
    """def f(x):
    return max(0.0,2*x+1)
x,eps=2.0,1e-5
numeric=(f(x+eps)-f(x-eps))/(2*eps)
assert abs(numeric-2.0)<1e-8
upstream=[1,3]
mask=[0,1]
bias_grad=sum(g*m for g,m in zip(upstream,mask,strict=True))
assert bias_grad==3
print("CPU gradient oracle:",numeric,bias_grad)""",
    "Finite-difference derivative approximately 2 and bias VJP 3.",
)

add(
    35,
    "Memory-saving training techniques",
    """Gradient accumulation splits an effective batch across microbatches and delays the optimizer step. To match a full mean-loss gradient, weight each microbatch by its number of examples divided by the total. Equal division by microbatch count works only when sizes are equal. Batch-dependent layers, random state and optimizer timing can still break equivalence.

Activation checkpointing saves selected intermediates and recomputes others during backward. It exchanges compute for memory rather than eliminating arithmetic. PyTorch checkpoint utilities and TensorFlow recomputation mechanisms have framework-specific state and randomness rules. Frozen parameters still occupy storage, and upstream activations may remain necessary for trainable downstream components. Compare updates first, then measured peak memory and time.""",
    "Microbatch mean gradients 2 and 8 over sizes 3 and 1 combine to\\((3\\times2+1\\times8)/4=3.5\\). Averaging the two means gives 5, which is wrong for the effective batch.",
    "Checkpointing reduces retained activations by an illustrative 20 MiB but adds another forward computation. Its benefit depends on memory pressure and the recomputation cost.",
    "Compute weighted accumulation;Find unequal-batch normalization error;Place optimizer steps;Explain checkpoint recomputation;Account for frozen weights;Design equal-update tests",
    "Use sample-count weights;Do not average unequal means blindly;Step once per effective batch;Recompute discarded intermediates during backward;Freezing gradients does not remove parameters;Match data order loss reduction state and random behavior",
    """sizes,means=[3,1],[2.0,8.0]
weighted=sum(n*g for n,g in zip(sizes,means,strict=True))/sum(sizes)
wrong=sum(means)/len(means)
assert weighted==3.5 and wrong==5
print("CPU accumulation oracle:",weighted,wrong)""",
    "Correct weighted gradient 3.5 versus incorrect 5.",
)

add(
    36,
    "Attention as GPU work",
    """Attention forms query-key scores, applies scaling and masks, normalizes with softmax, and combines values. Materializing a full sequence-by-sequence score matrix creates a quadratic intermediate. Fused algorithms can reorganize computation to reduce memory traffic while preserving the intended operation, but selected backend, dtype, head size and mask affect available implementations.

Stable softmax subtracts each row's maximum before exponentiation. A causal mask prevents positions from attending to later tokens; a padding mask excludes invalid positions. Define behavior for fully masked rows rather than accepting NaNs by accident. PyTorch scaled-dot-product attention and TensorFlow attention paths need actual backend inspection and forward/backward comparison. An API name alone cannot prove a particular fused kernel ran.""",
    "For scores [1000,1001], direct exponentiation can overflow. Subtracting 1001 yields [-1,0] and well-behaved probabilities summing to one.",
    "A causal row for token 0 can see only token 0. Masking later positions before normalization gives weight 1 to the sole valid position.",
    "Compute stable softmax;Draw a causal mask;Count score-matrix bytes;Define fully masked behavior;Compare fused and reference gradients;Separate backend selection from API name",
    "Subtract the maximum first;Allow key positions no greater than query position;Batch times heads times sequence squared times itemsize;Reject or use documented zero-output behavior;Check masks dtypes and tolerances;Inspect supported runtime evidence rather than guessing",
    """import math
scores=[1000.0,1001.0]
shift=max(scores)
exp=[math.exp(x-shift) for x in scores]
weights=[x/sum(exp) for x in exp]
assert abs(sum(weights)-1)<1e-12
assert weights[1]>weights[0]
causal=[[int(j<=i) for j in range(3)] for i in range(3)]
assert causal==[[1,0,0],[1,1,0],[1,1,1]]
print("CPU attention oracle:",weights,causal)""",
    "Stable probabilities sum to 1; lower-triangular causal mask.",
)

add(
    37,
    "LLM training, fine-tuning and GPU memory",
    """Full fine-tuning updates all selected model parameters. Adapter methods train additional small structures while retaining the base weights. Low-rank updates factor a matrix update into two thinner matrices, reducing trainable parameter count, but the base model still occupies memory and activations still flow through it. Optimizer membership should match the intended trainable set exactly.

Sequence length, padding, batch size, precision, saved activations and optimizer state can dominate different workloads. Build a tiny transformer locally with synthetic tokens before considering downloads. Compare full and adapter training on a held-out synthetic task with equal data accounting. Parameter efficiency is not a guarantee of lower total runtime memory or better quality. Both PyTorch and TensorFlow lanes should report their actual variable census and optimizer state.""",
    "A 1024 by 1024 matrix has 1,048,576 parameters. A rank 8 update uses\\(8(1024+1024)=16{,}384\\) trainable parameters while the original matrix remains present.",
    "Freezing the base matrix removes its gradient and optimizer-update requirement under the chosen implementation, but downstream training can still need intermediate activations.",
    "Count low-rank parameters;Include base storage;Inspect optimizer membership;Compare sequence-length budgets;Design tiny offline training;Define held-out evaluation",
    "Rank times sum of dimensions;Base parameters are not deleted;Only intended trainable tensors belong in optimizer state;Attention intermediates and caches grow with sequence geometry;Use generated tokens and bounded steps;Keep validation separate from fitting and tuning",
    """rows,cols,rank=1024,1024,8
base=rows*cols
adapter=rank*(rows+cols)
assert base==1048576 and adapter==16384
assert base+adapter>base
print("CPU adapter ledger:",base,adapter,"parameters")""",
    "Base 1,048,576 and adapter 16,384 parameters.",
)

add(
    38,
    "LLM inference, KV caches and precision",
    """Autoregressive generation separates prefill, which processes an input sequence, from decode, which adds one token repeatedly. A key-value cache stores previous attention projections so decode can reuse them. Cache size grows with layers, batch, sequence length, key/value head count, head dimension and element width. Grouped-query architectures require the actual KV-head count, not necessarily the query-head count.

Weight quantization changes one memory category; it does not automatically quantize the cache or every activation. Educational rounding examples demonstrate error but do not establish packed low-bit execution. Compare cached and uncached logits at each step, bound generation length, and measure prefill and token latency separately. State positional-encoding and mask conventions when testing cache equivalence.""",
    "For 2 layers, batch 1, sequence 16,4 KV heads, head dimension 8 and 2-byte elements, keys and values consume 4096 bytes in the simple dense model.",
    "Doubling sequence length doubles this cache payload even if model weights are unchanged. Reducing weight precision alone leaves this term unchanged.",
    "Derive cache bytes;Double the sequence;Distinguish query and KV heads;Compare cached logits;Separate prefill and decode timing;Label fake versus real quantization",
    "Multiply two for keys and values then all dimensions and width;Cache grows linearly in stored positions;Use the model actual KV layout;Compare each bounded step within tolerance;They stress different operation shapes;A rounding simulation is not a deployed quantized kernel",
    """layers,batch,seq,heads,dim,width=2,1,16,4,8,2
cache=2*layers*batch*seq*heads*dim*width
assert cache==4096
assert 2*layers*batch*(2*seq)*heads*dim*width==8192
print("CPU KV-cache ledger:",cache,"bytes")""",
    "4096 bytes, doubling to 8192 at twice the sequence length.",
)

add(
    39,
    "Multi-GPU training on one host",
    """Data parallelism gives replicas different examples, computes gradients and combines those gradients before consistent updates. Rank identifies a participant; a process often owns one GPU. Correctness depends on sample partition, loss normalization, collective order and optimizer state, not merely launching more processes. Different effective batch sizes change the optimization problem.

PyTorch DistributedDataParallel typically uses one process per device and a suitable collective backend. TensorFlow MirroredStrategy coordinates replicas with its own distribution and loss-scaling conventions. Test against a single-device effective-batch reference. Unequal final batches require deliberate handling; repeated examples from padding must be counted. A CPU weighted-average model teaches semantics but cannot validate NCCL, GPU peer access or communication performance.""",
    "Two equal-sized replicas with mean gradients 2 and 4 combine to 3. A single-device batch containing their examples should produce the same mathematical gradient.",
    "With replica sample counts 3 and 1 and gradients 2 and 4, the global sample mean is 2.5, not 3. Normalization must match the intended data accounting.",
    "Compute equal-replica average;Handle unequal counts;Assign rank and device;Check complete sample coverage;Design collective failure handling;Compare framework distribution contracts",
    "Average equal contributions;Weight by examples or use a documented equal-batch policy;Use explicit one-process ownership where required;No unintended omissions or duplication;Bound communication and terminate all owned ranks;Each framework needs its own integration test",
    """counts,gradients=[3,1],[2.0,4.0]
weighted=sum(n*g for n,g in zip(counts,gradients,strict=True))/sum(counts)
assert weighted==2.5
assert sum(gradients)/2==3.0
print("CPU distributed-gradient oracle:",weighted)""",
    "Global example-weighted gradient 2.5.",
)

add(
    40,
    "Capstone: an evidence-based GPU systems decision",
    """A systems decision balances correctness, model quality, latency, throughput, memory, cost and maintainability. Start with explicit constraints and a reproducible baseline. Choose an optimization tied to a measured bottleneck: input preparation, transfer, arithmetic, memory traffic or communication. A custom kernel and multiple GPUs are optional solutions, not achievements that must be forced into every project.

Retain source, environment, data recipe, checkpoint and rollback instructions. Report distributions and failure behavior, including unsupported shapes and resource limits. An acceptance matrix should show which claims have live evidence and which are still hypotheses. CPU-only work can produce a valuable model and decision report while honestly leaving GPU execution and deployment qualification open.""",
    "CandidateA uses 8 GiB and meets a 20 ms latency target; candidate B uses 12 GiB on an 8 GiB device. B is infeasible regardless of its optimistic kernel timing.",
    "CandidateC meets latency but reduces held-out accuracy below the required threshold. Performance and quality constraints both belong in acceptance.",
    "Write three constraints;Filter infeasible candidates;Choose a bottleneck hypothesis;Preserve rollback;Design failure tests;State evidence gaps",
    "Use measurable limits with units;Reject memory and quality violations before speed ranking;Tie a change to a trace;Keep the unchanged baseline runnable;Test bounded invalid inputs and resource refusal;Pending GPU validation must remain visible",
    """candidates=[{"name":"A","memory":8,"latency":18,"quality":0.95},{"name":"B","memory":12,"latency":10,"quality":0.96},{"name":"C","memory":6,"latency":12,"quality":0.80}]
valid=[c["name"] for c in candidates if c["memory"]<=8 and c["latency"]<=20 and c["quality"]>=0.9]
assert valid==["A"]
print("CPU decision fixture:",valid)""",
    "Only candidate A satisfies all three constraints.",
)

add(
    41,
    "Distributed training beyond one host",
    """Across hosts, the network joins GPU compute and storage as a first-class resource. A rendezvous establishes participants; collectives require compatible ordering and membership. Data parallelism replicates parameters, tensor parallelism partitions operations, pipeline parallelism partitions layers, and state sharding distributes selected model or optimizer state. Their communication patterns differ.

Stragglers delay synchronized steps. Worker failure requires a coordinated stop or a deliberately implemented recovery protocol; independently retrying one rank can hang the rest. Checkpoints need a consistent global boundary and data-position contract. This lesson uses diagrams and synthetic timelines by default. Actual multi-host work requires explicitly owned hosts, bounded access, suitable networking and separate PyTorch/TensorFlow qualification. Nothing in the browser creates a cluster.""",
    "Three ranks taking 10,12 and 30 ms before a barrier yield at least 30 ms compute-phase latency, even though their average is 17.3 ms.",
    "A checkpoint assembled from rank 0 at step 10 and rank 1 at step 11 is not a coherent global state unless a protocol explicitly reconciles that difference.",
    "Compute barrier time;Compare parallelism types;Diagnose a missing rank;Define checkpoint consistency;Budget communication;Design owned-host cleanup",
    "The slowest rank controls the barrier;Separate model replication and operation/layer/state partition;Bound waits and stop the owned job;Use a documented common update boundary;Count bytes and frequency per collective;Terminate only declared job resources and preserve checkpoints",
    """rank_ms=[10,12,30]
assert max(rank_ms)==30
steps={"rank0":10,"rank1":11}
consistent=len(set(steps.values()))==1
assert not consistent
print("CPU distributed trace: barrier",max(rank_ms),"ms; checkpoint consistent",consistent)""",
    "Barrier 30 ms; mixed-step checkpoint rejected.",
)

add(
    42,
    "A modern tile-based kernel DSL",
    """A thread-level model assigns scalar work to individual threads. A tile-level language describes a block of data and lets a compiler choose lower-level distribution and instructions. The abstraction can simplify matrix and reduction kernels, but layout, memory traffic, masks and numerical behavior still matter. Different DSL releases support different devices and operations.

Use a selected prepared Triton or CUDA tile implementation only after recording its compiler and architecture requirements. Compare the same mathematical operation against a library and the earlier thread-level reference. A masked tile must protect every invalid load and store at the boundary. This elective includes a CPU tiling model; the ordinary Python worker does not acquire a DSL compiler or GPU merely by opening the guide.""",
    "A vector of 10 elements partitioned into tiles of 4 has tiles [0..3],[4..7],[8,9]. The last tile has two valid lanes and two masked lanes.",
    "Changing tile size may improve reuse while increasing register pressure. The direction of the performance change must come from device evidence, not tile size alone.",
    "Create tile boundaries;Mask a final tile;Compare thread and tile abstractions;State compiler requirements;Design a library comparison;Explain a resource tradeoff",
    "Use half-open intervals;Guard both input and output;The compiler owns more mapping decisions in a tile DSL;Record exact release and supported architecture;Match data shape dtype and timing boundary;Larger tiles can increase live state and reduce concurrency",
    """n,tile=10,4
blocks=[list(range(start,min(start+tile,n))) for start in range(0,n,tile)]
assert blocks==[[0,1,2,3],[4,5,6,7],[8,9]]
assert [i for block in blocks for i in block]==list(range(n))
print("CPU tile model:",blocks)""",
    "Three tiles cover ten elements exactly once.",
)

add(
    43,
    "Python-accessible CUDA library algorithms",
    """Library algorithms expose more than an operation name. Sorting needs comparator and stability semantics; reductions need identity and dtype rules; matrix operations need layout and leading dimensions; FFTs need normalization and transform conventions. Some APIs create reusable plans or request temporary storage. Plan lifetime, workspace ownership and stream association affect both correctness and performance.

Choose a small release-pinned library family instead of installing every package. Compare an educational reference and a prepared library result on tiny fixtures, including empty or rejected cases and duplicate keys. Reuse plans only when their shape/dtype contract permits. Report plan creation separately from repeated execution. Python accessibility does not eliminate CUDA resource and compatibility requirements.""",
    "A stable sort of [(2, A),(1, B),(2, C)] by key retains A before C among equal keys. An unstable sort may legally change that relative order.",
    "A matrix multiply output shape follows contracted dimensions: a 2 by 3 matrix times 3 by 4 gives 2 by 4. A plan prepared for a different dtype or shape cannot be reused blindly.",
    "Trace stable sorting;Specify duplicate semantics;Calculate output shape;Account for temporary storage;Separate plan creation;Choose a release-specific contract",
    "Equal-key records preserve input order;State whether order is guaranteed;Outer dimensions become output;Workspace can affect peak live memory;Measure cold setup and steady execution;Use the documentation matching the prepared package",
    """records=[(2,"A"),(1,"B"),(2,"C")]
ordered=sorted(records,key=lambda row:row[0])
assert ordered==[(1,"B"),(2,"A"),(2,"C")]
a,b=(2,3),(3,4)
assert a[1]==b[0]
print("CPU library contracts:",ordered,"matrix output",(a[0],b[1]))""",
    "Stable duplicate order and matrix output shape (2,4).",
)

add(
    44,
    "Accelerator-aware data science pipelines",
    """Tabular acceleration connects schemas, null masks, columnar storage, preprocessing and model inputs. RAPIDS cuDF provides GPU dataframe operations; it is not the Spark scheduling engine. A single-process cuDF pipeline differs from the cuDF plugin that replaces supported Spark physical operators. Both require compatible NVIDIA execution for their GPU paths, and both can spend time moving data across boundaries.

Preserve null semantics, category mappings and row identity when converting a dataframe into dense tensors. A missing value is not always a NaN, and an integer nullable column may require a validity mask. Fit encoders on training data and define unknown-category behavior. Compare with a CPU dataframe or simple Python oracle before measuring. The Spark specialization follows this chapter for distributed plans, resource scheduling and operations.""",
    "Rows [(A,2),(A, null),(B,5)] grouped by category have non-null sums A=2 and B=5 under the declared skip-null rule. Counting rows and counting non-null values are different.",
    "Encoding categories A->0, B->1 then seeing C requires an explicit unknown policy. Relearning category IDs independently in another partition can corrupt model features.",
    "Compute grouped sums;Distinguish null and zero;Define category mapping;Preserve row identity;Count conversion bytes;Distinguish cuDF from Spark acceleration",
    "Ignore null only under the stated aggregate contract;Zero contributes a numeric value;Fit once and reserve an unknown category if needed;Carry a stable key through transformations;Count masks dtype conversions and host-device copies;One is a dataframe library and the other integrates Spark physical execution",
    """rows=[("A",2),("A",None),("B",5)]
totals={}
counts={}
for key,value in rows:
    totals.setdefault(key,0)
    counts[key]=counts.get(key,0)+1
    if value is not None:
        totals[key]+=value
assert totals=={"A":2,"B":5} and counts["A"]==2
print("CPU dataframe oracle:",totals,counts)""",
    "Grouped sums A 2, B 5 and row count A 2.",
)

add(
    45,
    "Deployment runtimes and engine building",
    """Export translates a model into an interchange or runtime representation. Building an execution engine chooses supported implementations for target shapes, precision and hardware. Successful export is weaker evidence than successful execution, and one successful shape is weaker than a complete supported-shape contract. Calibration for selected quantization workflows must use representative data separate from evaluation.

An optional TensorRT or another prepared runtime has its own operator, platform and version constraints. Engine caches may depend on hardware, toolkit and runtime versions. Preserve the source model and build recipe, then compare outputs and task quality over a bounded shape set. Report engine build, cold start and warm inference separately. The classroom's default CPU workers do not imply an engine builder is installed.""",
    "A deployment accepts batch sizes 1 through 8 and sequence lengths up to 32. Batch 9 should be rejected or handled by a separately documented path rather than silently truncating input.",
    "A lower-precision engine that passes shape checks but changes classification quality beyond tolerance fails the application contract despite compiling successfully.",
    "Define the shape envelope;Reject an invalid request;Separate export build and execution;Choose calibration data;Record engine compatibility;Compare task quality",
    "List bounded dimensions and dtypes;Return a clear error before unsafe execution;Each is a separate evidence step;Use representative training-side data without evaluation leakage;Store runtime device and build metadata;Evaluate the same held-out examples and metrics",
    """def accepted(batch,sequence):
    return 1<=batch<=8 and 1<=sequence<=32
assert accepted(1,32)
assert not accepted(9,16)
assert not accepted(2,0)
print("CPU deployment contract: supported shapes accepted; invalid shapes rejected")""",
    "Declared shape envelope enforced.",
)

add(
    46,
    "Custom operator packaging and binary portability",
    """A native extension package combines Python compatibility, framework ABI, host compiler, CUDA toolkit, architecture targets and system libraries. A wheel filename alone does not promise every GPU can execute its embedded code. Native device binaries target architectures; intermediate representations can provide a JIT path only within supported compatibility rules. Record what was built and what was actually executed.

Use a fixed project with reviewed build dependencies and reproducible metadata. Test import, operator registration, forward/backward behavior and unsupported-input failure in each declared environment. Keep build-time downloads explicit and separate from classroom reading. The browser's single-file pad does not become a general package manager. Publishing packages or using external registries is a separately authorized workflow.""",
    "A package can import because its host shared library loads, then fail when the first kernel lacks compatible device code. Import is only the first qualification step.",
    "Two environments with the same Python version but different framework ABI or CUDA assumptions may need separate builds. Preserve a matrix rather than claiming universal portability.",
    "List compatibility axes;Separate import and execution;Explain native code versus intermediate code;Design a build ledger;Test unsupported dtype;Define a package release gate",
    "Python framework compiler toolkit OS architecture and driver;Only real kernel work tests the device path;Their portability rules differ;Record inputs versions hashes and flags in a reviewed recipe;Reject with a clear contract error;Require functional tests in every declared supported environment",
    """required={"python","framework","toolkit","host_arch","device_targets"}
manifest={"python":"pinned","framework":"pinned","toolkit":"pinned","host_arch":"declared","device_targets":["qualified separately"]}
assert set(manifest)==required
assert "driver" not in manifest
print("CPU package ledger: build metadata complete; runtime driver still separate")""",
    "Build ledger completeness does not establish runtime driver or GPU acceptance.",
)

add(
    47,
    "A profiler-guided kernel case study",
    """Choose one operation, such as a bounded LayerNorm or segmented reduction, and derive an operation-count and byte-traffic model. Arithmetic intensity is operations divided by transferred bytes. A bandwidth-limited hypothesis suggests reducing traffic; a compute-limited hypothesis suggests improving arithmetic utilization. These bounds are simplified and need real profiler evidence for the target shape.

Change one mechanism at a time and keep an unchanged library baseline. Resource usage can reverse an apparent optimization: extra fusion may increase register pressure, and a larger tile may reduce active blocks. Test numerical behavior and boundary shapes after every change. Include a failed optimization because explaining why a hypothesis failed is part of independent performance engineering.""",
    "An operation performs 4096 arithmetic operations while moving 8192 bytes, giving intensity 0.5 operations/byte in the model. This low ratio motivates examining memory traffic.",
    "Fusion removes one intermediate write and read but raises register use. The expected traffic saving is a hypothesis; actual throughput might worsen for some shapes.",
    "Calculate arithmetic intensity;Count eliminated bytes;Name a profiler counter;Design one controlled change;Test a boundary shape;Explain a failed optimization",
    "Divide operations by bytes;Count both avoided write and read;Choose a relevant measured traffic or stall metric;Keep all other settings fixed;Use a nonmultiple and a tiny case;Relate observed resource use and timing to the rejected hypothesis",
    """operations,bytes_moved=4096,8192
intensity=operations/bytes_moved
intermediate=1024*4
saved=2*intermediate
assert intensity==0.5 and saved==8192
print("CPU roofline inputs:",intensity,"operations/byte; removable traffic",saved)""",
    "Intensity 0.5 and hypothetical 8192 bytes removable traffic.",
)

add(
    48,
    "Reproducible GPU performance review",
    """A performance review should let another person reproduce the computation, understand the comparison and identify its limits. Record source revision, hardware, driver, library versions, workload distribution, dtype, precision policy, warmup, synchronization and competing load. Preserve raw bounded timing samples instead of only the best number. Compare complete equivalent work and quantify variation.

Review correctness evidence before speed claims, including edge cases, error tolerance and any changed algorithm. Separate kernel-only time, transfers, preprocessing, compilation and end-to-end latency. Document unavailable platforms honestly. A result from one device is a result from that device; it does not establish a universal architecture ranking. The final artifact should make an independent reviewer able to say which claim is supported and which experiment is still missing.""",
    "Baseline samples [10,11,9] and candidate [8,8,9] have medians 10 and 8. The median speedup is 1.25, with only three samples and explicitly limited confidence.",
    "If candidate output differs beyond tolerance, the speed ratio remains a measurement of different behavior and cannot be accepted as a valid optimization.",
    "Calculate median speedup;Preserve raw observations;Check equivalence first;Separate cold and warm costs;Write supported platform scope;Prepare a reproducibility checklist",
    "Divide baseline median by candidate median;Keep samples and conditions;Fail correctness before performance acceptance;Report both boundaries;Name exactly tested hardware and software;Include source data commands versions metrics and unresolved limits",
    """import statistics
baseline,candidate=[10,11,9],[8,8,9]
speedup=statistics.median(baseline)/statistics.median(candidate)
assert speedup==1.25
report={"fixture":"synthetic CPU timing analysis","median_ratio":speedup,"gpu_benchmark":False}
print(report)""",
    "Synthetic median ratio 1.25; explicitly not a GPU benchmark.",
)
