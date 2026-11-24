# cuda-101: explained solutions

These answers explain the six practice tasks. CPU reference programs are mathematical or semantic checks, not proof of CUDA execution.

## Exercise 1: Count low-rank parameters

Rank times sum of dimensions.

**Approach.** Count low-rank adapter parameters as rank times the sum of dimensions: `8*(1024 + 1024) = 16384` for a 1024 by 1024 weight.

**Why it is correct here.** A low-rank update factors the change as a 1024 by 8 matrix times an 8 by 1024 matrix, so its parameters are `1024*8 + 8*1024`.

**A plausible wrong approach.** Computing rank times the product of dimensions, `8*1024*1024`, gives eight times the original matrix. That figure would make the adapter larger than the weight it adapts, which should immediately signal an error.

**How to verify.** The reference asserts `adapter == 16384`. In a framework, sum `numel()` over adapter parameters and compare.

## Exercise 2: Include base storage

Base parameters are not deleted.

**Approach.** Include base storage in the memory ledger: the 1048576 base parameters stay in memory, so the total is `1048576 + 16384`.

**Why it is correct here.** Adapters reduce trainable parameters, gradients and optimizer state, but the forward pass still needs the frozen base weights.

**A plausible wrong approach.** Budgeting memory from adapter parameters alone underestimates by the full base model. For this matrix the adapter is about 1.6 percent of the total, so the omitted base dominates the real footprint.

**How to verify.** The reference asserts `base + adapter > base`. Measured parameter memory should include the base.

## Exercise 3: Inspect optimizer membership

Only intended trainable tensors belong in optimizer state.

**Approach.** Inspect the optimizer's parameter groups and confirm only adapter tensors are present, such as by filtering `p.requires_grad`.

**Why it is correct here.** An optimizer built from `model.parameters()` includes frozen base weights, creating optimizer state for them even if gradients are absent.

**A plausible wrong approach.** Assuming freezing alone excludes parameters from the optimizer can waste memory. Some optimizers skip parameters whose `.grad` is None, but weight decay or other per-parameter bookkeeping may still allocate state, so membership should be explicit rather than implied.

**How to verify.** Count parameters in the optimizer groups and assert the count equals 16384. Also check that each base tensor reports `requires_grad == False`, so the two facts agree.

## Exercise 4: Compare sequence-length budgets

Attention intermediates and caches grow with sequence geometry.

**Approach.** Compare memory at two sequence lengths, such as 512 and 1024, since activations and attention intermediates grow with sequence geometry while parameters stay constant.

**Why it is correct here.** Activation memory grows at least linearly with sequence length and naive attention grows quadratically, so long sequences can exceed memory even with small adapters.

**A plausible wrong approach.** Assuming adapters make long-sequence fine-tuning cheap confuses parameter savings with activation savings. Gradients must still flow back through the frozen layers to reach adapters in earlier layers, so those activations are kept during the forward pass.

**How to verify.** Measure peak allocated memory at both lengths and check the growth against the ledger.

## Exercise 5: Design tiny offline training

Use generated tokens and bounded steps.

**Approach.** Design a tiny offline training run with generated token IDs, a small model or a few layers, and a bounded number of steps such as 20.

**Why it is correct here.** Synthetic tokens avoid licensing and download needs, and a small bounded run checks wiring and memory behavior safely.

**A plausible wrong approach.** Using a full public model and dataset for a first test risks long downloads and exhausting memory. A failure in that setting is also harder to localize, because data, model size and wiring all vary at once.

**How to verify.** Confirm the loss decreases on a repeated tiny batch, showing gradients reach the adapter.

## Exercise 6: Define held-out evaluation

Keep validation separate from fitting and tuning.

**Approach.** Keep a held-out evaluation set that is never used for fitting or hyperparameter tuning, and report its metric separately.

**Why it is correct here.** Fine-tuning can overfit small datasets quickly. Separate evaluation measures generalization.

**A plausible wrong approach.** Reporting the training loss as model quality overstates performance. Choosing the rank or learning rate by repeatedly looking at the evaluation set leaks it into tuning in the same way.

**How to verify.** Assert there is no overlap between training and evaluation example IDs, then report both metrics.

## Reference observation

Base 1,048,576 and adapter 16,384 parameters.

The reference file is `courses/cuda/python/references/cuda-101_cpu.py`. It includes deterministic assertions. These assertions establish the supplied bounded CPU example; hardware execution and architecture-specific performance remain separate checks.
