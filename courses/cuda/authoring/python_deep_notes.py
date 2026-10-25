"""Extended mechanism chapters for the CUDA Python and distributed-data route."""

DETAILS = {
    17: r"""## Read a shared-buffer contract line by line

Suppose a producer owns a float32 matrix with shape `(2, 3)` and a consumer receives a view. There are three independent agreements. **Representation** says how six values are encoded and addressed. **Lifetime** says who keeps the allocation alive. **Ordering** says when the writes that initialized those values become visible to the consumer. Correct representation cannot repair an allocation freed too early, and a long-lived allocation cannot repair a missing synchronization edge.

A useful ownership drawing is `producer object -> allocation <- consumer view`. The arrows are lifetime dependencies, not copies. Deleting one Python name only removes one reference; another owner can keep storage alive. Conversely, a raw integer pointer is not necessarily an owner. Before passing a pointer to an asynchronous consumer, retain the appropriate owner through that consumer's completion. Avoid modifying either view concurrently unless the algorithm explicitly defines that sharing.

For modern DLPack object interchange, read the producer's `__dlpack__` and `__dlpack_device__` protocol and the consumer's documented import function. Stream negotiation exists so a consumer can ask for data ready on its execution stream. Legacy capsule interfaces can have different one-consumption ownership rules; do not copy an old capsule recipe into a modern object API without checking it. `copy=False` where supported expresses a copy constraint, not a promise that every other contract is automatically satisfied.

Autograd adds a fourth agreement: the computation graph. Sharing a tensor's storage with another library does not by itself add that library's arithmetic to the first framework's differentiation graph. A forward output may be numerically perfect while the gradient is absent or wrong. The test sequence is therefore storage/value parity, deliberate alias mutation, lifetime safety, non-default stream behavior, and then independent gradient behavior if gradients are part of the objective.
""",
    18: r"""## Build the dependency graph before writing the API calls

Consider two batches and two device streams. Stream A copies and transforms batch 0; stream B prepares batch 1. The host can submit both without waiting only when their allocations are distinct or their reuse is ordered. If both write the same staging buffer, the apparent overlap is a race. Double buffering introduces two owners and alternates them, but each buffer must still wait for its previous consumer before reuse.

An event is a marker in an ordered stream. Recording E after the transform means E becomes complete after earlier work in that stream. A wait for E in another stream places later consumer operations after that completion. This is different from waiting on the host: a host wait delays Python submission, while a stream wait can preserve useful overlap elsewhere. The resulting partial order is more precise than placing a device-wide synchronize after every statement.

The host can also accidentally serialize the graph. Calling `.item()`, `.get()` or `.numpy()` on a device result can require it to be ready on the host. Logging every intermediate scalar may insert repeated waits between kernels. This is not inherently wrong, but it changes the benchmark and can remove the overlap the program was supposed to measure. Aggregate bounded diagnostics where the application permits and preserve one explicit final output boundary.

Allocator reuse is the subtle companion to stream ordering. A library may know the allocation was used on its own stream but not that an external consumer still reads it. Use that library's documented external-stream or allocation-recording protocol. Do not solve this by keeping arbitrary global references forever: that trades a race for a memory leak. The acceptance test uses two non-default streams, repeated bounded inputs with distinct values, explicit producer/consumer ordering and a final comparison against the CPU oracle.
""",
    23: r"""## Derive the update before invoking autograd

For observations \(x_i\), targets \(y_i\), scalar parameter \(w\) and batch size \(N\), use mean squared error:

\[
L(w)=\frac{1}{N}\sum_{i=1}^{N}(wx_i-y_i)^2,
\qquad
\frac{dL}{dw}=\frac{2}{N}\sum_{i=1}^{N}x_i(wx_i-y_i).
\]

The residual is prediction minus target. The chain rule multiplies its factor of two by the derivative of the prediction, which is the input. At the supplied initial weight, residuals are -2 and -4. Multiplying by inputs gives -2 and -8; doubling and averaging gives -10. SGD subtracts learning rate times gradient, so subtracting a negative gradient increases the weight. This sign check is a useful debugging habit.

In PyTorch, `requires_grad=True` requests gradient tracking on the parameter. `loss.backward()` accumulates into its `.grad`, so an ordinary repeated training loop must zero old gradients at the chosen update boundary. The optimizer owns references to the trainable parameter objects; replacing a parameter object carelessly can leave the optimizer updating the old one. Inspect both parameter identity and device when debugging.

In TensorFlow, `GradientTape` records operations involving watched trainable variables in its scope. `tape.gradient(loss, w)` returns the derivative, which is then paired with the variable for `apply_gradients`. A missing derivative is different from a zero derivative. Check that the intended variable was watched and that the forward computation stayed connected to it. Both frameworks need parameters, inputs and relevant optimizer state on compatible devices; neither makes a cross-device mismatch mathematically meaningful.
""",
    26: r"""## Precision policy, scaling and the optimizer boundary

A floating-point format allocates bits to sign, exponent and significand. More exponent range reduces overflow and underflow; more significand precision distinguishes nearby values. fp16 and bfloat16 have the same storage width but different allocations, so they are not interchangeable numerical policies. Hardware support for their fast operations must also be checked independently of a Python dtype existing.

Loss scaling multiplies the scalar loss by a positive scale \(s\), which multiplies its gradients by \(s\). Before the optimizer applies an update, divide by that same scale. In exact arithmetic:

\[
\nabla(sL)/s=\nabla L.
\]

The purpose is to change intermediate representability in finite precision, not change the intended learning rate. Dynamic scaling detects nonfinite gradients and adjusts according to the framework's supported procedure. A skipped optimizer update and a completed batch are different counters; a training report should not hide repeated overflow by reporting only loop iterations.

Gradient clipping belongs after unscaling because its threshold is defined in the original gradient units. Likewise, accumulating multiple microbatches needs a consistent scaling/normalization strategy across the effective batch. Do not update the scale halfway through a set of gradients that will be combined under one scale assumption.

For PyTorch, place forward and loss computation in the selected autocast context and follow the pinned `torch.amp` scaler sequence. For TensorFlow/Keras, select the dtype policy before layer construction, inspect variable dtype versus compute dtype, and follow that release's loss-scaling optimizer API. The supplied CPU scaling model is a mathematical explanation; it does not claim that either framework selected tensor cores. Qualification compares finite gradients, update direction, short loss trajectory, held-out metric, memory and synchronized completed-step timing against full precision.
""",
    33: r"""## What a framework operator must promise

Start with a schema in words: the input is a contiguous float32 tensor on one declared device; scale and bias are finite host scalars; output has the same shape and dtype; output is newly allocated; empty input produces an empty output. Every clause becomes a validation or implementation obligation. If the accepted contract later includes noncontiguous tensors, the kernel must consume strides or the wrapper must explicitly pack data and expose the cost.

The CUDA entrypoint receives raw addresses and scalar values. It cannot infer a Python object's meaning from those bytes. The host wrapper validates metadata, allocates output through the framework's allocator, chooses the current execution stream correctly and submits a bounded launch. Submission errors can be immediate, while illegal device accesses may appear only at a later synchronization point. Preserve the first meaningful error instead of blaming whichever later call happened to synchronize.

PyTorch integration needs a registered operator and appropriate backend implementation, with metadata or fake-tensor behavior when the chosen compilation path requires it. TensorFlow integration defines the op and shape behavior and supplies a kernel implementation for its device placement system. These are separate projects with different build and registration contracts. One working C++ function does not qualify both.

The practical acceptance matrix includes normal data, zero elements, a nonmultiple tail, rejected dtype, rejected layout, wrong-device input, stream ordering and output aliasing. The custom operator should match a native framework expression before performance is considered. A classroom single-file Python pad can inspect or call a prepared operation; it cannot safely infer arbitrary build commands, download compilers or manufacture a multi-file extension project from lesson metadata.
""",
    34: r"""## Derive the vector-Jacobian product, including shared parameters

Let \(z_i=ax_i+b\), \(y_i=\max(0,z_i)\), and let \(g_i\) be the upstream derivative of a scalar objective with respect to \(y_i\). Away from the kink, define \(m_i=1\) when \(z_i>0\) and zero otherwise. The backward equations are:

\[
\bar x_i=g_i a m_i,\qquad
\bar a=\sum_i g_i x_i m_i,\qquad
\bar b=\sum_i g_i m_i.
\]

Input gradients are elementwise because each input influences one output. Scale and bias gradients reduce over all outputs because those parameters are shared. Forgetting those reductions is a common error that can remain hidden when testing only one element. Broadcasting adds another version of the same issue: a broadcast dimension's gradient must be reduced back to the original parameter shape.

A central finite difference computes \([f(x+\epsilon)-f(x-\epsilon)]/(2\epsilon)\). Too large an epsilon introduces truncation error; too small can lose the difference to rounding. Use small double-precision inputs away from nondifferentiable boundaries and vary epsilon if a discrepancy is ambiguous. At the ReLU kink, test the documented chosen derivative rather than insisting a symmetric finite difference define it.

Backward also has memory and stream contracts. Saved forward intermediates must remain valid until consumed. Recomputing a mask can save storage only when it reproduces the same forward branch under the supported precision policy. Test non-unit upstream gradients, because differentiating a sum supplies all ones and may hide missing multiplication by the incoming gradient. State whether second derivatives are supported and test them separately; first-order correctness does not imply higher-order graph support.
""",
    36: r"""## Follow attention from shapes to memory traffic

For one head, queries have shape \((L_q,d)\), keys \((L_k,d)\), and values \((L_k,d_v)\). Scores have shape \((L_q,L_k)\). The operation is:

\[
S=QK^{\mathsf T}/\sqrt d,\quad
P=\operatorname{softmax}(S+M),\quad
O=PV.
\]

The mask \(M\) contributes zero for allowed positions and an effectively negative-infinite value for excluded positions under the chosen implementation. Causal masks depend on query/key position alignment, especially when decode uses a short query and a longer cache. Do not assume a square lower-triangular mask is correct for every cache layout.

A straightforward implementation writes the entire score matrix, reads it for normalization, writes probabilities, then reads those for the value product. When sequence length doubles, a square score matrix has four times as many elements. Memory-efficient attention reorganizes tiling and normalization to avoid some full intermediates. This is an algorithmic memory-traffic improvement, not a claim that all attention has linear arithmetic complexity.

For a row, subtracting the maximum leaves softmax unchanged because the same exponential factor divides out. A streaming/tiled implementation must combine partial normalization state correctly when a later tile changes that maximum. That state consists of a running maximum, a normalized exponential sum and a correspondingly rescaled weighted-value accumulator. Losing one rescaling factor can produce plausible-looking but wrong outputs.

Validation should include unequal query/key lengths, a causal case, padding, non-unit upstream gradients, and the explicitly defined fully masked behavior. The small PyTorch variant compares a supported attention API to the explicit reference; the TensorFlow variant builds the same reference arithmetic. Neither prints a fictitious fused-kernel identity. A real fast-backend comparison requires the prepared implementation, device trace and accepted dtype/head-size matrix.
""",
    37: r"""## Fine-tuning choices and what remains resident

For a dense weight matrix \(W\in\mathbb R^{m\times n}\), a low-rank update can be written \(\Delta W=AB\), where \(A\) has shape \((m,r)\) and \(B\) has shape \((r,n)\). The trainable update contains \(r(m+n)\) parameters instead of \(mn\). Rank controls the update's representational capacity as well as its parameter count; a smaller rank is a modeling decision that needs validation.

Freezing \(W\) does not remove the forward multiplication by \(W\). Inputs still traverse the base model, and activations may still be needed to train adapters at earlier or later layers. Optimizer state for the frozen weights can disappear when those weights are genuinely excluded from optimization, but the weights themselves remain resident unless an explicit offload or quantization scheme changes their storage. Count these categories separately.

The paired framework examples intentionally use a tiny low-rank matrix rather than downloading a model. The base is an identity matrix, one adapter factor is small and the other starts at zero. The zero update preserves the base function initially. Gradients for the two factors can differ at that initialization, so verify actual gradients instead of assuming both must change on the first step. Then connect this mechanism to attention projection matrices in the existing transformer curriculum.

A complete adaptation study defines the target task, training examples, held-out evaluation, trainable-variable list, optimizer membership, precision policy, sequence/batch cap, checkpoint and rollback. Subject-matter factual knowledge is not guaranteed by lowering training loss: evaluate whether answers use the intended domain evidence and compare a retrieval baseline where appropriate. Parameter-efficient tuning, RAG and prompt design solve overlapping but distinct problems. The GPU lesson supplies resource and training mechanics, while the applied-LLM route supplies grounded-answer and task evaluation design.
""",
    38: r"""## Derive a cache budget before serving requests

For a dense key/value cache with \(L\) layers, batch \(B\), stored positions \(T\), KV heads \(H_{kv}\), head width \(d_h\), and element width \(s\) bytes:

\[
\text{cache bytes}=2LBTH_{kv}d_hs.
\]

The factor two accounts for keys and values. This is the tensor payload, not allocator padding, fragmentation, page tables, temporary buffers or scheduler state. A paged cache changes allocation management but does not make its underlying values free. Grouped-query attention can use fewer KV heads than query heads, so inspect the model rather than assuming both counts match.

During prefill, many query positions are processed together. During decode, each new query reads the growing history, often producing a very different arithmetic-intensity pattern. Report time to first token and subsequent token latency separately, and state whether tokenization, sampling and output transfer are included. A throughput gain from batching may increase a single user's queueing delay.

Cache correctness requires position and mask consistency. Compare uncached and cached logits at every step for a small deterministic model, with dropout disabled and the same input prefix. Test batch members with different valid lengths and an explicit maximum generation length. If quantization is introduced, compare output quality and numerical error independently. A fake-quantization rounding exercise remains an educational approximation until a real packed low-bit backend executes and its memory/performance are measured.
""",
    49: r"""## Trace one query across language boundaries

A PySpark expression such as `df.groupBy("team").sum("amount")` builds a relational plan. Python is the authoring interface, but supported SQL execution is generally coordinated by Spark's JVM engine. Scala constructs a comparable plan directly through JVM APIs. The key question for GPU acceleration is the resulting supported physical work, not which of those two languages typed the expression.

An ordinary Python UDF is different: Spark must invoke Python code with its declared input/output contract. Vectorized pandas UDFs can reduce interchange overhead, but their body remains whatever Python and libraries actually execute. Arrow improves representation exchange; it does not translate arbitrary Python control flow into GPU instructions. A purpose-built GPU UDF integration needs explicit device allocation and package rules.

cuDF's local dataframe API works within a process and uses GPU columnar algorithms. The Spark plugin connects supported columnar operations to Spark's distributed scheduling, joins, shuffles, retries and SQL semantics. Spark RAPIDS ML adds a separate estimator surface. Keep these names in a diagram with arrows for data movement and process boundaries; treating them as one magic GPU switch leads to misleading performance claims.

The practical beginner sequence is CPU semantic oracle, ordinary Scala and PySpark query, logical/physical plan reading, then optional GPU plugin qualification. The same schema and expected rows carry through all four steps. This lets a learner on any CPU-only machine complete the reasoning and programming foundation without pretending that a container acquired NVIDIA hardware.
""",
    51: r"""## Read a plan as a sequence of contracts

A scan establishes a schema and row source. A filter applies a predicate, including SQL null logic. A projection chooses or computes columns. An exchange changes partition ownership. A join or aggregate combines records according to key and multiplicity rules. Each node has both a semantic contract and a physical representation. A GPU replacement must preserve the first while changing the second.

Start by drawing the logical intent without backend labels. Then inspect `explain("formatted")` in the exact Spark environment. Highlight CPU/GPU representation transitions and exchanges separately: a device transfer is not the same operation as redistribution across executors, although one stage can involve both. Add operator metrics after an action completes. If AQE is enabled, retain the final executed plan because broadcast and partition decisions may have changed.

The plugin's explain diagnostics can report why a node is not selected for GPU execution. Read the reason at the expression and dtype level. An unsupported child can change the useful acceleration region around it, and a small unsupported expression can force expensive conversions. Do not rewrite the query merely to maximize the count of GPU nodes; preserve semantics and compare complete latency.

A useful review table has columns node, semantic role, input/output representation, supported status, fallback reason, rows/batches, elapsed time and spill. This turns a screenshot into an argument. A GPU node in a planned diagram is weaker evidence than that node in an executed query with metrics, and even the executed node must be accompanied by a correct result comparison.
""",
    52: r"""## Four states that should never share one success label

**CPU baseline** means ordinary Spark runs with the GPU plugin absent or disabled. It should work on a supported CPU-only host and is the rollback and semantic comparison. **Plugin initialization failure** means the requested accelerated environment could not start correctly, perhaps because device exposure or native libraries are unavailable. That is a failure, not a successful fallback.

**Operator fallback** means a functioning plugin environment keeps an unsupported operator or expression on CPU while other supported work may use the GPU. **GPU execution** means the intended compatible operator actually ran on the device and produced an accepted result. These states require different troubleshooting and should be recorded separately in the learning notebook.

Suppose a query filters, invokes a Python UDF, then aggregates. The UDF may create a boundary even when the surrounding operators are supported. Replacing it with built-in expressions can expose the algebra to Catalyst, but only if the replacement matches null behavior, input types, overflow, timestamps and any error semantics. A mathematically similar expression can still differ under SQL's type rules.

Use the release's supported-operator list and `spark.rapids.sql.explain=NOT_ON_GPU` diagnostics as aids, not universal truths detached from versions. The published table may be generated against a particular Spark release; inspect the matching plugin and distribution notes. An explicit CPU/GPU parity test over adversarial tiny fixtures is the final semantic guard before measuring a larger workload.
""",
    55: r"""## Resource accounting versus physical isolation

The executor GPU amount describes how much GPU resource Spark assigns to an executor. A task GPU amount describes how much of that assignment a task consumes for scheduling. CPU cores and `spark.task.cpus` impose another bound. The plugin's concurrent-GPU-task setting limits admission to GPU work inside the executor. These controls can all constrain one task without being interchangeable.

In a simplified configuration with one assigned GPU, four CPU slots and a task GPU amount of 0.25, resource accounting allows at most four tasks. A plugin GPU concurrency of two can allow only two of those tasks into GPU work simultaneously. Others may prepare input or wait, depending on implementation. This can improve overlap when preparation is expensive, but the gain is workload-specific.

A fractional GPU request does not partition device memory into equal private slices. Two admitted tasks can each allocate variable-size batches and workspaces, and their combined live set can exceed VRAM. Hardware partitioning technologies have distinct administration and support contracts and must not be inferred from Spark fractions. Measure memory alongside throughput when changing concurrency.

Before a real run, verify resource discovery and assigned device addresses inside the exact executor environment. The plugin's supported executor-to-GPU mapping is release-specific and currently documented separately from general Spark scheduling. Copying a generic Spark GPU configuration without checking plugin requirements can produce a valid-looking but unsupported setup. Keep all resource choices in the compatibility and experiment ledger.
""",
    57: r"""## Derive join cardinality before tuning it

For an inner equijoin, let \(l_k\) be the number of left records for key \(k\) and \(r_k\) the number on the right. Output cardinality is:

\[
\sum_k l_k r_k.
\]

This explains why duplicate dimension keys can unexpectedly multiply a fact table. A GPU cannot optimize away required output rows. If the application assumes a unique dimension key, validate uniqueness as an input contract. Applying `distinct` after the join is not a general repair because it can erase legitimate duplicate facts.

Broadcast avoids redistributing the large side by replicating a suitably small side, but each executor must accommodate that replicated structure and the join's live state. A shuffle join moves records to key owners. Skew can make one key dominate both memory and runtime. Inspect maximum and percentile partition sizes, not only average rows per partition.

AQE may change the chosen join using observed statistics. Record the final executed plan and compare output multiplicity before and after any rewrite. Salting a hot key requires careful duplication or redistribution of the matching side and a proof that every intended pair appears once. Outer joins add unmatched-row/null behavior, making an informal salting recipe particularly risky. Start with the tiny duplicate-key oracle, then expand only after exact semantic parity.
""",
    60: r"""## Avoid the GPU-UDF shortcut trap

A common mistake is to create a GPU model or dataframe inside every UDF call. That can repeatedly initialize contexts, transfer tiny batches and duplicate model storage. Even when each call is numerically correct, the process and batching design can overwhelm the useful GPU work. A vectorized UDF changes batching, but still needs explicit resource ownership and package compatibility.

A declarative built-in expression gives Catalyst visibility into algebra and types. Prefer it when it expresses the same contract. When a genuinely custom GPU operation is needed, define per-worker initialization, bounded batch sizes, device assignment, input/output schema, null policy and cleanup. Do not let every partition choose device zero independently on a multi-executor host.

Machine-learning training is another boundary. A SQL acceleration plugin does not automatically coordinate gradient collectives across Spark tasks. Separate GPU-aware ML integrations can provide reviewed estimator behavior, but they need their own supported algorithms, versions and quality comparisons. The curriculum therefore links the Spark specialization to the PyTorch/TensorFlow distribution chapters without treating one scheduler as a drop-in replacement for the other.

For the included null-preserving doubling example, the built-in expression and reference function agree on integers and missing values. The next meaningful test adds type boundaries and verifies the output schema. Only after that should a real Spark plan be inspected for supported acceleration. This sequence makes correctness visible before any GPU configuration is introduced.
""",
    63: r"""## An end-to-end acceptance notebook

Begin with the grain of each table. A sales row represents one product quantity observation; the price table has one row per product under the declared input contract. Validate price-key uniqueness before joining. Derive revenue using exact integer cents or the chosen exact decimal schema rather than introducing floating rounding into a simple accounting example.

The Scala and PySpark programs should use the same explicit schemas and sorted output. Both build local finite fixtures, perform a declarative join and aggregate, collect only the tiny final table and stop the owned Spark session in a finally block. Printing the formatted plan teaches physical execution, but the result assertions remain independent literal expectations. Changing input cardinality or null rules requires updating the mathematical derivation, not merely copying observed output into the expected result.

On an optional GPU environment, repeat the same query and input. Add plugin release, jar checksum, Spark/Scala/JDK versions, CUDA variant, driver, GPU model and executor-resource configuration to the notebook. Capture the final executed plan after materialization and record operator fallback reasons, device use, task concurrency, spill and total completion time. Keep GPU evidence separate from the already completed CPU language parity tests.

The capstone is complete when another learner can reproduce the CPU semantics, explain the plan and understand exactly what remains unqualified. Real GPU performance is an additional evidence layer. A useful report can conclude that the tiny fixture is too small for a meaningful speed comparison while still demonstrating correct setup and operator execution on prepared hardware.
""",
}
