"""Measured execution, layout semantics, capstones and explicit hardware limits."""

from model import Unit, case

UNITS = [
    Unit(
        25,
        "Benchmark completed work and separate its costs",
        "advanced",
        (24,),
        ("asynchronous dispatch", "synchronization", "cold call", "warm call"),
        "Produce a bounded timing record that distinguishes compilation, warm execution and data placement without asserting a universal speedup.",
        r"""A timer around a JAX call can measure dispatch rather than completed numerical work. Results may represent work that is still executing. Synchronizing the timed result with block_until_ready establishes the completion boundary needed for a meaningful elapsed-time observation.

The first invocation of a jitted function can include tracing and compilation. Later compatible calls in the same process can reuse the compiled form. Combining those observations into one unlabeled average hides different costs. Likewise, constructing inputs or transferring data inside one measurement but outside another makes the comparison answer a different question.

Use a fixed shape, dtype and input policy, verify the output, then collect repeated completed-work measurements. Report the individual observations or a declared summary rather than selecting only the fastest-looking number. Small workloads can be dominated by dispatch and timing overhead. A larger workload may tell a different story; neither case establishes a universal JAX or accelerator advantage.

The classroom gives each Run a fresh process, so in-memory compilation reuse is studied within one submitted program. Pressing Run twice does not demonstrate a persistent compilation cache. This CPU worker also does not establish GPU/TPU transfer cost, memory use or throughput. Those require separately qualified devices and measurement tools.

Profiling is another evidence layer. A numerical timing says how long a measured boundary took. A trace can expose operations, synchronization and host/device activity, but saving and viewing trace files requires an artifact workflow that the ordinary single-source pad does not provide. The default example therefore emits bounded numerical timing records without starting a profiler server.""",
        r"""For measured repeats \(t_1,\ldots,t_r\), retain the count, units and work boundary with any summary. A speed ratio \(t_A/t_B\) is interpretable only when the two measurements include equivalent work and correct results. Timing uncertainty and background activity can dominate tiny computations. The assertions here require finite nonnegative times and correct outputs, not a predetermined ordering between cold and warm measurements.""",
        """from time import perf_counter


def product(values):
    return values @ values.T


def completed_times(function, argument, repeats):
    if type(repeats) is not int or repeats <= 0:
        raise ValueError("positive integer repeats required")
    times = []
    result = None
    for _ in range(repeats):
        start = perf_counter()
        result = function(argument)
        result.block_until_ready()
        times.append(perf_counter() - start)
    return result, np.asarray(times)

values = jnp.arange(256., dtype=jnp.float64).reshape(16, 16) / 256.""",
        (
            case(
                "Measure first and warm calls separately",
                "Time one first invocation and three later invocations of the same fresh jitted product.",
                "Correct products and two labeled timing groups; no required speed ordering.",
                "Every timer ends after synchronization. The first group can include compilation, while the warm group reuses the same callable and signature.",
                "compiled = jax.jit(product)\nfirst, cold = completed_times(compiled, values, 1)\nlast, warm = completed_times(compiled, values, 3)\nclose(first, np.asarray(values) @ np.asarray(values).T)\nclose(last, first)\nassert cold.shape == (1,) and warm.shape == (3,)\nassert np.isfinite(cold).all() and np.isfinite(warm).all()\nassert (cold >= 0).all() and (warm >= 0).all()\nprint({'first_seconds': cold.tolist(), 'warm_seconds': warm.tolist()})",
                "Do not stop the timer at dispatch.",
            ),
            case(
                "Keep placement outside a compute-only boundary",
                "Explicitly place a host array, synchronize it, then time the compiled computation.",
                "Matching product values and a finite completed-work time.",
                "This defines a compute-only measurement. A complete application benchmark would separately include its required input and output transfers.",
                "host = np.arange(256., dtype=np.float64).reshape(16, 16) / 256.\nplaced = jax.device_put(host)\nplaced.block_until_ready()\nresult, times = completed_times(jax.jit(product), placed, 1)\nclose(result, host @ host.T)\nassert np.isfinite(times).all()",
                "Declare what the timer intentionally includes.",
            ),
        ),
        (
            case(
                "Reject an empty timing sample",
                "Request zero repetitions.",
                "ValueError.",
                "An empty list does not support a meaningful elapsed-time summary.",
                "try:\n    completed_times(product, values, 0)\nexcept ValueError:\n    pass\nelse:\n    raise AssertionError('empty timing accepted')",
                "Validate the measurement plan before running work.",
            ),
            case(
                "Retain the shape contract",
                "Inspect the result shape of a completed product.",
                "(16,16).",
                "A fast result with the wrong output contract is not a performance success.",
                "result, times = completed_times(jax.jit(product), values, 1)\nassert result.shape == (16, 16)",
                "Correctness precedes timing interpretation.",
            ),
            case(
                "Compare eager and compiled outputs",
                "Compute the same product through eager and jitted functions.",
                "Matching numerical results.",
                "This comparison fixes values and dtype before considering any timing difference.",
                "close(product(values), jax.jit(product)(values))",
                "Do not change input construction between paths.",
            ),
            case(
                "Report a declared summary",
                "Collect three completed times and calculate the median.",
                "Finite median within the observed minimum and maximum.",
                "The summary is descriptive of these measurements, not a confidence interval or a hardware guarantee.",
                "_, times = completed_times(jax.jit(product), values, 3)\nmedian = float(np.median(times))\nassert float(times.min()) <= median <= float(times.max())",
                "Retain the original measurements alongside the summary.",
            ),
            case(
                "Change workload size explicitly",
                "Evaluate the product for an 8-by-8 array and check it against NumPy.",
                "Correct 8-by-8 result; a different workload identity.",
                "Changing shape can change both operation count and compilation specialization, so label it as another case.",
                "small = jnp.arange(64., dtype=jnp.float64).reshape(8, 8) / 64.\nresult, _ = completed_times(jax.jit(product), small, 1)\nclose(result, np.asarray(small) @ np.asarray(small).T)",
                "Do not combine different workload sizes into one unlabeled sample.",
            ),
            case(
                "Identify the executed backend",
                "Record the backend and result-device platform for this CPU lesson.",
                "CPU backend and CPU-resident result.",
                "This establishes the local execution identity, not accelerator performance.",
                "result = product(values)\nresult.block_until_ready()\nassert jax.default_backend() == 'cpu'\nassert all(device.platform == 'cpu' for device in result.devices())",
                "A library supporting GPUs does not prove this call used one.",
            ),
        ),
        "If timings look implausibly small, inspect synchronization. If the first call is slow, separate compilation from warm work. If a claimed speedup changes after moving data construction, the measurement boundary changed. Never assert a universal speed ratio in a small correctness test.",
        "Design a benchmark comparing two correct implementations with fixed shape/dtype, warmup, repeated measurements and explicit transfers. Then list the additional trace and hardware evidence needed for a GPU throughput or memory claim, connecting to cuda-031.",
        (
            ("Benchmarking", "https://docs.jax.dev/en/latest/benchmarking.html"),
            ("Asynchronous dispatch", "https://docs.jax.dev/en/latest/async_dispatch.html"),
            ("Profiling", "https://docs.jax.dev/en/latest/profiling.html"),
        ),
    ),
    Unit(
        26,
        "Recomputation and donation change resource ownership",
        "advanced",
        (25,),
        ("checkpoint", "rematerialization", "buffer donation", "memory evidence"),
        "Preserve numerical behavior while reasoning about recomputation and the ownership contract of donated buffers.",
        r"""Reverse differentiation may retain intermediate values needed by the backward pass. Gradient checkpointing, also called rematerialization, changes which intermediates are kept and which are recomputed. It is a storage-versus-computation tradeoff, not a different mathematical objective when applied correctly.

Where checkpoint boundaries are placed matters. Wrapping an entire function does not automatically produce a useful memory saving for every computation. Inspect the structure and measure the relevant workload. A small CPU parity example establishes that a chosen transformation preserves values and derivatives; it does not measure peak GPU memory or training throughput.

Buffer donation concerns a different resource relationship. A jitted call can be told that selected input buffers may be reused. After donating a value, the caller must not rely on reusing that input. Retain the returned result as the next state. If an independent reference is needed, make its host copy before donation.

Donation is a permission and lifetime contract, not a promise that every possible buffer will be reused or that an allocation count will shrink by a fixed amount. Shape, output structure, compiler decisions and backend behavior affect what can actually happen. Tests should verify correct returned values and disciplined ownership; hardware memory claims need measured evidence.

These mechanisms can combine in training, but they should not be conflated. Checkpointing changes recomputation of intermediates for differentiation. Donation changes whether an input buffer may be consumed by a compiled operation. Both require a correct baseline, a defined state transition and separate resource observation.""",
        r"""For \(f(x)=\sum_i x_i^3\), \(\nabla f(x)=3x^2\). At \([1,2,3]\), f=36 and the gradient is \([3,12,27]\). A checkpointed implementation should retain those results. For a donated transition \(x'=x+1\), the returned value is the next state; the old buffer's lifetime is intentionally surrendered even though the abstract numerical rule is simple.""",
        """def cubic_sum(values):
    return jnp.sum(values ** 3)

rematerialized = jax.checkpoint(cubic_sum)
consume = jax.jit(lambda values: values + 1., donate_argnums=(0,))""",
        (
            case(
                "Check recomputed derivatives",
                "Compare cubic_sum and its checkpointed form on [1,2,3].",
                "Value 36 and gradient [3,12,27] for both.",
                "This checks the mathematical behavior before making a memory-saving claim.",
                "values = jnp.array([1., 2., 3.])\nclose(rematerialized(values), 36.)\nclose(jax.grad(rematerialized)(values), [3., 12., 27.])\nclose(jax.grad(cubic_sum)(values), jax.grad(rematerialized)(values))",
                "Use an analytic gradient as well as parity between two transformed paths.",
            ),
            case(
                "Consume and replace a buffer",
                "Make a host oracle before donating an array to the increment transition.",
                "Returned values [2,3,4]; no later use of the donated input.",
                "The host copy is made before the call. The code deliberately follows the ownership rule rather than probing a potentially invalid old handle.",
                "values = jnp.array([1., 2., 3.])\nexpected = np.array(values) + 1.\nupdated = consume(values)\nupdated.block_until_ready()\nclose(updated, expected)",
                "Save the oracle before donation, then keep only the returned state.",
            ),
        ),
        (
            case(
                "Change the derivative input",
                "Check the rematerialized cubic gradient at [-2,0,2].",
                "[12,0,12].",
                "Negative inputs change the cubic value but the squared derivative remains nonnegative.",
                "close(jax.grad(rematerialized)(jnp.array([-2., 0., 2.])), [12., 0., 12.])",
                "Differentiate the mathematical function before evaluating signs.",
            ),
            case(
                "Compose checkpointing with JIT",
                "JIT the gradient of the rematerialized function.",
                "The same [3,12,27] derivative.",
                "This checks one supported composition, not every possible custom primitive or backend.",
                "close(jax.jit(jax.grad(rematerialized))(jnp.array([1., 2., 3.])), [3., 12., 27.])",
                "Hold the objective and inputs fixed.",
            ),
            case(
                "Continue from returned ownership",
                "Apply the donated increment transition twice, each time retaining the returned array.",
                "[3,4] from initial [1,2].",
                "The second call consumes the first call's returned state, not the original donated handle.",
                "state = jnp.array([1., 2.])\nstate = consume(state)\nstate = consume(state)\nclose(state, [3., 4.])",
                "Rebind state to each returned value.",
            ),
            case(
                "Keep an ordinary baseline",
                "Compare a donated update against a non-donating implementation using independently created inputs.",
                "Matching [5,6].",
                "Independent input arrays prevent the comparison from reusing consumed storage.",
                "baseline = jnp.array([4., 5.]) + 1.\nupdated = consume(jnp.array([4., 5.]))\nclose(updated, baseline)",
                "Do not pass the same donated array into the baseline afterward.",
            ),
            case(
                "Check a higher derivative",
                "Calculate the Hessian diagonal of the rematerialized cubic at [1,2].",
                "[6,12].",
                "The second derivative is 6x, providing an additional transformation check.",
                "hessian = jax.hessian(rematerialized)(jnp.array([1., 2.]))\nclose(hessian, [[6., 0.], [0., 12.]])",
                "Include the off-diagonal zero entries.",
            ),
            case(
                "Separate a resource claim",
                "Inspect result size for a donated length-four update and state what it does not measure.",
                "Four float64 entries, 32 bytes of logical array payload.",
                "Logical nbytes excludes allocator pools, compiler storage, intermediates and process/device overhead. It is not peak memory.",
                "result = consume(jnp.zeros(4, dtype=jnp.float64))\nassert result.size == 4 and result.nbytes == 32",
                "Name the measured quantity precisely.",
            ),
        ),
        "A deleted-buffer error indicates a lifetime violation, not a reason to disable correctness checks. A small nbytes value is not a peak-memory measurement. Validate the mathematical baseline before investigating checkpoint placement or donation performance.",
        "Propose checkpoint boundaries for a multi-stage model and a donation policy for its parameter-state transition. Explain which arrays a caller must retain for evaluation and which may be consumed, then specify an actual peak-memory measurement on owned hardware.",
        (
            ("Checkpointing", "https://docs.jax.dev/en/latest/301/remat.html"),
            ("JIT donation", "https://docs.jax.dev/en/latest/_autosummary/jax.jit.html"),
        ),
    ),
]

