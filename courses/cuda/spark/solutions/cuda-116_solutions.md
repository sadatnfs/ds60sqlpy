# cuda-116: explained solutions

Compare with your [worksheet](../lessons/cuda-116.md) attempt.

## Exercise 1: Classify fallback versus unavailable device

Fallback is per supported execution environment.

**Approach.** Classify the two states: a machine with no visible GPU and the plugin disabled runs the CPU baseline, while a GPU machine with the plugin enabled can still run one operator on CPU through fallback.

**Why it is correct here.** Fallback is a per-operator decision inside a valid plugin environment. An unavailable device is an environment condition that requires the CPU configuration for the whole job.

**A plausible wrong approach.** Calling a GPU-less run a fallback suggests the plugin was active and made per-operator choices, when actually it never started.

**How to verify.** The reference asserts the first state has `plugin_enabled` False and the second has a CPU operator inside an enabled plugin. Check `spark.plugins` and plan names for each state.

## Exercise 2: Find an unsupported expression

Consult operator type and expression rules.

**Approach.** Find an unsupported expression by consulting the plugin's supported operators and expressions for the selected release, and by reading fallback explanations the plugin can log.

**Why it is correct here.** Support depends on the operator, the expression and the data types involved. An aggregate can be supported while a specific function inside it is not.

**A plausible wrong approach.** Assuming support from the operator name alone misses expression-level and type-level restrictions, which are the usual cause of fallback.

**How to verify.** Enable the plugin's explain output for fallback reasons and confirm the listed reason names the expression found in the documentation.

## Exercise 3: Count boundary costs

Include representation and transfer costs.

**Approach.** Count boundary costs for GPU aggregate, CPU UDF, GPU projection: two transitions, each converting columnar device batches to host rows or back, with data copies in both directions.

**Why it is correct here.** Every transition copies data and changes representation. Two transitions around a single UDF can cost more than the UDF itself.

**A plausible wrong approach.** Assuming only the UDF runs slower and the rest stays fast ignores that the transitions stall the GPU sections on both sides.

**How to verify.** Read the transition nodes and their metrics in the executed plan, and compare their time with the UDF node's time.

## Exercise 4: Rewrite an opaque function declaratively

Use built-in expressions only when equivalent.

**Approach.** Rewrite an opaque function declaratively when an equivalent built-in exists, such as replacing a Python UDF that uppercases and trims with `upper(trim(col))`.

**Why it is correct here.** Built-in expressions are visible to Catalyst and can be supported by the plugin, removing the transitions around the UDF.

**A plausible wrong approach.** Rewriting with a built-in that differs on edge cases, such as whitespace or null handling, changes results while appearing equivalent.

**How to verify.** Run parity tests on nulls, empty strings and Unicode before accepting the rewrite, then confirm the transitions disappeared from the plan.

## Exercise 5: Preserve edge semantics

Test nulls overflow strings and timestamps.

**Approach.** Preserve edge semantics: test nulls, integer overflow, strings with multibyte characters and timestamps across time zones on both the CPU and GPU paths.

**Why it is correct here.** GPU implementations aim to match Spark semantics, but edge cases are where differences appear, and some may be documented incompatibilities.

**A plausible wrong approach.** Testing only typical values passes implementations that disagree exactly where production data is unusual.

**How to verify.** Build a small table containing each edge case and compare CPU and GPU outputs row by row.

## Exercise 6: Design a mixed-plan report

List each reason and observed transition.

**Approach.** Design a mixed-plan report listing each CPU node in an otherwise GPU plan, the reason given for fallback, and the transitions it created.

**Why it is correct here.** A report connects each fallback to its cause, guiding which rewrite or configuration change would help.

**A plausible wrong approach.** Reporting only the percentage of GPU operators hides which fallback is expensive. One fallback on a small lookup table may be harmless, while one on the widest projection can dominate the job.

**How to verify.** Generate the report from the executed plan and fallback log, and check each listed transition appears in the plan.

## Self-check answers

1. **What does support depend on in the plugin?** The operator, the expression, the data type and the configuration, so one aggregate can be supported for some types and not others.

2. **Why can a mixed plan be slower than expected?** It may pay row to columnar conversions and device transfers repeatedly around unsupported parts.

3. **How should CPU-only learners run Spark in this course?** Ordinary Spark with the GPU plugin disabled or absent.

## Reference observation

CPU-only baseline and per-operator fallback are modeled separately.

Asserted by `courses/cuda/spark/references/cuda-116_cpu.py`.
