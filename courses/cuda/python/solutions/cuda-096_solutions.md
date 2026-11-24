# cuda-096: explained solutions

These answers explain the six practice tasks. CPU reference programs are mathematical or semantic checks, not proof of CUDA execution.

## Exercise 1: Compute the validation metric

Mean squared errors 0,1,1 give 2/3.

**Approach.** Compute the validation MSE for predictions `[1, 2, 3]` against targets `[1, 3, 2]`: squared errors `0, 1, 1` sum to 2, divided by 3 gives `2/3`.

**Why it is correct here.** MSE averages squared errors over all validation examples. The reference computes this and asserts it is within `1e-12` of `2/3`.

**A plausible wrong approach.** Reporting the training loss in place of the validation metric mixes data used for fitting with data held out for evaluation.

**How to verify.** Run the reference and confirm the printed report lists `examples` 3 and `mse` about 0.6667.

## Exercise 2: Write the sample ledger

Track train validation and consumed counts.

**Approach.** Write a sample ledger with counts for training, validation and consumed examples, such as 3 validation examples evaluated and the number of training samples seen at checkpoint time.

**Why it is correct here.** Metrics depend on their denominators. A ledger makes it visible when an optimization changes how many examples were evaluated.

**A plausible wrong approach.** Accepting a candidate that is twice as fast but evaluates only half the held-out examples compares different metrics.

**How to verify.** Assert the validation count in each report equals the full held-out set size before comparing metrics.

## Exercise 3: Define a memory budget

Include weights state activations and reserve separately.

**Approach.** Define a memory budget with separate lines for weights, optimizer state, activations and allocator reserve, each in bytes for the chosen dtype and batch size.

**Why it is correct here.** Separate lines show which component grows when batch size or optimizer changes, and the reserve line acknowledges caching allocator behavior.

**A plausible wrong approach.** Giving a single total from a monitoring tool mixes reserved and live memory. It also hides which component to shrink when the budget is exceeded, such as switching optimizers or lowering the batch.

**How to verify.** Compare the budget with measured allocated memory at peak for one batch size. A gap larger than the reserve line means a component is missing from the ledger, often a framework workspace.

## Exercise 4: Design a restart comparison

Compare uninterrupted and resumed steps.

**Approach.** Design a restart comparison: run N steps uninterrupted, then run the same N steps with a save and resume midway, and compare final weights and losses.

**Why it is correct here.** Equal results show the checkpoint captures all state affecting training. Any divergence points to missing fields.

**A plausible wrong approach.** Testing only that the checkpoint loads without errors says nothing about continuation. A checkpoint missing momentum or sampler position loads cleanly and still diverges on the next step.

**How to verify.** Assert losses match step for step within tolerance and that weights agree at the end. Record the step at which any divergence first appears, since that step identifies the missing state.

## Exercise 5: Choose one optimization

Tie it to a measured bottleneck.

**Approach.** Choose one optimization tied to a measured bottleneck, such as removing a per-step host synchronization seen in a trace, and leave other settings fixed.

**Why it is correct here.** Linking the change to evidence makes the outcome interpretable: the bottleneck should shrink and outputs stay equal.

**A plausible wrong approach.** Applying a popular optimization without measuring may target a stage that is not the bottleneck. Mixed precision, for example, does little when the GPU sits idle waiting for host input.

**How to verify.** Compare traces before and after and confirm the metric and sample counts are unchanged. If the MSE or validation count changes, the optimization altered the computation and cannot be reported as a pure speedup.

## Exercise 6: State pending hardware evidence

Mark CPU and GPU results independently.

**Approach.** State hardware evidence separately: the report sets `backend` to `CPU reference` and `gpu_verified` to `False`, and lists the GPU checks still pending.

**Why it is correct here.** A trustworthy report never implies that a CPU run validated GPU behavior. Explicit fields prevent a reader from assuming coverage.

**A plausible wrong approach.** Leaving out the verification field lets readers assume the GPU path was tested. A later reader cannot then distinguish a validated deployment from a desk check.

**How to verify.** The reference asserts `not report["gpu_verified"]`. Only a real device run with recorded environment may set it to true.

## Reference observation

Three examples, MSE 2/3, GPU verification explicitly false.

The reference file is `courses/cuda/python/references/cuda-096_cpu.py`. It includes deterministic assertions. These assertions establish the supplied bounded CPU example; hardware execution and architecture-specific performance remain separate checks.