UNITS.extend(
    [
        Unit(
            27,
            "Array placement and sharding contracts on one CPU",
            "advanced",
            (26,),
            ("Mesh", "NamedSharding", "PartitionSpec", "addressable shard"),
            "Inspect real array placement and sharding metadata while keeping a single-device lesson distinct from multi-device performance.",
            r"""A distributed array has a logical global shape and a placement of its pieces across devices. A mesh names device axes; a partition specification describes how array dimensions relate to those axes. Replicated and partitioned dimensions express different layout contracts even when a one-device fixture makes their values look identical.

This lesson deliberately creates a mesh containing one CPU device. It can execute actual placement and inspect addressable shards without requiring optional hardware. Because the mesh has one device, no physical inter-device communication or scaling is established. The useful outcome is understanding the interface before moving to a separately qualified logical-multi-device or accelerator fixture.

NamedSharding combines a mesh with a PartitionSpec. For a two-dimensional observation table, assigning the first dimension to a data axis expresses row partitioning. A replicated output specification instead says each device should have the complete result. The chosen mesh axis mode and API version matter; the current documentation distinguishes explicit, automatic and manual modes. This lesson uses the established NamedSharding interface on a one-device Mesh and records that narrow contract.

Addressable shards are the pieces visible to the current process. In a multi-host setting, they need not cover every global element locally. Converting a non-addressable global array directly to NumPy is therefore a different operation from inspecting one local shard. The single-device example avoids pretending that these difficult distributed ownership questions have already been exercised.

Placement and numerical correctness should be inspected separately. A correctly shaped answer may have an unintended layout, while correct metadata does not prove the mathematical calculation. Compare values against a plain reference, inspect the actual device platforms and name the bounds of the observation.""",
            r"""For an observation matrix \(X\in\mathbb R^{N\times D}\), a row-partition specification maps the N axis to the mesh's data axis and leaves D unpartitioned. With one physical device, its only shard contains all N rows. A Gram calculation \(X^{\mathsf T}X\) returns a D-by-D matrix; a replicated output contract describes its placement, not a change to the matrix equation.""",
            """from jax.sharding import Mesh, NamedSharding, PartitionSpec

mesh = Mesh(np.asarray(jax.devices('cpu')[:1]), ('data',))
row_layout = NamedSharding(mesh, PartitionSpec('data', None))
replicated = NamedSharding(mesh, PartitionSpec())
host = np.arange(6., dtype=np.float64).reshape(3, 2)""",
            (
                case(
                    "Place and inspect a real array",
                    "Put the host table into the declared row layout and inspect its addressable shard.",
                    "Global shape (3,2), one CPU shard with the original values.",
                    "This is real one-device placement. It demonstrates layout metadata without claiming distributed execution.",
                    "placed = jax.device_put(host, row_layout)\nassert placed.shape == (3, 2)\nassert len(placed.addressable_shards) == 1\nassert placed.addressable_shards[0].device.platform == 'cpu'\nclose(placed.addressable_shards[0].data, host)",
                    "Separate the global array shape from local shard contents.",
                ),
                case(
                    "Specify output placement",
                    "JIT a Gram calculation with row-layout input and replicated output.",
                    "Correct 2-by-2 Gram result with declared replicated placement.",
                    "The layout specification accompanies the numerical function and does not replace its independent value oracle.",
                    "placed = jax.device_put(host, row_layout)\nfunction = jax.jit(lambda x: x.T @ x, in_shardings=row_layout, out_shardings=replicated)\nresult = function(placed)\nclose(result, host.T @ host)\nassert result.sharding.is_equivalent_to(replicated, result.ndim)",
                    "Check values and metadata separately.",
                ),
            ),
            (
                case(
                    "Inspect mesh identity",
                    "Check the named mesh size and its actual devices.",
                    "One data-axis device, CPU platform.",
                    "A mesh name does not imply more than the explicitly supplied device inventory.",
                    "assert mesh.shape['data'] == 1\nassert all(device.platform == 'cpu' for device in mesh.devices.flat)",
                    "Read the concrete device count.",
                ),
                case(
                    "Round-trip values",
                    "Place the table and convert it back to a host array.",
                    "Equal host values for this fully addressable fixture.",
                    "This operation is valid because the one-device array is addressable in the current process.",
                    "placed = jax.device_put(host, row_layout)\nassert placed.is_fully_addressable\nclose(np.asarray(placed), host)",
                    "Do not generalize full addressability to every multi-host array.",
                ),
                case(
                    "Inspect the specification",
                    "Compare the row-layout specification with an empty replicated specification.",
                    "The row spec names data on axis zero; replicated spec has no partition axes.",
                    "Their intended layout meanings differ even though one device makes their concrete storage coincide.",
                    "assert row_layout.spec == PartitionSpec('data', None)\nassert replicated.spec == PartitionSpec()",
                    "Metadata describes a distribution contract, not just today's values.",
                ),
                case(
                    "Differentiate a placed calculation",
                    "Differentiate the sum of squares for the placed input.",
                    "Twice the original table.",
                    "A supported one-device placement must preserve the ordinary derivative contract.",
                    "placed = jax.device_put(host, row_layout)\nclose(jax.grad(lambda x: jnp.sum(x * x))(placed), 2 * host)",
                    "Keep the independent derivative oracle.",
                ),
                case(
                    "Change the row count",
                    "Place a 5-by-2 table under the same named row layout.",
                    "Global shape (5,2), one local shard with all rows.",
                    "The specification describes axis meaning rather than hard-coding the original number of observations.",
                    "other = np.arange(10., dtype=np.float64).reshape(5, 2)\nplaced = jax.device_put(other, row_layout)\nassert placed.shape == (5, 2)\nclose(placed.addressable_shards[0].data, other)",
                    "The single-device partition contains every row.",
                ),
                case(
                    "State the evidence limit",
                    "Inspect how many physical devices actually hold the result.",
                    "Exactly one; no multi-device scaling claim.",
                    "Logical annotations and backend support do not establish unobserved hardware execution.",
                    "placed = jax.device_put(host, row_layout)\nassert len(placed.devices()) == 1",
                    "Count actual devices rather than course topic names.",
                ),
            ),
            "If a placed computation differs, inspect layout, global shape, local shard indexing and numerical logic independently. Do not infer communication cost or replica count from a one-device result. Multi-host addressability needs its own actual fixture.",
            "Draw a proposed two-device row partition and a replicated parameter vector. State the expected local shapes and the reduction needed for a global gradient, then identify the hardware and process evidence missing from this one-CPU lesson.",
            (
                ("Sharding", "https://docs.jax.dev/en/latest/201/sharding.html"),
                ("Sharding API", "https://docs.jax.dev/en/latest/jax.sharding.html"),
            ),
        ),
        Unit(
            28,
            "Collective mathematics and unequal shard counts",
            "advanced",
            (27,),
            ("named mapped axis", "psum", "global mean", "gradient aggregation"),
            "Validate collective reduction semantics on a named mapped CPU axis without confusing that model with physical distributed execution.",
            r"""A global statistic must combine quantities that represent the intended population. If one shard holds one observation and another holds three, equally averaging their local means weights shards equally rather than observations equally. The correct observation mean combines local sums and counts before dividing.

The same issue appears in gradients. A local mean gradient already contains a denominator. To obtain a global observation mean, either weight each local mean by its active count or accumulate local gradient sums and divide by the global count. An unweighted average of local means is correct only under the relevant equal-count assumptions.

JAX named mapped axes can express collective semantics. In this unit, vmap creates a logical replica axis and lax.psum reduces across it. All execution remains on the CPU fixture. This is an actual mapped collective operation, but it does not establish separate processes, physical devices, communication bandwidth or distributed failure behavior.

A collective result can appear on every logical participant. That replication is part of the output contract. An all-gather instead collects participant values while retaining their identities in an axis. Confusing a gathered list with an already reduced total can introduce another counting error.

Real multi-process programs must additionally agree on collective order, data ownership and which global arrays are addressable by each process. Those systems requirements are not solved by a numerically correct two-row CPU model. The next optional systems units make the separate qualification boundary explicit.""",
            r"""If local sums are \(s_r\) and counts \(n_r\), the global mean is \(\sum_r s_r/\sum_r n_r\). For sums (2,12) and counts (1,3), it is 14/4=3.5, while the mean of local means is 3. For squared loss with y=2x at w=0, each sample contributes gradient \(-4x^2\). Splitting x=(1,2,3,4) into counts one and three gives gradient sums -4 and -116; the global mean is -30.""",
            """def global_mean(local_sum, local_count):
    total = jax.lax.psum(local_sum, 'replica')
    count = jax.lax.psum(local_count, 'replica')
    return total / count

mapped_mean = jax.vmap(global_mean, in_axes=(0, 0), axis_name='replica')
local_sums = jnp.array([2., 12.])
local_counts = jnp.array([1., 3.])""",
            (
                case(
                    "Combine unequal shards correctly",
                    "Use the named mapped reduction on sums [2,12] and counts [1,3].",
                    "Both logical participants receive 3.5.",
                    "The output is a replicated global mean rather than two unrelated local means.",
                    "close(mapped_mean(local_sums, local_counts), [3.5, 3.5])\nclose(jnp.mean(local_sums / local_counts), 3.)",
                    "Reduce both numerator and denominator.",
                ),
                case(
                    "Aggregate gradient sums",
                    "Combine local gradient sums [-4,-116] with counts [1,3].",
                    "Global mean gradient -30 on both participants.",
                    "This matches a full-batch gradient over four observations; equal weighting of local means would be a different objective.",
                    "combined = mapped_mean(jnp.array([-4., -116.]), local_counts)\nclose(combined, [-30., -30.])\nx = jnp.array([1., 2., 3., 4.])\nfull = jax.grad(lambda w: jnp.mean((w * x - 2 * x) ** 2))(0.)\nclose(full, -30.)",
                    "Keep gradient sums and active counts paired.",
                ),
            ),
            (
                case(
                    "Check equal counts",
                    "Combine sums [2,6] with counts [2,2].",
                    "Both outputs two, equal to the mean of local means in this special case.",
                    "Equal counts make the weighting rules coincide; that fixture alone would not expose the unequal-count bug.",
                    "close(mapped_mean(jnp.array([2., 6.]), jnp.array([2., 2.])), [2., 2.])",
                    "Retain the unequal-count regression case too.",
                ),
                case(
                    "Add a zero-count participant",
                    "Combine sums [2,12,0] with counts [1,3,0].",
                    "Three replicated outputs 3.5.",
                    "A zero-count participant contributes neither observations nor numerator mass; the total count remains positive.",
                    "close(mapped_mean(jnp.array([2., 12., 0.]), jnp.array([1., 3., 0.])), [3.5, 3.5, 3.5])",
                    "Do not form that participant's undefined local mean first.",
                ),
                case(
                    "Gather participant identity",
                    "All-gather scalar values [2,5] across the mapped axis.",
                    "Each participant receives [2,5].",
                    "Gather retains a participant axis, whereas psum produces a reduced value.",
                    "gather = jax.vmap(lambda x: jax.lax.all_gather(x, 'replica'), axis_name='replica')\nclose(gather(jnp.array([2., 5.])), [[2., 5.], [2., 5.]])",
                    "Draw the output participant and gathered axes.",
                ),
                case(
                    "Check a global sum",
                    "Apply psum to participant values [2,5,7].",
                    "Each participant receives 14.",
                    "Replication of the reduced value does not mean the global sum should be counted three times afterward.",
                    "summed = jax.vmap(lambda x: jax.lax.psum(x, 'replica'), axis_name='replica')\nclose(summed(jnp.array([2., 5., 7.])), [14., 14., 14.])",
                    "Distinguish one global statistic from its replicated storage.",
                ),
                case(
                    "Compile the collective model",
                    "JIT the mapped weighted mean and compare its output.",
                    "The same [3.5,3.5].",
                    "Compilation parity does not add hardware or process evidence.",
                    "close(jax.jit(mapped_mean)(local_sums, local_counts), [3.5, 3.5])",
                    "Keep logical-axis semantics separate from physical placement.",
                ),
                case(
                    "Detect the wrong weighting",
                    "Compare the mean of local gradient means with the correct global mean.",
                    "The unweighted result differs from -30.",
                    "This negative control would pass if only equal-sized shards were tested.",
                    "wrong = jnp.mean(jnp.array([-4., -116.]) / local_counts)\nassert not np.isclose(float(wrong), -30.)",
                    "Use an adversarial count imbalance.",
                ),
            ),
            "Check whether each quantity is a sum, mean, count, replicated global value or gathered per-participant array. The all-zero global-count case needs a declared admission policy before division. Correct mapped CPU arithmetic is not evidence of actual multi-host collective ordering or recovery.",
            "Translate this calculation into a proposed data-parallel training step with unequal nonpadding token counts. Explain the actual collective order and ownership evidence a multi-process implementation would need, connecting to torch-030 and tf-030.",
            (
                ("vmap named axes", "https://docs.jax.dev/en/latest/_autosummary/jax.vmap.html"),
                ("Manual parallelism", "https://docs.jax.dev/en/latest/201/shard-map.html"),
            ),
        ),
    ]
)

