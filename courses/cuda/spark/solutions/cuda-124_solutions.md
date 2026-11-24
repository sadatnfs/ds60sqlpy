# cuda-124: explained solutions

These answers explain the six practice tasks. CPU reference programs are mathematical or semantic checks, not proof of CUDA execution.

## Exercise 1: Classify four APIs

Name SQL UDF pandas-style and local GPU dataframe surfaces.

**Approach.** Classify four API surfaces: built-in SQL and DataFrame expressions, row-at-a-time Python UDFs, pandas-style vectorized UDFs that receive Arrow batches, and a local GPU dataframe library such as cuDF called inside a task.

**Why it is correct here.** Each surface hands data to a different executor. Built-in expressions stay in the planner's view, while the other three move data into Python processes where Catalyst and the plugin cannot follow.

**A plausible wrong approach.** Treating a pandas UDF as equivalent to a built-in because it is vectorized ignores the process boundary and serialization that still surround it.

**How to verify.** For one example transformation, write it on all four surfaces and inspect the executed plan for Python evaluation nodes in the last three.

## Exercise 2: Replace an equivalent simple UDF

Use a built-in expression if null/type semantics match.

**Approach.** Replace a simple UDF that returns `x*2` with the built-in expression `col('x') * 2`, after confirming the null and type semantics match: null input gives null output in both.

**Why it is correct here.** The built-in expression is visible to the optimizer and can run on the GPU through the plugin, removing the transitions to and from a Python worker.

**A plausible wrong approach.** Replacing a UDF that maps null to 0 with the built-in, which keeps null, changes results while appearing to be the same arithmetic.

**How to verify.** The reference asserts `[2, None, 6]` from `[1, None, 3]`. Run the built-in on the same values and compare, including the null position and the result type.

## Exercise 3: Explain Arrow limits

Interchange format is not an execution device.

**Approach.** Explain Arrow limits: Arrow is an in-memory columnar interchange format that lets Spark pass batches to Python efficiently, but it is not an execution device.

**Why it is correct here.** Arrow reduces serialization cost at the boundary. The UDF body still runs wherever its own code runs, usually on the CPU.

**A plausible wrong approach.** Assuming that enabling Arrow moves UDF work to the GPU confuses data format with execution location.

**How to verify.** Compare UDF time with Arrow enabled and disabled on CPU, and check the plan for the same Python evaluation node in both.

## Exercise 4: Define GPU-aware UDF ownership

Record assigned device batches and cleanup.

**Approach.** Define GPU-aware UDF ownership: each task records which device address it was assigned, bounds the batch it moves to that device, and frees device memory before returning.

**Why it is correct here.** Several Python workers can share one GPU. Without explicit ownership they all default to device 0 and their memory adds up without any coordination.

**A plausible wrong approach.** Calling a GPU library from every partition with no device assignment risks oversubscription and out-of-memory errors that appear only at higher concurrency.

**How to verify.** Log the assigned address and the peak device memory per task, and confirm memory returns to its baseline after each task finishes.

## Exercise 5: Distinguish SQL and ML acceleration

They are separate integrations.

**Approach.** Distinguish SQL acceleration, which replaces Spark operators through the plugin, from ML acceleration, which uses separate GPU training libraries with their own integration.

**Why it is correct here.** The two have different configuration, support lists and evidence. A GPU-accelerated ETL plan says nothing about whether the training step used the GPU.

**A plausible wrong approach.** Reporting the whole pipeline as accelerated because the SQL plan shows GPU operators omits the training step.

**How to verify.** Collect evidence separately: the executed plan for SQL and the training library's device logs or metrics for ML.

## Exercise 6: Design quality parity tests

Use same split target metric and preprocessing.

**Approach.** Design quality parity tests for GPU and CPU model training: same train and test split, same target, same metric and same preprocessing, comparing the metric within a stated tolerance.

**Why it is correct here.** Training algorithms on different backends can differ in floating-point order and defaults, so model quality, not identical weights, is the right comparison.

**A plausible wrong approach.** Comparing a GPU model trained on a different split with a CPU model attributes data differences to the backend.

**How to verify.** Fix the split by a seeded key, record preprocessing steps, and report both metrics with the tolerance used.

## Reference observation

Null-preserving expression produces [2, None,6].

The reference file is `courses/cuda/spark/references/cuda-124_cpu.py`. It includes deterministic assertions. These assertions establish the supplied bounded CPU example; hardware execution and architecture-specific performance remain separate checks.
