# cuda-113: explained solutions

These answers explain the six practice tasks. CPU reference programs are mathematical or semantic checks, not proof of CUDA execution.

## Exercise 1: Classify four execution layers

Separate local dataframe Spark operators UDF processes and training.

**Approach.** Classify four execution layers: a local dataframe library such as cuDF on one process, Spark physical operators planned by Catalyst, Python UDF worker processes, and model training code that consumes the results.

**Why it is correct here.** Each layer has a different owner of execution. Catalyst can replace operators it understands, but it cannot see inside UDF processes or training code, so GPU use must be checked per layer.

**A plausible wrong approach.** Calling the whole pipeline GPU-accelerated because one layer uses the GPU hides the layers that still run on CPU and the transfers between them, which often dominate.

**How to verify.** For one sample pipeline, write each step beside its layer and the evidence that would show its device, such as a plan node name or the library object type.

## Exercise 2: Explain cuDF versus plugin

The plugin integrates cuDF with Spark planning and execution.

**Approach.** Explain the relationship: cuDF is a GPU dataframe library, while the RAPIDS Accelerator is a Spark plugin that uses cuDF kernels to execute Spark physical operators in place of CPU ones.

**Why it is correct here.** Spark code keeps the Spark API, and the plugin rewrites the physical plan at execution time. cuDF code calls GPU functions directly and has no Spark planner.

**A plausible wrong approach.** Assuming installing cuDF on executors accelerates Spark SQL confuses the two, since without the plugin configured Spark never routes operators to cuDF.

**How to verify.** Check the Spark configuration for the plugin class and inspect the executed plan for GPU operator names. In a cuDF script, check the dataframe type.

## Exercise 3: Identify an opaque UDF

Arbitrary host code is not automatically accelerated.

**Approach.** Identify an opaque UDF: a Python function applied row by row, such as one that parses a string with custom logic, is arbitrary host code that Catalyst cannot translate.

**Why it is correct here.** Spark sends rows to a Python worker and receives results back. The plugin cannot run arbitrary Python on the GPU, so the plan gains a CPU section around the UDF.

**A plausible wrong approach.** Assuming a UDF runs on the GPU because surrounding operators do ignores the boundary, and the measured time then includes conversions the plan does not advertise.

**How to verify.** Look for the Python evaluation node in the executed plan and the transitions immediately before and after it.

## Exercise 4: Write equivalent Scala and PySpark expressions

Use the same schema null policy and aggregation.

**Approach.** Write equivalent expressions: Scala `df.groupBy("label").agg(sum("value"))` and PySpark `df.groupBy("label").agg(F.sum("value"))`, both with the same schema and null policy, giving A 6 and B 14 for values `[2, 4, 6, 8]`.

**Why it is correct here.** Both front ends produce the same logical plan through Catalyst, so the language does not change the relational result.

**A plausible wrong approach.** Writing the PySpark version with a Python loop over collected rows changes where the work happens and loses the equivalence, even if the totals match.

**How to verify.** The reference asserts `totals == {'A': 6, 'B': 14}`. Run both versions and compare their outputs and physical plans.

## Exercise 5: Define CPU-only progress

Run semantic references and inspect teaching plans.

**Approach.** Define CPU-only progress: run semantic references such as the grouped totals, and inspect teaching plans, without claiming any GPU execution.

**Why it is correct here.** On a machine without a GPU, correct semantics and plan reading are real progress. GPU behavior remains unverified, and saying so keeps the record honest.

**A plausible wrong approach.** Reporting a CPU run as evidence that the GPU path works confuses semantic parity with accelerated execution.

**How to verify.** Each CPU result should be labeled as a CPU reference, as the reference output does with `no GPU execution claimed`.

## Exercise 6: List real GPU evidence

Require compatible GPU runtime executed operator plan metrics and equal results.

**Approach.** List real GPU evidence: a compatible GPU runtime, plugin enabled, the executed physical plan showing GPU operators, operator metrics from the run, and results equal to the CPU reference.

**Why it is correct here.** Each item rules out a separate failure, such as a plugin that is configured but falls back on every operator, or a GPU run that computes a different result.

**A plausible wrong approach.** Presenting only a configuration file as GPU evidence shows intent but not execution.

**How to verify.** Collect each item from a single run on the target host and attach them together in the validation record.

## Reference observation

Grouped totals A 6 and B 14; no GPU execution claimed.

The reference file is `courses/cuda/spark/references/cuda-113_cpu.py`. It includes deterministic assertions. These assertions establish the supplied bounded CPU example; hardware execution and architecture-specific performance remain separate checks.