UNITS.append(
    Unit(
        29,
        "Port attention and low-rank updates by their equations",
        "advanced",
        (28,),
        ("scaled attention", "causal mask", "LoRA", "framework parity"),
        "Reconstruct two small language-model mechanisms in JAX and compare values and gradients with independent shape-aware oracles.",
        r"""Porting a model mechanism begins with its mathematical contract, not a table of API renamings. Attention needs query/key/value shapes, the score scale, mask meaning and softmax axis. A low-rank update needs matrix orientation, factor dimensions, scale and initialization. A source file can look familiar while implementing a different function.

The attention fixture first uses zero scores so the causal mask determines exact averages. That isolates information access, but zero dot products cannot test whether the scale factor is correct. A second nonuniform row supplies an independent scalar softmax oracle. Future-only perturbations then test prefix invariance of the actual output.

Mask admission is explicit. Every query must have at least one available key under this lesson's categorical normalization contract. An all-forbidden row has no defined distribution. The pure attention calculation assumes admitted shapes and uses negative infinity to remove forbidden mass before normalization. This is a small square CPU mechanism, not a complete cached decoder or an optimized GPU kernel.

The adapter uses row-vector inputs: \(Y=X(W+sAB)\). W is fixed, A maps input features into a small rank space and B maps back to output features. Initializing B to zero preserves the base function. It also makes A's first gradient zero while B can receive a nonzero gradient through A. That is an expected connected derivative, not a reason to detach A.

Both mechanisms have existing counterparts in the LLM and framework routes. Matching their literal fixtures and objective reductions provides a useful porting check. It does not establish a full checkpoint conversion, model quality, GPU performance or universal equivalence between JAX, PyTorch and TensorFlow training workflows.""",
        r"""Attention is \(O=\operatorname{softmax}(QK^{\mathsf T}/\sqrt d+M)V\), with the transpose attached to K and softmax over allowed key columns. For the adapter, \(\partial L/\partial B=s(XA)^{\mathsf T}G\) and \(\partial L/\partial A=sX^{\mathsf T}GB^{\mathsf T}\). With X all ones, W=I_8, A entries 1/8, B=0, s=2 and mean squared output loss, the B gradient is 1/2 and A gradient zero. An SGD step of 0.1 yields output 0.8 and loss 0.64.""",
        """def admit_attention(query, keys, values, allowed):
    if query.ndim != 2 or keys.ndim != 2 or values.ndim != 2:
        raise ValueError("matrices required")
    if query.shape[1] <= 0 or query.shape[1] != keys.shape[1] or keys.shape[0] != values.shape[0]:
        raise ValueError("attention feature/source shapes disagree")
    if allowed.shape != (query.shape[0], keys.shape[0]) or np.asarray(allowed).dtype != np.bool_:
        raise ValueError("Boolean query-key mask required")
    if not np.asarray(allowed).any(axis=1).all():
        raise ValueError("a query has no allowed key")


def attention(query, keys, values, allowed):
    scores = query @ keys.T / jnp.sqrt(query.shape[1])
    weights = jax.nn.softmax(jnp.where(allowed, scores, -jnp.inf), axis=-1)
    return weights @ values

q = jnp.zeros((3, 2))
k = jnp.zeros((3, 2))
v = jnp.array([[2., 0.], [0., 2.], [6., 6.]])
mask = jnp.tril(jnp.ones((3, 3), dtype=bool))


def adapter_loss(a, b):
    output = jnp.ones((1, 8)) @ (jnp.eye(8) + 2. * a @ b)
    return jnp.mean(output ** 2)

a = jnp.full((8, 2), 1 / 8)
b = jnp.zeros((2, 8))""",
        (
            case(
                "An exact causal average",
                "Admit the zero-score attention fixture and calculate its outputs.",
                "[[2,0],[1,1],[8/3,8/3]].",
                "Each query averages only its available prefix. This fixture tests the mask and normalization, while a nonuniform case is still needed for scaling.",
                "admit_attention(q, k, v, mask)\nclose(attention(q, k, v, mask), [[2., 0.], [1., 1.], [8 / 3, 8 / 3]])",
                "Count allowed keys in each row.",
            ),
            case(
                "A complete low-rank first step",
                "Differentiate the adapter loss, update B at rate 0.1 and recompute.",
                "A gradient zero, B gradient 0.5, loss from one to 0.64.",
                "The scale factor appears in both forward and backward equations. The separate mean denominator gives the upstream output gradient one quarter.",
                "ga, gb = jax.grad(adapter_loss, argnums=(0, 1))(a, b)\nclose(ga, jnp.zeros_like(a))\nclose(gb, jnp.full_like(b, .5))\nclose(adapter_loss(a, b), 1.)\nclose(adapter_loss(a, b - .1 * gb), .64)",
                "Trace X A before differentiating B.",
            ),
        ),
        (
            case(
                "Perturb only the future",
                "Change the final value row and compare the first two attention outputs.",
                "Earlier outputs remain identical.",
                "This checks the complete output path, not only whether the mask looks triangular.",
                "changed = v.at[2].set(jnp.array([100., 200.]))\nclose(attention(q, k, changed, mask)[:2], attention(q, k, v, mask)[:2])",
                "The changed row is unavailable to the first two queries.",
            ),
            case(
                "Test the scale with nonuniform scores",
                "Use one query [1,0], keys [[1,0],[0,1]] and values [[2,0],[0,2]].",
                "Weights determined by softmax([1/sqrt(2),0]).",
                "A scalar logistic calculation detects omission of the square-root scale.",
                "query = jnp.array([[1., 0.]])\nkeys = jnp.eye(2)\nvalues = 2 * jnp.eye(2)\nprobability = 1 / (1 + math.exp(-1 / math.sqrt(2)))\nclose(attention(query, keys, values, jnp.ones((1, 2), dtype=bool)), [[2 * probability, 2 * (1 - probability)]])",
                "Do not use zero scores as the only scaling test.",
            ),
            case(
                "Refuse an empty allowed set",
                "Remove every key from the first query's mask.",
                "ValueError during admission.",
                "A fully masked query has no categorical distribution under this contract.",
                "try:\n    admit_attention(q, k, v, mask.at[0].set(False))\nexcept ValueError:\n    pass\nelse:\n    raise AssertionError('all-masked query admitted')",
                "Check each row, not only the mask's total number of true values.",
            ),
            case(
                "Trace value gradients",
                "Differentiate the sum of all attention outputs with respect to V in the zero-score fixture.",
                "Each feature receives source-row weights [11/6,5/6,1/3].",
                "A source value accumulates contributions from every query that can use it.",
                "g = jax.grad(lambda values: attention(q, k, values, mask).sum())(v)\nclose(g, [[11 / 6, 11 / 6], [5 / 6, 5 / 6], [1 / 3, 1 / 3]])",
                "Sum the attention weight of a source across query rows.",
            ),
            case(
                "Count and bound the adapter",
                "Count the trainable factor entries and verify the product's maximum rank.",
                "32 entries; rank at most two.",
                "A rank bound constrains a matrix family, not the number of nonzero visible entries or measured model quality.",
                "assert a.size + b.size == 32\nassert np.linalg.matrix_rank(np.asarray(a @ b)) <= 2",
                "Count input-rank and rank-output factors separately.",
            ),
            case(
                "Compile the admitted operation",
                "JIT the pure attention helper and compare the exact fixture.",
                "Matching causal-average outputs.",
                "This checks JAX transformation parity for the admitted CPU mechanism only.",
                "close(jax.jit(attention)(q, k, v, mask), attention(q, k, v, mask))",
                "Keep admission, computation and evidence claims separate.",
            ),
        ),
        "For a port mismatch, inspect factor orientation, score scale, axis, mask convention and reduction first. Square matrices and uniform scores can conceal wrong operations. Do not infer full-model equivalence from these two isolated mechanisms.",
        "Compare with llm-009, llm-032, llm-applied-016 and llm-046 using identical literal fixtures. Specify the additional tokenizer, position, normalization, parameter and optimizer contracts required before attempting a full model conversion.",
        (
            ("Attention paper", "https://arxiv.org/abs/1706.03762"),
            ("LoRA paper", "https://arxiv.org/abs/2106.09685"),
            (
                "JAX transformations",
                "https://docs.jax.dev/en/latest/automatic-differentiation.html",
            ),
        ),
    )
)

UNITS.extend(
    [
        Unit(
            30,
            "Capstone: a checked differentiable numerical component",
            "advanced",
            (29,),
            ("admission contract", "masked objective", "ridge solve", "independent validation"),
            "Deliver a small reusable numerical component with separate admission, mathematical, transformation and interpretation evidence.",
            r"""A component is ready for reuse only when another reader can identify its accepted inputs, output meaning and failure policy. This capstone combines a masked regression objective with a closed-form ridge solve. It deliberately separates host-side admission from the pure numerical functions, making the transformation boundary visible.

Each row represents an observation with a feature vector and one target. The mask selects participating observations. A ridge penalty applies to every supplied coefficient under this declared convention, including any intercept column. Other conventions can exclude an intercept; that would be a different objective and must be named rather than silently substituted.

The reference solves the normal equations for a tiny well-conditioned fixture. It is not a recommendation to form normal equations for every large or ill-conditioned regression problem. Their conditioning can be worse than the original design matrix. The scientific purpose here is a compact independently checkable objective with a known optimum and a gradient that should vanish there.

Acceptance has several layers. Shape and finite-value checks admit the data. An exact coefficient fixture checks the intended equation. A masked outlier and row permutation check the population and identity policy. The gradient at the solved optimum checks consistency between the objective and solution. JIT parity checks supported transformation behavior. None of those tests alone would establish a valid causal interpretation or population model.

For independent practice, close the reference and implement the contract from the equations. Explain why each negative control would reject a plausible wrong implementation. Then change the feature layout or penalty convention deliberately, deriving new expected behavior before modifying the code. A successful copied reference is rehearsal, not the final evidence of independence.""",
            r"""Define \(L(w)=\sum_i m_i(x_i^{\mathsf T}w-y_i)^2/\sum_i m_i+\lambda\lVert w\rVert_2^2\). Setting its gradient to zero gives \((X^{\mathsf T}MX/N+\lambda I)w=X^{\mathsf T}My/N\), where M is diagonal with mask entries and \(N=\sum_i m_i\). For rows (1,0),(1,1),(1,2), targets 1,3,5 and lambda zero, the unique fixture solution is (1,2).""",
            """def admit(design, targets, mask, penalty):
    if design.ndim != 2 or targets.shape != (design.shape[0],) or mask.shape != targets.shape:
        raise ValueError("row contracts differ")
    if np.asarray(mask).dtype != np.bool_ or not np.asarray(mask).any():
        raise ValueError("nonempty Boolean observation mask required")
    if not math.isfinite(penalty) or penalty < 0:
        raise ValueError("nonnegative finite penalty required")
    if not np.isfinite(np.asarray(design)).all() or not np.isfinite(np.asarray(targets)).all():
        raise ValueError("finite literal data required")


def objective(weight, design, targets, mask, penalty):
    squared = (design @ weight - targets) ** 2
    return jnp.where(mask, squared, 0.).sum() / mask.sum() + penalty * jnp.vdot(weight, weight)


def solve(design, targets, mask, penalty):
    count = mask.sum()
    weighted = mask[:, None] * design
    matrix = design.T @ weighted / count + penalty * jnp.eye(design.shape[1])
    rhs = design.T @ jnp.where(mask, targets, 0.) / count
    return jnp.linalg.solve(matrix, rhs)

design = jnp.array([[1., 0.], [1., 1.], [1., 2.]])
targets = jnp.array([1., 3., 5.])
mask = jnp.ones(3, dtype=bool)""",
            (
                case(
                    "An independently known solution",
                    "Admit and solve the unpenalized fixture, then evaluate its gradient.",
                    "Weights [1,2], zero loss and zero gradient within tolerance.",
                    "The coefficients are known from the target rule. A vanishing gradient additionally checks consistency between the coded objective and solved equation.",
                    "admit(design, targets, mask, 0.)\nweight = solve(design, targets, mask, 0.)\nclose(weight, [1., 2.])\nclose(objective(weight, design, targets, mask, 0.), 0.)\nclose(jax.grad(objective)(weight, design, targets, mask, 0.), [0., 0.])",
                    "Derive the feature-to-target equation before solving.",
                ),
                case(
                    "An ignored outlier is not an observation",
                    "Append a finite extreme row and target with mask false.",
                    "The solved weights remain [1,2].",
                    "Both numerator and denominator preserve the three-observation population.",
                    "x = jnp.concatenate([design, jnp.array([[100., 100.]])])\ny = jnp.concatenate([targets, jnp.array([-100.])])\nm = jnp.array([True, True, True, False])\nadmit(x, y, m, 0.)\nclose(solve(x, y, m, 0.), [1., 2.])",
                    "Test an outlier strong enough to expose accidental participation.",
                ),
            ),
            (
                case(
                    "Check a penalty convention",
                    "Solve with penalty 0.1 and verify the gradient of that same penalized objective.",
                    "A finite changed coefficient vector with zero penalized gradient.",
                    "The penalty applies to both coefficients in this contract, so compare against the matching objective.",
                    "weight = solve(design, targets, mask, .1)\nassert not np.allclose(np.asarray(weight), [1., 2.])\nclose(jax.grad(objective)(weight, design, targets, mask, .1), [0., 0.])",
                    "Do not compare a penalized solve with an unpenalized derivative.",
                ),
                case(
                    "Preserve row identity under permutation",
                    "Reverse design, targets and mask together.",
                    "Unchanged coefficients.",
                    "The sum objective is invariant to consistent row reordering.",
                    "close(solve(design[::-1], targets[::-1], mask[::-1], 0.), [1., 2.])",
                    "Permute every row-associated object together.",
                ),
                case(
                    "Reject an empty population",
                    "Admit a completely false mask.",
                    "ValueError.",
                    "The component refuses an undefined empirical mean before entering the numerical kernel.",
                    "try:\n    admit(design, targets, jnp.zeros(3, dtype=bool), 0.)\nexcept ValueError:\n    pass\nelse:\n    raise AssertionError('empty population admitted')",
                    "Storage capacity does not establish observation count.",
                ),
                case(
                    "Reject an invalid penalty",
                    "Admit a negative ridge penalty.",
                    "ValueError under the declared nonnegative-penalty contract.",
                    "A negative value would change the optimization problem and can destroy the intended convexity guarantee.",
                    "try:\n    admit(design, targets, mask, -.1)\nexcept ValueError:\n    pass\nelse:\n    raise AssertionError('negative penalty admitted')",
                    "Validate the objective configuration.",
                ),
                case(
                    "Check transformation parity",
                    "Compile the solve on admitted inputs and compare with the eager result.",
                    "Matching coefficients.",
                    "The compiled function receives the numerical representation after host admission.",
                    "close(jax.jit(solve)(design, targets, mask, .1), solve(design, targets, mask, .1))",
                    "A pure kernel and an admission wrapper have different responsibilities.",
                ),
                case(
                    "Transfer the target rule",
                    "Use targets [2,5,8] with the same feature rows.",
                    "Weights [2,3].",
                    "Changing the known affine rule provides a new oracle that is not satisfied by hard-coding the original coefficients.",
                    "close(solve(design, jnp.array([2., 5., 8.]), mask, 0.), [2., 3.])",
                    "Derive the new intercept and slope before running.",
                ),
            ),
            "A zero gradient can belong to the wrong objective. A low residual can belong to an ill-conditioned problem. A JIT pass can preserve the wrong mask. Retain separate evidence for admission, mathematical correctness, transformation behavior and the intended interpretation.",
            "Deliver your own implementation with a short contract, shape ledger, independent oracle and a failure case absent from the worked examples. Explain when a QR/SVD-based fit or a different regularization policy would be preferable to this tiny normal-equation teaching component.",
            (
                (
                    "Automatic differentiation",
                    "https://docs.jax.dev/en/latest/automatic-differentiation.html",
                ),
                ("Numerical accuracy", "https://docs.jax.dev/en/latest/accuracy.html"),
            ),
        ),
        Unit(
            31,
            "Capstone: a reproducible training comparison",
            "advanced",
            (30,),
            ("baseline", "held-out task", "fixed budget", "restart state", "model comparison"),
            "Complete a small training study whose data, optimization, comparison and limitations can be independently reconstructed.",
            r"""A training study should answer a specified question. Here the question is whether a quadratic feature representation can recover an authored nonlinear response rule under a bounded gradient-descent procedure. An affine baseline supplies a meaningful comparison because it cannot express the same quadratic term.

Training and held-out inputs are fixed separately before fitting. The target rule is known, so its coefficients and predictions provide an independent oracle. The gradient-descent path is still an actual numerical experiment: it starts from zero, applies a fixed update budget and reports a fresh final loss. The reference also calculates a least-squares solution as an independent optimum comparison.

A model comparison must preserve the intended evaluation population. Both candidates receive the same held-out inputs and targets. Training loss, held-out loss, model capacity and computation budget remain distinct quantities. A smaller held-out error on these four authored points is useful evidence about the fixture, not a broad claim about all nonlinear regression tasks.

Reproducibility means retaining enough state and configuration to reconstruct the result. This deterministic study has no stochastic sampling, so no random key is used. Its state consists of coefficients and completed updates, with a fixed batch, learning rate and feature construction. If stochastic batches or dropout were added, those additional states would enter the contract rather than being implied by the current demonstration.

The capstone's final product should be an explanation a reviewer can challenge: what was predicted, which rows were used for fitting, which quantities changed between candidates, how the numerical result was verified, and what the conclusion cannot establish. Independent competence includes identifying an invalid comparison and proposing a better one, not only reproducing the successful reference.""",
            r"""The authored rule is \(y=1+2x-\frac12x^2\). A feature row \(\phi(x)=(1,x,x^2)\) has exact coefficients \((1,2,-1/2)\). For mean squared loss, \(\nabla_w L=2\Phi^{\mathsf T}(\Phi w-y)/N\). The fixed full-batch update is \(w'=w-0.02\nabla_wL\). An affine candidate uses only (1,x), so it cannot represent the quadratic term over arbitrary inputs.""",
            """train_x = jnp.array([-2., -1., 0., 1., 2.])
heldout_x = jnp.array([-1.5, -.5, .5, 1.5])


def targets(values):
    return 1 + 2 * values - .5 * values * values


def features(values):
    return jnp.stack((jnp.ones_like(values), values, values * values), axis=1)

train_design = features(train_x)
train_y = targets(train_x)
heldout_design = features(heldout_x)
heldout_y = targets(heldout_x)


def loss(weight, design, labels):
    return jnp.mean((design @ weight - labels) ** 2)


def advance(weight, steps):
    def update(state, unused):
        gradient = jax.grad(loss)(state, train_design, train_y)
        state = state - .02 * gradient
        return state, loss(state, train_design, train_y)
    return jax.lax.scan(update, weight, xs=None, length=steps)

trained = jax.jit(lambda w: advance(w, 400))(jnp.zeros(3))[0]""",
            (
                case(
                    "Fit a bounded candidate",
                    "Train from zero for 400 updates and compare with the known coefficients.",
                    "Coefficients within 0.01 of [1,2,-0.5], with reduced training loss.",
                    "The known target rule supplies a distinct oracle for the numerical optimization path.",
                    "close(trained, [1., 2., -.5], atol=.01, rtol=0.)\nassert float(loss(trained, train_design, train_y)) < float(loss(jnp.zeros(3), train_design, train_y))",
                    "Verify the gradient and fresh final loss before increasing the budget.",
                ),
                case(
                    "Compare on fixed held-out inputs",
                    "Fit an affine least-squares baseline on training rows and compare held-out errors.",
                    "The trained quadratic candidate has lower held-out loss on these four authored points.",
                    "Both predictions are scored on the same untouched rows. The conclusion is bounded to this synthetic study.",
                    "affine_train = train_design[:, :2]\naffine = jnp.linalg.lstsq(affine_train, train_y, rcond=None)[0]\naffine_error = loss(affine, heldout_design[:, :2], heldout_y)\nquadratic_error = loss(trained, heldout_design, heldout_y)\nassert float(quadratic_error) < float(affine_error)\nprint({'quadratic_holdout_mse': float(quadratic_error), 'affine_holdout_mse': float(affine_error), 'holdout_count': 4})",
                    "Use the same held-out population for both candidates.",
                ),
            ),
            (
                case(
                    "Audit the initial gradient",
                    "Compare autodiff with the explicit matrix gradient at zero.",
                    "Matching three-coordinate gradients.",
                    "This isolates objective and feature construction before interpreting a long trajectory.",
                    "zero = jnp.zeros(3)\nexplicit = 2 * train_design.T @ (train_design @ zero - train_y) / train_y.size\nclose(jax.grad(loss)(zero, train_design, train_y), explicit)",
                    "Keep the mean denominator visible.",
                ),
                case(
                    "Check an independent optimum",
                    "Solve the full quadratic least-squares problem directly.",
                    "[1,2,-0.5] within numerical tolerance.",
                    "The linear-in-features optimum is a separate algorithmic reference for the gradient-descent endpoint.",
                    "optimum = jnp.linalg.lstsq(train_design, train_y, rcond=None)[0]\nclose(optimum, [1., 2., -.5])",
                    "The model is nonlinear in x but linear in coefficients.",
                ),
                case(
                    "Replay the fixed budget",
                    "Train again from zero with identical configuration.",
                    "Matching trained coefficients.",
                    "This study is deterministic under its stated numeric environment and contains no random data order.",
                    "again = jax.jit(lambda w: advance(w, 400))(jnp.zeros(3))[0]\nclose(again, trained)",
                    "Do not insert stochastic state without expanding the contract.",
                ),
                case(
                    "Resume a partial trajectory",
                    "Compare 400 consecutive steps with 200 followed by 200 from the returned coefficients.",
                    "Matching final coefficients.",
                    "For this fixed-batch plain SGD transition, the coefficient vector is sufficient numeric continuation state; the step count remains reporting metadata.",
                    "first = advance(jnp.zeros(3), 200)[0]\ncontinued = advance(first, 200)[0]\nclose(continued, trained)",
                    "A stateful optimizer or schedule would need additional continuation state.",
                ),
                case(
                    "Verify the held-out split",
                    "Check that the four held-out inputs do not coincide with training inputs.",
                    "No exact overlapping input values.",
                    "This is a literal split check, not proof that a real dataset has no semantic or source-family leakage.",
                    "assert not set(np.asarray(train_x).tolist()) & set(np.asarray(heldout_x).tolist())",
                    "Keep the scope of the leakage claim precise.",
                ),
                case(
                    "Transfer the coefficient rule",
                    "Predict at x=3 using the known coefficients and distinguish extrapolation from the held-out interpolation study.",
                    "Prediction 2.5 under the known synthetic rule.",
                    "The algebraic target is known here. A real model's extrapolation outside observed support would require additional evidence.",
                    "oracle = jnp.array([1., 2., -.5])\nclose(features(jnp.array([3.])) @ oracle, [2.5])",
                    "Do not use a known synthetic rule as proof of real-world extrapolation.",
                ),
            ),
            "A favorable score can come from leakage, a changed target reduction, unequal comparison rows or a stale reported loss. Preserve the split and configuration before fitting. Report a failed or disappointing comparison rather than repeatedly tuning on the final held-out points.",
            "Design a fresh nonlinear target or noisy dataset, choose development and final evaluation units, and defend a baseline before running. Produce a report with source identity, configuration, numerical checks, observed results and explicit limitations. A completed reference is not an expertise certificate.",
            (
                ("Training cookbook", "https://docs.jax.dev/en/latest/the-training-cookbook.html"),
                (
                    "Automatic differentiation",
                    "https://docs.jax.dev/en/latest/automatic-differentiation.html",
                ),
            ),
        ),
    ]
)

UNITS.extend(
    [
        Unit(
            32,
            "Optional GPU and TPU execution qualification",
            "advanced",
            (31,),
            ("backend admission", "device readback", "allocator", "hardware evidence"),
            "Design and assess a device-specific qualification record without treating CPU or compiler evidence as accelerator acceptance.",
            r"""JAX's ability to target an accelerator is not evidence that a particular program used one. Package compatibility, driver/runtime support, device availability, explicit placement, compilation, synchronized execution and readback are separate observations. This reading unit specifies how those observations should fit together before a hardware claim is made.

The ordinary JAX course uses the jax-cpu worker. GPU and TPU preparation are optional external workflows with their own reviewed environment and resource ownership. An unavailable requested backend must remain unavailable; silently running on CPU would not satisfy an accelerator exercise. Opening this chapter does not install a package, request a device or start a cloud resource.

A useful first device probe is small and independently checkable. Discover the requested device, place a literal array there, execute a compiled numerical operation, wait for completion and compare host-read values against an exact oracle. Retain the actual device/backend and package versions with the source. A device list alone proves none of the later computation steps.

Allocator behavior also needs careful language. A runtime can reserve a substantial pool before a model creates its visible arrays. Reserved memory, live payload, temporary intermediates and peak device use are different quantities. Current JAX GPU allocation documentation describes a default preallocation policy and alternatives with fragmentation or performance tradeoffs. Do not copy an allocator setting into every environment without recording its purpose and measuring its effect.

TPU and GPU qualification are distinct. They use different backend packages, hardware and precision/performance characteristics. An NVIDIA CUDA receipt does not qualify a TPU path. Likewise, a one-device correctness probe does not establish multi-device throughput, numerical accuracy for every operation or recovery from a serious device fault.""",
            r"""The minimal numerical oracle can be \(f(x)=x^2\) on \(x=(1,2,3)\), giving (1,4,9). The equation is deliberately trivial so evidence can focus on execution identity and completion. A later performance ratio must compare completed equivalent work with shape, dtype, transfers and warmup fixed. Logical payload bytes are \(N\times\mathrm{bytes\ per\ element}\); they are not peak allocator usage.""",
            "",
            (
                case(
                    "Evaluate a partial evidence record",
                    "A hypothetical record says imports succeeded and one GPU was listed, but contains no allocation or output check. Decide what it establishes.",
                    "Package/device discovery only; execution correctness remains unqualified.",
                    "The missing stages can fail independently. An import may succeed while the first compilation, allocation or kernel execution fails.",
                    "**Written trace:** import -> device inventory -> missing placement -> missing synchronized calculation -> missing readback. Retain the gaps rather than converting them into passed checks.",
                    "Locate the last actually observed stage.",
                ),
                case(
                    "Specify an exact device probe",
                    "Design a probe for the square operation with explicit device placement and synchronized readback.",
                    "A record containing source, versions, requested/observed backend, completed operation and [1,4,9] readback.",
                    "This qualifies one small computation on the selected device. It deliberately makes no model-quality or throughput claim.",
                    "**Probe contract:** request the backend explicitly; reject absence; place the literal vector; compile the square; wait for its result; inspect result device identity; compare the host values to the oracle; retain failures and cleanup observations.",
                    "Make silent CPU fallback a failed condition.",
                ),
            ),
            (
                case(
                    "Separate CPU evidence",
                    "A CPU reference passes every mathematical assertion. Decide whether it qualifies the optional GPU lesson.",
                    "It supports CPU numerical behavior only.",
                    "The same mathematics can be correct while the accelerator toolchain or device operation remains untested.",
                    "Retain the CPU receipt as a baseline and list the missing accelerator stages.",
                    "Do not discard useful CPU evidence or relabel it.",
                ),
                case(
                    "Separate compilation from execution",
                    "A lowered accelerator program compiles, but no device output is retained. Classify the result.",
                    "Compilation evidence, with execution/readback still missing.",
                    "Compilation can succeed without establishing that the intended device operation completed correctly.",
                    "The next required observation is an owned bounded execution with synchronization and an independent value check.",
                    "Identify the artifact actually produced.",
                ),
                case(
                    "Choose a memory measurement",
                    "A monitoring tool reports reserved memory much larger than array nbytes. Explain two possible categories without declaring a leak.",
                    "Allocator reservation and non-array/intermediate overhead can differ from logical payload.",
                    "Repeated controlled measurements and ownership checks are needed to diagnose a leak; one large pool is not sufficient evidence.",
                    "Report logical array payload, allocator reservation and measured peak separately, with the runtime's allocation policy.",
                    "Name the quantity each tool measures.",
                ),
                case(
                    "Design a precision comparison",
                    "Compare float32 and float64 on a numerically sensitive operation under one device.",
                    "A plan with analytic/reference values, conditioning, tolerances, actual dtype and separately synchronized timings.",
                    "Accuracy and speed are distinct outcomes. Hardware-specific observations cannot be assumed from the dtype name.",
                    "Hold inputs and operation fixed; validate numerical error first; then measure completed execution under the chosen precision policy.",
                    "Do not tune the tolerance to make an inaccurate result look equivalent.",
                ),
                case(
                    "Distinguish TPU qualification",
                    "A GPU probe succeeds. List what a TPU claim still requires.",
                    "A separately prepared TPU environment, actual TPU allocation/computation/readback and target-specific measurements.",
                    "The GPU receipt does not establish another backend's package or hardware behavior.",
                    "Use the same mathematical oracle where appropriate, while retaining separate environment and device evidence.",
                    "Keep model-independent arithmetic reusable without merging backend qualification.",
                ),
                case(
                    "Handle uncertain device health",
                    "A bounded job is interrupted during device work and its child process is reaped. Decide whether another device job may be declared safe automatically.",
                    "Process cleanup alone does not prove device recovery; retain the outcome for the resource owner to inspect.",
                    "The repository's optional-device workflow treats serious faults separately from an ordinary repairable syntax error and never resets a shared GPU automatically.",
                    "Preserve the receipt, identify the owned device and require the explicit recovery workflow before requalification.",
                    "Separate host-process lifecycle from device state.",
                ),
            ),
            "Hardware acceptance needs actual observations from the selected backend. No source snippet, imported package, CPU fallback or compiler artifact substitutes for allocation, synchronized computation and readback. Avoid global driver changes or device resets as incidental troubleshooting.",
            "Prepare an optional device-study specification with ownership, bounded inputs, source identity, correctness oracle, timing boundary, memory measurements and recovery responsibility. Execute it only through an explicitly prepared compatible workflow; this reading lesson launches nothing.",
            (
                ("Installation and platforms", "https://docs.jax.dev/en/latest/installation.html"),
                (
                    "GPU memory allocation",
                    "https://docs.jax.dev/en/latest/gpu_memory_allocation.html",
                ),
                ("Benchmarking", "https://docs.jax.dev/en/latest/benchmarking.html"),
            ),
            runtime="reading",
        ),
        Unit(
            33,
            "Optional multi-host arrays and collective lifecycle",
            "advanced",
            (32,),
            ("distributed initialization", "global array", "addressability", "collective order"),
            "Specify a multi-process numerical and lifecycle contract with explicit ownership, data placement and failure evidence.",
            r"""Multi-host execution adds process coordination to numerical computation. Each process has local devices and local data, while the program can describe global arrays spanning participants. Initialization and topology must be established before device queries or array computations that depend on the distributed context.

JAX does not launch the participating processes for the user. A separately prepared launcher or job system must provide the owned processes, configuration and lifecycle. The ordinary single-source classroom worker is not that orchestrator and does not receive ambient cluster credentials or arbitrary external endpoints to imitate one.

Every participant must follow a compatible collective sequence. A branch that makes one process call a reduction while another skips it can hang even if each local calculation looks correct in isolation. Logical order, participation and failure handling are therefore part of correctness, not just performance engineering.

Global shape and local addressability are different concepts. A process may own only a subset of a global array's shards. Inspecting its addressable shards is not equivalent to converting the whole global value to a local NumPy array. Global inputs should be constructed from the declared process-local data and sharding plan, with sample identity and counts retained.

A successful local multi-process experiment is useful, but it does not establish behavior across actual hosts or a production network. A multi-host receipt must identify participating processes/devices, topology, source and versions, correct global results, communication observations and lifecycle outcomes. Failure injection must be bounded and confined to resources owned for the study.""",
            r"""Suppose process zero owns three observations and process one owns one. Global mean loss remains \((S_0+S_1)/(N_0+N_1)\), not the mean of local means unless the weighting question is deliberately changed. A replicated global result may be visible on several participants without representing several independent observations. Collective mathematics and collective participation must both be correct.""",
            "",
            (
                case(
                    "Trace a valid global reduction",
                    "Two hypothetical processes report loss sums 6 and 10 with counts 3 and 1. Define the global mean and required collective order.",
                    "Global mean four, with both participants reducing sum and count in the same order.",
                    "An equal average of local means would be six, answering a different weighting question. Agreement on operation order is additional systems evidence.",
                    "**Written trace:** local data -> local sum/count -> collective sum -> collective count -> divide by positive global count -> replicated result four.",
                    "Track the numerator and denominator separately.",
                ),
                case(
                    "Diagnose divergent participation",
                    "Process zero enters a psum while process one takes a branch that skips it. Assess the program before any unbounded run.",
                    "Invalid collective participation; local numerical checks do not qualify it.",
                    "A collective needs the expected participants in a compatible order. A rank-dependent branch around it can prevent completion.",
                    "**Repair plan:** move the collective outside the divergent branch or make participation explicit and matched; use masks or neutral contributions where mathematically justified; test under a bounded owned lifecycle.",
                    "Draw each process's operation sequence side by side.",
                ),
            ),
            (
                case(
                    "Order initialization",
                    "Place distributed initialization, device inspection and global array construction in a valid sequence.",
                    "Initialize first, then inspect distributed devices, then construct arrays under the resulting topology.",
                    "Initialization after device-dependent work can leave the intended distributed contract unavailable or inconsistent.",
                    "Retain configuration identity and fail explicitly if the expected participant/device inventory differs.",
                    "Treat initialization as part of the environment contract.",
                ),
                case(
                    "Distinguish local and global views",
                    "A process can access two of four global shards. Decide what inspecting those two proves.",
                    "Only its local addressable shard values and placement.",
                    "Those observations do not establish the unseen shards or a successful global gather.",
                    "Use an explicit global validation operation when required; do not silently interpret a partial local view as the whole dataset.",
                    "Name the owner of each shard.",
                ),
                case(
                    "Preserve sample identities",
                    "Two processes accidentally load overlapping records while assuming disjoint shards. Explain the consequence.",
                    "The global objective double-counts some observations and changes the effective population.",
                    "A correct collective cannot repair incorrect data partitioning or duplicated sample ownership.",
                    "Validate IDs/counts and the partition policy before interpreting the global loss.",
                    "Data ownership precedes gradient aggregation.",
                ),
                case(
                    "Bound a failure experiment",
                    "Design a test in which an owned participant exits before a collective completes.",
                    "A bounded timeout/cancellation plan, retained per-process diagnostics and explicit cleanup responsibility.",
                    "Unbounded hangs are not acceptable teaching fixtures. Process termination and device recovery remain distinct observations.",
                    "Run only on explicitly owned resources; retain source/topology identity and inspect cleanup before a new job.",
                    "State how the test ends even when the expected failure occurs.",
                ),
                case(
                    "Interpret a local simulation",
                    "A named-axis CPU model computes the correct global mean. Decide whether it demonstrates multi-host throughput.",
                    "It demonstrates the mapped mathematical reduction, not network communication or multi-host performance.",
                    "The actual execution surface determines the scope of the evidence.",
                    "Use the CPU model as a numerical oracle for a later real deployment, retaining separate receipts.",
                    "Do not relabel a simulation as infrastructure acceptance.",
                ),
                case(
                    "Specify a scaling study",
                    "Compare one host with two hosts on a fixed training objective.",
                    "A plan fixing effective data/reduction, recording actual devices, synchronizing work, and separating communication, compilation and execution.",
                    "Changing total batch size or training semantics can make a throughput comparison scientifically misleading even when both programs complete.",
                    "Report the work definition, correctness parity, warmup, repeated completed-work timings and hardware/network limits.",
                    "Choose strong or weak scaling explicitly and explain the changed quantities.",
                ),
            ),
            "A correct local tensor shape does not establish global ownership, participation or recovery. Treat unknown outcomes as unknown rather than automatically replaying work. No cluster is launched and no host credentials are accessed by this reading unit.",
            "Write a distributed-run specification another engineer could review before execution: process inventory, device mesh, data partition, collective sequence, output checks, time limits and cleanup. Identify which checks need real hosts and which can first be modeled on CPU.",
            (
                ("Multi-process JAX", "https://docs.jax.dev/en/latest/501/multiprocess.html"),
                (
                    "Distributed initialization",
                    "https://docs.jax.dev/en/latest/_autosummary/jax.distributed.initialize.html",
                ),
                (
                    "Distributed data loading",
                    "https://docs.jax.dev/en/latest/501/data-loading.html",
                ),
            ),
            runtime="reading",
        ),
        Unit(
            34,
            "Optional kernels, FFI and an independent engineering review",
            "advanced",
            (33,),
            ("custom kernel", "FFI", "layout", "derivative rule", "evidence review"),
            "Decide when a lower-level extension is justified and specify the numerical, transformation and hardware evidence it must produce.",
            r"""A high-level JAX expression is often the clearest implementation of a numerical operation. A custom kernel or foreign-function interface can be justified when a measured limitation or external capability requires it. The decision should start with an observed problem and a correct baseline, not the assumption that lower-level code is automatically faster.

Pallas and FFI expose additional contracts: layouts, memory ownership, indexing, synchronization, supported devices, compiler/runtime versions and transformation rules. An operation with correct forward values may still have an incorrect gradient, incompatible batching behavior or unsafe handling of noncontiguous inputs. These are separate acceptance questions.

A custom derivative must correspond to the implemented mathematical function and its domain. For an affine operation y=ax+b, an input derivative of one is wrong when a is three, even if the forward result passes. Non-unit upstream sensitivities are important because a backward rule that returns only the local derivative can miss the chain-rule multiplier.

Performance qualification follows correctness. Compare completed equivalent work, include required transfers and account for allocation or launch overhead. Profile actual supported hardware rather than borrowing timings from another system. A CPU oracle can validate mathematics; it cannot qualify a GPU kernel's memory behavior, race freedom or device recovery.

The final review also integrates the rest of the course. A numerical component should have a shape/dtype/domain contract, explicit state and key policy, independent derivatives, transformation checks, bounded runtime evidence and an interpretation proportional to that evidence. An advanced learner should be able to identify which layer failed and propose a discriminating next observation.""",
            r"""For \(Y=AX+B\) with scalar A=a, \(\partial L/\partial X=aG\), where \(G=\partial L/\partial Y\). At a=3 and G=4, the input gradient is 12, not three or one. For matrix operations, orientation and layout must be translated explicitly. A forward-only comparison cannot establish the derivative or memory-access contract.""",
            "",
            (
                case(
                    "Review a proposed custom operator",
                    "A hypothetical affine GPU operator returns correct values for contiguous float32 inputs but has no backward or stride tests. Assess its status.",
                    "One narrow forward case only; derivative, layout, dtype and broader execution remain unqualified.",
                    "The correct observed case should be retained without extending its claim to untested interfaces.",
                    "**Review table:** forward contiguous float32 observed; noncontiguous input untested; dtype rejection untested; gradient untested; synchronization/error handling untested; performance unmeasured.",
                    "Separate interface dimensions rather than labeling the whole operator correct.",
                ),
                case(
                    "Find a backward-rule defect",
                    "For y=3x+1, a custom backward returns the incoming cotangent unchanged. Test incoming cotangent four.",
                    "Expected input sensitivity 12; returned four is incorrect.",
                    "The backward omitted the local derivative three. A unit or identity-scale fixture could hide the defect.",
                    "**Independent calculation:** local derivative three times upstream four equals twelve. Repeat with a changed scale and non-unit upstream value before considering a kernel implementation.",
                    "Use a counterexample that changes the missing factor.",
                ),
            ),
            (
                case(
                    "Justify the extension",
                    "List evidence needed before replacing a correct high-level operation with a custom kernel.",
                    "A measured limitation, equivalent work definition, supported target and independent numerical oracle.",
                    "Complexity is justified by a concrete benefit and an acceptance plan, not by the API's lower level.",
                    "Retain the high-level baseline and state the bottleneck the extension is intended to address.",
                    "Measure before choosing the optimization.",
                ),
                case(
                    "Define input layout",
                    "Specify how an operator handles transposed or strided inputs.",
                    "Either correct support or an explicit validated refusal/copy policy.",
                    "A shape alone does not describe memory layout. Silently assuming contiguity can return wrong values or access invalid memory.",
                    "Include a noncontiguous counterexample and retain the resulting policy in the public interface.",
                    "Translate both dimensions and strides.",
                ),
                case(
                    "Qualify transformation composition",
                    "A custom operation has a VJP. Decide whether JVP, vmap and higher derivatives are automatically accepted.",
                    "No; each required transformation needs its own supported rule and evidence.",
                    "A valid reverse rule does not imply every other transformation mode is implemented.",
                    "Test the compositions actually advertised and explicitly reject or exclude unsupported ones.",
                    "Use the custom_jvp/custom_vjp distinction from jax-022.",
                ),
                case(
                    "Design a fair kernel benchmark",
                    "Compare a fused operator with a sequence of high-level operations.",
                    "Matched inputs/outputs, synchronization, warmup, transfers, allocation policy and actual hardware identity.",
                    "A faster dispatch-only measurement or omitted transfer is not a valid completed-work speedup.",
                    "Validate values and derivatives first, then retain repeated timings and a profile of the measured boundary.",
                    "Ensure fusion has not changed the requested result or precision.",
                ),
                case(
                    "Preserve a CPU oracle",
                    "A GPU backend is unavailable. Define what useful work can still be completed.",
                    "Mathematical derivation, small CPU reference, interface review and planned failure cases, with GPU acceptance pending.",
                    "Unavailable hardware limits execution evidence but does not prevent rigorous source and numerical preparation.",
                    "Mark compilation, runtime, device correctness and profiling separately; do not fabricate a passed GPU check.",
                    "Keep missing evidence explicit without discarding completed analysis.",
                ),
                case(
                    "Defend the final result",
                    "Prepare a concise review of an independently built JAX component using the course's evidence layers.",
                    "A reproducible artifact and argument covering purpose, assumptions, source, tests, runtime observations, limits and unresolved risks.",
                    "The reviewer should be able to challenge a concrete claim and identify the observation supporting it. A lesson-completion count is not the evidence.",
                    "Use an unfamiliar input or failure case, explain the diagnosis, and propose a test that would distinguish your repair from a plausible alternative.",
                    "Demonstrate transfer and judgment rather than repeating the reference.",
                ),
            ),
            "Do not advertise unsupported dtype/layout/transform combinations. A successful source build is not device correctness, and a correct value is not a valid backward rule. Preserve resource ownership and the high-level oracle throughout optimization.",
            "Select one optional extension only after identifying an actual need. Produce a scoped design and qualification matrix before preparing the external toolchain. The default JAX CPU course remains complete without custom kernels, paid services or accelerator access.",
            (
                ("Pallas", "https://docs.jax.dev/en/latest/pallas/index.html"),
                ("FFI", "https://docs.jax.dev/en/latest/ffi.html"),
                (
                    "Custom derivative rules",
                    "https://docs.jax.dev/en/latest/301/custom-jvp-vjp.html",
                ),
            ),
            runtime="reading",
        ),
    ]
)
